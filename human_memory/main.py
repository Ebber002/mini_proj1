"""
Console launcher for the Human Memory Mini Project.

Future experiment modules should expose: run(participant_id: int) -> list[dict]
Each returned dictionary represents one row to be saved by the centralized CSV logger.
"""

from experiments import capacity, chunking, recall, secondary
from utils.data import get_run_counts, save_run
from utils.participants import allocate_participant_id, is_valid_returning_id


EXPERIMENTS = {
    "1": ("recall", "Recall", recall),
    "2": ("capacity", "Capacity", capacity),
    "3": ("chunking", "Chunking", chunking),
    "4": ("secondary", "Secondary", secondary),
}


def experiment_menu(participant_id: int) -> None:
    # Let a participant choose experiments until they go back.
    while True:
        counts = get_run_counts(participant_id)
        heading = "PILOT MODE" if participant_id == 0 else f"Participant {participant_id}"
        print(f"\n{heading}\n")

        for choice, (name, label, _) in EXPERIMENTS.items():
            count = counts[name]
            run_word = "run" if count == 1 else "runs"
            print(f"{choice}. {label:<12} [{count} {run_word}]")
        print("5. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "5":
            return
        if choice not in EXPERIMENTS:
            print("Please enter a number from 1 to 5.")
            continue

        name, label, module = EXPERIMENTS[choice]
        run = getattr(module, "run", None)
        if not callable(run):
            print(f"{label} experiment is not implemented yet.")
            continue

        try:
            rows = run(participant_id)
            path = save_run(name, participant_id, rows)
        except Exception as error:
            print(f"The experiment could not be completed: {error}")
            continue

        if path is None:
            print("The experiment returned no data, so no CSV was created.")
        else:
            print(f"Experiment complete.\nData saved to: {path}")


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
