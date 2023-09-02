from typing import List
from pydantic import BaseModel, Field

from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain import LLMChain
from langchain.chains.openai_functions import create_structured_output_chain

from data_integration_questionnaire.toml_support import read_prompts_toml
from data_integration_questionnaire.config import cfg

prompts = read_prompts_toml()


class BbestPracticesQuestions(BaseModel):
    """Contains the questions used to help a customer to enforce best practices"""

    questions: List[str] = Field(
        ...,
        description="The list of questions given used to enforce best practices.",
    )


def prompt_factory_best_practices() -> ChatPromptTemplate:
    data_integration_questionnaire_section = prompts[
        "data_integration_questionnaire_generator"
    ]
    best_practices = data_integration_questionnaire_section["best_practices"]
    human_message = str(data_integration_questionnaire_section["human_message"]).format(
        best_practices=best_practices
    )
    prompt_msgs = [
        SystemMessage(content=data_integration_questionnaire_section["system_message"]),
        HumanMessage(content=human_message),
        HumanMessage(content=prompts["general_messages"]["tip_correct_format"]),
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def chain_factory_best_practices() -> LLMChain:
    return create_structured_output_chain(
        BbestPracticesQuestions,
        cfg.llm,
        prompt_factory_best_practices(),
        verbose=cfg.verbose_llm,
    )


if __name__ == "__main__":
    from data_integration_questionnaire.log_init import logger

    chat_prompt_template = prompt_factory_best_practices()
    logger.info("chat_prompt_templat: %s", chat_prompt_template)

    res = chain_factory_best_practices().run({})
    logger.info("")
    logger.info(res)
