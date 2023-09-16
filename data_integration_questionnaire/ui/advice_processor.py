from typing import Optional, List

import chainlit as cl

from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.service.dynamic_quizz_service import (
    BestPracticesAdvices
)
from data_integration_questionnaire.ui.constants import AVATAR


async def display_advices(advices: BestPracticesAdvices) -> Optional[str]:
    plain_advices = advices.get_advices()
    advice_amount = len(plain_advices)
    if advice_amount > 0:
        pieces = "piece" if advice_amount == 1 else "pieces"
        await cl.Message(
            content=f"You have {advice_amount} {pieces} of advice.",
            author=AVATAR["CHATBOT"],
        ).send()
        advice_markdown = "\n- ".join(plain_advices)

        actions = []
        if cfg.use_tasklist:
            task_list: cl.TaskList = await create_task_list(plain_advices)
            cl.user_session.set("task_list", task_list)
            actions: List[cl.Action] = create_advice_task_actions(plain_advices)
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


async def create_task_list(advices: List[str]) -> cl.TaskList:
    task_list = cl.TaskList()
    task_list.status = "Running..."

    for advice in advices:
        task = cl.Task(title=advice, status=cl.TaskStatus.READY)
        await task_list.add_task(task)

    # Update the task list in the interface
    await task_list.send()
    return task_list


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
