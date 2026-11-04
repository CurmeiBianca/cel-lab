import numpy as np

from analysis.queries import (count_after_n, find_configuration, simulate_history,
                              state_after_n)
from data.dataset import build_dataset


def test_generation_n_and_configuration_search():
    initial = np.array([0, 0, 1, 0, 0], dtype=np.int8)
    history = simulate_history(initial, 2, "rule_30")
    assert np.array_equal(state_after_n(initial, 2, "rule_30"), history[2])
    assert count_after_n(initial, 1, 1, "rule_30") == 3
    assert find_configuration(history, history[1]) == {"found": True, "generation": 1}
    assert find_configuration(history, np.zeros((5, 5))) == {"found": False, "generation": None}


def test_dataset_uses_consecutive_generations_and_past_features():
    history = [np.array([0, 1]), np.array([1, 1]), np.array([0, 0])]
    rows = build_dataset([{"history": history, "automaton": "Rule 30"}])
    assert len(rows) == 2
    assert rows[0]["active_cells"] == 1
    assert rows[0]["target_active_cells_next"] == 2
    assert rows[0]["changed_cells"] == 0
    assert rows[1]["changed_cells"] == 1
