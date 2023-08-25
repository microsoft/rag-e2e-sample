# ACS + Chatbot

This branch provides following features: 
1. Making ACS index and uploading data to ACS using python sdk.
check Preprocessing_ACS_withsearch.ipynb

2. Chatbot with memory
chatbot_with_memory.py contains the functions with memory. 
There are two types of chains with memory:
a. qa_chain_ConversationBufferMemory: This chain saves the chat history and provides full chat history, along with context and human query to answer questions. It is recommended for small chats

b. qa_chain_ConversationSummaryMemory: This chain saves the chat history. It uses context, summary of the chat history, and human query to answer questions. We can retrieve all chat messages if use this chain and its associated memory.  It is recommended for long chats.

3. Combine various contexts so overall context token is less than some number
Sometimes vector search retrieves many contexts and its not possible to fit in one llm call. 
So, this feature combine all the context taking a user_query into consideration so relevant information is not lost.
combine_docs in chatbot_with_memory.py does that. 

4. acs_retriever: 
acs retriever retrieves data from ACS with following options:
options: "filter", "vector", "hybrid", filter vector", "filter hybrid"
  acs_retriever in chatFunctions.py does that

5. Chtabot with:
a. memory, b. context that fits in the token limit, c. ACS retrivers with filter/vector-hybrid search

chatBot class in chatFunctions.py

# How to test?
0. Go to ACS_example folder
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
