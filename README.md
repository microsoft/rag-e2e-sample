# Retrieval Augmentation Generation (RAG) patterns

This repo contains a collection of end to end samples that demonstrates various RAG patterns. It also provides feature specific code.

In general, RAG process can be decomposed into three major steps: 
1. Storing and retrieving documents from vector database: For this repo, we are using Azure cognitive search (ACS) service to store and retreive document. We have another repo that has other databases. 

2. Designing a chatbot: Chatbot can have many features such as memory, context retrieval, etc. This repo mainly focuses on different approaches to design a chatbot 

3. Deploying a chatbot: We are currently using streamlit just for demonstration of end-2-end functionality. However, there are many other ways in whic hthe chatbot can be deployed. 



| Sample name                       | Description                         | Tech Stack                                                       |
| --------------------------------- | ----------------------------------- | ---------------------------------------------------------------- |
| Financial Earnings calls assistant | Summarizes and Q&A on earning calls | PostGres Flex, Native vector search, deployed as a webapp        |
| [Fabric chatbot](https://github.com/microsoft/QnABot-for-FabricDocs.git)                    | Helps users on fabric documentation | Blob, Fabric One Lake, Azure Cognitive Search, deployed in Teams |
| ...                                  |                                     |                                                                  |

This branch provides following features: 
1. ACS index creation and data upload using python sdk.

    check Preprocessing_ACS_withsearch.ipynb

2. Chatbot with memory functionality: The file "chatbot_with_memory.py" contains functions for chatbot with memory capabilities. Two distinct types of memory chains are available:

    a. qa_chain_ConversationBufferMemory: This chain uses the entire chat history,context and human queries for generating responses. It's recommended for shorter conversations.

    b. qa_chain_ConversationSummaryMemory: This chain uses the condensed version of chat history, context and human queries for generating responses. It's preferable for longer conversations.


3. Multiple contexts combination: combines multiple contexts while ensuring that the total context token count remains below a certain threshold, and considering human query to retain relevant information. Useful when the vector search retrieves numerous contexts that cannot fit into a single language model call. 

    check "combine_docs" in chatbot_with_memory.py does that. 


4. acs_retriever: 
acs retriever retrieves data from ACS with following options:
options: "filter", "vector", "hybrid", filter vector", "filter hybrid"
      check acs_retriever in chatFunctions.py

5. Comprehensive Chtabot with:

    a. memory, 
    
    b. context within token limit, 
    
    c. ACS retrivers with filter/vector-hybrid search

    chatBot class in chatFunctions.py




# How to test?
0. Open ACS_example folder
1. Open Preprocessing_ACS_withsearch.ipynb and run it
2. Open chatBot.ipynb to run chatbot and its features


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.






