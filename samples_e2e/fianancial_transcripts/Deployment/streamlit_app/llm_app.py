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
env_name = os.path.join(os.path.dirname(__file__), "llm_env.env")

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


def createEmbeddings(question):
    """Create embeddings for the question"""
    response = openai.Embedding.create(input=question,engine=config['OPENAI_DEPLOYMENT_EMBEDDING'])
    embeddings = response['data'][0]['embedding']
    return embeddings

def parse_msg_regex(msg):
    """
    Parse the ticker, quarter and question from the raw message
    """
    import re
    match_ticker = re.search(r"ticker: (\w+)", msg)
    match_quarter = re.search(r"quarter: FY23Q(\w+)", msg)
    if match_ticker and match_quarter:
        ticker = match_ticker.group(1)
        quarter = match_quarter.group(1)
        question = msg
    else:
        return "Please provide ticker and quarter as in: \" ticker: <ticker id>. quarter (e.g. FY23Q1): <quarter> Then, the question."
    return ticker, quarter, question

def search_db(ticker, quarter, question, k=5):
    """
    Search and Retrieve the top k chunks from the database, given the question and filters: ticker and quarter
    """
    
    import psycopg2
    from psycopg2 import pool
    from psycopg2 import Error
    from pgvector.psycopg2 import register_vector
    
    filter_col_1 = "Ticker"
    filter_col_2 = "Quarter"
    host = config["HOST"]
    dbname = config["DBNAME"] 
    user = config["USER"] 
    password = config["PASSWORD"] 
    sslmode = config["SSLMODE"] 
    table_name = config["TABLE_NAME"]
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

    questionEmbedding = createEmbeddings(question)

    postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20,conn_string)
    if (postgreSQL_pool):
        print("Connection pool created successfully")

    # Use getconn() to get a connection from the connection pool
    connection = postgreSQL_pool.getconn()
    cursor = connection.cursor()

    #filter based on ticker and quarter
    connection = psycopg2.connect(conn_string)
    # Create a cursor after the connection
    # Register 'pgvector' type for the 'embedding' column
    register_vector(connection)
    cursor = connection.cursor()

    #TODO filter by quarter!

    select_query = f"SELECT Id FROM {table_name}  WHERE {filter_col_1} = '{ticker}' AND {filter_col_2} = '{quarter}' ORDER BY Embedding <-> %s LIMIT {k}"
    cursor = connection.cursor()
    cursor.execute(select_query, (np.array(questionEmbedding),))
    results = cursor.fetchall()   
    #print(results)
    top_ids = []
    for i in range(len(results)):
        top_ids.append(int(results[i][0]))
    #print(top_ids)

    # Rollback the current transaction
    connection.rollback()
    format_ids = ', '.join(['%s'] * len(top_ids))
    sql = f"SELECT CONCAT('PageNumber: ', PageNumber, ' ', 'Text: ', Chunk) AS concat FROM {table_name} WHERE id IN ({format_ids})"
    context = "" #empty for now
    # Execute the SELECT statement
    try:
        cursor.execute(sql, top_ids)    
        top_rows = cursor.fetchall()
        context = ""
        for row in top_rows:
            context += row[0]
            context += "\n"
    except (Exception, Error) as e:
        print("no search results corresponding to the ticker: {} and quarter: {}".format(ticker, quarter)) 
        print("-----------------------------------------")
        print(f"Error executing SELECT statement: {e}")
    #print(context)
    return context
    
def get_answer_from_context(context, question):
    """
    Given the context and question, return the answer to the question
    """
    llm= AzureOpenAI(deployment_name=config['OPENAI_MODEL_COMPLETION'], model_name=config['OPENAI_MODEL_EMBEDDING'], temperature=0)
    loader = TextFormatter(context)
    ### Question Prompt Template
    question_prompt_template = """Use the context below to answer the question. The question may have typo or missing question mark. Consider those while answering.
    context: {context}
    question: {question}
    If the context is empty, indicate it to the user. Otherwise, answer the question only using the context and cite the PageNumber and LineNumber in reference to the answer."""
    
    QUESTION_PROMPT = PromptTemplate(
        template=question_prompt_template, input_variables=["context", "question"]
        )
    chain = load_qa_chain(llm, chain_type="stuff", prompt=QUESTION_PROMPT)
    ans = chain({"input_documents": loader.load(), "question": question}, return_only_outputs=True)

    return ans['output_text'][2:]    

class TextFormatter(BaseLoader):
    """Load text files."""
    def __init__(self, text: str):
        """Initialize with file path."""
        self.text = text

    def load(self) -> List[Document]:
        """Load from file path."""
        metadata = {"source": ""}
        return [Document(page_content=self.text, metadata=metadata)]

def llm_chain(raw_msg):
    """Given the raw message from the user, parse the filter id and policy question, retrieve the top k chunks from the database, and return the answer to the policy question"""
    #llm_app_config = define_llm_app_config(config)
    ticker, quarter, question = parse_msg_regex(raw_msg)
    context = search_db(ticker, quarter, question, k=3)
    answer = get_answer_from_context(context, question)
 
    return answer

if __name__=="__main__":
    question = "ticker: MSFT, quarter: FY23Q2. What were the biggest revenues? please cite numbers."
    print('question: {}'.format(question))
    #ans = parse_msg_regex(question)
    #ans = search_db("MSFT", "FY23Q1", question, k=3)
    #ans = search_db("MSFT", "2", question, k=3)
    ans = llm_chain(question)

    print('answer: {}'.format(ans))
