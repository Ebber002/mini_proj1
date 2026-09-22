"""
Free Recall Block - pooled analysis across the four conditions.

Reads the CSV files produced by the Baseline, Fast Rate, WM Task, and Pause
Control experiment scripts, pools all rows across participants and
repetitions directly (Experimental_Architecture.md, Section 6), and reports
the serial position curve, primacy/recency baselines, and the two condition
comparisons the assignment asks for. Prints the results, saves them to a
summary text file, and saves three PNG figures - all under OUTPUT_DIR.

Run standalone: python analyze_free_recall.py
"""

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


# ---------------------------------------------------------------- #
# Parameters - change these, not the logic below.                  #
# ---------------------------------------------------------------- #
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BASELINE_CSV_PATH = DATA_DIR / "free_recall_baseline.csv"
FAST_RATE_CSV_PATH = DATA_DIR / "free_recall_fast_rate.csv"
WM_TASK_CSV_PATH = DATA_DIR / "free_recall_wm_task.csv"
PAUSE_CONTROL_CSV_PATH = DATA_DIR / "free_recall_pause_control.csv"

OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "free_recall"
SUMMARY_PATH = OUTPUT_DIR / "summary.txt"

LIST_LENGTH = 15   # positions 1..15, matches every Free Recall script's LIST_LENGTH
CI_Z = 1.96        # 95% CI via normal approximation to a proportion

# (condition key, display label, CSV path), in the order they should be reported.
CONDITIONS = [
    ("baseline", "Baseline", BASELINE_CSV_PATH),
    ("fast_rate", "Fast Rate", FAST_RATE_CSV_PATH),
    ("wm_task", "WM Task", WM_TASK_CSV_PATH),
    ("pause_control", "Pause Control", PAUSE_CONTROL_CSV_PATH),
]

PRIMACY_POSITIONS = (1, 2, 3)
MIDDLE_POSITIONS = (7, 8, 9)
RECENCY_POSITIONS = (13, 14, 15)


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


def _parse_free_recall_rows(raw_rows):
    # Convert the raw string CSV fields into the types the analysis needs.
    parsed = []
    for row in raw_rows:
        parsed.append(
            {
                "list_position": int(row["list_position"]),
                "recalled": row["recalled"].strip().lower() == "true",
            }
        )
    return parsed


def _proportion_ci(successes, n):
    # 95% CI for a proportion via the normal approximation: p +/- z * sqrt(p(1-p)/n).
    if n == 0:
        return 0.0, 0.0
    p = successes / n
    margin = CI_Z * math.sqrt(p * (1 - p) / n)
    return p, margin


def _accuracy_for_positions(rows, positions):
    # Pooled accuracy (and its CI) across all rows whose list_position is in `positions`.
    subset = [row for row in rows if row["list_position"] in positions]
    n = len(subset)
    successes = sum(1 for row in subset if row["recalled"])
    p, margin = _proportion_ci(successes, n)
    return p, margin, n


def _serial_position_curve(rows):
    # Proportion recalled (with CI and n) at each list position 1..LIST_LENGTH.
    curve = {}
    for position in range(1, LIST_LENGTH + 1):
        p, margin, n = _accuracy_for_positions(rows, (position,))
        curve[position] = (p, margin, n)
    return curve


