import os
import openai
import pandas as pd
import numpy as np
import json
from typing import List, Optional
import requests
from dotenv import dotenv_values
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.llms import AzureOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate
import tiktoken
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import Vector  
from langchain.callbacks import get_openai_callback
import time
import re
import sys
try:
    from chatBot import chatBot, createEmbeddings, acs_retriever, queryParser
    from chatbotSkills import count_tokens
except:
    sys.path.insert(0, '../..')
    from chatBot import chatBot, createEmbeddings, acs_retriever, queryParser
    from chatbotSkills import count_tokens
import pdb

VERBOSE = True
TEMPERATURE = 0.0
TOP_P = 1.0
NUM_CHUNKS = 10
MAX_TOKEN_FOR_CONTEXT = 27000
VECTOR_COL_NAME = "Embedding"
CHUNK_NAME = "Chunk"

TEMPLATE_QA_CHAIN = """You are a chatbot having a conversation with a human. 
        Given the Context, Chat History, and Human Query, 
        answer without hallucinating. If you don't have the answer say "I don't have the answer" """

TEMPLATE_CONTEXT_SUMMARIZATION =  """
        Summarize the context so it includes the details related to the human query. """

# Get the absolute path to the .env file
env_name = os.path.join(os.path.dirname(__file__), "llm.env")

# Load environment variables from the .env file
config = dotenv_values(env_name)

if len(config) == 0:
    env_name = os.path.join(os.path.dirname(__file__), "../../llm.env")
    config = dotenv_values(env_name)

    if len(config) == 0:
        raise Exception("No environment variables loaded. Please check the *.env file.")

for key, value in config.items():
    os.environ[key] = value

# LOAD OpenAI configs
openai.api_type = config["OPENAI_API_TYPE"]
openai.api_key = config['OPENAI_API_KEY']
openai.api_base = config['OPENAI_API_BASE']
openai.api_version = config['OPENAI_API_VERSION']
print("ENV VARIABLES LOADED")

# Model choice
DEPLOYMENT_NAME = config['OPENAI_DEPLOYMENT_COMPLETION']

## Azure cognitive search
cogsearch_name = os.getenv("COGSEARCH_NAME")
index_name = os.getenv("COGSEARCH_INDEX_NAME")
cogsearch_api_key = os.getenv("COGSEARCH_API_KEY")
service_endpoint = "https://" + config["COGSEARCH_NAME"] + ".search.windows.net"

credential = AzureKeyCredential(cogsearch_api_key)
search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)

optional_params = {
    'top_p': TOP_P,
}

llm = AzureChatOpenAI(
    deployment_name=DEPLOYMENT_NAME,
    openai_api_base=openai.api_base,
    openai_api_version=openai.api_version,
    openai_api_key=openai.api_key,
    openai_api_type = openai.api_type,
    temperature=TEMPERATURE,
    model_kwargs=optional_params,
    verbose=VERBOSE,
)

cb = chatBot(
    llm,
    search_client,
    max_token_for_context=MAX_TOKEN_FOR_CONTEXT, 
    template_qa_chain=TEMPLATE_QA_CHAIN,
    template_context_summarization=TEMPLATE_CONTEXT_SUMMARIZATION, 
    numChunks=NUM_CHUNKS,
    vectorColName=VECTOR_COL_NAME,
    chunkColName=CHUNK_NAME,
    to_debug=VERBOSE
)

def get_answer(msg):
    ticker, year, quarter = queryParser(msg)

    parsed_info = []
    if ticker != None and year != None and quarter != None:
        parsed_info.append({"ticker": ticker, "year": year, "quarter": quarter})

    # Error handling
    if "clear memory" in msg.lower():
        cb.qa_chain.memory.clear()
        return "Memory cleared."
    elif len(parsed_info) == 0 and len(cb.qa_chain.memory.chat_memory.messages) == 0:
        return "Sorry, please provide the ticker <INSERT>, year <INSERT>, and quarter <INSERT> in your ask so I can retrieve from the vector database. Example - ticker: MSFT, quarter: 3, year: 23. If you are still receiving this error, try changing the details of your ask because the similarity might not be surfacing many results within the database."
    elif len(parsed_info) > 0 and len(cb.qa_chain.memory.chat_memory.messages) == 0:
        # First retrieve 
        context_all = cb.retrieve_first(msg, ticker, year, quarter)
    elif len(parsed_info) > 0 and len(cb.qa_chain.memory.chat_memory.messages) > 0:
        # Retrieve new context, but continue conversation
        context_all = cb.retrieve_again(msg, ticker, year, quarter)
    elif len(parsed_info) == 0 and len(cb.qa_chain.memory.chat_memory.messages) > 0:
        # Continue using existing context
        context_all = cb.context_all
        pass
    else:
        return "SOMETHING ELSE HAPPENED"
    
    ans = cb.qa_chain.run(
        {
            'context': context_all,
            'human_input': msg
        }
    )

    return ans


if __name__ == '__main__':
    question = """what are the top 3 themes in the earnings call transcripts from ticker MSFT for the quarter 1 in year 23?
    """
    
    start = time.time()
    ans = get_answer(question)
    end = time.time()
    print(ans)
    print("Time elapsed: {}".format(end-start))
    
    result_num_tokens = count_tokens(ans)
    print("Response num tokens: {}".format(result_num_tokens))

    ans = get_answer("Who were the speakers about those themes?")
    print(ans)