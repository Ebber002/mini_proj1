"""
Letter confusability groupings for the Serial Recall error-type analysis.

These are approximate, literature-informed groupings (a phonologically
confusable group of letters whose spoken names rhyme, and a visually
confusable group of letters whose printed shapes are easily mistaken for one
another) covering the same LETTER_POOL used by the Letter Baseline
experiment script. They are used only to classify recall errors during
analysis - not experimental parameters, and not imported by any experiment
script.
"""

PHONOLOGICAL_CONFUSIONS = {
    "B": {"C", "D", "G", "P", "T", "V"},
    "C": {"B", "D", "G", "P", "T", "V"},
    "D": {"B", "C", "G", "P", "T", "V"},
    "G": {"B", "C", "D", "P", "T", "V"},
    "P": {"B", "C", "D", "G", "T", "V"},
    "T": {"B", "C", "D", "G", "P", "V"},
    "V": {"B", "C", "D", "G", "P", "T"},
    "F": {"S", "X"},
    "S": {"F", "X"},
    "X": {"F", "S"},
}

VISUAL_CONFUSIONS = {
    "E": {"F", "H"},
    "F": {"E", "H"},
    "H": {"E", "F"},
    "M": {"N", "W"},
    "N": {"M", "W"},
    "W": {"M", "N"},
}
