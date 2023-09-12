from typing import List

from data_integration_questionnaire.model.questionnaire import (
    QuestionAnswer,
    Questionnaire,
)
from data_integration_questionnaire.model.openai_schema import BestPracticesQuestions
from data_integration_questionnaire.service.dynamic_quizz_service import execute_initial_questions_chain


async def questionnaire_factory(generated_questions: BestPracticesQuestions) -> Questionnaire:
    question_answers = []
    questions = [{'text': q} for q in generated_questions.questions]
    for q in questions:
        question_answer = QuestionAnswer(question=q["text"], answer="", image=None, image_alt=None, image_title=None)
        if 'image_path' in q and 'image_alt' in q and 'image_title' in q:
            question_answer.image = q['image_path']
            question_answer.image_title = q['image_title']
            question_answer.image_alt = q['image_alt']
        question_answers.append(question_answer)
    return Questionnaire(questions=question_answers, clarifications=[])

