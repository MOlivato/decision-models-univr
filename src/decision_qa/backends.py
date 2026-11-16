"""Backends that speak /v1/systemone, plus an offline mock for free, key-free demos."""

from __future__ import annotations

import random
from typing import Any

import requests
from pydantic import BaseModel

from .config import BackendConfig, load_config
from .questions import Question, question_labels, to_systemone_payload


class DecisionResult(BaseModel):
    question_label: str
    probabilities: dict[str, float]
    raw: dict[str, Any] | None = None


def _uniform(labels: list[str]) -> dict[str, float]:
    return {label: 1.0 / len(labels) for label in labels}


def _normalize(values: dict[str, float]) -> dict[str, float]:
    if not values:
        return {}
    total = sum(value for value in values.values() if value > 0)
    if total <= 0:
        return _uniform(list(values))
    return {label: max(0.0, value) / total for label, value in values.items()}


def _answers_from(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("answers", "results", "questions", "decisions", "scores"):
            if isinstance(data.get(key), list):
                return data[key]
        if isinstance(data.get("probabilities"), dict):
            return [data]
    return []


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _probabilities_from(item: Any, labels: list[str]) -> dict[str, float]:
    """Read a probability dictionary from one answer, tolerating common shapes."""
    if isinstance(item, dict):
        for key in ("probabilities", "distribution", "scores", "probs"):
            value = item.get(key)
            if isinstance(value, dict):
                return {str(label): _as_float(probability) for label, probability in value.items()}
            if isinstance(value, list):
                return {
                    label: _as_float(probability)
                    for label, probability in zip(labels, value)
                }
        if item.get("label") is not None and "probability" in item:
            chosen = str(item["label"])
            others = [label for label in labels if label != chosen]
            leftover = max(0.0, 1.0 - _as_float(item["probability"]))
            share = leftover / len(others) if others else 0.0
            return {chosen: _as_float(item["probability"]), **{label: share for label in others}}
    return {}


class SystemOneClient:
    """HTTP client for any compatible /v1/systemone endpoint (local or free hosted)."""

    def __init__(self, config: BackendConfig | None = None):
        self.config = config or load_config()

    def decision(self, state: dict, questions: list[Question]) -> list[DecisionResult]:
        payload = to_systemone_payload(state, questions)
        payload["model"] = self.config.model
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        response = requests.post(
            self.config.endpoint,
            json=payload,
            headers=headers,
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        return self._parse(response.json(), questions)

    @staticmethod
    def _parse(data: Any, questions: list[Question]) -> list[DecisionResult]:
        answers = _answers_from(data)
        by_label = {
            str(answer["label"]): answer
            for answer in answers
            if isinstance(answer, dict) and answer.get("label") is not None
        }
        results: list[DecisionResult] = []
        for index, question in enumerate(questions):
            labels = question_labels(question)
            item = by_label.get(question.label)
            if item is None and index < len(answers):
                item = answers[index]
            probabilities = _probabilities_from(item, labels)
            probabilities = _normalize(
                {label: probabilities.get(label, 0.0) for label in labels}
            )
            results.append(
                DecisionResult(
                    question_label=question.label,
                    probabilities=probabilities,
                    raw=item,
                )
            )
        return results


class MockClient:
    """Deterministic, key-free stand-in for demos and tests.

    It uses the gold labels when present, matches them with probability
    `1 - error_rate`, and returns uniform probabilities when no gold is available.
    Higher `quality` produces more confident outputs.
    """

    def __init__(self, seed: int = 42, quality: float = 0.85, error_rate: float = 0.0):
        self.rng = random.Random(seed)
        if not 0.0 <= quality <= 1.0:
            raise ValueError("quality must be between 0 and 1")
        if not 0.0 <= error_rate <= 1.0:
            raise ValueError("error_rate must be between 0 and 1")
        self.quality = quality
        self.error_rate = error_rate

    def decision(self, state: dict, questions: list[Question]) -> list[DecisionResult]:
        results = []
        for question in questions:
            labels = question_labels(question)
            gold_label = None
            if getattr(question, "gold", None) is not None:
                gold_label = "true" if question.gold else "false"
            elif getattr(question, "gold_index", None) is not None:
                gold_label = labels[question.gold_index]

            if gold_label is None:
                probabilities = _uniform(labels)
            else:
                others = [label for label in labels if label != gold_label]
                floor = 1.0 / len(labels) + 0.02
                if others and self.rng.random() < self.error_rate:
                    # Simulate a wrong but confident choice.
                    chosen = self.rng.choice(others)
                    p = self.quality - self.rng.uniform(0.05, 0.25)
                else:
                    chosen = gold_label
                    p = self.quality + self.rng.uniform(0.0, 0.15)
                p = min(0.99, max(floor, p))
                rest = (1.0 - p) / max(1, len(labels) - 1)
                probabilities = {
                    label: (p if label == chosen else rest) for label in labels
                }
            results.append(
                DecisionResult(question_label=question.label, probabilities=probabilities)
            )
        return results


def make_client(config: BackendConfig | None = None, offline: bool = False):
    """Return a client. `offline=True` always uses the free mock (no keys, no network)."""
    return MockClient() if offline else SystemOneClient(config)
