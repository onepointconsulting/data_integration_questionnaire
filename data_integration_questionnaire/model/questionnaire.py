from dataclasses import dataclass
from typing import List

@dataclass
class QuestionAnswer:
    question: str
    answer: str

@dataclass
class Questionnaire:
    questions: List[QuestionAnswer]