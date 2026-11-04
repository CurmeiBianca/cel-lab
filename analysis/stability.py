import numpy as np


def is_stable(previous, current):
    """Returnează True când două generații au aceeași formă și aceleași valori."""
    previous = np.asarray(previous)
    current = np.asarray(current)
    return previous.shape == current.shape and np.array_equal(previous, current)


def first_stable_generation(history, start_generation=0):
    """Întoarce indexul absolut al primei generații stabile sau None."""
    for index in range(1, len(history)):
        if is_stable(history[index - 1], history[index]):
            return start_generation + index
    return None


def find_stability(history, start_generation=0):
    return first_stable_generation(history, start_generation)
