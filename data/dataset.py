import csv
import json
from pathlib import Path

import numpy as np

from analysis.count_cells import count_cells
from data.storage import SAVED_STATES_DIR


ACTIVE_STATES = {"game_of_life": 1, "brians_brain": 1, "rule_30": 1,
                 "game of life": 1, "brian's brain": 1, "rule 30": 1}
FEATURES = ["simulation_id", "generation", "total_cells", "active_cells", "inactive_cells",
            "active_density", "changed_cells", "rows", "columns", "automaton"]


def build_dataset(simulations):
    """Construiește exemple X/y din istorice reale; fiecare pereche consecutivă este un rând."""
    rows = []
    for simulation_index, simulation in enumerate(simulations):
        history = simulation.get("history", simulation.get("istoric", []))
        if not history:
            state = simulation.get("state", simulation.get("stare"))
            if state is not None:
                history = [state]
        if len(history) < 2:
            continue
        automaton = str(simulation.get("automaton", simulation.get("automat", "unknown")))
        rule = str(simulation.get("rule", simulation.get("regula", automaton))).lower()
        active_state = ACTIVE_STATES.get(rule, ACTIVE_STATES.get(automaton.lower(), 1))
        start = int(simulation.get("start_generation", simulation.get("gen_start", 0)))
        simulation_id = str(simulation.get("simulation_id", simulation_index))
        for index, (current, following) in enumerate(zip(history, history[1:])):
            current, following = np.asarray(current), np.asarray(following)
            if current.size == 0 or current.shape != following.shape:
                continue
            active = count_cells(current, active_state)
            total = int(current.size)
            rows.append({
                "simulation_id": simulation_id, "generation": start + index,
                "total_cells": total, "active_cells": active,
                "inactive_cells": total - active, "active_density": active / total,
                "changed_cells": (int(np.count_nonzero(np.asarray(history[index - 1]) != current))
                                  if index > 0 and np.asarray(history[index - 1]).shape == current.shape else 0),
                "rows": int(current.shape[0]) if current.ndim > 1 else 1,
                "columns": int(current.shape[-1]), "automaton": automaton,
                "target_active_cells_next": count_cells(following, active_state),
            })
    return rows


def build_dataset_from_saved(directory=SAVED_STATES_DIR):
    simulations = []
    for path in Path(directory).glob("*.json"):
        try:
            simulations.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return build_dataset(simulations)


def save_dataset(rows, path=None):
    target = Path(path) if path is not None else Path(__file__).resolve().parent / "datasets" / "cell_activity.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    columns = FEATURES + ["target_active_cells_next"]
    with target.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return target


if __name__ == "__main__":
    dataset_rows = build_dataset_from_saved()
    if dataset_rows:
        print(f"Salvat {len(dataset_rows)} tranziții reale în {save_dataset(dataset_rows)}")
    else:
        print("Nu există suficiente salvări cu cel puțin două generații pentru a construi datasetul.")
