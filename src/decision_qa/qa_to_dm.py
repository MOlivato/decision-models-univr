"""Turn public QA datasets (PubMedQA, Banking77) into decision-model training data."""

from __future__ import annotations

import json
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


def _read_sample(dataset: str, split: str) -> list[QaExample]:
    path = SAMPLES / f"{dataset}_{split}.jsonl"
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [QaExample(**row) for row in rows]


def load_examples(dataset: str, split: str = "train", limit: int = 50) -> list[QaExample]:
    """Load a free/public dataset; fall back to the bundled tiny sample offline."""
    try:
        from datasets import load_dataset

        if dataset == "pubmedqa":
            ds = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split=split)
            rows = []
            for i, row in enumerate(ds):
                ctx = row.get("context")
                if isinstance(ctx, dict):
                    ctx = ctx.get("contexts", [])
                context = "\n".join(ctx) if isinstance(ctx, list) else str(ctx or "")
                rows.append(
                    QaExample(
                        id=f"pubmedqa-{split}-{i}",
                        source="pubmedqa",
                        context=context,
                        question=row["question"],
                        answer=row.get("long_answer", ""),
                        label=row.get("final_decision"),
                    )
                )
        elif dataset == "banking77":
            ds = load_dataset("PolyAI/banking77", split=split)
            names = ds.features["label"].names
            rows = [
                QaExample(
                    id=f"banking77-{split}-{i}",
                    source="banking77",
                    context=row["text"],
                    question="What is the user's intent?",
                    answer=names[row["label"]],
                    label=names[row["label"]],
                )
                for i, row in enumerate(ds)
            ]
        else:
            raise ValueError(f"Unknown dataset: {dataset}")
        return rows[:limit]
    except Exception as exc:  # noqa: BLE001  # offline / no cache -> bundled free samples
        print(f"[offline fallback] {dataset}/{split}: {type(exc).__name__}: {exc}")
        return _read_sample(dataset, split)[:limit]


def convert_pubmedqa(
    rows: list[QaExample], cfg: ConversionConfig = ConversionConfig(), split: str = "train"
) -> list[DecisionRecord]:
    """Map PubMedQA's yes/no/maybe decision to Noul + Choice + Score questions."""
    rng = random.Random(cfg.seed)
    answers = [r.answer for r in rows if r.answer]
    decisions = ["yes", "no", "maybe"]
    score_levels = ["contradicted", "uncertain", "supported"]
    records = []

    for row in rows:
        decision = row.label if row.label in decisions else "maybe"
        options, gold_index = shuffle_with_gold(decisions, decisions.index(decision), rng)
        wrong = sample_distractors(row.answer, answers, 1, rng, hard_fraction=1.0)
        contradicted = wrong[0] if wrong else "There is no evidence for this answer."

        gold_score = {"yes": 2, "no": 0, "maybe": 1}[decision]
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
                        label="support",
                        rubric="Rate how well the proposed answer is supported by the context.",
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
    labels = sorted({r.label for r in rows if r.label})
    records = []

    for row in rows:
        distractors = sample_distractors(
            row.label, labels, cfg.n_distractors, rng, cfg.hard_fraction
        )
        options, gold_index = shuffle_with_gold([row.label, *distractors], 0, rng)
        wrong = distractors[0] if distractors else "an unrelated intent"

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
                        label="relevance",
                        rubric="How relevant is the candidate intent to the message?",
                        levels=["unrelated", "somewhat related", "correct"],
                        gold_index=2,
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

    with out_path.open("w", encoding="utf-8") as fh:
        for split, limit in limits.items():
            rows = load_examples(dataset, split=split, limit=limit)
            records = CONVERTERS[dataset](rows, cfg, split=split)
            for record in records:
                fh.write(record.model_dump_json() + "\n")
    return out_path


def read_jsonl(path: str | Path) -> list[DecisionRecord]:
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    return [DecisionRecord.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
