"""Accuracy, calibration and confidence-threshold utilities."""

from __future__ import annotations

import random
from collections.abc import Sequence
from itertools import pairwise

import numpy as np

from .backends import DecisionResult
from .distractors import shuffle_with_gold
from .questions import ChoiceQuestion, NoulQuestion, Question, ScoreQuestion


def gold_label(question: Question) -> str:
    """Return the text of the correct answer for one question."""
    if isinstance(question, NoulQuestion):
        if question.gold is None:
            raise ValueError("Noul question has no gold label")
        return "true" if question.gold else "false"
    if isinstance(question, ChoiceQuestion):
        options = question.options
    elif isinstance(question, ScoreQuestion):
        options = question.levels
    else:
        raise TypeError(f"Unsupported question type: {type(question).__name__}")
    if question.gold_index is None:
        raise ValueError("Question has no gold index")
    if not 0 <= question.gold_index < len(options):
        raise ValueError("gold_index is outside the declared options")
    return options[question.gold_index]


def gold_probability(result: DecisionResult, question: Question) -> float:
    """Probability the model assigned to the gold answer of one question."""
    return float(result.probabilities.get(gold_label(question), 0.0))


def predicted_label(result: DecisionResult) -> str:
    """The answer with the highest probability. Ties go to the first label."""
    if not result.probabilities:
        raise ValueError("Result has no probabilities")
    return max(result.probabilities, key=result.probabilities.get)


def accuracy(results: Sequence[DecisionResult], questions: Sequence[Question]) -> float:
    """Fraction of questions where the top answer is the gold answer.

    Ties count as wrong unless the gold label happens to be first. This avoids the
    inflated accuracy that a simple `gold >= max` check produces on uniform output.
    """
    if len(results) != len(questions):
        raise ValueError("results and questions must have the same length")
    if not results:
        return 0.0
    hits = sum(predicted_label(result) == gold_label(question) for result, question in zip(results, questions))
    return hits / len(results)


def brier(probabilities: Sequence[float]) -> float:
    """Mean binary Brier score of the gold probabilities (lower is better)."""
    values = np.asarray(probabilities, dtype=float)
    return float(np.mean((1.0 - values) ** 2)) if len(values) else 0.0


def brier_multiclass(
    results: Sequence[DecisionResult], questions: Sequence[Question]
) -> float:
    """Proper multiclass Brier score: mean of the squared error over all labels."""
    if len(results) != len(questions):
        raise ValueError("results and questions must have the same length")
    if not results:
        return 0.0
    total = 0.0
    for result, question in zip(results, questions):
        expected = gold_label(question)
        total += sum(
            (probability - (1.0 if label == expected else 0.0)) ** 2
            for label, probability in result.probabilities.items()
        )
    return total / len(results)


def reliability(
    confidences: Sequence[float], correct: Sequence[int], bins: int = 10
) -> list[dict]:
    """Bin predictions by confidence; return observed vs predicted accuracy per bin."""
    conf = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=int)
    if len(conf) != len(corr):
        raise ValueError("confidences and correct must have the same length")
    edges = np.linspace(0.0, 1.0, bins + 1)
    out = []
    for lo, hi in pairwise(edges):
        mask = (conf >= lo) & (conf < hi if hi < 1 else conf <= hi)
        if mask.any():
            out.append(
                {
                    "bin": f"{lo:.1f}-{hi:.1f}",
                    "count": int(mask.sum()),
                    "confidence": float(conf[mask].mean()),
                    "accuracy": float(corr[mask].mean()),
                }
            )
    return out


def ece(confidences: Sequence[float], correct: Sequence[int], bins: int = 10) -> float:
    """Expected calibration error of the predicted confidences (lower is better)."""
    rows = reliability(confidences, correct, bins)
    if not rows:
        return 0.0
    total = sum(row["count"] for row in rows)
    return float(
        sum(row["count"] * abs(row["confidence"] - row["accuracy"]) for row in rows) / total
    )


def fit_threshold(
    confidences: Sequence[float], correct: Sequence[int], target_precision: float = 0.9
) -> float:
    """Lowest confidence cutoff that reaches target precision.

    Predictions below the cutoff should be escalated to a stronger model or a human.
    Returning the lowest qualifying cutoff keeps as much coverage as possible.
    """
    conf = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=int)
    if len(conf) != len(corr):
        raise ValueError("confidences and correct must have the same length")
    if len(conf) == 0:
        return 1.0
    for cutoff in np.linspace(0.0, 1.0, 101):
        mask = conf >= cutoff
        if mask.sum() == 0:
            break
        if corr[mask].mean() >= target_precision:
            return float(cutoff)
    return 1.0


def option_order_invariance(
    client,
    state: dict,
    question: Question,
    permutations: int = 5,
) -> bool:
    """True when the top answer stays the same across option permutations."""
    if not isinstance(question, ChoiceQuestion):
        return True
    rng = random.Random(0)
    tops = []
    for _ in range(permutations):
        gold = question.gold_index if question.gold_index is not None else 0
        options, new_gold = shuffle_with_gold(question.options, gold, rng)
        variant = ChoiceQuestion(label=question.label, options=options, gold_index=new_gold)
        result = client.decision(state, [variant])[0]
        tops.append(predicted_label(result))
    return len(set(tops)) == 1
