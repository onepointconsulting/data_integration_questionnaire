import re

import chainlit as cl

from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.model.questionnaire import (
    QuestionAnswer,
    Questionnaire,
    merge_questionnaires,
)
from data_integration_questionnaire.model.questionnaire_factory import (
    questionnaire_factory,
)
from data_integration_questionnaire.model.openai_schema import (
    Clarifications,
    ResponseTags,
)
from data_integration_questionnaire.service.advice_service import (
    create_classification_profile_chain_pydantic,
)
from data_integration_questionnaire.service.clarification_service import (
    clarification_chain_factory,
    create_clarification_input,
)
from data_integration_questionnaire.service.dynamic_quizz_service import (
    BestPracticesAdvices,
    BestPracticesQuestions,
)

from data_integration_questionnaire.service.flexible_quizz_service import (
    chain_factory_advisor,
    chain_factory_initial_question,
    chain_factory_secondary_questions,
    ask_initial_question,
    prepare_initial_question,
    prepare_questions_parameters,
)

from data_integration_questionnaire.log_init import logger

from data_integration_questionnaire.service.similarity_search import (
    init_vector_search,
    similarity_search,
)
from data_integration_questionnaire.service.tagging_service import (
    sentiment_chain_factory,
)
from data_integration_questionnaire.ui.advice_processor import display_advices
from data_integration_questionnaire.ui.chat_settings_factory import (
    INITIAL_QUESTION,
    NUMBER_OF_BATCHES,
    QUESTION_PER_BATCH,
    create_chat_settings,
)
from data_integration_questionnaire.ui.constants import AVATAR, TOOL_NAME
from data_integration_questionnaire.ui.customized_chainlit_callback import (
    OnepointAsyncLangchainCallbackHandler,
)
from data_integration_questionnaire.ui.mail_processor import process_send_email
from data_integration_questionnaire.ui.model import LoopQuestionData
from data_integration_questionnaire.ui.pdf_processor import generate_display_pdf

docsearch = init_vector_search()


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
    settings = await create_chat_settings()
    await setup_agent(settings)


@cl.on_settings_update
async def setup_agent(settings: cl.ChatSettings):
    logger.info("Settings: %s", settings)

    await process_questionnaire(settings)


async def process_questionnaire(settings: cl.ChatSettings):
    number_of_batches: int = int(settings[NUMBER_OF_BATCHES]) - 1
    question_per_batch: int = int(settings[QUESTION_PER_BATCH])
    initial_question: str = settings[INITIAL_QUESTION]

    await setup_avatar()

    initial_message = f"""
### Hello! I will ask you a few questions about your data ecosystem. At the end, you will get recommendations and suggested courses of action.

- Onepoint’s Data & Analytics Body of Knowledge is the basis for the diagnostics and recommendations.
- If you’d like, you can ask for a copy of the results to be emailed to you.
- This is an experimental tool. Any feedback and improvement ideas are always welcome — thank you!
Let’s get started.
"""
    await cl.Message(content=initial_message, author=AVATAR["CHATBOT"]).send()
    initial_message_enhanced = f"""
### {initial_question}
The graphic below may help with your response — it captures some of the most common data and analytics challenges our clients face.
{display_image('data_ecosystem_areas.png', TOOL_NAME, TOOL_NAME)}
"""

    initial_questions: BestPracticesQuestions = ask_initial_question(initial_question)
    initial_questionnaire: Questionnaire = await questionnaire_factory(
        initial_questions
    )

    initial_loop_question_data = LoopQuestionData(
        message="",
        questionnaire=initial_questionnaire,
        show_sequence=False,
        batch_number=0,
        question_per_batch=1,
    )
    initial_loop_question_data.enhanced_question_map[
        initial_question
    ] = initial_message_enhanced
    await loop_questions(initial_loop_question_data)
    # Process initial question which is pre-defined
    merged_questions: Questionnaire = await generate_execute_primary_questions(
        LoopQuestionData(
            message="",
            questionnaire=initial_questionnaire,
            show_sequence=True,
            batch_number=0,
            question_per_batch=question_per_batch,
        )
    )

    merged_questions: Questionnaire = merge_questionnaires(
        [initial_questionnaire, merged_questions]
    )
    log_questionnaire(merged_questions)

    # Generate multiple batches of questions.
    merged_questions = await generate_multiple_batches(
        number_of_batches, question_per_batch, merged_questions
    )

    # Produce advices
    advisor_chain = chain_factory_advisor()
    callbacks = (
        [OnepointAsyncLangchainCallbackHandler()] if cfg.show_chain_of_thought else []
    )
    bp = similarity_search(
        docsearch,
        merged_questions.answers_str(),
        how_many=cfg.search_results_how_many * 3,
    )
    advices: BestPracticesAdvices = await advisor_chain.arun(
        prepare_questions_parameters(merged_questions, False, bp=bp),
        callbacks=callbacks,
    )

    # Check if there are questions
    loop_question_data = LoopQuestionData(
        message="",
        questionnaire=merged_questions,
        show_sequence=False,
        batch_number=0,
        question_per_batch=question_per_batch,
    )
    await check_has_questions(
        loop_question_data, loop_question_data.extract_last_questions()
    )
    if loop_question_data.questionnaire_has_questions:
        await loop_clarifications(loop_question_data)

    # Show advices
    logger.info("Advices: %s", advices)
    await display_advices(advices)
    await generate_display_pdf(advices, merged_questions)
    await process_send_email(merged_questions, advices)


