import re
from typing import List

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
from data_integration_questionnaire.service.dynamic_quizz_service import BestPracticesAdvices, BestPracticesQuestions, chain_factory_advices, chain_factory_secondary_questionnaire, convert_qa_to_string, execute_initial_questions_chain, get_best_practices
from data_integration_questionnaire.service.mail_sender import (
    send_email,
    validate_address,
)
from data_integration_questionnaire.log_init import logger

from asyncer import asyncify

AVATAR = {"CHATBOT": "Chatbot", "USER": "User"}


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
# Data Integration Questionnaire
{display_image('imagesmonitor-1307227_600.webp', 'Data Integration Questionnaire', 'Data Integration Questionnaire')}
Welcome to the **Onepoints's data integration** questionnaire
"""
    await setup_avatar()
    await cl.Message(content=initial_message, author=AVATAR["CHATBOT"]).send()
    generated_questions = await asyncify(execute_initial_questions_chain)()
    questionnaire: Questionnaire = await questionnaire_factory(generated_questions)
    await loop_questions(questionnaire)
    await process_secondary_questionnaire(questionnaire)


async def loop_questions(questionnaire):
    for question_answer in questionnaire.questions:
        response = await cl.AskUserMessage(
            content=question_message_factory(question_answer),
            timeout=cfg.ui_timeout,
            author=AVATAR["CHATBOT"],
        ).send()
        question_answer.answer = response


async def setup_avatar():
    await cl.Avatar(
        name=AVATAR["CHATBOT"],
        url="https://avatars.githubusercontent.com/u/128686189?s=400&u=a1d1553023f8ea0921fba0debbe92a8c5f840dd9&v=4",
    ).send()
    await cl.Avatar(
        name=AVATAR["USER"],
        url="/public/images/blank-profile-picture-973460_300.webp",
    ).send()


async def process_secondary_questionnaire(questionnaire: Questionnaire):

    customer_questionnaire: str = questionnaire.convert_to_string()
    best_practices = get_best_practices()
    secondary_chain = chain_factory_secondary_questionnaire()
    secondary_questions: BestPracticesQuestions = await secondary_chain.arun(
        {
            "best_practices": best_practices,
            "customer_questionnaire": customer_questionnaire,
        }
    )
    logger.info("secondary_questions: %s", secondary_questions)
    second_questionnaire: Questionnaire = await questionnaire_factory(secondary_questions.questions)
    await loop_questions(second_questionnaire)

    second_customer_questionnaire: str = second_questionnaire.convert_to_string()
    advice_chain = chain_factory_advices()
    advices: BestPracticesAdvices = await advice_chain.arun(
        {
            "best_practices": best_practices,
            "customer_questionnaire": customer_questionnaire,
            "secondary_questionnaire": second_customer_questionnaire,
        }
    )
    
    await display_advices(advices)

async def display_advices(advices: BestPracticesAdvices):
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

    else:
        await cl.Message(
            content="You are doing great. We have no advice for you right now.",
            author=AVATAR["CHATBOT"],
        ).send()

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


async def process_send_email(questionnaire: Questionnaire, advice_markdown: str):
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
