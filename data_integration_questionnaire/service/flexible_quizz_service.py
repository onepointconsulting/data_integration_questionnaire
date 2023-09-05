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


def prompt_factory_initial_questions() -> ChatPromptTemplate:
    section = prompts["flexible_qustionnaire"]["initial"]
    human_message = section["human_message"]
    prompt_msgs = [
        SystemMessage(content=section["system_message"]),
        HumanMessagePromptTemplate(prompt=PromptTemplate(
                template=human_message,
                input_variables=[
                    "best_practices",
                    "knowledge_base",
                    "question",
                    "answer"
                ],
            )),
        HumanMessage(content=human_message_correct_format),
    ]
    return ChatPromptTemplate(messages=prompt_msgs)


def chain_factory_initial_question() -> LLMChain:
    return create_structured_output_chain(
        BestPracticesQuestions,
        cfg.llm,
        prompt_factory_initial_questions(),
        verbose=cfg.verbose_llm,
    )

def prepare_initial_question(answer: str) -> dict:
    section = prompts["flexible_qustionnaire"]["initial"]
    best_practices = prompts["data_integration_questionnaire_generator"][
        "best_practices"
    ]
    knowledge_base = prompts["data_sources"]["knowledge_base"]
    question = section["question"]
    return {
        'best_practices': best_practices,
        'knowledge_base': knowledge_base,
        'question': question,
        'answer': answer
    }



if __name__ == "__main__":
    chain = chain_factory_initial_question()
    input = prepare_initial_question('There are two main areas of improvement: speed of implementation of data pipelines and documenting the whole data flows and keep the documentation up to date.')
    res = chain.run(input)
    for q in res.questions:
        logger.info(q)