async def generate_multiple_batches(
    number_of_batches: int, question_per_batch: int, merged_questions: Questionnaire
):
    for batch in range(number_of_batches):
        loop_question_data = LoopQuestionData(
            message="",
            questionnaire=merged_questions,
            show_sequence=True,
            batch_number=batch + 1,
            question_per_batch=question_per_batch,
        )
        new_questions: Questionnaire = await generate_execute_secondary_questions(
            loop_question_data
        )
        merged_questions = merge_questionnaires([merged_questions, new_questions])
        log_questionnaire(merged_questions)
    return merged_questions


async def loop_questions(loop_question_data: LoopQuestionData):
    question_start_number = (
        loop_question_data.batch_number * loop_question_data.question_per_batch
    )
    if loop_question_data.questionnaire_has_questions:
        await loop_clarifications(loop_question_data)
    if loop_question_data.message and len(loop_question_data.message):
        await cl.Message(
            content=loop_question_data.message, author=AVATAR["CHATBOT"]
        ).send()
    for i, question_answer in enumerate(loop_question_data.questionnaire.questions):
        logger.info(
            "loop_question_data.enhanced_question_map: %s",
            loop_question_data.enhanced_question_map,
        )
        logger.info("question_answer.question: %s", question_answer.question)
        if question_answer.question in loop_question_data.enhanced_question_map:
            message = loop_question_data.enhanced_question_map[question_answer.question]
        else:
            message = (
                f"Question {int(i + 1 + question_start_number)}: {question_message_factory(question_answer)}"
                if loop_question_data.show_sequence
                else question_message_factory(question_answer)
            )
        response = await cl.AskUserMessage(
            content=message,
            timeout=cfg.ui_timeout,
            author=AVATAR["CHATBOT"],
        ).send()
        question_answer.answer = response


async def loop_clarifications(loop_question_data: LoopQuestionData):
    clarifications = loop_question_data.clarifications
    if clarifications:
        clarifications_str = ""
        for c in clarifications:
            clarifications_str += f"- {c}\n"
        await cl.Message(content=clarifications_str).send()


async def setup_avatar():
    await cl.Avatar(
        name=AVATAR["CHATBOT"],
        url="/public/images/natural-language-processing.png",
    ).send()
    await cl.Avatar(
        name=AVATAR["USER"],
        url="/public/images/User_icon_512.png",
    ).send()


async def generate_execute_primary_questions(
    loop_question_data: LoopQuestionData,
) -> Questionnaire:
    first_qa = loop_question_data.questionnaire.questions[0]
    search_res = similarity_search(docsearch, first_qa.answer_str())
    input = prepare_initial_question(
        first_qa.question,
        first_qa.answer,
        loop_question_data.question_per_batch,
        best_practices=search_res,
    )
    initial_chain = chain_factory_initial_question()
    await cl.Message(content="").send()
    callbacks = (
        [OnepointAsyncLangchainCallbackHandler()] if cfg.show_chain_of_thought else []
    )
    initial_best_practices_questions: BestPracticesQuestions = await initial_chain.arun(
        input, callbacks=callbacks
    )
    best_practices_questionnaire: Questionnaire = await questionnaire_factory(
        initial_best_practices_questions
    )

    # Check if there are questions
    if "content" in first_qa.answer:
        await check_has_questions(loop_question_data, first_qa.answer["content"])

    loop_question_data.message = ""
    loop_question_data.questionnaire = best_practices_questionnaire
    await loop_questions(loop_question_data)
    return best_practices_questionnaire


