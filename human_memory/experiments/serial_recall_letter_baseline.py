"""
Serial Recall Block - Letter Baseline condition.

Standard-rate presentation of a 7-letter sequence drawn from a pool that
mixes phonologically confusable letters (B C D G P T V, which sound alike)
and visually confusable letters (E F H M N S W X, which look alike),
followed by exact-order recall (Experimental_Architecture.md, Section 3,
condition 1). Scores each position and, for the Section 6 error analysis,
classifies incorrect responses as phonological or visual confusions against
a small letter-confusability lookup table.
"""

import csv
import random
import time
from pathlib import Path


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
SEQUENCE_LENGTH = 7               # number of letters presented per trial
PRESENTATION_RATE_SEC = 2.0       # seconds each letter stays on screen
COUNTDOWN_SEC = 3                 # countdown shown before presentation starts
BLANK_LINES_BETWEEN_LETTERS = 30  # printed to clear the previous letter from view
OUTPUT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "serial_recall_letter_baseline.csv"
CSV_FIELDNAMES = [
    "participant_id",
    "repetition",
    "list_position",
    "letter",
    "typed_letter",
    "correct",
    "error_type",
]

# The stimulus pool: a mix of a phonologically confusable group (letters
# whose spoken names rhyme) and a visually confusable group (letters whose
# printed shapes are easily mistaken for one another).
PHONOLOGICAL_CONFUSABLE_LETTERS = ["B", "C", "D", "G", "P", "T", "V"]
VISUAL_CONFUSABLE_LETTERS = ["E", "F", "H", "M", "N", "S", "W", "X"]
LETTER_POOL = PHONOLOGICAL_CONFUSABLE_LETTERS + VISUAL_CONFUSABLE_LETTERS

# Pairwise letter-confusability lookup, used only to classify recall errors.
PHONOLOGICAL_NEIGHBORS = {
    "B": {"C", "D", "G", "P", "T", "V"},
    "C": {"B", "D", "G", "P", "T", "V"},
    "D": {"B", "C", "G", "P", "T", "V"},
    "G": {"B", "C", "D", "P", "T", "V"},
    "P": {"B", "C", "D", "G", "T", "V"},
    "T": {"B", "C", "D", "G", "P", "V"},
    "V": {"B", "C", "D", "G", "P", "T"},
    "F": {"S", "X"},
    "S": {"F", "X"},
    "X": {"F", "S"},
}
VISUAL_NEIGHBORS = {
    "E": {"F", "H"},
    "F": {"E", "H"},
    "H": {"E", "F"},
    "M": {"N", "W"},
    "N": {"M", "W"},
    "W": {"M", "N"},
}


def _generate_letter_sequence():
    # Sample SEQUENCE_LENGTH letters from the pool, no repeats within a trial.
    return random.sample(LETTER_POOL, SEQUENCE_LENGTH)


def _present_letter_sequence(letters):
    # Show a countdown, then print each letter alone for PRESENTATION_RATE_SEC seconds.
    for remaining in range(COUNTDOWN_SEC, 0, -1):
        print(f"Get ready... {remaining}")
        time.sleep(1)

    for letter in letters:
        print("\n" * BLANK_LINES_BETWEEN_LETTERS)
        print(letter)
        time.sleep(PRESENTATION_RATE_SEC)
    print("\n" * BLANK_LINES_BETWEEN_LETTERS)


def _collect_recall_response():
    # Ask once for the typed sequence and split it into individual letters.
    typed = input(
        "Type the letters exactly as they appeared, in order, without spaces:\n"
    )
    return [char.upper() for char in typed.strip() if char.strip()]


def _classify_error(target_letter, typed_letter):
    # Explain why a wrong response was wrong, for the Section 6 error analysis.
    if typed_letter is None:
        return "omission"
    if typed_letter in PHONOLOGICAL_NEIGHBORS.get(target_letter, set()):
        return "phonological"
    if typed_letter in VISUAL_NEIGHBORS.get(target_letter, set()):
        return "visual"
    return "other"


def _score_letter_sequence(letters, typed_letters):
    # Build one row per presented letter, correct only if letter and position both match.
    rows = []
    for position, letter in enumerate(letters, start=1):
        typed_letter = typed_letters[position - 1] if position - 1 < len(typed_letters) else None
        correct = typed_letter == letter
        rows.append(
            {
                "list_position": position,
                "letter": letter,
                "typed_letter": typed_letter or "",
                "correct": correct,
                "error_type": "" if correct else _classify_error(letter, typed_letter),
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


def run_serial_recall_letter_baseline(participant_id, repetition_number):
    """
    Run one Letter Baseline Serial Recall trial for a participant.

    Generates a SEQUENCE_LENGTH-letter sequence from LETTER_POOL, presents it
    at PRESENTATION_RATE_SEC seconds per letter, collects a single typed
    response, scores each position as correct only if the letter and its
    exact position both match, classifies incorrect responses as
    phonological, visual, omission, or other confusions, and appends the
    results to OUTPUT_CSV_PATH. Returns the list of row dictionaries that
    were logged.
    """
    letters = _generate_letter_sequence()
    _present_letter_sequence(letters)
    typed_letters = _collect_recall_response()
    rows = _score_letter_sequence(letters, typed_letters)
    _append_rows_to_csv(rows, participant_id, repetition_number)
    return rows
