"""
Serial Recall Block - pooled analysis across Letter Baseline, Chunking A,
Chunking B, Articulatory Suppression, and Tapping Control.

Reads the per-participant CSV files produced by the corresponding experiment
scripts (one file per participant per condition, named
"<stem>_<participant_id>.csv"; Chunking A and B share one file per
participant, distinguished by their "condition" column), pools rows across
participants directly (Experimental_Architecture.md, Section 6), and reports
capacity limits, the chunking effect, the articulatory suppression effect,
and a phonological-vs-visual error type analysis. Prints the results, saves
them to a summary text file, and saves two PNG figures - all under
OUTPUT_DIR.

Run standalone: python analyze_serial_recall.py
"""

import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt

# So "experiments.*" is importable regardless of the current working
# directory this script is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiments.serial_recall_articulatory_suppression import (
    OUTPUT_CSV_DIR as ARTICULATORY_SUPPRESSION_OUTPUT_CSV_DIR,
    OUTPUT_CSV_STEM as ARTICULATORY_SUPPRESSION_OUTPUT_CSV_STEM,
)
from experiments.serial_recall_chunking import (
    OUTPUT_CSV_DIR as CHUNKING_OUTPUT_CSV_DIR,
    OUTPUT_CSV_STEM as CHUNKING_OUTPUT_CSV_STEM,
)
from experiments.serial_recall_letter_baseline import (
    OUTPUT_CSV_DIR as LETTER_BASELINE_OUTPUT_CSV_DIR,
    OUTPUT_CSV_STEM as LETTER_BASELINE_OUTPUT_CSV_STEM,
)
from experiments.serial_recall_tapping_control import (
    OUTPUT_CSV_DIR as TAPPING_CONTROL_OUTPUT_CSV_DIR,
    OUTPUT_CSV_STEM as TAPPING_CONTROL_OUTPUT_CSV_STEM,
)

from letter_confusability import PHONOLOGICAL_CONFUSIONS, VISUAL_CONFUSIONS


# ---------------------------------------------------------------- #
# Parameters - change these, not the logic below.                  #
# ---------------------------------------------------------------- #
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "serial_recall"
SUMMARY_PATH = OUTPUT_DIR / "summary.txt"

SEQUENCE_LENGTH = 7   # positions 1..7, matches every Serial Recall script's SEQUENCE_LENGTH
CI_Z = 1.96           # 95% CI via normal approximation


def _load_csv_dicts(csv_path):
    # Return the CSV's rows as plain dicts, or [] with a printed warning if missing/empty.
    if not csv_path.exists():
        print(f"WARNING: {csv_path} does not exist - skipping this condition.")
        return []
    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))
    if not rows:
        print(f"WARNING: {csv_path} is empty - skipping this condition.")
    return rows


def _load_condition_rows(output_csv_dir, output_csv_stem):
    # Glob every per-participant CSV for this condition and concatenate their rows.
    matching_files = sorted(output_csv_dir.glob(f"{output_csv_stem}_*.csv"))
    if not matching_files:
        print(f"WARNING: no files matching {output_csv_stem}_*.csv in {output_csv_dir} - skipping this condition.")
        return []
    rows = []
    for csv_path in matching_files:
        rows.extend(_load_csv_dicts(csv_path))
    if not rows:
        print(f"WARNING: files matching {output_csv_stem}_*.csv in {output_csv_dir} were all empty - skipping this condition.")
    return rows


def _parse_letter_baseline_rows(raw_rows):
    # Normalize the Letter Baseline's own column names to the common shape.
    # Same column names as Articulatory Suppression / Tapping Control.
    parsed = []
    for row in raw_rows:
        parsed.append(
            {
                "participant_id": row["participant_id"],
                "repetition": row["repetition"],
                "position": int(row["position"]),
                "presented": row["presented_letter"].strip().upper(),
                "response": row["response_letter"].strip().upper(),
                "correct": row["correct"].strip().lower() == "true",
            }
        )
    return parsed


def _parse_position_letter_rows(raw_rows):
    # Normalize Articulatory Suppression / Tapping Control (same column names) to the common shape.
    parsed = []
    for row in raw_rows:
        parsed.append(
            {
                "participant_id": row["participant_id"],
                "repetition": row["repetition"],
                "position": int(row["position"]),
                "presented": row["presented_letter"].strip().upper(),
                "response": row["response_letter"].strip().upper(),
                "correct": row["correct"].strip().lower() == "true",
            }
        )
    return parsed


