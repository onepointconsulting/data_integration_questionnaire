import chainlit as cl

from data_integration_questionnaire.log_init import logger
from data_integration_questionnaire.service.html_generator import generate_pdf_from

from asyncer import asyncify


async def generate_display_pdf(advices, merged_questionnaire):
    pdf_path = await asyncify(generate_pdf_from)(merged_questionnaire, advices)
    logger.info("PDF path: %s", pdf_path)
    elements = [
        cl.File(
            name=pdf_path.name,
            path=pdf_path.as_posix(),
            display="inline",
        ),
    ]
    await cl.Message(
        content="Please download the advices in the pdf!", elements=elements
    ).send()