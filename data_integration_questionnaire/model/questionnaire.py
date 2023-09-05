from dataclasses import dataclass
from typing import List, Optional, Union, Tuple

from data_integration_questionnaire.service.dynamic_quizz_service import (
    convert_qa_to_string
)
from data_integration_questionnaire.log_init import logger


@dataclass
class QuestionAnswer:
    question: str
    answer: Union[str, dict]
    image: Optional[str]
    image_alt: Optional[str]
    image_title: Optional[str]


@dataclass
class Questionnaire:
    questions: List[QuestionAnswer]

    def __str__(self):
        res = ""
        for q in self.questions:
            res += f"""
{q.question}
{render_answer(q.answer)}
"""
        return res

    def convert_to_arrays(self) -> Tuple[List[str], List[str]]:
        questions = [q.question for q in self.questions]
        answers = [q.answer for q in self.questions]
        return questions, answers

    def convert_to_string(self) -> str:
        questions, answers = self.convert_to_arrays()
        return convert_qa_to_string(questions, answers)
    
    def to_html(self) -> str:
        html = """<table>       
"""
        for qa in self.questions:
            answer = qa.answer
            html += f"""
<tr>
    <td>
        <br />
        Q: {qa.question}
    </td>
</tr>
<tr>
    <td>A: {answer['content']}</td>
</tr>
"""
        html += "</table>"
        return html


def render_answer(answer: Union[str, dict]) -> str:
    if isinstance(answer, dict):
        return f"{answer['createdAt']}: {answer['content']}"
    return answer if answer else "No answer"


def merge_questionnaires(questionnaire_list: List[Questionnaire]):
    logger.info("Merging %d questionnaires", len(questionnaire_list))
    questions: List[QuestionAnswer] = []
    for q in questionnaire_list:
        questions += q.questions
        logger.info("Questions length: %d", len(questions))
    return Questionnaire(questions=questions)
    
