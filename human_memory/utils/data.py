#-------------------------------------------#
# Central CSV logging and run-count helpers #
#-------------------------------------------#

import csv
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Optional


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
PILOT_DATA_DIR = PROJECT_DIR / "data_pilot"
EXPERIMENT_NAMES = ("recall", "capacity", "chunking", "secondary")
METADATA_FIELDS = ("participant_id", "experiment", "run_timestamp")


def _validate_experiment(experiment: str) -> None:
    if experiment not in EXPERIMENT_NAMES:
        allowed = ", ".join(EXPERIMENT_NAMES)
        raise ValueError(f"Unknown experiment {experiment!r}. Choose from: {allowed}.")


def _output_directory(participant_id: int) -> Path:
    if isinstance(participant_id, bool) or not isinstance(participant_id, int):
        raise TypeError("participant_id must be an integer.")
    if participant_id < 0:
        raise ValueError("participant_id cannot be negative.")
    return PILOT_DATA_DIR if participant_id == 0 else DATA_DIR


def save_run(
    experiment: str,
    participant_id: int,
    rows: Optional[list[dict]],
) -> Optional[Path]:
    # Save one completed run, or return None when it contains no rows.
    _validate_experiment(experiment)
    output_directory = _output_directory(participant_id)
    if not rows:
        return None
    if any(not isinstance(row, Mapping) for row in rows):
        raise TypeError("Every experiment row must be a dictionary-like mapping.")

    experiment_fields: list[str] = []
    for row in rows:
        for field in row:
            if field in METADATA_FIELDS:
                raise ValueError(f"Experiment rows cannot override {field!r}.")
            if field not in experiment_fields:
                experiment_fields.append(field)

    output_directory.mkdir(parents=True, exist_ok=True)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = output_directory / f"{experiment}_id{participant_id}_{run_timestamp}.csv"
    fieldnames = [*METADATA_FIELDS, *experiment_fields]

    with path.open("x", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "participant_id": participant_id,
                    "experiment": experiment,
                    "run_timestamp": run_timestamp,
                    **row,
                }
            )
    return path


def count_runs(experiment: str, participant_id: int) -> int:
    # Count completed runs by matching filenames without reading CSV files.
    _validate_experiment(experiment)
    output_directory = _output_directory(participant_id)
    return sum(1 for _ in output_directory.glob(f"{experiment}_id{participant_id}_*.csv"))


def get_run_counts(participant_id: int) -> dict[str, int]:
    # Return run counts for every experiment for one participant.
    return {
        experiment: count_runs(experiment, participant_id)
        for experiment in EXPERIMENT_NAMES
    }
