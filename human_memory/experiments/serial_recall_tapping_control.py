"""
Serial Recall Block - Tapping Control condition.

Standard-rate presentation of a 7-letter sequence, same pool and no-repeat
rule as the Letter Baseline, but while the letters are shown the participant
continuously taps a complex rhythm on the table - concurrent, non-verbal
interference that isolates the effect to articulatory rehearsal by leaving
the phonological loop free (Experimental_Architecture.md, Section 3,
condition 5). Exact-order recall, same response modality as Section 5.
"""

import csv
import random
import time
from pathlib import Path


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
SEQUENCE_LENGTH = 7               # number of letters presented per trial
PRESENTATION_RATE_SEC = 1.0       # seconds each letter stays on screen
COUNTDOWN_SEC = 3                 # countdown shown before presentation starts
BLANK_LINES_BETWEEN_LETTERS = 30  # printed to clear the previous letter from view
OUTPUT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "serial_recall_tapping_control.csv"
CSV_FIELDNAMES = ["participant_id", "repetition", "position", "presented_letter", "response_letter", "correct"]

# Same confusable-letter pool as the Letter Baseline: a phonologically
# confusable group (letters whose spoken names rhyme) mixed with a visually
# confusable group (letters whose printed shapes are easily mistaken for
# one another). Defined here directly, not imported, to keep this script
# standalone.
PHONOLOGICAL_CONFUSABLE_LETTERS = ["B", "C", "D", "G", "P", "T", "V"]
VISUAL_CONFUSABLE_LETTERS = ["E", "F", "H", "M", "N", "S", "W", "X"]
LETTER_POOL = PHONOLOGICAL_CONFUSABLE_LETTERS + VISUAL_CONFUSABLE_LETTERS

# One clear, complex but learnable rhythm: a five-beat LONG-short-short-LONG-short
# pattern, spelled out so a participant reading it once knows exactly what to do.
RHYTHM_INSTRUCTIONS = (
    "Tap this 5-beat rhythm on the table, repeatedly: one LONG, heavy tap - "
    "two quick, light taps - one LONG, heavy tap - one quick, light tap "
    "(LONG-short-short-LONG-short). Keep repeating this exact pattern."
)


def _generate_letter_sequence():
    # Sample SEQUENCE_LENGTH letters from the pool, no repeats within a trial.
    return random.sample(LETTER_POOL, SEQUENCE_LENGTH)


def _present_letter_sequence(letters):
    # Show a countdown, then print each letter alone for PRESENTATION_RATE_SEC
    # seconds, with a short reminder to keep tapping the rhythm.
    for remaining in range(COUNTDOWN_SEC, 0, -1):
        print(f"Get ready... {remaining}")
        time.sleep(1)

    for letter in letters:
        print("\n" * BLANK_LINES_BETWEEN_LETTERS)
        print(f"(Keep tapping: {RHYTHM_INSTRUCTIONS})")
        print(letter)
        time.sleep(PRESENTATION_RATE_SEC)
    print("\n" * BLANK_LINES_BETWEEN_LETTERS)


def _collect_recall_response():
    # Ask once for the typed sequence and split it into individual letters.
    typed = input(
        "Type the letters exactly as they appeared, in order, without spaces:\n"
    )
    return [char.upper() for char in typed.strip() if char.strip()]


def _score_letter_sequence(letters, typed_letters):
    # Build one row per presented letter, correct only if letter and position both match.
    rows = []
    for position, letter in enumerate(letters, start=1):
        response_letter = typed_letters[position - 1] if position - 1 < len(typed_letters) else ""
        rows.append(
            {
                "position": position,
                "presented_letter": letter,
                "response_letter": response_letter,
                "correct": response_letter == letter,
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


def run_serial_recall_tapping_control(participant_id, repetition_number):
    """
    Run one Tapping Control Serial Recall trial for a participant.

    Instructs the participant to start tapping RHYTHM_INSTRUCTIONS
    continuously. Generates a SEQUENCE_LENGTH-letter sequence from
    LETTER_POOL and presents it at PRESENTATION_RATE_SEC seconds per letter
    while a reminder to keep tapping stays on screen. After the sequence
    ends, tells the participant to stop, collects a single typed response,
    scores each position as correct only if the letter and its exact
    position both match, and appends the results to OUTPUT_CSV_PATH.
    Returns the list of row dictionaries that were logged.
    """
    print(
        "\nStarting now, tap the following rhythm continuously and without "
        "stopping, until told otherwise:\n"
    )
    print(RHYTHM_INSTRUCTIONS)
    print()

    letters = _generate_letter_sequence()
    _present_letter_sequence(letters)
    print("Stop tapping. Get ready to recall the letters.\n")

    typed_letters = _collect_recall_response()
    rows = _score_letter_sequence(letters, typed_letters)
    _append_rows_to_csv(rows, participant_id, repetition_number)
    return rows
