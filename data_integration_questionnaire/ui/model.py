from dataclasses import dataclass
from data_integration_questionnaire.model.questionnaire import Questionnaire
from data_integration_questionnaire.service.test.questionnaire_factory import create_complete_questionnaire

@dataclass
class LoopQuestionData:
    message: str
    questionnaire: Questionnaire
    questionnaire_has_questions: bool = False
    show_sequence: bool = True
    batch_number: int = 0
    question_per_batch: int = 2
    clarifications = []
    enhanced_question_map = {}

    def extract_last_questions(self) -> str:
        last_answers = [q.answer['content'] if 'content' in q.answer else q.answer for q in self.questionnaire.questions][-self.question_per_batch:]
        return "\n\n".join(last_answers)


if __name__ == "__main__":

    question_per_batch = 2
    loop_question_data = LoopQuestionData(
        message="test",
        questionnaire=create_complete_questionnaire(),
        questionnaire_has_questions=False,
        show_sequence=True,
        batch_number=0
    )
    last_questions = loop_question_data.extract_last_questions()
    print(last_questions)
    assert len(last_questions.split("\n\n")) == question_per_batch