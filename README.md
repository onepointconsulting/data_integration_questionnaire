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