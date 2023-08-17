# Project

> This README explains the process of using native search on postgresql using Azure Flex and pgvector for search.


Please Move your documents to the `DATA\` directory in the repo. Then execute the `data_preprocessor.py` for converting to pdf. Make sure the git/ADO repo is as close to the root e.g. C:\ as possible, in order to avoid long filename issues with path on Windows (or even MacOS and Linux).

## Folder structure

```bash
 ├── DATA
 ├── Deployment
 │   └── streamlit_app
 │       ├── config.yaml
 │       ├── images
 │       ├── llm_app.py
 │       ├── main.py
 │       ├── example.env
 │       └── requirements.txt
 ├── Notebooks
 │   ├── mlruns
 │   ├── example.env
 │   ├── requirements.txt
 │   ├── step0_data_preprocessor.ipynb
 │   ├── step1_chunk_and_extract.ipynb
 │   ├── step1_chunk_and_extract.ipynb
 │   ├── step2_embed.ipynb
 │   ├── step3_db_data_insert_vectorsearch.ipynb
 │   ├── step4_retrieve_prompt_chain_design.ipynb
 │   ├── step5_mlflow_experimentation.ipynb
 │   ├── step6_mlflow_experimentation_jsonIO.ipynb
 │   └── requirements.txt
 ├── README.md
 └── ValidationSetOfQA

```

Before starting the project work, make sure to add keys to example.env and rename it as `llm_pgvector.env` in Notebooks as well as Deployment directories.

The repo consists of six steps that should be followed in the below order:
1. `Notebooks\step0_data_preprocessor.py` accesses the DATA\ word docs and converts to pdf to be used by the form recognizer step.
2. `Notebooks\step1_chunk_and_extract.ipynb` chunks and extracts client code and text and saves to csv files.
3. `Notebooks\step2_embed.ipynb` reads, embeds and saves to csv files.
4. `Notebooks\step3_db_data_insert_vectorsearch.ipynb` reads and inserts data into the postgresql database and shows examples of hybrid search.
5. `Notebooks\step4_retrieve_prompt_chain_design.ipynb` does design of hybrid search, retrieval, prompting, chaining and shows each step for getting generated answers to questions.
6. `Notebooks\step_5_mlflow_experimentation.ipynb` shows experiment examples and mlflow tracking.

For deployment, please `cd Deployment` and go over the `Deployment\README.md`.

As the maintainer of this project, please make a few updates:

- Improving this README.MD file to provide a great experience
- Updating SUPPORT.MD with content about this project's support experience
- Understanding the security reporting process in SECURITY.MD
- Remove this section from the README


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
