"""Shared word sampling for experiment modules."""

import random
from typing import Optional

from .wordlist import WORDS


def sample_words(
    n: int,
    *,
    categories: Optional[list[str]] = None,
    unique: bool = True,
    rng: Optional[random.Random] = None,
) -> list[dict]:
    # Return a randomized sequence of words with stimulus metadata
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer.")
    if n < 0:
        raise ValueError("n cannot be negative.")

    selected_categories = list(WORDS) if categories is None else categories
    unknown_categories = [
        category for category in selected_categories if category not in WORDS
    ]
    if unknown_categories:
        unknown = ", ".join(repr(category) for category in unknown_categories)
        available = ", ".join(WORDS)
        raise ValueError(
            f"Unknown categor{'y' if len(unknown_categories) == 1 else 'ies'} "
            f"{unknown}. Available categories: {available}."
        )

    # Repeated category names should not give that category extra sampling weight.
    selected_categories = list(dict.fromkeys(selected_categories))
    pool = [
        {"word": word, "category": category}
        for category in selected_categories
        for word in WORDS[category]
    ]

    if unique and n > len(pool):
        raise ValueError(
            f"Cannot sample {n} unique words from the selected categories; "
            f"only {len(pool)} are available."
        )
    if not unique and n and not pool:
        raise ValueError("Cannot sample words because no categories were selected.")

    generator = rng if rng is not None else random.Random()
    if unique:
        sampled = generator.sample(pool, n)
    else:
        sampled = generator.choices(pool, k=n)

    return [
        {**record, "serial_position": position}
        for position, record in enumerate(sampled, start=1)
    ]
