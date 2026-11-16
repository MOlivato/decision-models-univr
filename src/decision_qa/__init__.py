"""Reusable code for the decision-models-univr curriculum."""

from .backends import DecisionResult, MockClient, SystemOneClient, make_client
from .config import BackendConfig, load_config
from .evaluate import (
    accuracy,
    brier,
    brier_multiclass,
    ece,
    fit_threshold,
    gold_label,
    gold_probability,
    predicted_label,
    reliability,
)
from .qa_to_dm import (
    ConversionConfig,
    build_dataset,
    convert_banking77,
    convert_pubmedqa,
    load_examples,
    read_jsonl,
)
from .questions import (
    ChoiceQuestion,
    DecisionRecord,
    NoulQuestion,
    ScoreQuestion,
    question_labels,
    to_systemone_payload,
)

__all__ = [
    "BackendConfig",
    "ChoiceQuestion",
    "ConversionConfig",
    "DecisionRecord",
    "DecisionResult",
    "MockClient",
    "NoulQuestion",
    "ScoreQuestion",
    "SystemOneClient",
    "accuracy",
    "brier",
    "brier_multiclass",
    "build_dataset",
    "convert_banking77",
    "convert_pubmedqa",
    "ece",
    "fit_threshold",
    "gold_label",
    "gold_probability",
    "load_config",
    "load_examples",
    "make_client",
    "predicted_label",
    "question_labels",
    "read_jsonl",
    "reliability",
    "to_systemone_payload",
]
