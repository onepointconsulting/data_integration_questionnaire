import chainlit as cl

from chainlit.config import config

from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.model.questionnaire import (
    QuestionAnswer,
    Questionnaire,
)
from data_integration_questionnaire.model.questionnaire_factory import (
    questionnaire_factory,
)
from data_integration_questionnaire.service.advice_service import (
    create_classification_profile_chain_pydantic,
    create_input_dict,
    create_match_profile_chain_pydantic,
    extract_advices,
)
from data_integration_questionnaire.service.mail_sender import send_email, validate_address
from data_integration_questionnaire.log_init import logger

from asyncer import asyncify


def display_image(image_path: str, alt: str, title: str):
    return f'![{alt}](/public/images/{image_path} "{title}")'


def question_message_factory(question_answer: QuestionAnswer) -> str:
    message = question_answer.question
    if (
        question_answer.image is not None
        and question_answer.image_alt is not None
        and question_answer.image_title is not None
    ):
        message += "\n\n"
        message += display_image(
            question_answer.image,
            question_answer.image_alt,
            question_answer.image_title,
        )
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
        await cl.Message(
            content="You are doing great. We have no advice for you right now."
        ).send()

    classification_chain = create_classification_profile_chain_pydantic()
    res = await classification_chain.arun(quizz_input)
    await cl.Message(content=f"Classification: {res}").send()

    await process_send_email(questionnaire, advice_markdown)


async def process_send_email(questionnaire: Questionnaire, advice_markdown: str):
    response = await cl.AskUserMessage(
        content="Would you like to receive an email with the recommendations? If so please write your email in the chat.",
        timeout=cfg.ui_timeout,
    ).send()
    response_content = response['content']
    if validate_address(response_content):
        logger.info("Sending email to %s", response_content)
        await asyncify(send_email)(
                "Dear customer",
                response_content,
                "Onepoint Data Integration Quizz",
                f"""
<p>Big thank you for completing the <b>Onepoint's Data Integration Assessment Quiz</b>.</p>

<h2>Questionnaire</h2>
<pre>
{questionnaire}
</pre>

<h2>Advice</h2>
<pre>
{advice_markdown}
</pre>

For more information, please visit our <a href="https://onepointltd.com">webpage</a>.

""",
        )
        await cl.Message(content=f"Thank you for submitting the query. We really appreciate that you have taken time to do this.").send()
    else:
        logger.warn("%s is not a valid email", response_content)
        await cl.ErrorMessage(
            content=f"Sorry, '{response_content}' does not seem to be an email address"
        ).send()
    await cl.Message(content=f"The quizz is complete. Please press the 'New Chat' button to restart.").send()