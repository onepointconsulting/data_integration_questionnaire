from typing import Any, Dict, List, Optional

from chainlit.prompt import Prompt
from chainlit.message import Message
from chainlit import LangchainCallbackHandler
from chainlit.langchain.callbacks import (
    get_llm_settings,
    AsyncLangchainCallbackHandler,
    convert_message,
    build_prompt
)
from langchain.schema import BaseMessage
from data_integration_questionnaire.log_init import logger

IGNORE_LIST = []  # type: List[str]


def _on_llm_start(
    self: LangchainCallbackHandler,
    serialized: Dict[str, Any],
    prompts: List[str],
    **kwargs: Any,
) -> None:
    logger.info("######################")
    logger.info("Invoked _on_llm_start")
    logger.info("######################")
    invocation_params = kwargs.get("invocation_params")
    provider, settings = get_llm_settings(invocation_params, serialized)

    if self.current_prompt:
        self.current_prompt.formatted = prompts[0]
        self.current_prompt.provider = provider
        self.current_prompt.settings = settings
    else:
        self.prompt_sequence.append(
            Prompt(
                formatted=prompts[0],
                provider=provider,
                settings=settings,
            )
        )


def _on_chat_model_start(
    self: LangchainCallbackHandler,
    serialized: Dict[str, Any],
    messages: List[List[BaseMessage]],
    **kwargs: Any,
):
    
    logger.info("######################")
    logger.info("Invoked _on_chat_model_start")
    logger.info("######################")

    invocation_params = kwargs.get("invocation_params")
    provider, settings = get_llm_settings(invocation_params, serialized)

    formatted_messages = messages[0]

    if self.current_prompt:
        logger.info("Invoked _on_chat_model_start: current_prompt")
        self.current_prompt.provider = provider
        self.current_prompt.settings = settings
        # Chat mode
        if self.current_prompt.messages:
            logger.info("Invoked _on_chat_model_start: if self.current_prompt.message")
            # This is needed to compute the correct message index to read
            placeholder_offset = 0
            # The final list of messages
            prompt_messages = []
            # Looping the messages built in build_prompt
            # They only contain the template
            for templated_index, templated_message in enumerate(
                self.current_prompt.messages
            ):
                logger.info("templated message: %s", templated_message)
                # If a message has a placeholder size, we need to replace it
                # With the N following messages, where N is the placeholder size
                if templated_message.placeholder_size:
                    for _ in range(templated_message.placeholder_size):
                        formatted_message = formatted_messages[
                            templated_index + placeholder_offset
                        ]
                        prompt_messages += [convert_message(formatted_message)]
                        # Increment the placeholder offset
                        placeholder_offset += 1
                    # Finally, decrement the placeholder offset by one
                    # Because the message representing the placeholder is now consumed
                    placeholder_offset -= 1
                # The current message is not a placeholder
                else:
                    formatted_message = formatted_messages[
                        templated_index + placeholder_offset
                    ]
                    # Update the role and formatted value, keep the template
                    prompt_messages += [
                        convert_message(
                            formatted_message, template=templated_message.template
                        )
                    ]
            # Finally set the prompt messages
            logger.info("prompt_messages: %s", prompt_messages)
            self.current_prompt.messages = prompt_messages
        # Non chat mode
        elif self.current_prompt.template:
            unique_message = messages[0][0]
            prompt_message = convert_message(
                unique_message, template=self.current_prompt.template
            )
            self.current_prompt.messages = [prompt_message]
            self.current_prompt.template = None
    # No current prompt, create it (formatted only)
    else:
        prompt_messages = [convert_message(m) for m in messages[0]]
        self.prompt_sequence.append(
            Prompt(
                messages=prompt_messages,
                provider=provider,
                settings=settings,
            )
        )


class OnepointAsyncLangchainCallbackHandler(AsyncLangchainCallbackHandler):

    def create_message(
        self,
        content: str = "",
        prompt: Optional[Prompt] = None,
        author: Optional[str] = None,
        parent_id: Optional[str] = None,
    ):
        logger.info("######################################################")
        logger.info("Creating message !")
        logger.info("content: %s", content)
        logger.info("prompt: %s", prompt)
        logger.info("author: %s", author)
        logger.info("parent_id: %s", parent_id)
        logger.info("######################################################")
        if parent_id is None:
            last_message = self.get_last_message()
            parent_id = last_message.id

        return Message(
            str(content),
            # author=author or self.get_author(),
            author="ChatGPT",
            prompt=prompt,
            parent_id=parent_id,
        )


    async def add_message(self, message: Message):
        
        if message.author in IGNORE_LIST:
            return

        logger.info("######################")
        logger.info("Invoked add_message")
        logger.info("######################")

        await message.send()
