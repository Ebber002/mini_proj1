#----------------------------------------------------#
# Anonymous participant ID allocation and validation #
#----------------------------------------------------#

from pathlib import Path


NEXT_ID_FILE = Path(__file__).resolve().parent.parent / "next_participant_id.txt"


def _read_next_participant_id() -> int:
    # Read and validate the next participant ID from disk.
    try:
        next_id = int(NEXT_ID_FILE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError) as error:
        raise RuntimeError("Could not read a valid next participant ID.") from error

    if next_id < 1:
        raise RuntimeError("The next participant ID must be at least 1.")
    return next_id


def allocate_participant_id() -> int:
    # Return the next anonymous ID and advance the stored counter.
    participant_id = _read_next_participant_id()
    NEXT_ID_FILE.write_text(f"{participant_id + 1}\n", encoding="utf-8")
    return participant_id


def is_valid_returning_id(participant_id: int) -> bool:
    # Return whether a real participant ID was previously allocated.
    if isinstance(participant_id, bool) or not isinstance(participant_id, int):
        return False
    return 1 <= participant_id < _read_next_participant_id()
