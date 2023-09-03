from data_integration_questionnaire.log_init import logger
from data_integration_questionnaire.service.dynamic_quizz_service import (
    convert_qa_to_string,
)
from data_integration_questionnaire.service.test.dynamic_quizz_factory import (
    create_initial_quizz,
)


def test_convert_qa_to_string():
    questions, answers = create_initial_quizz()
    qa_str = convert_qa_to_string(questions, answers)
    assert len(qa_str) > 0
