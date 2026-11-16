"""Minimal LoRA fine-tuning on converted decision data (notebook 04).

Install the optional extra first: `uv sync --extra train`.
Uses open weights and runs locally; no paid service is involved.
"""

from __future__ import annotations

import os
from pathlib import Path

from .config import ROOT
from .qa_to_dm import read_jsonl
from .questions import ChoiceQuestion, DecisionRecord


def _prompt_and_answer(record: DecisionRecord) -> tuple[str, str] | None:
    question = next((q for q in record.questions if isinstance(q, ChoiceQuestion)), None)
    if question is None or question.gold_index is None:
        return None
    state = "\n".join(f"{key}: {value}" for key, value in record.state.items())
    options = "\n".join(
        f"{chr(65 + index)}) {option}" for index, option in enumerate(question.options)
    )
    task = record.state.get("question", question.label)
    prompt = (
        "### State\n"
        + state
        + "\n\n### Question\n"
        + task
        + "\n\n### Options\n"
        + options
        + "\n\n### Answer"
    )
    return prompt, " " + chr(65 + question.gold_index)


def build_text_pairs(records: list[DecisionRecord]) -> list[tuple[str, str]]:
    pairs = [_prompt_and_answer(r) for r in records]
    return [p for p in pairs if p is not None]


def train(
    data_path: str | Path = "data/decision_dataset.jsonl",
    output_dir: str | Path = "checkpoints/dm-lora",
    base_model: str | None = None,
    epochs: float = 1.0,
    max_length: int = 512,
) -> Path:
    """Fine-tune a small open causal LM with LoRA and return the adapter directory."""
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        Trainer,
        TrainingArguments,
    )

    base_model = base_model or os.getenv("DM_BASE_MODEL", "Qwen/Qwen2.5-0.5B")
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    pairs = build_text_pairs(read_jsonl(data_path))
    if not pairs:
        raise ValueError("No choice questions found in the dataset.")

    class DecisionDataset(torch.utils.data.Dataset):
        def __len__(self):
            return len(pairs)

        def __getitem__(self, idx):
            prompt, answer = pairs[idx]
            prompt_ids = tokenizer(prompt, add_special_tokens=True)["input_ids"]
            answer_ids = tokenizer(answer, add_special_tokens=False)["input_ids"]
            # Reserve room for the answer: truncate the prompt, never the label.
            keep = max(0, max_length - len(answer_ids))
            prompt_ids = prompt_ids[-keep:] if keep else []
            input_ids = prompt_ids + answer_ids
            labels = [-100] * len(prompt_ids) + answer_ids
            return {
                "input_ids": input_ids,
                "attention_mask": [1] * len(input_ids),
                "labels": labels,
            }

    def collate(features):
        longest = max(len(f["input_ids"]) for f in features)
        batch = {"input_ids": [], "attention_mask": [], "labels": []}
        for f in features:
            pad = longest - len(f["input_ids"])
            batch["input_ids"].append(f["input_ids"] + [tokenizer.pad_token_id] * pad)
            batch["attention_mask"].append(f["attention_mask"] + [0] * pad)
            batch["labels"].append(f["labels"] + [-100] * pad)
        return {k: torch.tensor(v) for k, v in batch.items()}

    model = AutoModelForCausalLM.from_pretrained(base_model)
    model = get_peft_model(
        model,
        LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj"],
            task_type="CAUSAL_LM",
        ),
    )

    args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
        logging_steps=10,
        save_strategy="no",
        report_to=[],
        seed=42,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=DecisionDataset(),
        data_collator=collate,
    )
    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    return output_dir
