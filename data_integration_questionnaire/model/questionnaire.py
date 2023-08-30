from dataclasses import dataclass
from typing import List, Optional

@dataclass
class QuestionAnswer:
    question: str
    answer: str
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
{q.answer if q.answer else 'No answer'}
"""
        return res
    

if __name__ == "__main__":
    print(QuestionAnswer(question='test', answer="", image=None, image_alt=None, image_title=None))



    