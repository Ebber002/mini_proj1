"""
Generic base class for all 8 experiment conditions (Free Recall and Serial
Recall alike).

BaseExperiment fixes the shared trial flow in run() - generate stimuli,
present them, run any concurrent/post-presentation interference, collect the
participant's response, score it, and log the results - while leaving the
condition-specific parts (what a stimulus looks like, how the response is
collected, and how it's scored) to each subclass.
"""

import csv
import random
import time

from utils.wordlist import CATEGORIES, WORDLIST


class BaseExperiment:
    """
    Shared trial flow for every experiment condition.

    Subclasses MUST override generate_stimuli(), collect_response(), and
    score() - the base class raises NotImplementedError for these, since
    each condition's stimuli, response format, and scoring rule are
    fundamentally different. Subclasses MAY override present_stimuli(),
    run_interference(), and log_results() if the shared default here isn't
    enough, but most conditions should be able to use them as-is.

    Subclasses that log to their own CSV files must set output_csv_dir and
    output_csv_stem class attributes (see log_results() below for why).
    """

    output_csv_dir = None
    output_csv_stem = None

    # Pre-presentation countdown and screen-clearing, matching every one of
    # the 8 existing experiment scripts exactly (COUNTDOWN_SEC = 3,
    # 30 blank lines printed before each item).
    countdown_sec = 3
    blank_lines_between_items = 30

    def __init__(self, participant_id, repetition_number, list_length, presentation_rate_sec):
        self.participant_id = participant_id
        self.repetition_number = repetition_number
        self.list_length = list_length
        self.presentation_rate_sec = presentation_rate_sec

    # ---------------------------------------------------------------- #
    # Fixed orchestration - do not override in subclasses.              #
    # ---------------------------------------------------------------- #
    def run(self):
        """Run one full trial: generate, present, interfere, respond, score, log. Returns the logged rows."""
        stimuli = self.generate_stimuli()
        self.present_stimuli(stimuli)
        self.run_interference()
        response = self.collect_response()
        rows = self.score(stimuli, response)
        self.log_results(rows)
        return rows

    # ---------------------------------------------------------------- #
    # Must be overridden by every subclass.                             #
    # ---------------------------------------------------------------- #
    def generate_stimuli(self):
        """
        Return the list of items to present, in presentation order.

        The shape is whatever the subclass's own present_stimuli/score
        methods need: (word, category) tuples for word-based conditions,
        plain letters or chunk strings for others.
        """
        raise NotImplementedError("Subclasses must implement generate_stimuli().")

    def collect_response(self):
        """
        Prompt the participant and return their raw typed input.

        Free Recall (space-separated, order doesn't matter) and Serial
        Recall (with or without spaces, position matters) need different
        prompt wording and parsing, so the base class assumes nothing about
        the format here.
        """
        raise NotImplementedError("Subclasses must implement collect_response().")

    def score(self, stimuli, response):
        """
        Compare stimuli to the participant's response and return the list of
        row dicts to log - one per presented item, WITHOUT participant_id or
        repetition (log_results adds those). Free Recall scoring is
        order-independent; Serial Recall scoring is positional - fundamentally
        different rules, so the base class makes no assumption here.

        Contract for every Serial Recall subclass going forward (Letter
        Baseline, Chunking A, Chunking B, Articulatory Suppression, Tapping
        Control): each row must be shaped as
        {"position": ..., "presented_<item>": ..., "response_<item>": ...,
        "correct": ...} - e.g. presented_letter/response_letter for
        letter-based conditions, presented_word/response_word for
        Chunking B, presented_chunk/response_chunk for Chunking A. Do not
        add an error_type or any error-classification field here - phonological
        vs. visual classification is computed later by
        analyze_serial_recall.py using letter_confusability.py, not stored
        in the raw per-trial rows. This is a contract for the (not yet
        written) subclasses; it does not change anything in this file.
        """
        raise NotImplementedError("Subclasses must implement score().")

    # ---------------------------------------------------------------- #
    # Have a shared default - override only if a subclass truly needs to. #
    # ---------------------------------------------------------------- #
    def present_stimuli(self, stimuli):
        """
        Show a countdown_sec countdown, then print each stimulus item alone
        - clearing the screen with blank_lines_between_items blank lines
        first - waiting presentation_rate_sec between items, and clearing
        the screen once more after the last item.

        Works for a plain string item (a letter, a chunk) or a
        (word, category) tuple item - only the first element of a tuple is
        shown, since the category is scoring information, not something the
        participant should see.
        """
        for remaining in range(self.countdown_sec, 0, -1):
            print(f"Get ready... {remaining}")
            time.sleep(1)

        for item in stimuli:
            display_text = item[0] if isinstance(item, tuple) else item
            print("\n" * self.blank_lines_between_items)
            print(display_text)
            time.sleep(self.presentation_rate_sec)
        print("\n" * self.blank_lines_between_items)

    def run_interference(self):
        """
        Hook for a concurrent or post-presentation task (tongue-twister
        reading, a silent pause, tapping a rhythm). Does nothing by default;
        WM Task, Pause Control, Articulatory Suppression, and Tapping
        Control override this.
        """
        pass

    def log_results(self, rows):
        """
        Append rows to a per-participant CSV file at
        self.output_csv_dir / f"{self.output_csv_stem}_{participant_id}.csv",
        adding participant_id and repetition first. Writes a header only if
        the file doesn't exist yet. The CSV's column set is taken from the
        first row's keys, since each subclass's row shape differs (Free
        Recall vs. the two different Serial Recall column layouts already
        in this project).

        Splitting output into one file per condition PER PARTICIPANT
        (instead of one shared file per condition) avoids git merge
        conflicts when multiple group members run experiments locally and
        push their data.
        """
        if not rows:
            return
        if self.output_csv_dir is None or self.output_csv_stem is None:
            raise NotImplementedError("Subclasses must set output_csv_dir and output_csv_stem class attributes.")

        # Minimal sanitizing so a weird participant_id can't escape output_csv_dir.
        safe_participant_id = str(self.participant_id).replace("/", "_").replace("\\", "_")
        output_csv_path = self.output_csv_dir / f"{self.output_csv_stem}_{safe_participant_id}.csv"

        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = output_csv_path.exists()
        fieldnames = ["participant_id", "repetition", *rows[0].keys()]

        with output_csv_path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "participant_id": self.participant_id,
                        "repetition": self.repetition_number,
                        **row,
                    }
                )

    # ---------------------------------------------------------------- #
    # Reusable helper for word-based subclasses - not itself             #
    # generate_stimuli(); subclasses call this FROM their own override.  #
    #                                                                    #
    # word_bank.py (the project's original word source, used via         #
    # stimulus.py by the 4 not-yet-migrated Free Recall scripts) is       #
    # deprecated in favor of utils/wordlist.py used here. Do not delete   #
    # word_bank.py yet - it can only go once every Free Recall subclass   #
    # has been migrated off it.                                          #
    # ---------------------------------------------------------------- #
    def generate_word_list(self, same_category=False):
        """
        Build a self.list_length-word list of (word, category) tuples,
        sourced from utils/wordlist.py's WORDLIST/CATEGORIES.

        same_category=False (default): categories are sampled with repeats
        allowed but never the same category twice in a row, and no word is
        repeated anywhere in the list - the same no-adjacent-category,
        no-repeated-word algorithm the project's original founding
        generation function used.

        same_category=True: one random category with at least
        self.list_length words is chosen, then self.list_length distinct
        words are sampled from just that category, in random order.
        """
        if same_category:
            return self._generate_same_category_word_list()
        return self._generate_mixed_category_word_list()

    def _unused_words(self, category, used_words):
        # Words from this category not already placed elsewhere in the list.
        return [word for word in WORDLIST[category] if word not in used_words]

    def _pick_category(self, previous_category, used_words):
        # Pick a category different from the previous one that still has at
        # least one unused word available.
        candidates = [
            name
            for name in CATEGORIES
            if name != previous_category and self._unused_words(name, used_words)
        ]
        if not candidates:
            raise ValueError("Not enough unused words available to build the requested list.")
        return random.choice(candidates)

    def _generate_mixed_category_word_list(self):
        used_words = set()
        previous_category = None
        word_list = []
        for _ in range(self.list_length):
            category = self._pick_category(previous_category, used_words)
            word = random.choice(self._unused_words(category, used_words))
            word_list.append((word, category))
            used_words.add(word)
            previous_category = category
        return word_list

    def _generate_same_category_word_list(self):
        eligible_categories = [name for name in CATEGORIES if len(WORDLIST[name]) >= self.list_length]
        if not eligible_categories:
            raise ValueError(f"No category has at least {self.list_length} words.")
        category = random.choice(eligible_categories)
        words = random.sample(WORDLIST[category], self.list_length)
        return [(word, category) for word in words]
