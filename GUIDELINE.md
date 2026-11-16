# Guideline

Working rules for `decision-models-univr`. Italian version: [GUIDA.md](GUIDA.md).

## Scope

A bachelor-thesis/internship workspace on **decision models**: learn the paradigms,
convert a QA dataset into decision-model training data, evaluate it, then bridge to
an agent/RL task. Keep it **minimal and clean** - a few small, focused files beat
sprawling scaffolding.

## Quickstart

```bash
uv sync                    # base + dev environment
uv sync --extra train      # optional, only for notebook 04
cp .env.example .env       # local backend by default
uv run jupyter lab
```

## Conventions

- **Free only.** Public datasets, open models, open-source libraries and free routes.
  Never introduce a paid API key or paid tier.
- **Notebooks**: `notebooks/en/` and `notebooks/it/` - same seven notebooks, identical
  code cells, translated markdown prose only. Add reusable code to `src/decision_qa/`,
  not to notebook cells.
- **Data**: small regenerable samples live in `data/samples/`. Generated JSONL and
  checkpoints are gitignored. Never commit datasets, `.env`, or secrets.
- **Agent notes**: `AGENTS.md` is local-only and gitignored; it is intentionally
  shadowed online. Do not force-add it.

## Workflow

1. Start at notebook `00` and proceed in order; `03` produces the JSONL that `04`
   and `05` consume.
2. Run offline (`MockClient`) until a local free endpoint is available, then switch
   to `SystemOneClient` - the interface is the same.
3. Before committing: `uv run ruff format src tests`, `uv run ruff check src tests`
   and `uv run pytest -q`.
4. Execute every changed notebook's code cells in both language folders.

## Quality bar

- Report probabilities, not just labels: accuracy **and** calibration (Brier, ECE).
- Fit confidence thresholds on a held-out split; escalate uncertain decisions.
- Test option-order invariance - a decision must not depend on option ordering.
- Treat the model's `state` as untrusted input (see JevAdvBench).

Further detail: [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md),
[data/SCHEMA.md](data/SCHEMA.md).
