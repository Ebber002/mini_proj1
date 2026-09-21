"""
Free Recall Block - Pause Control condition.

Standard presentation rate, followed by 15 seconds of silence, then immediate
free recall (Experimental_Architecture.md, Section 2, condition 4). Presents
a 15-word list built by the shared stimulus-generation function, runs a
silent pause phase, collects one typed recall response, scores it against
the presented words, and appends the results to a CSV file.
"""

import csv
import time
from pathlib import Path

from stimulus import generate_word_list


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
LIST_LENGTH = 15                # number of words presented per trial
PRESENTATION_RATE_SEC = 2.0     # seconds each word stays on screen
COUNTDOWN_SEC = 3               # countdown shown before presentation starts
BLANK_LINES_BETWEEN_WORDS = 30  # printed to clear the previous word from view
PAUSE_DURATION_SEC = 15         # seconds spent waiting quietly, no task
OUTPUT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "free_recall_pause_control.csv"
CSV_FIELDNAMES = ["participant_id", "repetition", "list_position", "word", "category", "recalled"]


def _present_word_list(word_category_pairs):
    # Show a countdown, then print each word alone for PRESENTATION_RATE_SEC seconds.
    for remaining in range(COUNTDOWN_SEC, 0, -1):
        print(f"Get ready... {remaining}")
        time.sleep(1)

    for word, _category in word_category_pairs:
        print("\n" * BLANK_LINES_BETWEEN_WORDS)
        print(word)
        time.sleep(PRESENTATION_RATE_SEC)
    print("\n" * BLANK_LINES_BETWEEN_WORDS)


def _run_pause_phase():
    # Have the participant wait quietly, with no task, for PAUSE_DURATION_SEC.
    print("\nPlease wait quietly. No task - just sit and relax until told to continue.\n")
    time.sleep(PAUSE_DURATION_SEC)
    print("\nGet ready to recall the words.\n")


def _collect_recall_response():
    # Ask once for every recalled word, space-separated, and return it as a lowercase set.
    typed = input(
        "Type all the words you remember, separated by spaces, in any order:\n"
    )
    return {word.strip().lower() for word in typed.split() if word.strip()}


def _score_word_list(word_category_pairs, recalled_words):
    # Build one row per presented word, marking whether it was recalled.
    rows = []
    for position, (word, category) in enumerate(word_category_pairs, start=1):
        rows.append(
            {
                "list_position": position,
                "word": word,
                "category": category,
                "recalled": word.strip().lower() in recalled_words,
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


def run_free_recall_pause_control(participant_id, repetition_number):
    """
    Run one Pause Control Free Recall trial for a participant.

    Generates a LIST_LENGTH-word list, presents it at PRESENTATION_RATE_SEC
    seconds per word, runs a silent PAUSE_DURATION_SEC pause phase, collects
    a single typed recall response, scores each presented word as recalled
    or not, and appends the results to OUTPUT_CSV_PATH. Returns the list of
    row dictionaries that were logged.
    """
    word_category_pairs = generate_word_list(LIST_LENGTH)
    _present_word_list(word_category_pairs)
    _run_pause_phase()
    recalled_words = _collect_recall_response()
    rows = _score_word_list(word_category_pairs, recalled_words)
    _append_rows_to_csv(rows, participant_id, repetition_number)
    return rows
