# Decision-dataset schema

One JSON object per line. The structure mirrors a `/v1/systemone` request while adding
the supervision needed to train and evaluate a decision model.

```json
{
  "id": "pubmedqa-0",
  "source": "pubmedqa",
  "split": "train",
  "state": {
    "context": "The study enrolled 240 patients ...",
    "question": "Does treatment X improve outcomes?"
  },
  "questions": [
    {
      "type": "noul",
      "label": "answer_is_supported",
      "statement": "The answer to the question is: yes.",
      "gold": true
    },
    {
      "type": "choice",
      "label": "answer",
      "options": ["no", "yes", "maybe"],
      "gold_index": 1
    },
    {
      "type": "score",
      "label": "correctness",
      "rubric": "Rate how well the answer is supported by the context.",
      "levels": ["unsupported", "partially supported", "supported"],
      "gold_index": 2
    }
  ]
}
```

## Fields

- `id`, `source`, `split` — provenance and split (`train` / `val` / `test`).
- `state` — the information the model conditions on. `context` may be a string or an
  object; `question` is the task question.
- `questions` — a list of typed questions:
  - `noul`: `statement` to judge; `gold` is a boolean.
  - `choice`: `options` (declared up front); `gold_index` indexes the correct option.
  - `score`: `rubric` + ordered `levels`; `gold_index` indexes the correct level.

## Conventions

- Options are shuffled with a fixed seed; `gold_index` always refers to the
  post-shuffle list.
- Each true `noul` is paired with at least one contradicted statement so the model
  learns both sides.
- Hard negatives are sampled from similar labels (e.g. similar Banking77 intents).
- The evaluation code reads `gold` / `gold_index` only; predictions are probabilities
  returned for the declared answers.
