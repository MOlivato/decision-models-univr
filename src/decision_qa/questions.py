"""The three question paradigms and the /v1/systemone payload."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class NoulQuestion(BaseModel):
    """Probability that a statement is true."""

    type: Literal["noul"] = "noul"
    label: str = "statement"
    statement: str
    gold: bool | None = None


class ChoiceQuestion(BaseModel):
    """Probability of each declared option; exactly one is correct."""

    type: Literal["choice"] = "choice"
    label: str = "answer"
    options: list[str]
    gold_index: int | None = None


class ScoreQuestion(BaseModel):
    """Probability of each level of an ordered rubric."""

    type: Literal["score"] = "score"
    label: str = "score"
    rubric: str
    levels: list[str]
    gold_index: int | None = None


Question = Annotated[
    NoulQuestion | ChoiceQuestion | ScoreQuestion, Field(discriminator="type")
]


class DecisionRecord(BaseModel):
    """One labelled example in the dataset produced by notebook 03."""

    id: str
    source: str
    split: str = "train"
    state: dict
    questions: list[Question]


def to_systemone_payload(state: dict, questions: list[Question]) -> dict:
    """Translate typed questions into the wire shape used by /v1/systemone."""
    payload_questions: list[dict] = []
    for q in questions:
        if isinstance(q, NoulQuestion):
            payload_questions.append({"type": "noul", "text": q.statement})
        elif isinstance(q, ChoiceQuestion):
            payload_questions.append({"type": "choice", "options": q.options})
        else:
            payload_questions.append(
                {"type": "score", "rubric": q.rubric, "levels": q.levels}
            )
    return {"state": state, "questions": payload_questions}


def question_labels(question: Question) -> list[str]:
    """Return the answer labels a decision model must score for a question."""
    if isinstance(question, NoulQuestion):
        return ["true", "false"]
    if isinstance(question, ChoiceQuestion):
        return list(question.options)
    return list(question.levels)
