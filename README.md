# Retrieval Augmentation Generation (RAG) patterns

Following the launch of ChatGPT, many companies express a keen interest in developing search engines in the style of ChatGPT, tailored to their specific datasets. To address this challenge, Retrieval Augmentation Generation (RAG) has emerged as a popular solution. RAG comprises a three-step process: 

First, pertinent information (referred to as context) is retrieved from the database based on the human query
Then, this context is enhanced and integrated with the human query.
Finally, the enriched context is presented to GPT-style models to generate a response.

We've observed that the RAG approach can take on various forms. For instance, certain problems necessitate a memory of past conversations, while in others, the database may offer an extensive context that surpasses the limits of LLM prompts. We've devised solutions for these challenges, which we refer to as skills. The objective of this repository is to offer a compendium of these skills, showcase how each can be applied independently, and also present some end-to-end examples demonstrating their utilization.

Please note that in addition to this repository, we maintain others that focus on different aspects of RAG.

1. This repo would illustrate the use of Azure Cognitive Search (ACS) as a vector store. For those interested in employing other databases such as Postgres, AzureSQL, MongoDB, please refer to this [repository](https://github.com/microsoft/AzureDataRetrievalAugmentedGenerationSamples).

2. For deployment, We employ [Streamlit](https://streamlit.io/). Alternatively, other options such as deploying through Azure Web App using docker containers or creating a chatbot in Microsoft Teams can be explored in this [repository](https://github.com/microsoft/QnABot-for-FabricDocs.git).

## Skills

This repo contains a collection of skills available in `rag_skills/chatbotSkills.py` and their code samples for individual skills: 

1. Chatbot with memory functionality: `chatbotSkills.py` contains functions for chatbot enabled with memory capabilities. Two distinct types of memory skills are available:

    a. `qa_chain_ConversationBufferMemory`: This skill leverages the entire chat history, context and human queries for generating responses. It's recommended for shorter conversations.

    b. `qa_chain_ConversationSummaryMemory`: This skill uses the condensed version of chat history, context and human queries for generating responses. It's preferable for longer conversations.

2. `user_query_based_context_summarization`: Summarize or extract the relevant information from the context based on the user query. 

3. `combine_docs`: This skill is useful when search retrieves multiple contexts from the database that cannot fit into a single language model call. It combines multiple contexts while retaining the information that is relevant to user query. It also ensures that the total context token count remains below a certain threshold. 

> NOTE: Skills are being updated as code snippets faster than this repo at [rag_skills](https://github.com/microsoft/rag_skills)

## End2End Sample for Different RAG patterns

This repository also includes one end-to-end sample centered around financial transcripts. Please note that the plan is to incorporate additional samples that showcase various RAG patterns in the future.


| Sample name                       | Description                         | Tech Stack                                                       |
| --------------------------------- | ----------------------------------- | ---------------------------------------------------------------- |
| Financial Earnings calls assistant | Summarizes and Q&A on earning calls | ACS, deployed on streamlit        |


## How to use?

1. Lightweight examples of various skills are provided in `rag_skills/demonstrateSkills.ipynb`
2. End2End samples are at `samples/` folder. Please follow the README in the folder itself.

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






