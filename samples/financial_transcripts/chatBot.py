# Import required libraries  
import os
import re
import openai
import sys  
from dotenv import dotenv_values
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents.models import Vector
sys.path.append("../..")   ## add directory above
from rag_skills.chatbotSkills import qa_chain_ConversationSummaryMemory, combine_docs


# Get the absolute path to the .env file
env_name = os.path.join(os.path.dirname(__file__), "llm.env")

# Load environment variables from the .env file
config = dotenv_values(env_name)

if len(config) == 0:
    env_name = os.path.join(os.path.dirname(__file__), "../../llm.env")
    config = dotenv_values(env_name)

    if len(config) == 0:
        raise Exception("No environment variables loaded. Please check the *.env file.")

#Azure OpenAI
openai.api_type = config["OPENAI_API_TYPE"] #"azure"
openai.api_key = config['OPENAI_API_KEY']
openai.api_base = config['OPENAI_API_BASE']
openai.api_version = config['OPENAI_API_VERSION']

## Cog Search
cogsearch_name = config["COGSEARCH_NAME"] 
index_name = config["COGSEARCH_INDEX_NAME"]
key = config["COGSEARCH_API_KEY"]
service_endpoint = "https://"+config["COGSEARCH_NAME"] + ".search.windows.net"

credential = AzureKeyCredential(key)

def createEmbeddings(text):
    response = openai.Embedding.create(input=text , engine=config["OPENAI_DEPLOYMENT_EMBEDDING"])
    embeddings = response['data'][0]['embedding']
    return embeddings

## Retrieves relevant content from Azure Cognitive Search (ACS)
def acs_retriever(search_client, query=None, queryEmbedding = None, 
                  colName=None, colVal=None, searchtype=None, numChunks=5, vectorColName="Embedding"):
    # query: user query
    # colName: List of column name to search in ACS columns
    # colVal: List of column values to search in ACS
    # searchtype options: "filter", "vector", "hybrid", filter vector", "filter hybrid"
    # vectorColName: Name of vector embedding in ACS

    if query is not None:
        vector = Vector(value=queryEmbedding, k=numChunks, fields=vectorColName)
  
    if colName == None: ## No filters
        if searchtype == None or searchtype == "vector": #(default vector)
            results = search_client.search(search_text=None, vectors= [vector])
        else: # hybrid
            results = search_client.search(search_text=query, vectors= [vector])
            
    else: ## Filters        
        filter_str = " and ".join(f"({key} eq '{value}')" for key, value in zip(colName, colVal))
        filter_str = f"({filter_str})"
        
        if query == None: #Pure filter
            results = search_client.search(search_text = None, filter = filter_str)
        elif searchtype == None or searchtype == "filter vector" or searchtype == "vector": # (default filter vector)
            results = search_client.search(search_text = None, vectors = [vector], filter = filter_str)
        else: # filter hybrid
            results = search_client.search(search_text = query, vectors = [vector], filter = filter_str)
         
    output = [result for result in results]
    return output

def queryParser(query):
    # Extract ticker using regular expression
    ticker_match = re.search(r'\bticker\s+(\w+)', query, re.IGNORECASE)
    ticker = ticker_match.group(1) if ticker_match else None

    # Extract year using regular expression
    year_match = re.search(r'\byear\s+(\d{2})', query, re.IGNORECASE)
    year = int(year_match.group(1)) if year_match else None

    # Extract quarter using regular expression
    quarter_match = re.search(r'\bquarter\s+(\d)', query, re.IGNORECASE)
    quarter = quarter_match.group(1) if quarter_match else None

    return ticker, str(year), quarter


######################################
## Chatbot
######################################

class chatBot:
    def __init__(
        self,
        llm,
        acs_search_client,
        max_token_for_context=16000, 
        template_qa_chain=None,
        template_context_summarization=None, 
        numChunks=10,
        vectorColName="contentVector",
        chunkColName="Chunk",
        to_debug=False
    ):
        
        # ACS
        self.search_client = acs_search_client
        self.numChunks = numChunks
        self.vectorColName = vectorColName
        self.chunkColName = chunkColName
        
        # LLM chain
        self.llm = llm
        self.max_token_for_context = max_token_for_context
        
        if template_qa_chain:
            self.template_qa_chain = template_qa_chain
        else: 
            self.template_qa_chain= """You are a chatbot having a conversation with a human. 
                                    Given the Context, Chat History, and Human Query, 
                                    answer without hallucinating. 
                                    If you don't have the answer say 'I don't have the answer'
                                    """
            
        if template_context_summarization:
            self.template_context_summarization = template_context_summarization
        else:
            self.template_context_summarization =  """Summarize the context so it includes 
                                                    the details related to the human query.
                                                    """
        
        # Memory chain
        self.qa_chain = qa_chain_ConversationSummaryMemory(
            prefix_template=self.template_qa_chain, 
            to_debug=to_debug,
            llm=self.llm
        )

        # Transcripts specific
        self.ticker = None
        self.year = None
        self.quarter = None

    
    def run(self, human_query):

        queryEmbedding = createEmbeddings(human_query)
        ############## Parse query
        ticker, year, quarter = queryParser(human_query)

        ## if user query doesn't contain ticker, year, and quarter, use the previous one
        if ticker != None:
            self.ticker = ticker
        if year != str(None):
            self.year = year
        if quarter != None:
            self.quarter = quarter

        ## If ticker, year, and quarter are not found, return error message
        if self.ticker == None or self.year == None or self.quarter == None:
            print(self.ticker, self.year, self.quarter)
            return "Sorry, please provide the ticker <INSERT>, year <INSERT>, and quarter <INSERT>. Example - ticker MSFT, quarter 3, year 23."
        
        ############### Retrieve from ACS
        output = acs_retriever(
            self.search_client,
            query=human_query, 
            queryEmbedding=queryEmbedding,
            colName=['Ticker', 'Year', 'Quarter'],
            colVal=[self.ticker, self.year, self.quarter], 
            searchtype=None,
            numChunks=self.numChunks,
            vectorColName=self.vectorColName
        )

        #################### Combine Context
        context_list = [i[self.chunkColName]  for i in output]
        
        context_all = combine_docs(
            context_list,
            to_debug=False,
            llm=self.llm, 
            max_tokens=self.max_token_for_context,
            user_query=human_query,
            prefix_template=self.template_context_summarization
        )

        ## Append Ticker, Year, Quarter to the context
        context_all = "\nTicker: " + self.ticker + "\nYear: " + self.year + "\nQuarter: " + self.quarter + "\n"+ context_all

        # Augment and Generate Answer
        # qa_chain below is a predefined chain with memory. It summarizes the chat history and augment to the context      
        answer = self.qa_chain.run({'context': context_all,'human_input': human_query})
        return answer
    
    
    def retrieveChatHistory(self):
        return self.qa_chain.memory.chat_memory
        
        
    



    