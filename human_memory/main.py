"""
Console launcher for the Human Memory Mini Project.

Experiment selection is a two-level menu: choose a block (Free Recall or
Serial Recall), then choose Baseline or the block's other conditions. Each
block's "other experiments" are gated behind having completed that block's
Baseline at least once, checked by reading the Baseline's own CSV output.
"""

import csv

from experiments.free_recall_baseline import OUTPUT_CSV_PATH, run_free_recall_baseline
from experiments.free_recall_fast_rate import (
    OUTPUT_CSV_PATH as FAST_RATE_OUTPUT_CSV_PATH,
    run_free_recall_fast_rate,
)
from experiments.free_recall_pause_control import (
    OUTPUT_CSV_PATH as PAUSE_CONTROL_OUTPUT_CSV_PATH,
    run_free_recall_pause_control,
)
from experiments.free_recall_wm_task import (
    OUTPUT_CSV_PATH as WM_TASK_OUTPUT_CSV_PATH,
    run_free_recall_wm_task,
)
from experiments.serial_recall_articulatory_suppression import (
    OUTPUT_CSV_PATH as ARTICULATORY_SUPPRESSION_OUTPUT_CSV_PATH,
    run_serial_recall_articulatory_suppression,
)
from experiments.serial_recall_chunking import (
    OUTPUT_CSV_PATH as CHUNKING_OUTPUT_CSV_PATH,
    run_serial_recall_chunking,
)
from experiments.serial_recall_letter_baseline import (
    OUTPUT_CSV_PATH as SERIAL_RECALL_OUTPUT_CSV_PATH,
    run_serial_recall_letter_baseline,
)
from experiments.serial_recall_tapping_control import (
    OUTPUT_CSV_PATH as TAPPING_CONTROL_OUTPUT_CSV_PATH,
    run_serial_recall_tapping_control,
)
from utils.participants import allocate_participant_id, is_valid_returning_id


def has_completed_baseline(csv_path, participant_id: int) -> bool:
    # Return whether csv_path already has at least one row for this participant.
    if not csv_path.exists():
        return False
    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return any(row.get("participant_id") == str(participant_id) for row in reader)


def ask_repetition_number():
    # Ask for a repetition number, returning None (after printing why) if invalid.
    entered = input("Enter repetition number (1-5): ").strip()
    try:
        return int(entered)
    except ValueError:
        print("Repetition number must be a whole number.")
        return None


def free_recall_other_menu(participant_id: int) -> None:
    # "Other experiments" submenu for Free Recall - conditions not implemented yet.
    while True:
        print("\nFree Recall - Other Experiments\n")
        print("1. Fast Rate")
        print("2. WM Task")
        print("3. Pause Control")
        print("4. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "4":
            return
        if choice == "1":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_free_recall_fast_rate(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {FAST_RATE_OUTPUT_CSV_PATH}")
        elif choice == "2":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_free_recall_wm_task(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {WM_TASK_OUTPUT_CSV_PATH}")
        elif choice == "3":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_free_recall_pause_control(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {PAUSE_CONTROL_OUTPUT_CSV_PATH}")
        else:
            print("Please enter a number from 1 to 4.")


def serial_recall_other_menu(participant_id: int) -> None:
    # "Other experiments" submenu for Serial Recall - conditions not implemented yet.
    while True:
        print("\nSerial Recall - Other Experiments\n")
        print("1. Chunking (A+B)")
        print("2. Articulatory Suppression")
        print("3. Tapping Control")
        print("4. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "4":
            return
        if choice == "1":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_serial_recall_chunking(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {CHUNKING_OUTPUT_CSV_PATH}")
        elif choice == "2":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_serial_recall_articulatory_suppression(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {ARTICULATORY_SUPPRESSION_OUTPUT_CSV_PATH}")
        elif choice == "3":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_serial_recall_tapping_control(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {TAPPING_CONTROL_OUTPUT_CSV_PATH}")
        else:
            print("Please enter a number from 1 to 4.")


def free_recall_menu(participant_id: int) -> None:
    # Level 2 menu for the Free Recall block: Baseline or other experiments.
    while True:
        print("\nFree Recall\n")
        print("1. Baseline")
        print("2. Other experiments")
        print("3. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "3":
            return

        if choice == "1":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_free_recall_baseline(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {OUTPUT_CSV_PATH}")
        elif choice == "2":
            if not has_completed_baseline(OUTPUT_CSV_PATH, participant_id):
                print("Please complete the Free Recall Baseline at least once before accessing other experiments.")
                continue
            free_recall_other_menu(participant_id)
        else:
            print("Please enter a number from 1 to 3.")


def serial_recall_menu(participant_id: int) -> None:
    # Level 2 menu for the Serial Recall block: Baseline or other experiments.
    while True:
        print("\nSerial Recall\n")
        print("1. Baseline")
        print("2. Other experiments")
        print("3. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "3":
            return

        if choice == "1":
            repetition_number = ask_repetition_number()
            if repetition_number is None:
                continue
            try:
                run_serial_recall_letter_baseline(participant_id, repetition_number)
            except Exception as error:
                print(f"The experiment could not be completed: {error}")
                continue
            print(f"Experiment complete.\nData saved to: {SERIAL_RECALL_OUTPUT_CSV_PATH}")
        elif choice == "2":
            if not has_completed_baseline(SERIAL_RECALL_OUTPUT_CSV_PATH, participant_id):
                print("Please complete the Serial Recall Letter Baseline at least once before accessing other experiments.")
                continue
            serial_recall_other_menu(participant_id)
        else:
            print("Please enter a number from 1 to 3.")


def experiment_menu(participant_id: int) -> None:
    # Level 1 menu: let a participant choose a block until they go back.
    while True:
        heading = "PILOT MODE" if participant_id == 0 else f"Participant {participant_id}"
        print(f"\n{heading}\n")
        print("1. Free Recall")
        print("2. Serial Recall")
        print("3. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "3":
            return
        if choice == "1":
            free_recall_menu(participant_id)
        elif choice == "2":
            serial_recall_menu(participant_id)
        else:
            print("Please enter a number from 1 to 3.")


def returning_participant() -> None:
    # Validate a returning participant ID and open the experiment menu.
    entered = input("Enter participant ID: ").strip()
    try:
        participant_id = int(entered)
    except ValueError:
        print("Participant ID must be a whole number.")
        return

    if not is_valid_returning_id(participant_id):
        print("That participant ID has not been allocated.")
        return

    experiment_menu(participant_id)


def main() -> None:
    # Run the top-level console menu.
    while True:
        print("\nHuman Memory Experiment\n")
        print("1. New participant")
        print("2. Returning participant")
        print("3. Pilot mode")
        print("4. Exit")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            participant_id = allocate_participant_id()
            print(f"\nYour participant ID is: {participant_id}")
            print("Please remember this number if you return for another session.")
            experiment_menu(participant_id)
        elif choice == "2":
            returning_participant()
        elif choice == "3":
            experiment_menu(0)
        elif choice == "4":
            print("Goodbye.")
            return
        else:
            print("Please enter a number from 1 to 4.")


if __name__ == "__main__":
    main()
