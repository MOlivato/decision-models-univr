"""Accuracy, calibration and confidence-threshold utilities."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import pairwise

import numpy as np

from .backends import DecisionResult
from .questions import NoulQuestion, Question


def gold_probability(result: DecisionResult, question: Question) -> float:
    """Probability the model assigned to the gold answer of one question."""
    if isinstance(question, NoulQuestion):
        key = "true" if question.gold else "false"
    else:
        key = (
            question.options[question.gold_index]
            if hasattr(question, "options")
            else question.levels[question.gold_index]
        )
    return float(result.probabilities.get(key, 0.0))


def brier(probabilities: Sequence[float]) -> float:
    """Mean Brier score of the gold answers (lower is better)."""
    values = np.asarray(probabilities, dtype=float)
    return float(np.mean((1.0 - values) ** 2)) if len(values) else 0.0


def accuracy(results: Sequence[DecisionResult], questions: Sequence[Question]) -> float:
    """Fraction of questions whose gold answer is the model's top answer."""
    if not results:
        return 0.0
    hits = 0
    for result, question in zip(results, questions):
        gold = gold_probability(result, question)
        top = max(result.probabilities.values())
        hits += int(gold >= top - 1e-12)
    return hits / len(results)


def reliability(
    confidences: Sequence[float], correct: Sequence[int], bins: int = 10
) -> list[dict]:
    """Bin predictions by confidence; return observed vs predicted accuracy per bin."""
    conf = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=int)
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
    """Expected calibration error (lower is better)."""
    rows = reliability(confidences, correct, bins)
    if not rows:
        return 0.0
    total = sum(r["count"] for r in rows)
    return float(sum(r["count"] * abs(r["confidence"] - r["accuracy"]) for r in rows) / total)


def fit_threshold(
    confidences: Sequence[float], correct: Sequence[int], target_precision: float = 0.9
) -> float:
    """Lowest confidence cutoff reaching target precision on a validation split.

    Predictions below the cutoff should be escalated to a stronger model or a human.
    """
    conf = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=int)
    best = 1.0
    for cutoff in np.linspace(0.0, 1.0, 101):
        mask = conf >= cutoff
        if mask.sum() == 0:
            break
        if corr[mask].mean() >= target_precision:
            best = float(cutoff)
    return best


def option_order_invariance(
    client,
    state: dict,
    question: Question,
    permutations: int = 5,
) -> float:
    """How often the top answer stays the same when option order changes."""
    import random

    from .distractors import shuffle_with_gold
    from .questions import ChoiceQuestion

    if not isinstance(question, ChoiceQuestion):
        return 1.0
    rng = random.Random(0)
    tops = []
    for _ in range(permutations):
        options, new_gold = shuffle_with_gold(question.options, question.gold_index or 0, rng)
        variant = ChoiceQuestion(label=question.label, options=options, gold_index=new_gold)
        result = client.decision(state, [variant])[0]
        tops.append(max(result.probabilities, key=result.probabilities.get))
    return len(set(tops)) == 1
