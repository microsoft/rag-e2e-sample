# Description: This file contains the logic for the LLM bot
import os
import openai
import pandas as pd
import pandas as pd
import numpy as np
import psycopg2, json
from typing import List, Optional
from dotenv import dotenv_values
from psycopg2 import pool
from psycopg2 import Error
from pgvector.psycopg2 import register_vector
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.prompts import PromptTemplate
from langchain.llms import AzureOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain

# Get the absolute path to the .env file in the streamlit_app subdirectory
env_name = os.path.join(os.path.dirname(__file__), "llm_pgvector.env")

# Load environment variables from the .env file
config = dotenv_values(env_name)

for key, value in config.items():
    os.environ[key] = value

# LOAD OpenAI configs
openai.api_type = config["OPENAI_API_TYPE"]
openai.api_key = config['OPENAI_API_KEY']
openai.api_base = config['OPENAI_API_BASE']
openai.api_version = config['OPENAI_API_VERSION']
print("ENV VARIABLES LOADED")

class TextFormatter(BaseLoader):
    """Load text files."""
    def __init__(self, text: str):
        """Initialize with file path."""
        self.text = text

    def load(self) -> List[Document]:
        """Load from file path."""
        metadata = {"source": ""}
        return [Document(page_content=self.text, metadata=metadata)]

def createEmbeddings(text):
    """Create embeddings for the question"""
    response = openai.Embedding.create(input=text,engine=config['OPENAI_DEPLOYMENT_EMBEDDING'])
    embeddings = response['data'][0]['embedding']
    return embeddings

def Parsefilter_idQuestion_llm(msg):
    "Parse the filter id and policy question from the user's raw message, using LLM, returns a dict"
    llm= AzureOpenAI(deployment_name=config['OPENAI_MODEL_COMPLETION'], model_name=config['OPENAI_MODEL_EMBEDDING'], temperature=0)
    parse_prompt_template = """Parse the filter_id from the user's message and the message as a policy_question, and return a json. User's message may miss a question mark, have typos or punctuations. Fix these while parsing. 
    message: {msg}"""
    
    PARSE_PROMPT = PromptTemplate(
        input_variables=["msg"],
        template=parse_prompt_template,
        )
    print("Parsing filter id and policy question...")
    chain = LLMChain(llm=llm, prompt=PARSE_PROMPT)
    ans = chain.run({"msg": msg})
    print(f"Answer:{ans}")
    return json.loads(ans)

def Parsefilter_idQuestion_regex(msg):
    """Parse the filter id and policy question from the user's raw message using regex"""
    import re
    match = re.search(r"filter id: (\w+)", msg)
    if match:
        filter_id = match.group(1)
        return filter_id
    else:
        return "Please provide filter id as filter id: <filter id>. Then, the question."

def retrieve_k_chunk(retrieve_k, questionEmbedding, filter_id1_val):
    """Search and Retrieve the top k chunks from the database, given the question embedding and filter id"""
    
    # LOAD DB configs
    host = config["HOST"]
    dbname = config["DBNAME"]
    user = config["USER"]
    password = config["PASSWORD"]
    sslmode  = config["SSLMODE"]

    # Build a connection string from the variables
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    connection = psycopg2.connect(conn_string)
    # Create a cursor after the connection
    # Register 'pgvector' type for the 'embedding' column
    register_vector(connection)
    cursor = connection.cursor()
    print("filter_id_1:", filter_id1_val)
    
    table_name1 = 'filter_id_1'
    table_name2 = 'ChunksEmbedding'
    select_docid_query = f"SELECT DocId FROM {table_name1} WHERE filter_id_1 = '{filter_id1_val}'"
    cursor.execute(select_docid_query)
    next_result = cursor.fetchone() # Retrieve the docid corresponding to the filter id
   
    if next_result is None: # if there are no chunks corresponding to the filter id
        top_rows = None
    else: # look for the chunks relevant to the question in the document docid
        doc_id = next_result[0]
        print('docid:', doc_id)
        select_query = f"SELECT Id FROM {table_name2} where DocId = '{doc_id}' ORDER BY embedding <-> %s LIMIT {retrieve_k}"
        cursor = connection.cursor()
        cursor.execute(select_query, (np.array(questionEmbedding),))
        results = cursor.fetchall()
        top_ids = []
        for i in range(len(results)):
            top_ids.append(int(results[i][0]))

        # Rollback the current transaction
        connection.rollback()
        format_ids = ', '.join(['%s'] * len(top_ids))
        sql = f"SELECT CONCAT('PageNumber: ', PageNumber, ' ', 'LineNumber: ', LineNumber, ' ', 'Text: ', Chunk) AS concat FROM {table_name2} WHERE id IN ({format_ids})"

        # Execute the SELECT statement
        try:
            cursor.execute(sql, top_ids)    
            top_rows = cursor.fetchall()
        except (Exception, Error) as e:
            print(f"Error executing SELECT statement: {e}")
        finally:
            cursor.close()
        
    print('top_rows:', top_rows)

    return top_rows

def get_answer(raw_msg):
    """Given the raw message from the user, parse the filter id and policy question, retrieve the top k chunks from the database, and return the answer to the policy question"""
    
    print("raw_msg:", raw_msg)
    #filter_id = Parsefilter_idQuestion_regex(raw_msg)
    #msg = raw_msg
    parsed_dict = Parsefilter_idQuestion_llm(raw_msg)
    print(parsed_dict)
    msg = parsed_dict['policy_question']
    filter_id = parsed_dict['filter_id']
    
    print('filter_id:', filter_id)
    questionEmbedding = createEmbeddings(msg)
    retrieve_k = 3

    top_rows = retrieve_k_chunk(retrieve_k, questionEmbedding, filter_id)
    print(top_rows)
    if top_rows:
        context = ""
        for row in top_rows:
            context += row[0]
            context += "\n"
    else:
        return "No documents were found corresponding to the supplied filter id {}. Please verify the filter id and contact customer representative. ".format(filter_id)
    llm= AzureOpenAI(deployment_name=config['OPENAI_MODEL_COMPLETION'], model_name=config['OPENAI_MODEL_EMBEDDING'], temperature=0)

    loader = TextFormatter(context)
    print("Context Retrieved: {}".format(context))

    ### Question Prompt Template
    question_prompt_template = """Use the context below to answer the question. The question may have typo or missing question mark. Consider those while answering.
    context: {context}
    question: {question}
    If the context contains "No documents were found", indicate that to the user, and also ask them to verify the filter id and contact support representative. Otherwise, answer the question only using the context and cite the PageNumber and LineNumber in reference to the answer."""
    
    QUESTION_PROMPT = PromptTemplate(
        template=question_prompt_template, input_variables=["context", "question"]
        )
    print("Sending prompt...")
    chain = load_qa_chain(llm, chain_type="stuff", prompt=QUESTION_PROMPT)
    ans = chain({"input_documents": loader.load(), "question": msg}, return_only_outputs=True)
    print(ans)

    return ans['output_text'][2:]

    def get_answer_dummy(msg):
        """Dummy bot to test the API
        """
    return "Dummy bot: I'm a dummy bot"

if __name__=="__main__":

    question = "What is the policy for filter id abc?"
    ans = get_answer(question)
    print(ans)
