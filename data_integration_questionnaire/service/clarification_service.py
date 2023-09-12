from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain import LLMChain
from langchain.chains.openai_functions import create_structured_output_chain

from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.log_init import logger
from data_integration_questionnaire.model.openai_schema import Clarifications

from data_integration_questionnaire.toml_support import read_prompts_toml

INPUT_VAR_QUESTIONS = "questions"

prompts = read_prompts_toml()

section = prompts["clarifications"]

def prompt_factory_clarifications() -> ChatPromptTemplate:
    human_message = section["human_message"]
    prompt_msgs = [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template=section["system_message"], input_variables=[]
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=human_message,
                input_variables=[INPUT_VAR_QUESTIONS],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=prompts["general_messages"]["tip_language"],
                input_variables=[],
            )
        )
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def clarification_chain_factory() -> LLMChain:
    return create_structured_output_chain(
        Clarifications,
        cfg.llm,
        prompt_factory_clarifications(),
        verbose=cfg.verbose_llm,
    )


def create_clarification_input(questions) -> dict:
    return {INPUT_VAR_QUESTIONS: questions}


if __name__ == "__main__":
    from data_integration_questionnaire.log_init import logger

    questions = (
        "What is CDC (Change Data Capture)?\n\nWhat is the meaning of dark data?"
    )
    input = create_clarification_input(questions=questions)
    chain = clarification_chain_factory()
    clarifications: Clarifications = chain.run(input)
    logger.info(clarifications)
