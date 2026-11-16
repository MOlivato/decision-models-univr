# Contributing

Keep it minimal and clean.

- Add one idea per file; prefer small, focused notebooks and modules.
- Every notebook exists twice: `notebooks/en/` and `notebooks/it/`. Keep **code cells
  identical** and translate only the markdown prose.
- Reusable code goes in `src/decision_qa/`, not in notebook cells.
- Use free or open resources only. Never add a paid API, a paid tier, or a dataset
  that requires a paid account.
- Never commit `.env`, API keys, checkpoints, downloaded datasets, or caches.
- Document new learning material in `docs/README.md`, including its source URL and
  license. Prefer open-access papers and public blog posts.
- Before opening a PR, run:

```bash
uv run ruff format src tests
uv run ruff check src tests
uv run pytest -q
```

- Execute every changed notebook in both language folders; the parity test only
  checks that the code cells match, not that they run.
- Agent-specific local notes belong in the gitignored `AGENTS.md`, which is local
  only and intentionally shadowed online. Do not force-add it.
