"""
Serial Recall Block - Chunking A and Chunking B conditions.

Runs the two chunking conditions back to back in one trial: Chunking A
(7 random consonant triplets, a low-capacity baseline) followed by a short
break, then Chunking B (7 three-letter words, testing whether associative
patterns increase capacity), per Experimental_Architecture.md, Section 3,
conditions 2 and 3. Exact-order recall, same response modality as Section 5.
Both conditions log to the same CSV file, distinguished by a "condition"
column.
"""

import csv
import random
import time
from pathlib import Path


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
SEQUENCE_LENGTH = 7                # number of items presented per trial
PRESENTATION_RATE_SEC = 1.0        # seconds each item stays on screen
COUNTDOWN_SEC = 3                  # countdown shown before presentation starts
BLANK_LINES_BETWEEN_ITEMS = 30     # printed to clear the previous item from view
INTER_CONDITION_BREAK_SEC = 30     # seconds of break between Chunking A and Chunking B
OUTPUT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "serial_recall_chunking.csv"
CSV_FIELDNAMES = [
    "participant_id",
    "repetition",
    "condition",
    "position",
    "presented_item",
    "response_item",
    "correct",
]

# Chunking A stimulus pool: consonants only (vowels A, E, I, O, U excluded).
CONSONANT_POOL = [
    "B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R",
    "S", "T", "V", "W", "X", "Y", "Z",
]

# Chunking B stimulus pool: common, real, concrete English three-letter nouns.
THREE_LETTER_WORDS = [
    "cat", "dog", "cup", "pen", "hat", "box", "bag", "key", "jar", "bed",
    "sun", "cow", "pig", "bus", "van", "fox", "owl", "bee", "ant", "rug",
]


def _generate_chunking_a_sequence():
    # Build SEQUENCE_LENGTH triplets, each 3 distinct random consonants.
    return ["".join(random.sample(CONSONANT_POOL, 3)) for _ in range(SEQUENCE_LENGTH)]


def _generate_chunking_b_sequence():
    # Sample SEQUENCE_LENGTH distinct words, no repeats within the sequence.
    return random.sample(THREE_LETTER_WORDS, SEQUENCE_LENGTH)


def _present_sequence(items):
    # Show a countdown, then print each item alone for PRESENTATION_RATE_SEC seconds.
    for remaining in range(COUNTDOWN_SEC, 0, -1):
        print(f"Get ready... {remaining}")
        time.sleep(1)

    for item in items:
        print("\n" * BLANK_LINES_BETWEEN_ITEMS)
        print(item)
        time.sleep(PRESENTATION_RATE_SEC)
    print("\n" * BLANK_LINES_BETWEEN_ITEMS)


def _collect_response(prompt_text):
    # Ask once for the typed sequence and split it into individual items.
    typed = input(prompt_text)
    return typed.split()


def _score_sequence(presented_items, typed_items, condition):
    # Build one row per presented item, correct only if the item and its exact position both match.
    rows = []
    for position, presented in enumerate(presented_items, start=1):
        response = typed_items[position - 1] if position - 1 < len(typed_items) else ""
        correct = response.strip().lower() == presented.strip().lower()
        rows.append(
            {
                "condition": condition,
                "position": position,
                "presented_item": presented,
                "response_item": response,
                "correct": correct,
            }
        )
    return rows


def _append_rows_to_csv(rows, participant_id, repetition_number):
    # Append rows to OUTPUT_CSV_PATH, writing the header only if the file is new.
    OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = OUTPUT_CSV_PATH.exists()

    with OUTPUT_CSV_PATH.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "participant_id": participant_id,
                    "repetition": repetition_number,
                    **row,
                }
            )


def run_serial_recall_chunking(participant_id, repetition_number):
    """
    Run one Chunking A trial, a short break, then one Chunking B trial.

    Chunking A presents SEQUENCE_LENGTH random consonant triplets from
    CONSONANT_POOL at PRESENTATION_RATE_SEC seconds each, collects one typed
    response (chunks separated by spaces), scores each position as correct
    only if the triplet and its exact position both match, and appends the
    rows to OUTPUT_CSV_PATH under condition "chunking_a". After an
    INTER_CONDITION_BREAK_SEC break, Chunking B does the same with
    SEQUENCE_LENGTH distinct three-letter words from THREE_LETTER_WORDS,
    logged under condition "chunking_b". Returns the combined list of row
    dictionaries that were logged, Chunking A's rows first.
    """
    print("\nChunking A - Random Consonant Triplets\n")
    triplets = _generate_chunking_a_sequence()
    _present_sequence(triplets)
    typed_triplets = _collect_response(
        "Type the 7 triplets exactly as they appeared, separated by spaces:\n"
    )
    rows_a = _score_sequence(triplets, typed_triplets, "chunking_a")
    _append_rows_to_csv(rows_a, participant_id, repetition_number)

    print(f"\nShort break. Please wait {INTER_CONDITION_BREAK_SEC} seconds...\n")
    time.sleep(INTER_CONDITION_BREAK_SEC)

    print("\nChunking B - Three-Letter Words\n")
    words = _generate_chunking_b_sequence()
    _present_sequence(words)
    typed_words = _collect_response(
        "Type the 7 words exactly as they appeared, separated by spaces:\n"
    )
    rows_b = _score_sequence(words, typed_words, "chunking_b")
    _append_rows_to_csv(rows_b, participant_id, repetition_number)

    return rows_a + rows_b
