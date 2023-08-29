
import chainlit as cl

from chainlit.config import config

from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.model.questionnaire import Questionnaire
from data_integration_questionnaire.model.questionnaire_factory import questionnaire_factory



@cl.on_chat_start
async def init():
    """
    Main entry point for the application.
    This application will ask you questions about your data integration strategy and at the end give you some evaluation.
    """
    initial_message = f"""
# Data Integration Quizz
![Data Integration Questionnaire](/public/images/imagesmonitor-1307227_800.webp "Title")
Welcome to the **Onepoints's data integration** quizz
"""
    await cl.Message(
        content=initial_message,
    ).send()
    questionnaire: Questionnaire = questionnaire_factory()
    for question_answer in questionnaire.questions:
        response = await cl.AskUserMessage(
            content=question_answer.question,
            timeout=cfg.ui_timeout,
        ).send()
        question_answer.answer = response
    # application_docs = await upload_and_extract_text(
    #     "job description files", max_files=cfg.max_jd_files
    # )

    # if application_docs is not None and len(application_docs) > 0:
    #     cv_docs = await upload_and_extract_text("CV files", max_files=cfg.max_cv_files)
    #     if application_docs and cv_docs:
    #         await start_process_applications_and_cvs(application_docs, cv_docs)
    #     else:
    #         await cl.ErrorMessage(
    #             content=f"Could not process the CVs. Please try again",
    #         ).send()
    # else:
    #     await cl.ErrorMessage(
    #         content=f"Could not process the application document. Please try again",
    #     ).send()