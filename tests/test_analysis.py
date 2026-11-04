import numpy as np

from analysis.count_cells import count_cells
from analysis.cycles import find_cycle
from analysis.stability import first_stable_generation, is_stable


def test_stability_and_generation_index():
    first = np.array([[0, 1], [1, 0]])
    assert is_stable(first, first.copy())
    assert not is_stable(first, np.zeros((2, 3)))
    assert first_stable_generation([np.zeros((2, 2)), first, first.copy()]) == 2
    assert first_stable_generation([first]) is None


def test_cycle_reports_start_and_period():
    a = np.array([0, 1])
    b = np.array([1, 0])
    assert find_cycle([a, b, a.copy()], start_generation=4) == {
        "found": True, "start_generation": 4, "repeat_generation": 6, "period": 2
    }
    assert find_cycle([a, b])["found"] is False


def test_count_cells_works_for_1d_and_2d():
    assert count_cells(np.array([0, 1, 2, 1]), 1) == 2
    assert count_cells(np.array([[0, 2], [2, 2]]), 2) == 3