async def check_has_questions(loop_question_data: LoopQuestionData, answer_str: str):
    sentiment_chain = sentiment_chain_factory()
    logger.info("answer_str: %s", answer_str)
    callbacks = (
        [OnepointAsyncLangchainCallbackHandler()] if cfg.show_chain_of_thought else []
    )
    response_tags: ResponseTags = await sentiment_chain.arun(
        {"answer": answer_str}, callbacks=callbacks
    )
    loop_question_data.questionnaire_has_questions = (
        response_tags.has_questions and len(response_tags.extracted_questions) > 0
    )
    if loop_question_data.questionnaire_has_questions:
        clarification_chain = clarification_chain_factory()
        questions_str = "\n\n".join(response_tags.extracted_questions)
        clarifications: Clarifications = await clarification_chain.arun(
            create_clarification_input(questions_str),
            callbacks=callbacks,
        )
        loop_question_data.clarifications = clarifications.answers


async def generate_execute_secondary_questions(
    loop_question_data=LoopQuestionData,
) -> Questionnaire:
    secondary_chain = chain_factory_secondary_questions()
    await cl.Message(content="").send()
    callbacks = (
        [OnepointAsyncLangchainCallbackHandler()] if cfg.show_chain_of_thought else []
    )
    bp = similarity_search(
        docsearch,
        loop_question_data.questionnaire.answers_str(),
        how_many=cfg.search_results_how_many * 2,
    )
    secondary_questions: BestPracticesQuestions = await secondary_chain.arun(
        prepare_questions_parameters(
            questionnaire=loop_question_data.questionnaire,
            questions_per_batch=loop_question_data.question_per_batch,
            include_questions_per_batch=True,
            bp=bp,
        ),
        callbacks=callbacks,
    )
    best_practices_secondary_questionnaire: Questionnaire = await questionnaire_factory(
        secondary_questions
    )

    # Check if there are questions
    # answer_str = loop_question_data.
    await check_has_questions(
        loop_question_data, loop_question_data.extract_last_questions()
    )

    loop_question_data.questionnaire = best_practices_secondary_questionnaire

    await loop_questions(loop_question_data)
    return best_practices_secondary_questionnaire



@cl.action_callback("task_button")
async def on_action(action):
    task_list: cl.TaskList = cl.user_session.get("task_list")
    task_number = int(re.sub(r".+?(\d+)", r"\1", action.label)) - 1
    task: cl.Task = task_list.tasks[task_number]
    task.status = cl.TaskStatus.DONE
    await task_list.send()
    logger.info(f"Discussed {action.label}")
    # Optionally remove the action button from the chatbot user interface
    await action.remove()


async def process_classification(questionnaire, quizz_input, advice_markdown):
    classification_chain = create_classification_profile_chain_pydantic()

    res = await classification_chain.arun(
        quizz_input, callbacks=[OnepointAsyncLangchainCallbackHandler()]
    )
    await cl.Message(
        content=f"Classification: {res.classification}", author=AVATAR["CHATBOT"]
    ).send()
    await process_send_email(questionnaire, advice_markdown)



def log_questionnaire(merged_questions: Questionnaire):
    for qa in merged_questions.questions:
        logger.info("Q: %s", qa.question)
        logger.info("A: %s", qa.answer)
        print()


from chainlit.server import app
from fastapi import File, UploadFile
from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.log_init import logger

CODES = {"OK": "OK", "ERROR": "ERROR"}


@app.post("/onepoint/best_practices")
def upload_best_practices(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(cfg.knowledge_base_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.exception("Could not upload file.")
        return {"code": CODES["ERROR"], "message": f"Failed to upload file: {str(e)}"}
    return {"code": CODES["OK"], "message": f"Successfully uploaded {file.filename}"}
