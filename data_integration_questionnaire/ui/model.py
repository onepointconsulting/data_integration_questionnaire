from dataclasses import dataclass
from data_integration_questionnaire.model.questionnaire import Questionnaire

@dataclass
class LoopQuestionData:
    message: str
    questionnaire: Questionnaire
    show_sequence: bool = True
    batch_number: int = 0
    question_per_batch: int = 2
