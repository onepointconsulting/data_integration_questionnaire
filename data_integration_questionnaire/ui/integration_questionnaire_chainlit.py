
import chainlit as cl

from chainlit.config import config

from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.model.questionnaire import QuestionAnswer, Questionnaire
from data_integration_questionnaire.model.questionnaire_factory import questionnaire_factory
from data_integration_questionnaire.service.advice_service import create_classification_profile_chain_pydantic, create_input_dict, create_match_profile_chain_pydantic, extract_advices

def display_image(image_path: str, alt: str, title: str):
    return f'![{alt}](/public/images/{image_path} "{title}")'

def question_message_factory(question_answer: QuestionAnswer) -> str:
    message = question_answer.question
    if question_answer.image is not None and question_answer.image_alt is not None and question_answer.image_title is not None:
        message += "\n\n"
        message += display_image(question_answer.image, question_answer.image_alt, question_answer.image_title)
    return message

@cl.on_chat_start
async def init():
    """
    Main entry point for the application.
    This application will ask you questions about your data integration strategy and at the end give you some evaluation.
    """
    initial_message = f"""
# Data Integration Quizz
{display_image('imagesmonitor-1307227_600.webp', 'Data Integration Questionnaire', 'Data Integration Quizz')}
Welcome to the **Onepoints's data integration** quizz
"""
    await cl.Message(
        content=initial_message,
    ).send()
    questionnaire: Questionnaire = questionnaire_factory()
    for question_answer in questionnaire.questions:
        response = await cl.AskUserMessage(
            content=question_message_factory(question_answer),
            timeout=cfg.ui_timeout,
        ).send()
        question_answer.answer = response
    await process_questionnaire(questionnaire)


async def process_questionnaire(questionnaire: Questionnaire):
    
    chain = create_match_profile_chain_pydantic()
    # await chain.acall(str(questionnaire), callbacks=[cl.AsyncLangchainCallbackHandler()])
    quizz_input = create_input_dict(str(questionnaire))
    res = await chain.arun(quizz_input)
    advices = extract_advices(res)
    advice_amount = len(advices)
    if advice_amount > 0:
        pieces = "piece" if advice_amount == 1 else "pieces"
        await cl.Message(content=f"You have {advice_amount} {pieces} of advice.").send()
        advice_markdown = "\n- ".join(advices)
        await cl.Message(content="\n- " + advice_markdown).send()
    else:
        await cl.Message(content="You are doing great. We have no advice for you right now.").send()

    classification_chain = create_classification_profile_chain_pydantic()
    res = await classification_chain.arun(quizz_input)
    await cl.Message(content=f"Classification: {res}").send()
