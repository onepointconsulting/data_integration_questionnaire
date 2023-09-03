from pathlib import Path
import os

from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI

load_dotenv()

from data_integration_questionnaire.log_init import logger

class Config:
    model = os.getenv("OPENAI_MODEL")
    request_timeout = int(os.getenv("REQUEST_TIMEOUT"))
    has_langchain_cache = os.getenv("LANGCHAIN_CACHE") == "true"
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        request_timeout=request_timeout,
        cache=has_langchain_cache,
        streaming=True
    )
    verbose_llm = os.getenv("VERBOSE_LLM") == "true"
    ui_timeout = int(os.getenv("UI_TIMEOUT"))
    project_root = Path(os.getenv("PROJECT_ROOT"))
    assert project_root.exists()
    question_cache_folder = os.getenv("QUESTION_CACHE_FOLDER")
    question_cache_folder_path = Path(question_cache_folder)
    if not question_cache_folder_path.exists():
        question_cache_folder_path.mkdir(parents=True, exist_ok=True)

cfg = Config()

class MailConfig:
    mail_user = os.getenv('MAIL_USER')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_from = os.getenv('MAIL_FROM')
    mail_server = os.getenv('MAIL_SERVER')
    mail_from_person = os.getenv('MAIL_FROM_PERSON')

mail_config = MailConfig()

if __name__ == "__main__":
    logger.info("Model: %s", cfg.model)
    logger.info("Verbose: %s", cfg.verbose_llm)
    logger.info("mail_config user: %s", mail_config.mail_user)