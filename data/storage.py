import json
from datetime import datetime
from pathlib import Path

import numpy as np


SAVED_STATES_DIR = Path(__file__).resolve().parent / "saved_states"


def save_simulation(initial_state=None, history=None, generation=None, automaton="Game of Life",
                    rule=None, states=None, metadata=None, path=None, start_generation=0):
    """Salvează un istoric JSON compatibil și cu formatul folosit de interfață."""
    if history is None:
        if initial_state is None:
            raise ValueError("Furnizează initial_state sau history.")
        history = [initial_state]
    arrays = [np.asarray(item) for item in history]
    if not arrays:
        raise ValueError("Istoricul nu poate fi gol.")
    last_generation = start_generation + len(arrays) - 1 if generation is None else int(generation)
    payload = {
        "automat": automaton,
        "regula": rule,
        "generatie": last_generation,
        "stare": arrays[-1].tolist(),
        "istoric": [array.tolist() for array in arrays],
        "gen_start": int(start_generation),
        "dimensiuni": list(arrays[-1].shape),
        "stari": states,
        "metadata": metadata or {},
        "salvat_la": datetime.now().isoformat(timespec="seconds"),
    }
    target = Path(path) if path is not None else SAVED_STATES_DIR / f"simulation_{datetime.now():%Y%m%d_%H%M%S_%f}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_simulation(path):
    """Încarcă formatul propriu sau salvarea istorică a interfeței."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if "automat" not in payload or "generatie" not in payload or "stare" not in payload:
        raise ValueError("Fișierul nu conține câmpurile obligatorii ale unei simulări.")
    if payload.get("istoric"):
        payload["istoric"] = [np.asarray(item) for item in payload["istoric"]]
    else:
        payload["istoric"] = [np.asarray(payload["stare"])]
        payload.setdefault("gen_start", int(payload["generatie"]))
    payload["stare"] = np.asarray(payload["stare"])
    payload.setdefault("dimensiuni", list(payload["stare"].shape))
    return payload
