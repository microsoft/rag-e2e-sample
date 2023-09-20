# Import required libraries  
import os 
import openai
from dotenv import dotenv_values
from azure.core.credentials import AzureKeyCredential
from langchain.chat_models import AzureChatOpenAI
from azure.search.documents import SearchClient

from chatFunctions import chatBot

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

engine = "gpt-4-32k"
#engine = "gpt-35-turbo"
llm = AzureChatOpenAI(
    deployment_name=engine,
    openai_api_base=openai.api_base,
    openai_api_version=openai.api_version,
    openai_api_key=openai.api_key,
    openai_api_type = openai.api_type,
    temperature=0.0, verbose = True
)

## ACS 
numChunks = 10
search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)

## llm
human_query = " earning calls for Target"

template_qa_chain = """You are a chatbot having a conversation with a human. 
        Given the Context, Chat History, and Human Query, 
        answer without hallucinating. If you don't have the answer say "I don't have the answer" """

template_context_summarization =  """
        Summarize the context so it includes the details related to the human query. """

max_token_for_context = 16000


cb = chatBot(llm, search_client, max_token_for_context = max_token_for_context, 
                 template_qa_chain = template_qa_chain, template_context_summarization = template_context_summarization, 
                 numChunks= numChunks, vectorColName = "contentVector",
                 to_debug = False)