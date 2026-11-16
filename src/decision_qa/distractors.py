"""Distractor sampling and option shuffling for choice questions."""

from __future__ import annotations

import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def shuffle_with_gold(
    options: list[str], gold_index: int, rng: random.Random
) -> tuple[list[str], int]:
    """Shuffle options and return the new position of the gold option."""
    order = list(range(len(options)))
    rng.shuffle(order)
    shuffled = [options[i] for i in order]
    return shuffled, order.index(gold_index)


def _hard_negatives(gold: str, pool: list[str], k: int) -> list[str]:
    """Pick the most lexically similar labels to `gold` (cheap, free, offline)."""
    texts = [gold, *pool]
    vectors = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)).fit_transform(texts)
    similarities = cosine_similarity(vectors[0], vectors[1:]).ravel()
    ranked = sorted(range(len(pool)), key=lambda i: similarities[i], reverse=True)
    return [pool[i] for i in ranked[:k]]


def sample_distractors(
    gold: str,
    pool: list[str],
    k: int,
    rng: random.Random,
    hard_fraction: float = 0.5,
) -> list[str]:
    """Sample `k` distinct distractors, mixing lexical hard negatives with random ones."""
    candidates = list(dict.fromkeys(p for p in pool if p != gold))
    k = min(k, len(candidates))
    if k == 0:
        return []

    n_hard = round(k * hard_fraction)
    chosen = _hard_negatives(gold, candidates, n_hard)
    remaining = [c for c in candidates if c not in chosen]
    rng.shuffle(remaining)
    chosen.extend(remaining[: k - len(chosen)])
    rng.shuffle(chosen)
    return chosen
