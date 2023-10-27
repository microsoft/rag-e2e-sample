# Import required libraries from LangChain and set up OpenAI
from langchain.llms import AzureOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.prompts import PromptTemplate
import openai
import os
from dotenv import dotenv_values
import tiktoken

##############################################################
###### QA chain with converational buffer memory #############
##############################################################
def qa_chain_ConversationBufferMemory(llm, prefix_template=None, to_debug=False):
    # Write a preprompt with context and query as variables
    if prefix_template is None:
        prefix_template = """
        You are a chatbot having a conversation with a human. 
        Given the Context, Chat History, and a Human Query, 
        create a final answer only using the Context. Don't hallucinate at all. """
        
    template = prefix_template + """
    Context: 
    {context}
    
    Chat History: 
    {chat_history}

    Human Query: {human_input}
    Chatbot:"""

    # Define a prompt template
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input", "context"], template=template
    )
    
    # Define Memory
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")
    
    # Define a chain
    qa_chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=to_debug)
    return qa_chain


##############################################################
###### QA chain with converational Summary memory #############
##############################################################
def qa_chain_ConversationSummaryMemory(llm, prefix_template=None, to_debug=False):
    # Write a preprompt with context and query as variables
    if prefix_template is None:
        prefix_template = """
        You are a chatbot having a conversation with a human. 
        Given the Context, Chat History, and a Human Query, 
        create a final answer. Don't hallucinate at all. If you don't have an answer, say "I don't know".
        """
        
    template = prefix_template + """
    Context: 
    {context}
    
    Chat History: 
    {chat_history}

    Human Query: {human_input}
    Chatbot:
    """

    # Define a prompt template
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input", "context"],
        template=template
    )
    
    #Define Memory
    
    memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", input_key="human_input")
    memory.prompt.template = """
    Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.

    Current summary:
    {summary}

    New lines of conversation:
    {new_lines}

    New summary:
    """
    
    # Define a chain
    qa_chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=to_debug)
    return qa_chain

################################################################
###### Summarize chain with user query and context #############
################################################################
def user_query_based_context_summarization(llm, prefix_template=None, to_debug=False):
    # Write a preprompt with context and query as variables
    if prefix_template is None:
        prefix_template = """
        Write a concise summary of the context so that it includes the details related to the human query.
        """
        
    template = prefix_template + """
    Context: 
    {context}
    
    Human Query: {human_input}
    Concise Summary:
    """

    # Define a prompt template
    prompt = PromptTemplate(
        input_variables=["human_input", "context"], template=template
    )    
  
    # Define a chain
    query_based_summary_chain = LLMChain(llm=llm, prompt=prompt, verbose=to_debug)
    return query_based_summary_chain

################################################################
###### Write a summary given multiple contexts #############
################################################################

def combine_docs(context_list, llm, to_debug=False, max_tokens=16000, user_query=None, prefix_template=None):
    """Given a list of documents, combine them into a single document with a max token limit."""

    ## When all the documents can be concatenated
    context_all = ""
    for i in context_list:
        context_all = context_all + i + "\n\n"

    if count_tokens(context_all) < max_tokens:
        return context_all

    ## When all the documents cannot be concatenated
    if user_query is None:
        user_query = ""

    query_based_summary_chain = user_query_based_context_summarization(llm,
        prefix_template=prefix_template,
        to_debug=to_debug
    )

    context_all = ""
    for i in context_list:
        context_all = context_all + i + "\n\n"

        ## If the context_all is greater than max_tokens, then summarize the context_all again
        if count_tokens(context_all) > max_tokens: 
            context_all = query_based_summary_chain.run({
                'context': context_all,
                'human_input': user_query
            })
    
    return context_all


##############################################################
###### Tokens #############
##############################################################
def count_tokens(string: str, encoding_name: str="gpt-4-32k") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

##############################################################
###### Get Prompt Template from csv  #############
##############################################################

def get_prompt_template(prompt_id, prompt_templates_name=None):
    """
    Retrieve LLM prompt template using prompt_id from a csv file.
    """
    if prompt_templates_name == None:
        prompt_templates_name = config['PROMPT_TEMPLATE_FILE']
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), prompt_templates_name))
    prompt = df[df['prompt_id'] == prompt_id]['prompt_template'].values[0]
    return prompt


