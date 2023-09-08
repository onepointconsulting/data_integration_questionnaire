from chainlit.input_widget import Slider, TextInput
import chainlit as cl
from data_integration_questionnaire.service.flexible_quizz_service import prompts

NUMBER_OF_BATCHES = "Number of batches"
QUESTION_PER_BATCH = "Questions per batch"
INITIAL_QUESTION = "Initial question"


async def create_chat_settings() -> cl.ChatSettings:
    questions_per_batch = prompts["general_settings"]["questions_per_batch"]
    number_of_batches = prompts["general_settings"]["number_of_batches"]
    initial_question = prompts["flexible_qustionnaire"]["initial"]["question"]
    settings = await cl.ChatSettings(
        [
            TextInput(
                id=INITIAL_QUESTION, label=INITIAL_QUESTION, initial=initial_question
            ),
            Slider(
                id=NUMBER_OF_BATCHES,
                label="Number of question batches",
                initial=number_of_batches,
                min=0,
                max=5,
                step=1,
            ),
            Slider(
                id=QUESTION_PER_BATCH,
                label="Number of question per batch",
                initial=questions_per_batch,
                min=0,
                max=5,
                step=1,
            ),
        ]
    ).send()
    return settings
