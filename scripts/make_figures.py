"""Generate the conceptual diagrams used by the notebooks.

Run with: uv run python scripts/make_figures.py
Output: notebooks/images/*.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "images"

BLUE = "#DCEAF7"
BLUE_EDGE = "#2F5D8A"
GREEN = "#DDEEDD"
GREEN_EDGE = "#3E6B3E"
AMBER = "#FBEFD5"
AMBER_EDGE = "#8A5A00"
GRAY = "#EEEEEE"
GRAY_EDGE = "#666666"
TEXT = "#1F2937"


def canvas(width: float = 12, height: float = 4):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, face=BLUE, edge=BLUE_EDGE, size=10):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.4,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=size,
        color=TEXT,
    )


def arrow(ax, start, end, color="#555555", style="-|>", rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=14,
            linewidth=1.4,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
        )
    )


def save(fig, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def decision_flow():
    fig, ax = canvas(12, 3.6)
    box(ax, 0.01, 0.36, 0.24, 0.30, "State\ncontext + question")
    box(
        ax,
        0.34,
        0.36,
        0.26,
        0.30,
        "Decision model\nreads state,\nscores declared answers",
        face=GREEN,
        edge=GREEN_EDGE,
    )
    box(
        ax,
        0.70,
        0.36,
        0.28,
        0.30,
        "Probabilities\none value per\ndeclared answer",
        face=AMBER,
        edge=AMBER_EDGE,
    )
    arrow(ax, (0.25, 0.51), (0.34, 0.51))
    arrow(ax, (0.60, 0.51), (0.70, 0.51))
    ax.text(0.47, 0.20, "Questions: Noul, Choice, Score", ha="center", fontsize=10, color=TEXT)
    ax.text(0.84, 0.20, "No generated text", ha="center", fontsize=10, color=TEXT)
    save(fig, "decision_model_flow.png")


def question_types():
    examples = [
        ("Noul: is the treatment effective?", ["true", "false"], [0.86, 0.14]),
        (
            "Choice: what is the verdict?",
            ["effective", "ineffective", "unclear"],
            [0.80, 0.10, 0.10],
        ),
        (
            "Score: how strong is the evidence?",
            ["weak", "moderate", "strong"],
            [0.09, 0.09, 0.82],
        ),
    ]
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.4))
    for ax, (title, labels, values), color in zip(axes, examples, colors):
        ax.barh(labels, values, color=color, height=0.55)
        ax.set_xlim(0, 1)
        ax.set_xlabel("Probability")
        ax.set_title(title, fontsize=10)
        ax.grid(axis="x", alpha=0.25)
        for index, value in enumerate(values):
            ax.text(value + 0.02, index, f"{value:.2f}", va="center", fontsize=9)
    fig.tight_layout()
    save(fig, "question_types.png")


def backend_choices():
    fig, ax = canvas(12, 4.2)
    items = [
        (
            0.01,
            "Local open model\nOllama or llama.cpp\nLaya, Kev, Tev1\nfree, offline",
        ),
        (
            0.34,
            "Free hosted route\nfree tier only\nno local GPU needed\nfree account",
        ),
        (
            0.67,
            "Training-free logits\nLitJev, SemIf, AnyJev\nread option tokens\nfree, open source",
        ),
    ]
    for x, text in items:
        box(ax, x, 0.50, 0.30, 0.34, text, size=9)
        arrow(ax, (x + 0.15, 0.50), (x + 0.15, 0.32))
    box(
        ax,
        0.20,
        0.10,
        0.60,
        0.18,
        "Same interface: probabilities for the answers you declare",
        face=GRAY,
        edge=GRAY_EDGE,
        size=10,
    )
    ax.text(
        0.50, 0.92, "Three free ways to obtain a decision", ha="center", fontsize=12, color=TEXT
    )
    save(fig, "backend_choices.png")


def qa_to_dm():
    fig, ax = canvas(14, 5)
    box(ax, 0.01, 0.30, 0.16, 0.40, "QA example\ncontext\nquestion\nanswer\nlabel")
    box(ax, 0.21, 0.36, 0.14, 0.28, "convert_*\nfunction", face=GREEN, edge=GREEN_EDGE)
    arrow(ax, (0.17, 0.50), (0.21, 0.50))

    questions = [
        (0.64, "Noul\nstatement -> true / false"),
        (0.42, "Choice\noptions -> one correct"),
        (0.20, "Score\nordered levels -> one level"),
    ]
    for y, text in questions:
        box(ax, 0.40, y, 0.24, 0.16, text, face=AMBER, edge=AMBER_EDGE, size=9)
        arrow(ax, (0.35, 0.50), (0.40, y + 0.08), rad=0.0)

    box(ax, 0.69, 0.32, 0.13, 0.36, "JSONL\none record\nper example", face=GRAY, edge=GRAY_EDGE)
    for y, _ in questions:
        arrow(ax, (0.64, y + 0.08), (0.69, 0.50))

    box(ax, 0.87, 0.54, 0.12, 0.20, "Train\nnotebook 04", face=BLUE, edge=BLUE_EDGE, size=9)
    box(ax, 0.87, 0.26, 0.12, 0.20, "Evaluate\nnotebook 05", face=BLUE, edge=BLUE_EDGE, size=9)
    arrow(ax, (0.82, 0.55), (0.87, 0.64))
    arrow(ax, (0.82, 0.45), (0.87, 0.36))
    save(fig, "qa_to_decision_dataset.png")


def training_pipeline():
    fig, ax = canvas(13, 4.2)
    box(ax, 0.01, 0.42, 0.20, 0.24, "Open base model\nQwen2.5-0.5B")
    box(ax, 0.28, 0.42, 0.20, 0.24, "LoRA adapter\nrank 16", face=GREEN, edge=GREEN_EDGE)
    box(ax, 0.55, 0.42, 0.18, 0.24, "Decision\nbehaviour")
    box(ax, 0.80, 0.42, 0.18, 0.24, "Saved adapter\ncheckpoints/", face=AMBER, edge=AMBER_EDGE)
    arrow(ax, (0.21, 0.54), (0.28, 0.54))
    arrow(ax, (0.48, 0.54), (0.55, 0.54))
    arrow(ax, (0.73, 0.54), (0.80, 0.54))

    box(ax, 0.28, 0.10, 0.20, 0.18, "JSONL\nfrom notebook 03", face=GRAY, edge=GRAY_EDGE, size=9)
    box(ax, 0.55, 0.10, 0.18, 0.18, "Trainer\none epoch", face=GRAY, edge=GRAY_EDGE, size=9)
    arrow(ax, (0.48, 0.19), (0.55, 0.19))
    arrow(ax, (0.64, 0.28), (0.64, 0.42))
    save(fig, "training_pipeline.png")


def agent_loop():
    fig, ax = canvas(13, 5)
    box(ax, 0.02, 0.40, 0.15, 0.22, "State\nquestion +\nhistory")
    box(
        ax,
        0.21,
        0.40,
        0.17,
        0.22,
        "Decision model\nChoice over actions",
        face=GREEN,
        edge=GREEN_EDGE,
        size=9,
    )
    box(ax, 0.42, 0.40, 0.15, 0.22, "Rules\nhard constraints", face=AMBER, edge=AMBER_EDGE, size=9)
    box(
        ax,
        0.61,
        0.40,
        0.16,
        0.22,
        "Confidence gate\ncommit or escalate",
        face=AMBER,
        edge=AMBER_EDGE,
        size=9,
    )
    box(ax, 0.81, 0.40, 0.16, 0.22, "Action\nenvironment", face=BLUE, edge=BLUE_EDGE, size=9)
    for start, end in [
        ((0.17, 0.51), (0.21, 0.51)),
        ((0.38, 0.51), (0.42, 0.51)),
        ((0.57, 0.51), (0.61, 0.51)),
        ((0.77, 0.51), (0.81, 0.51)),
    ]:
        arrow(ax, start, end)
    # Return path above the boxes: up, left, then down into the state.
    arrow(ax, (0.89, 0.62), (0.89, 0.80), style="-", color="#8A5A00")
    arrow(ax, (0.89, 0.80), (0.10, 0.80), style="-", color="#8A5A00")
    arrow(ax, (0.10, 0.80), (0.10, 0.62), color="#8A5A00")
    ax.text(
        0.50,
        0.89,
        "new state + reward = task success - step cost",
        ha="center",
        fontsize=10,
        color="#8A5A00",
    )
    ax.text(
        0.50,
        0.14,
        "Deterministic code owns rules and gates; the model only scores actions",
        ha="center",
        fontsize=10,
        color=TEXT,
    )
    save(fig, "agent_loop.png")


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    decision_flow()
    question_types()
    backend_choices()
    qa_to_dm()
    training_pipeline()
    agent_loop()


if __name__ == "__main__":
    main()
