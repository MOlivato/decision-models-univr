# decision-models-univr

Thesis and internship material on **decision models** (System One / typed decision
models), a collaboration between the University of Verona and the University of
Brescia (Matteo Olivato).

A decision model reads a *state* plus questions whose answers are declared up front
and returns a probability for every answer instead of generated text. The three
question types are **Noul** (is it true?), **Choice** (one of N options), and
**Score** (an ordinal rubric).

Everything in this repository is **free or open**: public datasets, open-weight
models, open-source libraries, and open-access papers. The default backend is local,
so no paid API key is required.

## Start here

| Document | Purpose |
|---|---|
| [brief_EN.md](brief_EN.md) / [brief_IT.md](brief_IT.md) | Project aim, phases, and logistics |
| [GUIDELINE.md](GUIDELINE.md) | Working rules and quality bar (English) |
| [GUIDA.md](GUIDA.md) | Step-by-step student guide (Italian) |
| [docs/README.md](docs/README.md) | Free papers and saved articles as PDF |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution rules |
| [data/SCHEMA.md](data/SCHEMA.md) | Decision-dataset JSONL schema |

## Layout

```
notebooks/en|it/    zero-to-hero curriculum (identical code, translated prose)
src/decision_qa/    backends, question types, conversion, evaluation, training
tests/              pipeline, metrics, notebook parity, and character checks
data/               schema documentation and small regenerable samples
docs/               free papers and saved blog posts as PDF
configs/            backend configurations (local and free hosted)
```

## Curriculum

| # | Notebook | Goal | Output |
|---|---|---|---|
| 00 | Setup and first decision | Configure a backend and make a first call | A probability distribution |
| 01 | Question paradigms | Noul, Choice, Score; confidence and invariance | Validated question types |
| 02 | Local, hosted, and logits | Compare the operational approaches | A backend choice |
| 03 | QA to decision dataset | Convert PubMedQA and Banking77 | `data/*_decisions.jsonl` |
| 04 | Train a small model | LoRA fine-tune on the converted data | `checkpoints/dm-lora` |
| 05 | Evaluate and calibrate | Accuracy, Brier, ECE, thresholds | Metrics and a cutoff |
| 06 | Agent and RL bridge | Typed decisions inside an agent loop | A reward trace |

Every notebook exists in `notebooks/en/` and `notebooks/it/` with the same code
cells and translated markdown.

## Setup with uv

```bash
uv python install 3.12          # once, if Python 3.12 is not available
uv sync                         # base and dev environment in .venv
uv sync --extra train           # optional, only for notebook 04
cp .env.example .env            # local backend by default
uv run jupyter lab
```

Run scripts with `uv run python ...`. The project is installed in editable mode, so
`import decision_qa` works from notebooks, tests, and scripts.

## Data flow

1. `load_examples` reads a free public dataset, or the bundled sample when offline.
2. `convert_pubmedqa` and `convert_banking77` create typed Noul, Choice, and Score questions.
3. `build_dataset` writes JSONL in the schema from `data/SCHEMA.md`.
4. Notebook 04 trains on that JSONL and notebook 05 evaluates the probabilities.

## Quality checks

```bash
uv run ruff format src tests
uv run ruff check src tests
uv run pytest -q
```

The test suite covers the conversion pipeline, metrics, response parsing, EN/IT
notebook code parity, and the ban on uncommon characters.

## Troubleshooting

- **No local model running**: notebooks use `MockClient`, which is deterministic and offline.
- **Hugging Face unavailable**: the loader falls back to the tiny samples in `data/samples/`.
- **Wrong endpoint**: check the `base_url` in `configs/` and see `cfg.endpoint`.
- **Training extra missing**: run `uv sync --extra train`, then set `RUN_TRAINING = True`.

## Resources

- Local library: [docs/README.md](docs/README.md) with free arXiv papers and saved articles.
- Curated ecosystem: [awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models).
- Concept docs: [TypeSafe introduction](https://docs.typesafe.ai/introduction).
- Hands-on cookbook: [Milvus search with Jev](https://github.com/milvus-io/bootcamp/tree/master/bootcamp/RAG/search_with_jev).
- Question patterns: [awesome-jev-prompts](https://github.com/vicfei/awesome-jev-prompts).
- Evaluation: [JevBench](https://github.com/fstandhartinger/jevbench) under MIT.
