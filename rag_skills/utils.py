import tiktoken
import pandas as pd

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