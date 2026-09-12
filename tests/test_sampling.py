import random
import unittest

from human_memory.stimuli.sampling import sample_words
from human_memory.stimuli.wordlist import WORDS


class WordlistTests(unittest.TestCase):
    def test_words_are_lowercase_strings_and_unique_across_categories(self):
        all_words = [word for words in WORDS.values() for word in words]

        self.assertTrue(all(isinstance(word, str) for word in all_words))
        self.assertTrue(all(word == word.lower() for word in all_words))
        self.assertEqual(len(all_words), len(set(all_words)))


class SampleWordsTests(unittest.TestCase):
    def test_returns_requested_number_of_unique_words(self):
        records = sample_words(20, rng=random.Random(10))

        self.assertEqual(len(records), 20)
        self.assertEqual(len({record["word"] for record in records}), 20)

    def test_records_have_valid_word_category_pairs(self):
        records = sample_words(30, rng=random.Random(20))

        for record in records:
            self.assertIn(record["category"], WORDS)
            self.assertIn(record["word"], WORDS[record["category"]])

    def test_filters_by_category(self):
        records = sample_words(
            15,
            categories=["animals", "tools"],
            rng=random.Random(30),
        )

        self.assertTrue(
            all(record["category"] in {"animals", "tools"} for record in records)
        )

    def test_serial_positions_follow_returned_order(self):
        records = sample_words(12, rng=random.Random(40))

        self.assertEqual(
            [record["serial_position"] for record in records],
            list(range(1, 13)),
        )

    def test_seeded_generators_produce_deterministic_output(self):
        first = sample_words(20, rng=random.Random(50))
        second = sample_words(20, rng=random.Random(50))

        self.assertEqual(first, second)

    def test_too_many_unique_words_has_useful_error(self):
        available = len(WORDS["tools"])

        with self.assertRaisesRegex(
            ValueError, rf"Cannot sample {available + 1} unique words.*only {available}"
        ):
            sample_words(available + 1, categories=["tools"])

    def test_unknown_category_has_useful_error(self):
        with self.assertRaisesRegex(ValueError, "Unknown category 'weather'"):
            sample_words(1, categories=["weather"])


if __name__ == "__main__":
    unittest.main()
