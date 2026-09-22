"""
Free Recall Block - WM Task condition.

Standard presentation rate, followed by 15 seconds of active tongue-twister
reading, then immediate free recall (Experimental_Architecture.md, Section 2,
condition 3). Presents a 15-word list built by the inherited word-list
generator, runs the working-memory interference phase, collects one typed
recall response, scores it against the presented words, and appends the
results to a CSV file - all via BaseExperiment's shared trial flow.
"""

import random
import time
from pathlib import Path

from experiments.base_experiment import BaseExperiment


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
LIST_LENGTH = 15                  # number of words presented per trial
PRESENTATION_RATE_SEC = 1.0       # seconds each word stays on screen
INTERFERENCE_DURATION_SEC = 15    # seconds spent reading the tongue twister aloud
OUTPUT_CSV_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_CSV_STEM = "free_recall_wm_task"

TONGUE_TWISTERS = [
    "Peter Piper picked a peck of pickled peppers.",
    "She sells seashells by the seashore.",
    "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
    "Betty Botter bought some butter, but she said the butter's bitter.",
    "Fuzzy Wuzzy was a bear, Fuzzy Wuzzy had no hair.",
    "Red lorry, yellow lorry, red lorry, yellow lorry.",
]


class FreeRecallWmTask(BaseExperiment):
    """Standard-rate Free Recall followed by tongue-twister interference - the WM Task condition."""

    output_csv_dir = OUTPUT_CSV_DIR
    output_csv_stem = OUTPUT_CSV_STEM

    def generate_stimuli(self):
        return self.generate_word_list(same_category=False)

    def run_interference(self):
        # Have the participant read a tongue twister aloud, repeatedly, for INTERFERENCE_DURATION_SEC.
        twister = random.choice(TONGUE_TWISTERS)
        print("\nNow read the following sentence aloud, over and over, until told to stop:\n")
        print(twister)
        time.sleep(INTERFERENCE_DURATION_SEC)
        print("\nStop. Get ready to recall the words.\n")

    def collect_response(self):
        return input(
            "Type all the words you remember, separated by spaces, in any order:\n"
        )

    def score(self, stimuli, response):
        recalled_words = {word.strip().lower() for word in response.split() if word.strip()}
        rows = []
        for position, (word, category) in enumerate(stimuli, start=1):
            rows.append(
                {
                    "list_position": position,
                    "word": word,
                    "category": category,
                    "recalled": word.strip().lower() in recalled_words,
                }
            )
        return rows


def run_free_recall_wm_task(participant_id, repetition_number):
    """
    Run one WM Task Free Recall trial for a participant.

    Builds a FreeRecallWmTask instance with LIST_LENGTH and
    PRESENTATION_RATE_SEC and runs it end to end. Returns the list of row
    dictionaries that were logged.
    """
    return FreeRecallWmTask(participant_id, repetition_number, LIST_LENGTH, PRESENTATION_RATE_SEC).run()
