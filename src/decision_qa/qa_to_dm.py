"""Turn public QA datasets (PubMedQA, Banking77) into decision-model training data."""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path

from .config import ROOT
from .distractors import sample_distractors, shuffle_with_gold
from .questions import ChoiceQuestion, DecisionRecord, NoulQuestion, ScoreQuestion

SAMPLES = ROOT / "data" / "samples"


@dataclass
class QaExample:
    id: str
    source: str
    context: str
    question: str
    answer: str
    label: str | None = None
    alternatives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConversionConfig:
    n_distractors: int = 3
    seed: int = 42
    max_context_chars: int = 1200
    hard_fraction: float = 0.5


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + " ..."


def _cache_dir() -> str | None:
    value = os.getenv("HF_CACHE_DIR")
    if not value:
        return None
    path = Path(value)
    return str(path if path.is_absolute() else ROOT / path)


def _read_sample(dataset: str, split: str) -> list[QaExample]:
    path = SAMPLES / f"{dataset}_{split}.jsonl"
    if not path.exists():
        return []
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [QaExample(**row) for row in rows]


def _load_hf(dataset: str, split: str) -> list[QaExample]:
    from datasets import load_dataset

    cache_dir = _cache_dir()
    if dataset == "pubmedqa":
        ds = load_dataset(
            "qiaojin/PubMedQA", "pqa_labeled", split=split, cache_dir=cache_dir
        )
        rows = []
        for index, row in enumerate(ds):
            ctx = row.get("context")
            if isinstance(ctx, dict):
                ctx = ctx.get("contexts", [])
            context = "\n".join(ctx) if isinstance(ctx, list) else str(ctx or "")
            rows.append(
                QaExample(
                    id=f"pubmedqa-{split}-{index}",
                    source="pubmedqa",
                    context=context,
                    question=row["question"],
                    answer=row.get("long_answer", ""),
                    label=row.get("final_decision"),
                )
            )
        return rows

    if dataset == "banking77":
        ds = load_dataset("PolyAI/banking77", split=split, cache_dir=cache_dir)
        names = list(ds.features["label"].names)
        return [
            QaExample(
                id=f"banking77-{split}-{index}",
                source="banking77",
                context=row["text"],
                question="What is the user's intent?",
                answer=names[row["label"]],
                label=names[row["label"]],
                alternatives=names,
            )
            for index, row in enumerate(ds)
        ]

    raise ValueError(f"Unknown dataset: {dataset}")


def _partition(
    rows: list[QaExample], split: str, limit: int, seed: int
) -> list[QaExample]:
    """Deterministically split one pool into train/val/test without overlap."""
    pool = list(rows)
    random.Random(seed).shuffle(pool)
    size = len(pool)
    train_end = int(size * 0.8)
    val_end = int(size * 0.9)
    parts = {
        "train": pool[:train_end],
        "val": pool[train_end:val_end],
        "test": pool[val_end:],
    }
    return parts[split][:limit]


def load_examples(
    dataset: str, split: str = "train", limit: int = 50, seed: int = 42
) -> list[QaExample]:
    """Load a free/public dataset; fall back to the bundled sample when offline.

    PubMedQA only ships a train split. When val or test is requested, we partition
    the train pool deterministically, so the three splits never overlap.
    """
    try:
        return _load_hf(dataset, split)[:limit]
    except Exception as exc:  # noqa: BLE001  # missing split or offline cache
        if split != "train":
            try:
                return _partition(_load_hf(dataset, "train"), split, limit, seed)
            except Exception as nested:  # noqa: BLE001
                print(f"[offline fallback] {dataset}/train: {type(nested).__name__}")
        print(f"[offline fallback] {dataset}/{split}: {type(exc).__name__}: {exc}")
        return _read_sample(dataset, split)[:limit]