def _parse_chunking_rows(raw_rows, condition_value):
    # Normalize Chunking's rows to the common shape, keeping only the given "condition" value.
    parsed = []
    for row in raw_rows:
        if row["condition"] != condition_value:
            continue
        parsed.append(
            {
                "participant_id": row["participant_id"],
                "repetition": row["repetition"],
                "position": int(row["position"]),
                "presented": row["presented_item"],
                "response": row["response_item"],
                "correct": row["correct"].strip().lower() == "true",
            }
        )
    return parsed


def _capacity_counts_per_trial(rows):
    # For each unique (participant_id, repetition) trial, count correct positions out of SEQUENCE_LENGTH.
    counts_by_trial = {}
    for row in rows:
        key = (row["participant_id"], row["repetition"])
        counts_by_trial.setdefault(key, 0)
        if row["correct"]:
            counts_by_trial[key] += 1
    return list(counts_by_trial.values())


def _mean_ci(values):
    # 95% CI for a mean via the normal approximation: mean +/- z * (sample std / sqrt(n)).
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0
    mean = sum(values) / n
    if n > 1:
        variance = sum((value - mean) ** 2 for value in values) / (n - 1)
        margin = CI_Z * (math.sqrt(variance) / math.sqrt(n))
    else:
        margin = 0.0
    return mean, margin, n


def _classify_error(presented, response):
    # Phonological is checked first; a pair in both groups counts as phonological.
    if response in PHONOLOGICAL_CONFUSIONS.get(presented, set()):
        return "phonological"
    if response in VISUAL_CONFUSIONS.get(presented, set()):
        return "visual"
    return "other"


def _error_type_proportions(rows):
    # Among incorrect rows with a single non-empty response letter, the share of each error type.
    error_rows = [row for row in rows if not row["correct"] and len(row["response"]) == 1]
    total = len(error_rows)
    counts = {"phonological": 0, "visual": 0, "other": 0}
    for row in error_rows:
        counts[_classify_error(row["presented"], row["response"])] += 1
    if total == 0:
        proportions = {"phonological": 0.0, "visual": 0.0, "other": 0.0}
    else:
        proportions = {key: value / total for key, value in counts.items()}
    proportions["n"] = total
    return proportions


