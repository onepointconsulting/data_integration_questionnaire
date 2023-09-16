# Data Integration Questionnaire

This is a reverse chatbot that asks the users questions about data integration practices and then gives advice based on a body of knowledge.

## Setup

We suggest to use [Conda](https://docs.conda.io/en/latest/) to manage the virtual environment and then install poetry.

```
conda activate base
conda remove -n data_integration_questionnaire --all
conda create -n data_integration_questionnaire python=3.11
conda activate data_integration_questionnaire
pip install poetry
```

## Installation

```
poetry install
poetry add --editable \\wsl.localhost\Ubuntu\home\gilf\projects\chainlit-sept-2023\backend\dist\chainlit-0.6.410-py3-none-any.whl
```

## Running

```
chainlit run ./data_integration_questionnaire/ui/integration_questionnaire_chainlit.py --port 8080
```

## Configuration

```
OPENAI_API_KEY=<open_ai_key>
# OPENAI_MODEL=gpt-3.5-turbo-0613
OPENAI_MODEL=gpt-4-0613
# OPENAI_MODEL=gpt-4-32k-0613
REQUEST_TIMEOUT=140

VERBOSE_LLM=true
LANGCHAIN_CACHE=false

UI_TIMEOUT = 2400

# Email related
MAIL_FROM_PERSON=Gil Fernandes
MAIL_USER=gil.fernandes@onepointltd.com
MAIL_PASSWORD=jvjeudtliwwmqqlk
MAIL_FROM=gil.fernandes@onepointltd.com
MAIL_SERVER=smtp.gmail.com:587

# General stuff
PROJECT_ROOT=C:/development/playground/langchain/data_integration_questionnaire
QUESTION_CACHE_FOLDER=c:/tmp/data_integration_questionnaire/cache

# PDF Related
WKHTMLTOPDF_BINARY=C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe
TEMPLATE_LOCATION=C:/development/playground/langchain/data_integration_questionnaire/templates
PDF_FOLDER=C:/tmp/data_integration_questionnaire/pdfs

# Whether to show the task list or not
TASKLIST=false

# The knowledge base path
KNOWLEDGE_BASE_PATH=C:/development/playground/langchain/data_integration_questionnaire/docs/knowledge_base.txt

# UI
SHOW_CHAIN_OF_THOUGHT=true

# Embedding related
RAW_TEXT_FOLDER=C:\development\playground\langchain\data_integration_questionnaire\docs\raw_text
EMBEDDINGS_PERSISTENCE_DIR=C:\development\playground\langchain\data_integration_questionnaire\embeddings
EMBEDDINGS_CHUNK_SIZE=2500
SEARCH_RESULTS_HOW_MANY=4

```