def convert_pubmedqa(
    rows: list[QaExample], cfg: ConversionConfig = ConversionConfig(), split: str = "train"
) -> list[DecisionRecord]:
    """Map PubMedQA's yes/no/maybe decision to Noul + Choice + Score questions."""
    rng = random.Random(cfg.seed)
    answers = [row.answer for row in rows if row.answer]
    decisions = ["yes", "no", "maybe"]
    score_levels = ["contradicted", "uncertain", "supported"]
    records = []

    for index, row in enumerate(rows):
        decision = row.label if row.label in decisions else "maybe"
        options, gold_index = shuffle_with_gold(decisions, decisions.index(decision), rng)
        wrong = sample_distractors(row.answer, answers, 1, rng, hard_fraction=1.0)
        contradicted = wrong[0] if wrong else "There is no evidence for this answer."

        # Alternate the candidate shown to the Score question, so the rubric has
        # both supported and contradicted examples instead of a constant label.
        use_gold = index % 2 == 0
        candidate = row.answer if use_gold else contradicted
        gold_score = 2 if use_gold else 0

        records.append(
            DecisionRecord(
                id=row.id,
                source="pubmedqa",
                split=split,
                state={
                    "context": _truncate(row.context, cfg.max_context_chars),
                    "question": row.question,
                },
                questions=[
                    NoulQuestion(
                        label="answer_supported",
                        statement=f"The answer to the question is: {row.answer}",
                        gold=True,
                    ),
                    NoulQuestion(
                        label="answer_contradicted",
                        statement=f"The answer to the question is: {contradicted}",
                        gold=False,
                    ),
                    ChoiceQuestion(label="decision", options=options, gold_index=gold_index),
                    ScoreQuestion(
                        label="candidate_support",
                        rubric=(
                            "Rate how well this candidate answer is supported by the context: "
                            + _truncate(candidate, 240)
                        ),
                        levels=score_levels,
                        gold_index=gold_score,
                    ),
                ],
            )
        )
    return records


def convert_banking77(
    rows: list[QaExample], cfg: ConversionConfig = ConversionConfig(), split: str = "train"
) -> list[DecisionRecord]:
    """Map Banking77's 77-way intent label to a Choice + Noul + Score question set."""
    rng = random.Random(cfg.seed)
    labels = sorted(
        {row.label for row in rows if row.label}
        | {name for row in rows for name in row.alternatives}
    )
    records = []

    for index, row in enumerate(rows):
        distractors = sample_distractors(
            row.label, labels, cfg.n_distractors, rng, cfg.hard_fraction
        )
        options, gold_index = shuffle_with_gold([row.label, *distractors], 0, rng)
        wrong = distractors[0] if distractors else "an unrelated intent"

        use_gold = index % 2 == 0
        candidate = row.label if use_gold else wrong
        gold_score = 2 if use_gold else 0

        records.append(
            DecisionRecord(
                id=row.id,
                source="banking77",
                split=split,
                state={
                    "context": _truncate(row.context, cfg.max_context_chars),
                    "question": row.question,
                },
                questions=[
                    ChoiceQuestion(label="intent", options=options, gold_index=gold_index),
                    NoulQuestion(
                        label="intent_true",
                        statement=f"This message is about {row.label}.",
                        gold=True,
                    ),
                    NoulQuestion(
                        label="intent_false",
                        statement=f"This message is about {wrong}.",
                        gold=False,
                    ),
                    ScoreQuestion(
                        label="candidate_relevance",
                        rubric=(
                            "Rate how relevant this candidate intent is to the message: "
                            + candidate
                        ),
                        levels=["unrelated", "partially related", "correct"],
                        gold_index=gold_score,
                    ),
                ],
            )
        )
    return records


CONVERTERS = {"pubmedqa": convert_pubmedqa, "banking77": convert_banking77}


def build_dataset(
    dataset: str,
    out_path: str | Path,
    limits: dict[str, int] | None = None,
    cfg: ConversionConfig = ConversionConfig(),
) -> Path:
    """Load, convert, split and write JSONL. Returns the output path."""
    limits = limits or {"train": 60, "val": 10, "test": 10}
    out_path = Path(out_path)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as handle:
        for split, limit in limits.items():
            rows = load_examples(dataset, split=split, limit=limit, seed=cfg.seed)
            records = CONVERTERS[dataset](rows, cfg, split=split)
            for record in records:
                handle.write(record.model_dump_json() + "\n")
    return out_path


def read_jsonl(path: str | Path) -> list[DecisionRecord]:
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    lines = path.read_text(encoding="utf-8").splitlines()
    return [
        DecisionRecord.model_validate_json(line) for line in lines if line.strip()
    ]
