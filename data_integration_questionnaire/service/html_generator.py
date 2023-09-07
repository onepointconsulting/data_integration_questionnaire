from pathlib import Path

from data_integration_questionnaire.service.test.best_practices_advice_provider import (
    simple_advice_provider,
)
from data_integration_questionnaire.service.test.questionnaire_factory import (
    create_simple_questionnaire,
)
import jinja2
import pdfkit
from datetime import datetime

from data_integration_questionnaire.model.questionnaire import Questionnaire
from data_integration_questionnaire.service.dynamic_quizz_service import (
    BestPracticesAdvices,
)
from data_integration_questionnaire.config import cfg
from data_integration_questionnaire.log_init import logger


def generate_html(questionnaire: Questionnaire, advices: BestPracticesAdvices) -> str:
    timestamp = datetime.today().strftime("%A, %b %d %Y")
    context = {
        "questionnaire": questionnaire.to_html(),
        "advices": advices.to_html(),
        "timestamp": timestamp,
    }
    template_loader = jinja2.FileSystemLoader(cfg.template_location)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("results-template.html")
    return template.render(context)


def generate_pdf_from(questionnaire: Questionnaire, advices: BestPracticesAdvices) -> Path:
    if questionnaire is None:
        return None
    html = generate_html(questionnaire, advices)
    file_name = cfg.pdf_folder/f"questionnaire_{generate_iso()}.pdf"
    config = pdfkit.configuration(wkhtmltopdf=cfg.wkhtmltopdf_binary.as_posix())
    pdfkit.from_string(html, file_name, configuration=config)
    logger.info("Created PDF: %s", file_name)
    return file_name


def generate_iso() -> str:
    current_time = datetime.now()
    return current_time.isoformat().replace(':', '.')


if __name__ == "__main__":
    questionnaire: Questionnaire = create_simple_questionnaire()
    advices: BestPracticesAdvices = simple_advice_provider()
    generate_pdf_from(questionnaire, advices)

