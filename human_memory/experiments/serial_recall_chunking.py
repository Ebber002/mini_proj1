"""
Serial Recall Block - Chunking A and Chunking B conditions.

Redesigned to use word_list items from utils/wordlist.py instead of the old
consonant-triplet / three-letter-word design: Chunking A presents 7 words
drawn from different categories (a low-associative-structure baseline),
Chunking B presents 7 words drawn from a single category (testing whether
shared category membership increases capacity), per
Experimental_Architecture.md, Section 3, conditions 2 and 3. Both run
back-to-back with a break in between, via BaseExperiment's shared trial
flow, and log to the same per-participant CSV file distinguished by a
"condition" column.
"""

import time
from pathlib import Path

from experiments.base_experiment import BaseExperiment


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
LIST_LENGTH = 7                    # number of words presented per trial
PRESENTATION_RATE_SEC = 1.0        # seconds each word stays on screen
INTER_CONDITION_BREAK_SEC = 30     # seconds of break between Chunking A and Chunking B
OUTPUT_CSV_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_CSV_STEM = "serial_recall_chunking"


def _score_word_sequence(stimuli, response, condition):
    # Build one row per presented (word, category) item, correct only if the
    # word and its exact position both match. The category is not used for
    # scoring, only for stimulus generation.
    typed_words = response.split()
    rows = []
    for position, (word, _category) in enumerate(stimuli, start=1):
        response_word = typed_words[position - 1] if position - 1 < len(typed_words) else ""
        rows.append(
            {
                "condition": condition,
                "position": position,
                "presented_word": word,
                "response_word": response_word,
                "correct": response_word.strip().lower() == word.strip().lower(),
            }
        )
    return rows


class ChunkingA(BaseExperiment):
    """7 words drawn from different categories - the Chunking A condition."""

    output_csv_dir = OUTPUT_CSV_DIR
    output_csv_stem = OUTPUT_CSV_STEM

    def generate_stimuli(self):
        return self.generate_word_list(same_category=False)

    def collect_response(self):
        return input(
            "Type the 7 words exactly as they appeared, in order, separated by spaces:\n"
        )

    def score(self, stimuli, response):
        return _score_word_sequence(stimuli, response, "chunking_a")


class ChunkingB(BaseExperiment):
    """7 words drawn from a single, shared category - the Chunking B condition."""

    output_csv_dir = OUTPUT_CSV_DIR
    output_csv_stem = OUTPUT_CSV_STEM

    def generate_stimuli(self):
        return self.generate_word_list(same_category=True)

    def collect_response(self):
        return input(
            "Type the 7 words exactly as they appeared, in order, separated by spaces:\n"
        )

    def score(self, stimuli, response):
        return _score_word_sequence(stimuli, response, "chunking_b")


def run_serial_recall_chunking(participant_id, repetition_number):
    """
    Run one Chunking A trial, a short break, then one Chunking B trial.

    Builds and runs a ChunkingA instance, waits INTER_CONDITION_BREAK_SEC,
    then builds and runs a ChunkingB instance - both with LIST_LENGTH and
    PRESENTATION_RATE_SEC. Returns the combined list of row dictionaries
    that were logged, Chunking A's rows first.
    """
    print("\nChunking A - Different Categories\n")
    rows_a = ChunkingA(participant_id, repetition_number, LIST_LENGTH, PRESENTATION_RATE_SEC).run()

    print(f"\nShort break. Please wait {INTER_CONDITION_BREAK_SEC} seconds...\n")
    time.sleep(INTER_CONDITION_BREAK_SEC)

    print("\nChunking B - Same Category\n")
    rows_b = ChunkingB(participant_id, repetition_number, LIST_LENGTH, PRESENTATION_RATE_SEC).run()

    return rows_a + rows_b
