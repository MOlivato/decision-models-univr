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


def _normalize(values: dict[str, float]) -> dict[str, float]:
    total = sum(values.values())
    if total <= 0:
        return {k: 1.0 / len(values) for k in values}
    return {k: v / total for k, v in values.items()}


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


def _probabilities_from(item: Any, labels: list[str]) -> dict[str, float]:
    if isinstance(item, dict):
        for key in ("probabilities", "distribution", "scores", "probs"):
            value = item.get(key)
            if isinstance(value, dict):
                return _normalize({str(k): float(v) for k, v in value.items()})
            if isinstance(value, list):
                return _normalize(dict(zip(labels, (float(v) for v in value))))
        if item.get("label") in labels and "probability" in item:
            chosen = str(item["label"])
            other = 1.0 - float(item["probability"])
            return _normalize({chosen: float(item["probability"]), **{l: other for l in labels if l != chosen}})
    return _normalize({label: 1.0 for label in labels})


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
        data = response.json()
        return self._parse(data, questions)

    @staticmethod
    def _parse(data: Any, questions: list[Question]) -> list[DecisionResult]:
        answers = _answers_from(data)
        results: list[DecisionResult] = []
        for i, question in enumerate(questions):
            labels = question_labels(question)
            item = answers[i] if i < len(answers) else None
            probs = _probabilities_from(item, labels)
            # Keep only the declared answers, in declared order.
            probs = _normalize({label: probs.get(label, probs.get(str(i), 1.0)) for i, label in enumerate(labels)})
            results.append(DecisionResult(question_label=question.label, probabilities=probs, raw=item))
        return results


class MockClient:
    """Deterministic, key-free stand-in. Uses gold labels when present; otherwise uniform.

    It lets every notebook run offline and for free, and makes the data pipeline testable.
    """

    def __init__(self, seed: int = 42, quality: float = 0.85):
        self.rng = random.Random(seed)
        self.quality = quality

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
                probs = _normalize({label: 1.0 for label in labels})
            else:
                p = min(0.99, max(0.5, self.quality + self.rng.uniform(-0.05, 0.05)))
                rest = (1.0 - p) / max(1, len(labels) - 1)
                probs = {label: (p if label == gold_label else rest) for label in labels}
            results.append(DecisionResult(question_label=question.label, probabilities=probs))
        return results


def make_client(config: BackendConfig | None = None, offline: bool = False):
    """Return a client. `offline=True` always uses the free mock (no keys, no network)."""
    return MockClient() if offline else SystemOneClient(config)
