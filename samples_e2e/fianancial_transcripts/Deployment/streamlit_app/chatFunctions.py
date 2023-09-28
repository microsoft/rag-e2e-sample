# Import required libraries  
import os
import re
import pandas as pd
import json  
import openai  
from dotenv import load_dotenv
from dotenv import dotenv_values
from tenacity import retry, wait_random_exponential, stop_after_attempt  
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import Vector  
from azure.search.documents.indexes.models import (  
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    PrioritizedFields,  
    SemanticField,  
    SearchField,  
    SemanticSettings,  
    VectorSearch,  
    HnswVectorSearchAlgorithmConfiguration
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
from chatbot_with_memory import qa_chain_ConversationSummaryMemory, combine_docs, summary_chain_with_user_query

env_name = "../../llm.env" # change to use your own .env file
config = dotenv_values(env_name)

#Azure OpenAI
openai.api_type = config["OPENAI_API_TYPE"] #"azure"
openai.api_key = config['OPENAI_API_KEY']
openai.api_base = config['OPENAI_API_BASE']
openai.api_version = config['OPENAI_API_VERSION']

## Cog Search
cogsearch_name = config["COGSEARCH_NAME"] #TODO: fill in your cognitive search name
index_name = config["COGSEARCH_INDEX_NAME"] #TODO: fill in your index name: must only contain lowercase, numbers, and dashes
key = config["COGSEARCH_API_KEY"] #TODO: fill in your api key with admin key
service_endpoint = "https://"+config["COGSEARCH_NAME"] + ".search.windows.net"

credential = AzureKeyCredential(key)

def createEmbeddings(text):
    response = openai.Embedding.create(input=text , engine=config["OPENAI_DEPLOYMENT_EMBEDDING"])
    embeddings = response['data'][0]['embedding']
    return embeddings

def acs_retriever(search_client, query = None, colName = None, colVal= None, searchtype = None, numChunks = 5, vectorColName = "contentVector"):
    # query: user query
    # colName: List of column name to search in ACS columns
    # colVal: List of column values to search in ACS
    # searchtype options: "filter", "vector", "hybrid", filter vector", "filter hybrid"
    #vectorColName: Name of vector embedding in ACS

    if query is not None:
        vector = Vector(value=createEmbeddings(query), k=numChunks, fields=vectorColName)
  
    if colName == None: ## No filters
        if searchtype == None or seachtype == "vector": #(default vector)
            results = search_client.search(search_text=None,vectors= [vector])
        else: # hybrid
            results = search_client.search(search_text=query,vectors= [vector])
            
    else: ## Filters        
        filter_str = " and ".join(f"({key} eq '{value}')" for key, value in zip(colName, colVal))
        filter_str = f"({filter_str})"
        # print(filter_str)
        
        if query == None: #Pure filter
            results = search_client.search(search_text = None, filter = filter_str)
            
        elif searchtype == None or searchtype == "filter vector" or searchtype == "vector": #(default filter vector)
            results = search_client.search(search_text = None, vectors = [vector], filter = filter_str)
            
        else: # filter hybrid
            results = search_client.search(search_text = query, vectors = [vector], filter = filter_str)
         
    output = [result for result in results]
    return output

## 
def queryParser(query):
    # Extract ticker using regular expression
    ticker_match = re.search(r'\bticker\s+(\w+)', query, re.IGNORECASE)
    ticker = ticker_match.group(1) if ticker_match else None

    # Extract year using regular expression
    year_match = re.search(r'\byear\s+(\d{4})', query, re.IGNORECASE)
    year = int(year_match.group(1)) if year_match else None

    # Extract quarter using regular expression
    quarter_match = re.search(r'\bquarter\s+(Q\d)', query, re.IGNORECASE)
    quarter = quarter_match.group(1) if quarter_match else None

    return ticker, str(year), quarter


## ####################################
## Chatbot
######################################

class chatBot:
    def __init__(self, llm, acs_search_client, max_token_for_context = 16000, 
                 template_qa_chain = None, template_context_summarization = None, 
                 numChunks= 10, vectorColName = "contentVector",
                 to_debug = False):
        
        #ACS
        self.search_client = acs_search_client
        self.numChunks = numChunks
        self.vectorColName = vectorColName
        
        #llm chain
        self.llm = llm
        self.max_token_for_context = max_token_for_context
        
        if template_qa_chain:
            self.template_qa_chain = template_qa_chain
        else: 
            self.template_qa_chain= """You are a chatbot having a conversation with a human. 
                                    Given the Context, Chat History, and Human Query, 
                                    answer without hallucinating. 
                                    If you don't have the answer say "I don't have the answer" """
            
        if template_context_summarization:
            self.template_context_summarization = template_context_summarization
        else:
            self.template_context_summarization =  """Summarize the context so it includes 
                                                        the details related to the human query. """
        
        self.qa_chain = qa_chain_ConversationSummaryMemory(prefix_template = self.template_qa_chain, 
                                                           to_debug = to_debug, llm = self.llm)
        
#         answer = qa_chain.run({'context': context_all,'human_input': human_query})
              
    
        
    def run(self, human_query):
        ticker, year, quarter = queryParser(human_query)
        
        ## acs
        output = acs_retriever(self.search_client, query = human_query, 
                               colName = ['Ticker', 'Year', 'Quarter'], colVal= [ticker, year, quarter], 
                               searchtype = None, numChunks = self.numChunks, vectorColName = self.vectorColName)
        context_list = [i['FileContentsChunked'] for i in output]
        
        
        context_all = combine_docs(context_list, to_debug = False, llm = self.llm, 
                           max_tokens = self.max_token_for_context, user_query = human_query,
                                   prefix_template = self.template_context_summarization)
        
        answer = self.qa_chain.run({'context': context_all,'human_input': human_query})
        return answer
    
    def retrieveChatHistory(self):
        return self.qa_chain.memory.chat_memory
        
        
    



    