def _format_stat(p, margin, n):
    return f"{p:.3f} (95% CI +/- {margin:.3f}, n={n})"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_lines = []

    def report(line=""):
        print(line)
        report_lines.append(line)

    report("Free Recall Block - Pooled Analysis")
    report("=" * 40)

    data_by_condition = {}
    curve_by_condition = {}
    for key, label, csv_path in CONDITIONS:
        raw_rows = _load_csv_dicts(csv_path)
        rows = _parse_free_recall_rows(raw_rows) if raw_rows else []
        data_by_condition[key] = rows
        if rows:
            curve_by_condition[key] = _serial_position_curve(rows)
            report(f"\nLoaded {label}: {len(rows)} rows from {csv_path}")
        else:
            report(f"\n{label}: no data available ({csv_path}).")

    # --- 1. Serial position curve per condition ---
    report("\n\n1. Serial Position Curves (proportion recalled per position)")
    report("-" * 60)
    for key, label, _ in CONDITIONS:
        curve = curve_by_condition.get(key)
        if curve is None:
            report(f"{label}: skipped, no data.")
            continue
        report(f"\n{label}:")
        for position in range(1, LIST_LENGTH + 1):
            p, margin, n = curve[position]
            report(f"  position {position:>2}: {_format_stat(p, margin, n)}")

    # --- 2 & 3. Baseline primacy and recency ---
    report("\n\n2. Primacy Baseline (Baseline condition only)")
    report("-" * 60)
    baseline_rows = data_by_condition["baseline"]
    if baseline_rows:
        primacy_p, primacy_margin, primacy_n = _accuracy_for_positions(baseline_rows, PRIMACY_POSITIONS)
        middle_p, middle_margin, middle_n = _accuracy_for_positions(baseline_rows, MIDDLE_POSITIONS)
        report(f"Positions 1-3:  {_format_stat(primacy_p, primacy_margin, primacy_n)}")
        report(f"Positions 7-9:  {_format_stat(middle_p, middle_margin, middle_n)}")
    else:
        report("Skipped: no Baseline data available.")

    report("\n\n3. Recency Baseline (Baseline condition only)")
    report("-" * 60)
    if baseline_rows:
        recency_p, recency_margin, recency_n = _accuracy_for_positions(baseline_rows, RECENCY_POSITIONS)
        middle_p, middle_margin, middle_n = _accuracy_for_positions(baseline_rows, MIDDLE_POSITIONS)
        report(f"Positions 13-15: {_format_stat(recency_p, recency_margin, recency_n)}")
        report(f"Positions 7-9:   {_format_stat(middle_p, middle_margin, middle_n)}")
    else:
        report("Skipped: no Baseline data available.")

    # --- 4. Primacy comparison: Fast Rate vs Baseline ---
    report("\n\n4. Primacy Comparison: Fast Rate vs Baseline (positions 1-3)")
    report("-" * 60)
    primacy_comparison = {}
    for key, label in (("baseline", "Baseline"), ("fast_rate", "Fast Rate")):
        rows = data_by_condition[key]
        if rows:
            p, margin, n = _accuracy_for_positions(rows, PRIMACY_POSITIONS)
            primacy_comparison[key] = (p, margin, n)
            report(f"{label}: {_format_stat(p, margin, n)}")
        else:
            report(f"{label}: skipped, no data.")

    # --- 5. Recency comparison: WM Task vs Baseline and Pause Control ---
    report("\n\n5. Recency Comparison: WM Task vs Baseline vs Pause Control (positions 13-15)")
    report("-" * 60)
    recency_comparison = {}
    for key, label in (("baseline", "Baseline"), ("wm_task", "WM Task"), ("pause_control", "Pause Control")):
        rows = data_by_condition[key]
        if rows:
            p, margin, n = _accuracy_for_positions(rows, RECENCY_POSITIONS)
            recency_comparison[key] = (p, margin, n)
            report(f"{label}: {_format_stat(p, margin, n)}")
        else:
            report(f"{label}: skipped, no data.")

    SUMMARY_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nSummary written to: {SUMMARY_PATH}")

    # --- Figure 1: serial position curves overlaid ---
    if curve_by_condition:
        fig, ax = plt.subplots(figsize=(8, 5))
        for key, label, _ in CONDITIONS:
            curve = curve_by_condition.get(key)
            if curve is None:
                continue
            positions = [pos for pos in range(1, LIST_LENGTH + 1) if curve[pos][2] > 0]
            proportions = [curve[pos][0] for pos in positions]
            margins = [curve[pos][1] for pos in positions]
            ax.errorbar(positions, proportions, yerr=margins, marker="o", capsize=3, label=label)
        ax.set_xlabel("List position")
        ax.set_ylabel("Proportion recalled")
        ax.set_title("Free Recall - Serial Position Curves")
        ax.set_xticks(range(1, LIST_LENGTH + 1))
        ax.set_ylim(0, 1)
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "serial_position_curves.png")
        plt.close(fig)
        print(f"Saved: {OUTPUT_DIR / 'serial_position_curves.png'}")
    else:
        print("WARNING: no condition had data - skipping serial position curve figure.")

    # --- Figure 2: primacy comparison bar chart ---
    if primacy_comparison:
        labels = [label for key, label in (("baseline", "Baseline"), ("fast_rate", "Fast Rate")) if key in primacy_comparison]
        values = [primacy_comparison[key][0] for key, _ in (("baseline", "Baseline"), ("fast_rate", "Fast Rate")) if key in primacy_comparison]
        errors = [primacy_comparison[key][1] for key, _ in (("baseline", "Baseline"), ("fast_rate", "Fast Rate")) if key in primacy_comparison]
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.bar(labels, values, yerr=errors, capsize=6, color=["#4C72B0", "#DD8452"][: len(labels)])
        ax.set_ylabel("Proportion recalled (positions 1-3)")
        ax.set_title("Primacy Comparison: Fast Rate vs Baseline")
        ax.set_ylim(0, 1)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "primacy_comparison.png")
        plt.close(fig)
        print(f"Saved: {OUTPUT_DIR / 'primacy_comparison.png'}")
    else:
        print("WARNING: no data for either Baseline or Fast Rate - skipping primacy comparison figure.")

    # --- Figure 3: recency comparison bar chart ---
    if recency_comparison:
        order = (("baseline", "Baseline"), ("wm_task", "WM Task"), ("pause_control", "Pause Control"))
        labels = [label for key, label in order if key in recency_comparison]
        values = [recency_comparison[key][0] for key, _ in order if key in recency_comparison]
        errors = [recency_comparison[key][1] for key, _ in order if key in recency_comparison]
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.bar(labels, values, yerr=errors, capsize=6, color=["#4C72B0", "#55A868", "#C44E52"][: len(labels)])
        ax.set_ylabel("Proportion recalled (positions 13-15)")
        ax.set_title("Recency Comparison: WM Task vs Baseline vs Pause Control")
        ax.set_ylim(0, 1)
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "recency_comparison.png")
        plt.close(fig)
        print(f"Saved: {OUTPUT_DIR / 'recency_comparison.png'}")
    else:
        print("WARNING: no data for Baseline, WM Task, or Pause Control - skipping recency comparison figure.")


if __name__ == "__main__":
    main()
