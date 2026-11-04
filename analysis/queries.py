import numpy as np

from analysis.count_cells import count_cells
from analysis.cycles import find_cycle
from analysis.stability import first_stable_generation
from core.automaton import Automaton
from core.world import World


RULE_ALIASES = {
    "game of life": "game_of_life", "game_of_life": "game_of_life",
    "brian's brain": "brians_brain", "brians brain": "brians_brain",
    "brians_brain": "brians_brain", "rule 30": "rule_30", "rule_30": "rule_30",
}


def _step(state, rule):
    state = np.asarray(state)
    is_1d = state.ndim == 1
    grid = state.reshape(1, -1) if is_1d else state
    if grid.ndim != 2:
        raise ValueError("Starea trebuie să fie o matrice 1D sau 2D.")
    height, width = grid.shape
    normalized_rule = RULE_ALIASES.get(str(rule).lower(), rule)
    automaton = Automaton(World(width, height, initial_state=grid.copy()), rule=normalized_rule)
    automaton.step()
    result = np.asarray(automaton.world.grid)
    return result.reshape(-1) if is_1d else result


def simulate_history(initial_state, generations, rule="game_of_life"):
    """Construiește istoricul pornind de la starea inițială (generația 0)."""
    if generations < 0:
        raise ValueError("Numărul de generații nu poate fi negativ.")
    history = [np.asarray(initial_state).copy()]
    for _ in range(generations):
        history.append(_step(history[-1], rule))
    return history


def state_after_n(initial_state, generations, rule="game_of_life"):
    return simulate_history(initial_state, generations, rule)[-1]


def stable_generation(history, start_generation=0):
    return first_stable_generation(history, start_generation)


def find_configuration(history, configuration, start_generation=0):
    target = np.asarray(configuration)
    for index, generation in enumerate(history):
        current = np.asarray(generation)
        if current.shape == target.shape and np.array_equal(current, target):
            return {"found": True, "generation": start_generation + index}
    return {"found": False, "generation": None}


def count_after_n(initial_state, generations, state=1, rule="game_of_life"):
    return count_cells(state_after_n(initial_state, generations, rule), state)


def cycle_in_history(history, start_generation=0):
    return find_cycle(history, start_generation)
