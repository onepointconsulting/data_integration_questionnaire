# Data Integration Questionnaire

This is a reverse chatbot that asks the users questions about data integration practices and then gives advice based on a body of knowledge.

## Setup

We suggest to use [Conda](https://docs.conda.io/en/latest/) to manage the virtual environment and then install poetry.

```
conda create -n data_integration_questionnaire python=3.11
conda activate data_integration_questionnaire
pip install poetry
```

## Installation

```
poetry install
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
REQUEST_TIMEOUT=120

VERBOSE_LLM=true
LANGCHAIN_CACHE=false

UI_TIMEOUT = 1200

# Email related
MAIL_FROM_PERSON=<name of person>
MAIL_USER=<email sender>
MAIL_PASSWORD=<Gmail app password or password>
MAIL_FROM=<email sender>
MAIL_SERVER=<smtp mail server, like smtp.gmail.com:587>

```