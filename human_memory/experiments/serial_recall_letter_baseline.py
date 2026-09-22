"""
Serial Recall Block - Letter Baseline condition.

Standard-rate presentation of a 7-letter sequence drawn from a pool that
mixes phonologically confusable letters (B C D G P T V, which sound alike)
and visually confusable letters (E F H M N S W X, which look alike),
followed by exact-order recall (Experimental_Architecture.md, Section 3,
condition 1) - all via BaseExperiment's shared trial flow. Rows carry only
the raw position/letter/correctness data; phonological-vs-visual error
classification is computed later by analyze_serial_recall.py using
letter_confusability.py, not stored here.
"""

import random
from pathlib import Path

from experiments.base_experiment import BaseExperiment


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
LIST_LENGTH = 7                 # number of letters presented per trial
PRESENTATION_RATE_SEC = 1.0     # seconds each letter stays on screen
OUTPUT_CSV_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_CSV_STEM = "serial_recall_letter_baseline"

# The stimulus pool: a mix of a phonologically confusable group (letters
# whose spoken names rhyme) and a visually confusable group (letters whose
# printed shapes are easily mistaken for one another).
PHONOLOGICAL_CONFUSABLE_LETTERS = ["B", "C", "D", "G", "P", "T", "V"]
VISUAL_CONFUSABLE_LETTERS = ["E", "F", "H", "M", "N", "S", "W", "X"]
LETTER_POOL = PHONOLOGICAL_CONFUSABLE_LETTERS + VISUAL_CONFUSABLE_LETTERS


class SerialRecallLetterBaseline(BaseExperiment):
    """Standard-rate, exact-order Serial Recall of letters - the Letter Baseline condition."""

    output_csv_dir = OUTPUT_CSV_DIR
    output_csv_stem = OUTPUT_CSV_STEM

    def generate_stimuli(self):
        # Sample self.list_length letters from the pool, no repeats within a trial.
        return random.sample(LETTER_POOL, self.list_length)

    def collect_response(self):
        return input(
            "Type the letters exactly as they appeared, in order, without spaces:\n"
        )

    def score(self, stimuli, response):
        typed_letters = [char.upper() for char in response.strip() if char.strip()]
        rows = []
        for position, letter in enumerate(stimuli, start=1):
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


def run_serial_recall_letter_baseline(participant_id, repetition_number):
    """
    Run one Letter Baseline Serial Recall trial for a participant.

    Builds a SerialRecallLetterBaseline instance with LIST_LENGTH and
    PRESENTATION_RATE_SEC and runs it end to end. Returns the list of row
    dictionaries that were logged.
    """
    return SerialRecallLetterBaseline(participant_id, repetition_number, LIST_LENGTH, PRESENTATION_RATE_SEC).run()
