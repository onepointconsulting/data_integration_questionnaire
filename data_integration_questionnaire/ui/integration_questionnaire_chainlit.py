import re
from typing import List, Optional

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
from data_integration_questionnaire.service.advice_service import (
    create_classification_profile_chain_pydantic,
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

from data_integration_questionnaire.service.html_generator import generate_pdf_from
from data_integration_questionnaire.service.mail_sender import (
    send_email,
    validate_address,
)
from data_integration_questionnaire.log_init import logger

from asyncer import asyncify
from data_integration_questionnaire.ui.chat_settings_factory import (
    NUMBER_OF_BATCHES,
    QUESTION_PER_BATCH,
    create_chat_settings,
)
from data_integration_questionnaire.ui.model import LoopQuestionData

AVATAR = {"CHATBOT": "Chatbot", "USER": "You"}


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
async def setup_agent(settings):
    logger.info("Settings: %s", settings)
    number_of_batches = int(settings[NUMBER_OF_BATCHES]) - 1
    question_per_batch = int(settings[QUESTION_PER_BATCH])
    await process_questionnaire(number_of_batches, question_per_batch)


async def process_questionnaire(number_of_batches: int, question_per_batch: int):
    initial_message = f"""
# Data And Analytics Health Check
{display_image('main_image.png', 'Data Integration Questionnaire', 'Data Integration Questionnaire')}
Welcome to the **Onepoints's data integration** questionnaire
"""
    await setup_avatar()
    await cl.Message(content=initial_message, author=AVATAR["CHATBOT"]).send()
    initial_questions: BestPracticesQuestions = ask_initial_question()
    initial_questionnaire: Questionnaire = await questionnaire_factory(
        initial_questions.questions
    )

    await loop_questions(
        LoopQuestionData(
            questionnaire=initial_questionnaire,
            show_sequence=False,
            batch_number=0,
            question_per_batch=1,
        )
    )
    merged_questions: Questionnaire = await generate_execute_primary_questions(
        LoopQuestionData(
            questionnaire=initial_questionnaire,
            show_sequence=True,
            batch_number=0,
            question_per_batch=question_per_batch,
        )
    )

    merged_questions = merge_questionnaires([initial_questionnaire, merged_questions])
    log_questionnaire(merged_questions)
    # Generate multiple batches of questions.
    for batch in range(number_of_batches):
        loop_question_data = LoopQuestionData(
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

    advisor_chain = chain_factory_advisor()
    advices: BestPracticesAdvices = await advisor_chain.arun(
        prepare_questions_parameters(merged_questions, False)
    )
    logger.info("Advices: %s", advices)
    await display_advices(advices)
    await generate_display_pdf(advices, merged_questions)
    await process_send_email(merged_questions, advices)


async def loop_questions(loop_question_data: LoopQuestionData):
    question_start_number = (
        loop_question_data.batch_number * loop_question_data.question_per_batch
    )
    for i, question_answer in enumerate(loop_question_data.questionnaire.questions):
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


async def setup_avatar():
    await cl.Avatar(
        name=AVATAR["CHATBOT"],
        url="/public/images/natural-language-processing.png",
    ).send()
    await cl.Avatar(
        name=AVATAR["USER"],
        url="/public/images/blank-profile-picture-973460_300.webp",
    ).send()


async def generate_execute_secondary_questions(
    loop_question_data = LoopQuestionData
) -> Questionnaire:
    secondary_chain = chain_factory_secondary_questions()
    secondary_questions: BestPracticesQuestions = await secondary_chain.arun(
        prepare_questions_parameters(
            questionnaire=loop_question_data.questionnaire,
            questions_per_batch=loop_question_data.question_per_batch,
            include_questions_per_batch=True
        )
    )
    best_practices_secondary_questionnaire: Questionnaire = await questionnaire_factory(
        secondary_questions.questions
    )

    questions_length = len(best_practices_secondary_questionnaire.questions)
    await cl.Message(
        content=f"""
We have generated {questions_length} more question{'s' if questions_length > 1 else ''} to get a better understanding.
Here you go:
""",
        author=AVATAR["CHATBOT"],
    ).send()

    loop_question_data.questionnaire = best_practices_secondary_questionnaire
    await loop_questions(loop_question_data)
    return best_practices_secondary_questionnaire


async def generate_execute_primary_questions(loop_question_data: LoopQuestionData) -> Questionnaire:
    input = prepare_initial_question(loop_question_data.questionnaire.questions[0].answer, loop_question_data.question_per_batch)
    initial_chain = chain_factory_initial_question()
    initial_best_practices_questions: BestPracticesQuestions = await initial_chain.arun(
        input
    )
    best_practices_questionnaire: Questionnaire = await questionnaire_factory(
        initial_best_practices_questions.questions
    )

    questions_length = len(initial_best_practices_questions.questions)
    await cl.Message(
        content=f"""
We have generated {questions_length} question{'s' if questions_length > 1 else ''} to better understand your concerns.
Here you go:
""",
        author=AVATAR["CHATBOT"],
    ).send()

    loop_question_data.questionnaire = best_practices_questionnaire
    await loop_questions(loop_question_data)
    return best_practices_questionnaire


async def generate_display_pdf(advices, merged_questionnaire):
    pdf_path = await asyncify(generate_pdf_from)(merged_questionnaire, advices)
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


async def display_advices(advices: BestPracticesAdvices) -> Optional[str]:
    advices = advices.advices
    advice_amount = len(advices)
    if advice_amount > 0:
        pieces = "piece" if advice_amount == 1 else "pieces"
        await cl.Message(
            content=f"You have {advice_amount} {pieces} of advice.",
            author=AVATAR["CHATBOT"],
        ).send()
        advice_markdown = "\n- ".join(advices)
        task_list: cl.TaskList = await create_task_list(advices)
        cl.user_session.set("task_list", task_list)
        actions: List[cl.Action] = create_advice_task_actions(advices)
        await cl.Message(
            content="\n- " + advice_markdown, author=AVATAR["CHATBOT"], actions=actions
        ).send()
        return advice_markdown
    else:
        await cl.Message(
            content="You are doing great. We have no advice for you right now.",
            author=AVATAR["CHATBOT"],
        ).send()
        return None

    # await process_classification(questionnaire, quizz_input, advice_markdown)


def create_advice_task_actions(advices: List[str]) -> List[cl.Action]:
    # Sending an action button within a chatbot message
    actions = []
    for i, advice in enumerate(advices):
        actions.append(
            cl.Action(
                name="task_button",
                label=f"Advice {i + 1}",
                value=advice,
                description=advice[:50],
            )
        )
    return actions


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
    res = await classification_chain.arun(quizz_input)
    await cl.Message(
        content=f"Classification: {res.classification}", author=AVATAR["CHATBOT"]
    ).send()
    await process_send_email(questionnaire, advice_markdown)


async def create_task_list(advices: List[str]) -> cl.TaskList:
    task_list = cl.TaskList()
    task_list.status = "Running..."

    for advice in advices:
        task = cl.Task(title=advice, status=cl.TaskStatus.READY)
        await task_list.add_task(task)

    # Update the task list in the interface
    await task_list.send()
    return task_list


async def process_send_email(
    questionnaire: Questionnaire, advices: BestPracticesAdvices
):
    response = await cl.AskUserMessage(
        content="Would you like to receive an email with the recommendations? If so please write your email in the chat.",
        timeout=cfg.ui_timeout,
        author=AVATAR["CHATBOT"],
    ).send()
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


def log_questionnaire(merged_questions: Questionnaire):
    for qa in merged_questions.questions:
        logger.info("Q: %s", qa.question)
        logger.info("A: %s", qa.answer)
        print()
