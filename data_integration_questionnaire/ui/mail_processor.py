import chainlit as cl

from asyncer import asyncify

from data_integration_questionnaire.model.openai_schema import BestPracticesAdvices
from data_integration_questionnaire.model.questionnaire import Questionnaire
from data_integration_questionnaire.ui.constants import AVATAR

from data_integration_questionnaire.service.mail_sender import (
    send_email,
    validate_address,
)

from data_integration_questionnaire.log_init import logger
from data_integration_questionnaire.config import cfg


async def process_send_email(
    questionnaire: Questionnaire, advices: BestPracticesAdvices
):
    response = await cl.AskUserMessage(
        content="Would you like to receive an email with the recommendations? If so please write your email in the chat.",
        timeout=cfg.ui_timeout,
        author=AVATAR["CHATBOT"],
    ).send()
    if "content" in response:
        response_content = response["content"]
        if validate_address(response_content):
            logger.info("Sending email to %s", response_content)
            await asyncify(send_email)(
                "Dear customer",
                response_content,
                "Onepoint Data Integration Questionnaire",
                f"""
    <p>Big thank you for completing the <b>Onepoint's Data Integration Assessment Quiz</b>.</p>

    <h2>Questionnaire</h2>
    {questionnaire.to_html()}

    <h2>Advice</h2>
    {advices.to_html()}

    For more information, please visit our <a href="https://onepointltd.com">webpage</a>.

    """,
            )
            await cl.Message(
                content=f"Thank you for submitting the query. We really appreciate that you have taken time to do this.",
                author=AVATAR["CHATBOT"],
            ).send()
        else:
            logger.warn("%s is not a valid email", response_content)
            await cl.ErrorMessage(
                content=f"Sorry, '{response_content}' does not seem to be an email address",
                author=AVATAR["CHATBOT"],
            ).send()
    await cl.Message(
        content=f"The questionnaire is complete. Please press the 'New Chat' button to restart.",
        author=AVATAR["CHATBOT"],
    ).send()
