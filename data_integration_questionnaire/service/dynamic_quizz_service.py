import pickle
from typing import List
from pydantic import BaseModel, Field

from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain import LLMChain
from langchain.chains.openai_functions import create_structured_output_chain

from data_integration_questionnaire.toml_support import read_prompts_toml
from data_integration_questionnaire.config import cfg


prompts = read_prompts_toml()

human_message_correct_format = prompts["general_messages"]["tip_correct_format"]


class BestPracticesQuestions(BaseModel):
    """Contains the questions used to help a customer to enforce best practices"""

    questions: List[str] = Field(
        ...,
        description="The list of questions given used to enforce best practices.",
    )


class BestPracticesAdvices(BaseModel):
    """Contains the advices used to help a customer to enforce best practices based on a set of questions and best practices"""

    advices: List[str] = Field(
        ...,
        description="The list of advices given used to enforce best practices.",
    )


def prompt_factory_best_practices() -> ChatPromptTemplate:
    section = prompts["data_integration_questionnaire_generator"]
    best_practices = section["best_practices"]
    human_message = str(section["human_message"]).format(best_practices=best_practices)
    prompt_msgs = [
        SystemMessage(content=section["system_message"]),
        HumanMessage(content=human_message),
        HumanMessage(content=human_message_correct_format),
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def convert_qa_to_string(questions: List[str], answers: List[str]) -> str:
    assert len(questions) == len(answers)
    res = ""
    for q, a in zip(questions, answers):
        res += f"{q}\n{a}\n\n"
    return res


def prompt_factory_seconday_query() -> ChatPromptTemplate:
    section = prompts["data_integration_secondary_questionnaire_generator"]
    human_message = section["human_message"]
    prompt_msgs = [
        SystemMessage(content=section["system_message"]),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=human_message,
                input_variables=["best_practices", "customer_questionnaire"],
            )
        ),
        HumanMessage(content=human_message_correct_format),
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def prompt_factory_advice_generator() -> ChatPromptTemplate:
    section = prompts["data_integration_advice_generator"]
    human_message = section["human_message"]
    prompt_msgs = [
        SystemMessage(content=section["system_message"]),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template=human_message,
                input_variables=[
                    "best_practices",
                    "customer_questionnaire",
                    "secondary_questionnaire",
                ],
            )
        ),
        HumanMessage(content=human_message_correct_format),
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def chain_factory_best_practices() -> LLMChain:
    return create_structured_output_chain(
        BestPracticesQuestions,
        cfg.llm,
        prompt_factory_best_practices(),
        verbose=cfg.verbose_llm,
    )


def chain_factory_secondary_questionnaire() -> LLMChain:
    return create_structured_output_chain(
        BestPracticesQuestions,
        cfg.llm,
        prompt_factory_seconday_query(),
        verbose=cfg.verbose_llm,
    )


def chain_factory_advices() -> LLMChain:
    return create_structured_output_chain(
        BestPracticesAdvices,
        cfg.llm,
        prompt_factory_advice_generator(),
        verbose=cfg.verbose_llm,
    )


def execute_initial_questions_chain() -> BestPracticesQuestions:
    cached_file = cfg.question_cache_folder_path / "initial_questions.pkl"
    if cached_file.exists():
        with open(cached_file, "rb") as f:
            return pickle.load(f)
    res: BestPracticesQuestions = chain_factory_best_practices().run({})
    questions = res.questions
    with open(cached_file, "wb") as f:
        pickle.dump(questions, f)
    return questions


def get_best_practices():
    return prompts["data_integration_questionnaire_generator"]["best_practices"]


def execute_secondary_query_chain(
    questions: List[str], answers: List[str]
) -> BestPracticesQuestions:
    customer_questionnaire = convert_qa_to_string(questions, answers)
    best_practices = get_best_practices()
    res: BestPracticesQuestions = chain_factory_secondary_questionnaire().run(
        {
            "best_practices": best_practices,
            "customer_questionnaire": customer_questionnaire,
        }
    )
    return res.questions


def execute_advice_chain(
    questions: List[str],
    answers: List[str],
    secondary_questions: List[str],
    secondary_answers: List[str],
) -> BestPracticesAdvices:
    customer_questionnaire = convert_qa_to_string(questions, answers)
    secondary_questionnaire = convert_qa_to_string(
        secondary_questions, secondary_answers
    )
    best_practices = prompts["data_integration_questionnaire_generator"][
        "best_practices"
    ]
    res: BestPracticesAdvices = chain_factory_advices().run(
        {
            "best_practices": best_practices,
            "customer_questionnaire": customer_questionnaire,
            "secondary_questionnaire": secondary_questionnaire,
        }
    )
    return res.advices


if __name__ == "__main__":
    from data_integration_questionnaire.log_init import logger

    chat_prompt_template = prompt_factory_best_practices()
    logger.info("chat_prompt_templat: %s", chat_prompt_template)

    for i in range(3):
        res = execute_initial_questions_chain()
        logger.info("")
        logger.info(res)
        logger.info(type(res))

    from data_integration_questionnaire.service.test.dynamic_quizz_factory import (
        create_initial_quizz,
        create_secondary_quizz,
    )

    questions, answers = create_initial_quizz()
    logger.info("Prompt Secondary query:")
    logger.info("=======================")
    logger.info(prompt_factory_seconday_query())

    secondary_questions = execute_secondary_query_chain(questions, answers)

    for question in secondary_questions:
        logger.info("secondary question: %s", question)

    secondary_questions, secondary_answers = create_secondary_quizz()
    advices = execute_advice_chain(
        questions, answers, secondary_questions, secondary_answers
    )

    logger.info("Advices:")
    for question in secondary_questions:
        logger.info("%s", question)