def _format_stat(mean, margin, n):
    return f"{mean:.3f} (95% CI +/- {margin:.3f}, n={n})"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_lines = []

    def report(line=""):
        print(line)
        report_lines.append(line)

    report("Serial Recall Block - Pooled Analysis")
    report("=" * 40)

    raw_letter_baseline = _load_condition_rows(LETTER_BASELINE_OUTPUT_CSV_DIR, LETTER_BASELINE_OUTPUT_CSV_STEM)
    letter_baseline_rows = _parse_letter_baseline_rows(raw_letter_baseline) if raw_letter_baseline else []

    raw_chunking = _load_condition_rows(CHUNKING_OUTPUT_CSV_DIR, CHUNKING_OUTPUT_CSV_STEM)
    chunking_a_rows = _parse_chunking_rows(raw_chunking, "chunking_a") if raw_chunking else []
    chunking_b_rows = _parse_chunking_rows(raw_chunking, "chunking_b") if raw_chunking else []

    raw_articulatory_suppression = _load_condition_rows(
        ARTICULATORY_SUPPRESSION_OUTPUT_CSV_DIR, ARTICULATORY_SUPPRESSION_OUTPUT_CSV_STEM
    )
    articulatory_suppression_rows = (
        _parse_position_letter_rows(raw_articulatory_suppression) if raw_articulatory_suppression else []
    )

    raw_tapping_control = _load_condition_rows(TAPPING_CONTROL_OUTPUT_CSV_DIR, TAPPING_CONTROL_OUTPUT_CSV_STEM)
    tapping_control_rows = _parse_position_letter_rows(raw_tapping_control) if raw_tapping_control else []

    conditions = [
        ("letter_baseline", "Letter Baseline", letter_baseline_rows),
        ("chunking_a", "Chunking A", chunking_a_rows),
        ("chunking_b", "Chunking B", chunking_b_rows),
        ("articulatory_suppression", "Articulatory Suppression", articulatory_suppression_rows),
        ("tapping_control", "Tapping Control", tapping_control_rows),
    ]

    for key, label, rows in conditions:
        if rows:
            report(f"\nLoaded {label}: {len(rows)} rows")
        else:
            report(f"\n{label}: no data available.")

    # --- 1. Capacity limit per condition ---
    report("\n\n1. Capacity Limit per Condition (mean correct out of {})".format(SEQUENCE_LENGTH))
    report("-" * 60)
    capacity_stats = {}
    for key, label, rows in conditions:
        if rows:
            counts = _capacity_counts_per_trial(rows)
            mean, margin, n_trials = _mean_ci(counts)
            capacity_stats[key] = (mean, margin, n_trials)
            report(f"{label}: {_format_stat(mean, margin, n_trials)}")
        else:
            report(f"{label}: skipped, no data.")

    # --- 2. Chunking effect ---
    report("\n\n2. Chunking Effect: Chunking A vs Chunking B")
    report("-" * 60)
    for key, label in (("chunking_a", "Chunking A"), ("chunking_b", "Chunking B")):
        if key in capacity_stats:
            report(f"{label}: {_format_stat(*capacity_stats[key])}")
        else:
            report(f"{label}: skipped, no data.")

    # --- 3. Articulatory suppression effect ---
    report("\n\n3. Articulatory Suppression Effect: Articulatory Suppression vs Tapping Control")
    report("-" * 60)
    for key, label in (("articulatory_suppression", "Articulatory Suppression"), ("tapping_control", "Tapping Control")):
        if key in capacity_stats:
            report(f"{label}: {_format_stat(*capacity_stats[key])}")
        else:
            report(f"{label}: skipped, no data.")

    # --- 4. Error type analysis ---
    report("\n\n4. Error Type Analysis: Letter Baseline vs Articulatory Suppression")
    report("-" * 60)
    error_type_stats = {}
    for key, label, rows in (
        ("letter_baseline", "Letter Baseline", letter_baseline_rows),
        ("articulatory_suppression", "Articulatory Suppression", articulatory_suppression_rows),
    ):
        if rows:
            proportions = _error_type_proportions(rows)
            error_type_stats[key] = proportions
            report(
                f"{label}: phonological={proportions['phonological']:.3f}, "
                f"visual={proportions['visual']:.3f}, other={proportions['other']:.3f} "
                f"(n errors={proportions['n']})"
            )
        else:
            report(f"{label}: skipped, no data.")

    SUMMARY_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nSummary written to: {SUMMARY_PATH}")

    # --- Figure 1: capacity limit across all 5 conditions ---
    if capacity_stats:
        order = [("letter_baseline", "Letter Baseline"), ("chunking_a", "Chunking A"), ("chunking_b", "Chunking B"),
                 ("articulatory_suppression", "Articulatory Suppression"), ("tapping_control", "Tapping Control")]
        labels = [label for key, label in order if key in capacity_stats]
        values = [capacity_stats[key][0] for key, label in order if key in capacity_stats]
        errors = [capacity_stats[key][1] for key, label in order if key in capacity_stats]
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(labels, values, yerr=errors, capsize=6, color="#4C72B0")
        ax.set_ylabel(f"Mean items correct (out of {SEQUENCE_LENGTH})")
        ax.set_title("Serial Recall - Capacity Limit by Condition")
        ax.set_ylim(0, SEQUENCE_LENGTH)
        fig.autofmt_xdate(rotation=20)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "capacity_limit.png")
        plt.close(fig)
        print(f"Saved: {OUTPUT_DIR / 'capacity_limit.png'}")
    else:
        print("WARNING: no condition had data - skipping capacity limit figure.")

    # --- Figure 2: phonological vs visual errors, grouped by condition ---
    if error_type_stats:
        condition_keys = [key for key in ("letter_baseline", "articulatory_suppression") if key in error_type_stats]
        condition_labels = {"letter_baseline": "Letter Baseline", "articulatory_suppression": "Articulatory Suppression"}
        x_positions = range(len(condition_keys))
        phonological_values = [error_type_stats[key]["phonological"] for key in condition_keys]
        visual_values = [error_type_stats[key]["visual"] for key in condition_keys]
        bar_width = 0.35

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar([x - bar_width / 2 for x in x_positions], phonological_values, width=bar_width, label="Phonological", color="#4C72B0")
        ax.bar([x + bar_width / 2 for x in x_positions], visual_values, width=bar_width, label="Visual", color="#DD8452")
        ax.set_xticks(list(x_positions))
        ax.set_xticklabels([condition_labels[key] for key in condition_keys])
        ax.set_ylabel("Proportion of errors")
        ax.set_title("Error Type: Phonological vs Visual")
        ax.set_ylim(0, 1)
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "error_type_by_condition.png")
        plt.close(fig)
        print(f"Saved: {OUTPUT_DIR / 'error_type_by_condition.png'}")
    else:
        print("WARNING: no data for Letter Baseline or Articulatory Suppression - skipping error type figure.")


if __name__ == "__main__":
    main()
