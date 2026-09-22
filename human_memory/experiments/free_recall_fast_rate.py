"""
Free Recall Block - Fast Rate condition.

Fast presentation rate, immediate free recall (Experimental_Architecture.md,
Section 2, condition 2). Presents a 15-word list built by the inherited
word-list generator, collects one typed recall response, scores it against
the presented words, and appends the results to a CSV file - all via
BaseExperiment's shared trial flow.
"""

from pathlib import Path

from experiments.base_experiment import BaseExperiment


# ---------------------------------------------------------------- #
# Tunable parameters - change these, not the logic below.          #
# ---------------------------------------------------------------- #
LIST_LENGTH = 15                # number of words presented per trial
PRESENTATION_RATE_SEC = 0.4     # seconds each word stays on screen
OUTPUT_CSV_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_CSV_STEM = "free_recall_fast_rate"


class FreeRecallFastRate(BaseExperiment):
    """Fast presentation rate, immediate Free Recall - the Fast Rate condition."""

    output_csv_dir = OUTPUT_CSV_DIR
    output_csv_stem = OUTPUT_CSV_STEM

    def generate_stimuli(self):
        return self.generate_word_list(same_category=False)

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


def run_free_recall_fast_rate(participant_id, repetition_number):
    """
    Run one Fast Rate Free Recall trial for a participant.

    Builds a FreeRecallFastRate instance with LIST_LENGTH and
    PRESENTATION_RATE_SEC and runs it end to end. Returns the list of row
    dictionaries that were logged.
    """
    return FreeRecallFastRate(participant_id, repetition_number, LIST_LENGTH, PRESENTATION_RATE_SEC).run()
