# ACS + Chatbot

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


# Deployment

1. Run locally

```
streamlit run main.py --server.port 8000
```

2. Build docker. Since the chatBot.py and environment.yaml files are at the parent directory, the Dockerfile only works if you run the command from the parent directory.   
```
docker build -t bot:v1 -f samples_e2e/financial_transcripts/Dockerfile .
docker run --rm -p 8000:8000 bot:v1
```

Go to an open web browser and type `localhost:8000`




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
