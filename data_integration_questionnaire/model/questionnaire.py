from dataclasses import dataclass
from typing import List, Optional, Union


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


def render_answer(answer: Union[str, dict]) -> str:
    if isinstance(answer, dict):
        return f"{answer['createdAt']}: {answer['content']}"
    return answer if answer else "No answer"


if __name__ == "__main__":
    print(
        QuestionAnswer(
            question="test", answer="", image=None, image_alt=None, image_title=None
        )
    )
