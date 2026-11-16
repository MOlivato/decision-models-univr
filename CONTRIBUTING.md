# Contributing

Keep it minimal and clean.

- Add one idea per file; prefer small, focused notebooks and modules.
- Every notebook exists twice: `notebooks/en/` and `notebooks/it/`. Keep **code cells
  identical** and translate only the markdown prose.
- Reusable code goes in `src/decision_qa/`, not in notebook cells.
- Never commit `.env`, API keys, checkpoints, or downloaded datasets.
- Run `uv run ruff check src` and `uv run pytest -q` before opening a PR.
- Agent-specific local notes belong in the gitignored `AGENTS.md`, which is local
  only and intentionally shadowed online.
