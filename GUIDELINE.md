# Guideline

Working rules for `decision-models-univr`. Italian version: [GUIDA.md](GUIDA.md).
Overview: [README.md](README.md).

## Scope

A bachelor-thesis and internship workspace on **decision models**: learn the
paradigms, convert a QA dataset into decision-model training data, evaluate it, and
then bridge to an agent/RL task. Keep the repository **minimal and clean**: a few
small, focused files beat sprawling scaffolding.

## Quickstart

```bash
uv python install 3.12          # once, if Python 3.12 is not available
uv sync                         # base and dev environment
uv sync --extra train           # optional, only for notebook 04
cp .env.example .env            # local backend by default
uv run jupyter lab
```

## Repository map

- `notebooks/en/` and `notebooks/it/`: the seven lessons, same code cells.
- `notebooks/images/`: diagrams used by the lessons.
- `src/decision_qa/`: reusable code. Notebooks import from here.
- `scripts/make_figures.py`: regenerates the diagrams.
- `tests/`: pipeline and repository quality checks.
- `data/`: schema documentation and tiny offline samples.
- `docs/`: free papers and saved articles as PDF.
- `configs/`: local and free hosted backend settings.

## Conventions

- **Free only.** Use public datasets, open models, open-source libraries, and free
  routes. Never introduce a paid API key or paid tier.
- **Notebooks.** Keep `notebooks/en/` and `notebooks/it/` in sync: identical code
  cells, translated markdown only. Add reusable code to `src/decision_qa/`, not to
  notebook cells.
- **Atomic cells.** Each code cell should demonstrate one idea and end with a print
  or an assert that validates it.
- **Data.** Small regenerable samples live in `data/samples/`. Generated JSONL,
  checkpoints, caches, and datasets are gitignored.
- **Secrets.** Never commit `.env`, API keys, or credentials. Read values from the
  environment and document them in `.env.example`.
- **Agent notes.** `AGENTS.md` is local-only and gitignored. It is intentionally
  shadowed online; do not force-add it.
- **Characters.** Keep prose ASCII-friendly. Do not use em dashes, arrows, or other
  uncommon typographic characters.

## Workflow

1. Start at notebook `00` and proceed in order. Notebook `03` produces the JSONL
   consumed by notebooks `04` and `05`.
2. Run offline with `MockClient` until a free local endpoint is available, then switch
   to `SystemOneClient`. The interface does not change.
3. Add or update tests when behavior changes.
4. Execute every changed notebook in both language folders.
5. Before committing, run the full check sequence below.

## Quality bar

- Report probabilities, not just labels: accuracy **and** calibration (Brier, ECE).
- Fit confidence thresholds on a validation split; escalate uncertain decisions.
- Test option-order invariance: a decision must not depend on option ordering.
- Treat the model's `state` as untrusted input. See the JevAdvBench paper in `docs/`.
- Document any new resource in `docs/README.md` and keep it free or open.

## Definition of done

```bash
uv run ruff format .
uv run ruff check .
uv run pytest -q
```

All three must pass, and every code cell in a changed notebook must execute without
errors. If you change a diagram, run `uv run python scripts/make_figures.py` and
commit the updated PNG.

Further detail: [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md),
[data/SCHEMA.md](data/SCHEMA.md), [docs/README.md](docs/README.md).
