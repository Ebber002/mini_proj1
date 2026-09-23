"""
Serial Recall Block - Tapping Control condition.

Standard-rate presentation of a 7-letter sequence, same pool and no-repeat
rule as the Letter Baseline, but while the letters are shown the participant
continuously taps a complex rhythm on the table - concurrent, non-verbal
interference that isolates the effect to articulatory rehearsal by leaving
the phonological loop free (Experimental_Architecture.md, Section 3,
condition 5). Exact-order recall, same response modality as Section 5 - all
via BaseExperiment's shared trial flow, with present_stimuli() overridden so
the tapping instructions are visible WHILE the letters are shown.
"""

import random
import time
from pathlib import Path

from experiments.base_experiment import BaseExperiment


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
LIST_LENGTH = 7                 # number of letters presented per trial
PRESENTATION_RATE_SEC = 1.0     # seconds each letter stays on screen
RHYTHM_PREVIEW_SEC = 10         # seconds to read and get ready to tap the rhythm before letters start
OUTPUT_CSV_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_CSV_STEM = "serial_recall_tapping_control"

# Same confusable-letter pool as the Letter Baseline: a phonologically
# confusable group (letters whose spoken names rhyme) mixed with a visually
# confusable group (letters whose printed shapes are easily mistaken for
# one another). Defined here directly, not imported, to keep this script
# standalone.
PHONOLOGICAL_CONFUSABLE_LETTERS = ["B", "C", "D", "G", "P", "T", "V"]
VISUAL_CONFUSABLE_LETTERS = ["E", "F", "H", "M", "N", "S", "W", "X"]
LETTER_POOL = PHONOLOGICAL_CONFUSABLE_LETTERS + VISUAL_CONFUSABLE_LETTERS

# One clear, countable rhythm: a repeating 2-1-3 tap-count pattern, spelled
# out with numbers so a participant reading it once knows exactly what to do,
# but with enough distinct groups to demand sustained attention.
RHYTHM_INSTRUCTIONS = (
    "Tap this pattern on the table, over and over: tap twice quickly, pause, "
    "tap once, pause, tap three times quickly, pause. Then start the pattern "
    "over again from the beginning, and keep repeating it without stopping."
)


class SerialRecallTappingControl(BaseExperiment):
    """Serial Recall of letters with concurrent rhythm tapping - the Tapping Control condition."""

    output_csv_dir = OUTPUT_CSV_DIR
    output_csv_stem = OUTPUT_CSV_STEM

    def generate_stimuli(self):
        # Sample self.list_length letters from the pool, no repeats within a trial.
        return random.sample(LETTER_POOL, self.list_length)

    def present_stimuli(self, stimuli):
        # Tell the participant to start tapping now, then run the same
        # countdown + letter loop as the inherited default, reprinting a
        # reminder of the rhythm above each letter so the interference is
        # concurrent with presentation.
        print(
            "\nStarting now, tap the following rhythm continuously and without "
            "stopping, until told otherwise:\n"
        )
        print(RHYTHM_INSTRUCTIONS)
        print()
        time.sleep(RHYTHM_PREVIEW_SEC)

        for remaining in range(self.countdown_sec, 0, -1):
            print(f"Get ready... {remaining}")
            time.sleep(1)

        for letter in stimuli:
            print("\n" * self.blank_lines_between_items)
            print(f"(Keep tapping: {RHYTHM_INSTRUCTIONS})")
            print(letter)
            time.sleep(self.presentation_rate_sec)
        print("\n" * self.blank_lines_between_items)

        print("Stop tapping. Get ready to recall the letters.\n")

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


def run_serial_recall_tapping_control(participant_id, repetition_number):
    """
    Run one Tapping Control Serial Recall trial for a participant.

    Builds a SerialRecallTappingControl instance with LIST_LENGTH and
    PRESENTATION_RATE_SEC and runs it end to end. Returns the list of row
    dictionaries that were logged.
    """
    return SerialRecallTappingControl(participant_id, repetition_number, LIST_LENGTH, PRESENTATION_RATE_SEC).run()
