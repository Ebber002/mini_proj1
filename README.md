<div align="center">
  <h1>Mini Project 1</h1>
  <a href="">
    <img src="https://github.com/user-attachments/assets/e21f2d45-6775-48d8-bf8b-9b1cb99d22e5" alt="Logo" height="80">
  </a>
  <h3>Group 3 - 02464 AI and Human Cognition</h3>
</div>

---

Python infrastructure for the **Human Memory Mini Project** in *Artificial Intelligence and Human Cognition*.

The project runs behavioural memory experiments designed to replicate effects from free recall and serial recall tasks, including:

- primacy and recency
- presentation-rate effects
- working-memory interference and delay
- working-memory capacity
- chunking
- articulatory suppression
- finger-tapping control
- recall error patterns

## Structure

```text
human_memory/
├── main.py
├── next_participant_id.txt
├── experiments/
│   ├── recall.py
│   ├── capacity.py
│   ├── chunking.py
│   └── secondary.py
├── utils/
│   ├── data.py
│   └── participants.py
├── data/
├── data_pilot/
└── analysis/
````

The experiment files are currently placeholders. Their actual implementations will be added separately.

## Running

Start the program with:

```bash
python main.py
```

The launcher supports:

* **New participant** — automatically assigns the next anonymous ID.
* **Returning participant** — enter an existing ID and run any experiment again.
* **Pilot mode** — uses participant ID `0`.

Participants only need to remember their numeric ID. No names or other identifying information are stored.

The experiment menu also shows how many times the participant has already run each experiment.

## Data

Each completed experiment run creates one CSV file.

Filename format:

```text
<experiment>_id<id>_<timestamp>.csv
```

Example:

```text
recall_id4_20260906_203015.csv
capacity_id4_20260908_142201.csv
secondary_id0_20260906_194455.csv
```

Real participant data are stored in:

```text
data/
```

Pilot data (`id0`) are stored separately in:

```text
data_pilot/
```

The CSV files are the source of truth for counting completed runs. Participants may run any experiment, in any order, any number of times.

## Experiments

| Experiment  | Purpose                                                                 |
| ----------- | ----------------------------------------------------------------------- |
| `recall`    | Free recall, primacy/recency, presentation rate, interference and pause |
| `capacity`  | Serial recall and working-memory capacity                               |
| `chunking`  | Meaningful chunks versus unstructured material                          |
| `secondary` | Articulatory suppression, finger tapping and error patterns             |

Analysis will be implemented separately and will read the collected CSV files after data collection.