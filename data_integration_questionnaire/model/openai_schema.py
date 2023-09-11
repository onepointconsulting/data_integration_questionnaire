from pydantic import BaseModel, Field

from typing import List, Optional


class BestPracticesQuestions(BaseModel):
    """Contains the questions used to help a customer to enforce best practices"""

    questions: List[str] = Field(
        ...,
        description="The list of questions given used to enforce best practices.",
    )

    answers: Optional[List[str]] = Field(
        ...,
        description="Answers to any questions from the user answers.",
    )

    def __str__(self) -> str:
        return "\n".join(self.questions)


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


class ResponseTags(BaseModel):
    """Contains information about the answer given by the user"""

    has_questions: bool = Field(
        ...,
        description="Whether the text with the answers contains embedded questions or not.",
    )
    sounds_confused: bool = Field(
        ...,
        description="Whether the text with the answers suggests that the user is confused.",
    )
    extracted_questions: Optional[List[str]] = Field(
        ...,
        description="If the text with the answers contains questions, these are the questions.",
    )


class Clarifications(BaseModel):
    answers: Optional[List[str]] = Field(
        ...,
        description="Answers to any questions from mthe user answers.",
    )
