import numpy as np


def find_cycle(history, start_generation=0):
    """Găsește prima configurație repetată; întoarce start, perioada și repetarea."""
    seen = {}
    for index, generation in enumerate(history):
        array = np.asarray(generation)
        # Tuplă Python pentru a trata, de exemplu, int32 și int64 cu aceleași
        # valori ca aceeași stare.
        key = (array.shape, tuple(array.reshape(-1).tolist()))
        if key in seen:
            first_index = seen[key]
            return {
                "found": True,
                "start_generation": start_generation + first_index,
                "repeat_generation": start_generation + index,
                "period": index - first_index,
            }
        seen[key] = index
    return {"found": False, "start_generation": None, "repeat_generation": None, "period": None}


def detect_cycle(history, start_generation=0):
    return find_cycle(history, start_generation)
