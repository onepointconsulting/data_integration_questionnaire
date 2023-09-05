

from pydantic import BaseModel, Field

from typing import List


class BestPracticesQuestions(BaseModel):
    """Contains the questions used to help a customer to enforce best practices"""

    questions: List[str] = Field(
        ...,
        description="The list of questions given used to enforce best practices.",
    )


class BestPracticesAdvices(BaseModel):
    """Contains the advices used to help a customer to enforce best practices based on a set of questions and best practices"""

    advices: List[str] = Field(
        ...,
        description="The list of advices given used to enforce best practices.",
    )

    def to_html(self) -> str:
        html = "<ul>"
        for advice in self.advices:
            html += f"<li>{advice}</li>"
        html += "</ul>"
        return html