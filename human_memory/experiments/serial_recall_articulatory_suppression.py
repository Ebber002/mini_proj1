"""
Serial Recall Block - Articulatory Suppression condition.

Standard-rate presentation of a 7-letter sequence, same pool and no-repeat
rule as the Letter Baseline, but while the letters are shown the participant
must continuously read a tongue twister aloud - concurrent interference with
the phonological loop (Experimental_Architecture.md, Section 3, condition 4).
Exact-order recall, same response modality as Section 5 - all via
BaseExperiment's shared trial flow, with present_stimuli() overridden so the
tongue twister is visible WHILE the letters are shown rather than as a
separate post-presentation phase.
"""

import random
import time
from pathlib import Path

from experiments.base_experiment import BaseExperiment


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
LIST_LENGTH = 7                    # number of letters presented per trial
PRESENTATION_RATE_SEC = 1.0        # seconds each letter stays on screen
TONGUE_TWISTER_PREVIEW_SEC = 5     # seconds to read/memorize the tongue twister before letters start
OUTPUT_CSV_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_CSV_STEM = "serial_recall_articulatory_suppression"

# Same confusable-letter pool as the Letter Baseline: a phonologically
# confusable group (letters whose spoken names rhyme) mixed with a visually
# confusable group (letters whose printed shapes are easily mistaken for
# one another). Defined here directly, not imported, to keep this script
# standalone.
PHONOLOGICAL_CONFUSABLE_LETTERS = ["B", "C", "D", "G", "P", "T", "V"]
VISUAL_CONFUSABLE_LETTERS = ["E", "F", "H", "M", "N", "S", "W", "X"]
LETTER_POOL = PHONOLOGICAL_CONFUSABLE_LETTERS + VISUAL_CONFUSABLE_LETTERS

TONGUE_TWISTERS = [
    "Peter Piper picked a peck of pickled peppers.",
    "She sells seashells by the seashore.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
    "Betty Botter bought some butter, but she said the butter's bitter.",
    "Fuzzy Wuzzy was a bear, Fuzzy Wuzzy had no hair.",
    "Red lorry, yellow lorry, red lorry, yellow lorry.",
]


class SerialRecallArticulatorySuppression(BaseExperiment):
    """Serial Recall of letters with concurrent tongue-twister reading - the Articulatory Suppression condition."""

    output_csv_dir = OUTPUT_CSV_DIR
    output_csv_stem = OUTPUT_CSV_STEM

    def generate_stimuli(self):
        # Sample self.list_length letters from the pool, no repeats within a trial.
        return random.sample(LETTER_POOL, self.list_length)

    def present_stimuli(self, stimuli):
        # Pick a tongue twister, tell the participant to start reading it
        # aloud now, then run the same countdown + letter loop as the
        # inherited default, reprinting a reminder to keep reading above
        # each letter so the interference is concurrent with presentation.
        twister = random.choice(TONGUE_TWISTERS)
        print(
            "\nStarting now, read the following sentence aloud, continuously and "
            "without stopping, until told otherwise:\n"
        )
        print(twister)
        print()
        time.sleep(TONGUE_TWISTER_PREVIEW_SEC)

        for remaining in range(self.countdown_sec, 0, -1):
            print(f"Get ready... {remaining}")
            time.sleep(1)

        for letter in stimuli:
            print("\n" * self.blank_lines_between_items)
            print(f'(Keep reading aloud: "{twister}")')
            print(letter)
            time.sleep(self.presentation_rate_sec)
        print("\n" * self.blank_lines_between_items)

        print("Stop reading. Get ready to recall the letters.\n")

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


def run_serial_recall_articulatory_suppression(participant_id, repetition_number):
    """
    Run one Articulatory Suppression Serial Recall trial for a participant.

    Builds a SerialRecallArticulatorySuppression instance with LIST_LENGTH
    and PRESENTATION_RATE_SEC and runs it end to end. Returns the list of
    row dictionaries that were logged.
    """
    return SerialRecallArticulatorySuppression(
        participant_id, repetition_number, LIST_LENGTH, PRESENTATION_RATE_SEC
    ).run()
