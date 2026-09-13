"""
Founding stimulus-generation script.

This is the base module other experiment scripts (Baseline free recall, etc.)
build on. It only handles STIMULUS GENERATION: choosing which words appear
and in what order. It does not present words, read participant input, score
responses, or save data — those concerns belong to the scripts that call it.
"""

import random

from word_bank import WORD_CATEGORIES


def _unused_words(categories_dict, category, used_words):
    # Words from this category that have not already been placed in the list.
    return [word for word in categories_dict[category] if word not in used_words]


def _pick_category(category_names, categories_dict, previous, used_words):
    # Pick a category different from the previous one that still has at
    # least one unused word available.
    candidates = [
        name
        for name in category_names
        if name != previous and _unused_words(categories_dict, name, used_words)
    ]
    if not candidates:
        raise ValueError("Not enough unused words available to build the requested list.")
    return random.choice(candidates)


def generate_word_list(n_words, categories_dict=WORD_CATEGORIES):
    """
    Generate a random sequence of words drawn from category pools.

    n_words categories are randomly selected from categories_dict (repeats
    allowed, but the same category never appears twice in a row), then one
    random word, never repeated elsewhere in the list, is drawn from each
    selected category's word list.

    Returns a list of (word, category) tuples, in presentation order.
    """
    category_names = list(categories_dict.keys())
    used_words = set()
    previous_category = None
    word_list = []

    for _ in range(n_words):
        category = _pick_category(category_names, categories_dict, previous_category, used_words)
        word = random.choice(_unused_words(categories_dict, category, used_words))
        word_list.append((word, category))
        used_words.add(word)
        previous_category = category

    return word_list
