from typing import List
from data_integration_questionnaire.model.questionnaire import Questionnaire
from data_integration_questionnaire.service.test.questionnaire_factory import (
    create_complete_questionnaire,
    create_simple_questionnaire,
)

from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)

from data_integration_questionnaire.model.questions_advices import (
    BestPracticesAdvices,
    BestPracticesQuestions,
)
from langchain import LLMChain

from data_integration_questionnaire.toml_support import read_prompts_toml
from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.log_init import logger

from langchain.chains.openai_functions import create_structured_output_chain

prompts = read_prompts_toml()


human_message_correct_format = prompts["general_messages"]["tip_correct_format"]
best_practices = prompts["data_integration_questionnaire_generator"]["best_practices"]
knowledge_base = prompts["data_sources"]["knowledge_base"]


def ask_initial_question() -> BestPracticesQuestions:
    initial_questions = [prompts["flexible_qustionnaire"]["initial"]["question"]]
    return BestPracticesQuestions(questions=initial_questions)


def prompt_factory_generic(
    section: dict, input_variables: List[str]
) -> ChatPromptTemplate:
    human_message = section["human_message"]
    prompt_msgs = [
        SystemMessage(content=section["system_message"]),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=human_message,
                input_variables=input_variables,
            )
        ),
        HumanMessage(content=human_message_correct_format),
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def prompt_factory_initial_questions() -> ChatPromptTemplate:
    section = prompts["flexible_qustionnaire"]["initial"]
    return prompt_factory_generic(
        section,
        [
            "best_practices",
            "knowledge_base",
            "question",
            "answer",
        ],
    )


def chain_factory_initial_question() -> LLMChain:
    return create_structured_output_chain(
        BestPracticesQuestions,
        cfg.llm,
        prompt_factory_initial_questions(),
        verbose=cfg.verbose_llm,
    )


def prepare_initial_question(answer: str) -> dict:
    section = prompts["flexible_qustionnaire"]["initial"]
    question = section["question"]
    return {
        "best_practices": best_practices,
        "knowledge_base": knowledge_base,
        "question": question,
        "answer": answer,
    }


def prompt_factory_basic(sub_section) -> ChatPromptTemplate:
    return prompt_factory_generic(
        prompts["flexible_qustionnaire"][sub_section],
        ["best_practices", "knowledge_base", "questions_answers"],
    )


def prompt_factory_secondary_question() -> ChatPromptTemplate:
    return prompt_factory_basic("secondary")


def chain_factory_secondary_questions() -> LLMChain:
    return create_structured_output_chain(
        BestPracticesQuestions,
        cfg.llm,
        prompt_factory_secondary_question(),
        verbose=cfg.verbose_llm,
    )


def prepare_questions_parameters(questionnaire: Questionnaire) -> dict:
    return {
        "best_practices": best_practices,
        "knowledge_base": knowledge_base,
        "questions_answers": str(questionnaire),
    }


def prompt_factory_advisor() -> ChatPromptTemplate:
    return prompt_factory_basic("advisor")


def chain_factory_advisor() -> LLMChain:
    return create_structured_output_chain(
        BestPracticesAdvices,
        cfg.llm,
        prompt_factory_advisor(),
        verbose=cfg.verbose_llm,
    )


if __name__ == "__main__":

    def primary_test():
        chain = chain_factory_initial_question()
        input = prepare_initial_question(
            "There are two main areas of improvement: speed of implementation of data pipelines and documenting the whole data flows and keep the documentation up to date."
        )
        res = chain.run(input)
        for q in res.questions:
            logger.info(q)

    def sedondary_test():
        secondary_chain = chain_factory_secondary_questions()
        questionnaire = create_simple_questionnaire()
        secondary_questions: BestPracticesQuestions = secondary_chain.run(
            prepare_questions_parameters(questionnaire=questionnaire)
        )

        for q in secondary_questions.questions:
            logger.info(q)

    advisor_chain = chain_factory_advisor()
    questionnaire = create_complete_questionnaire()
    advices: BestPracticesAdvices = advisor_chain.run(
        prepare_questions_parameters(questionnaire)
    )
    for a in advices.advices:
        logger.info(a)