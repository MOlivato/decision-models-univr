# decision-models-univr

Thesis + internship material on **decision models** (System One / typed decision models),
a collaboration between UniVR and the University of Brescia (Matteo Olivato).

A decision model reads a *state* plus questions whose answers are declared up front and
returns a probability for every answer instead of generated text. The three question
types are **Noul** (is it true?), **Choice** (one of N options) and **Score** (an ordinal rubric).

## Project briefs

- [English](brief_EN.md) · [Italiano](brief_IT.md)

## Guides

- [Guideline (EN)](GUIDELINE.md) · [Guida (IT)](GUIDA.md) · [Contributing](CONTRIBUTING.md)

## Layout

```
notebooks/en|it/    zero-to-hero curriculum (identical code, translated prose)
src/decision_qa/    reusable conversion, backend, evaluation and training code
data/               schema docs and small regenerable samples
configs/            backend configurations (hosted / local)
```

## Curriculum

| # | Notebook | Goal |
|---|---|---|
| 00 | Setup and first decision | Install, configure a backend, make a first call |
| 01 | Question paradigms | Noul, Choice, Score; confidence and invariance |
| 02 | Hosted vs open vs logits | Compare the operational approaches |
| 03 | QA → decision dataset | Convert PubMedQA and Banking77 to the target schema |
| 04 | Train a small model | LoRA fine-tune on the converted data |
| 05 | Evaluate and calibrate | Accuracy, Brier, ECE, thresholds |
| 06 | Agent / RL bridge | From typed decisions to an agent loop |

## Setup (uv)

```bash
uv python install 3.12
uv sync                         # base + dev environment in .venv
uv sync --extra train           # add torch/transformers/peft for notebook 04
cp .env.example .env            # local by default; free route only if hosted
uv run jupyter lab
```

Run code directly with `uv run python ...`. The project is installed editable, so
`import decision_qa` works from notebooks and scripts.

## Resources

Everything here is **free or open**: public datasets (PubMedQA, Banking77), open-weight
models (Laya, Kev, Tev1, minimind-jev), open-source runtimes (Ollama, llama.cpp) and
free papers/docs. No paid API key is required — the local backend is the default.

Start from the curated [awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models)
list; free entry points are the [concept docs](https://docs.typesafe.ai/introduction),
the [Milvus cookbook](https://github.com/milvus-io/bootcamp/tree/master/bootcamp/RAG/search_with_jev),
[awesome-jev-prompts](https://github.com/vicfei/awesome-jev-prompts), and the open-access
papers linked in notebook 05.
