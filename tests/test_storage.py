import numpy as np

from data.storage import load_simulation, save_simulation


def test_save_and_load_round_trip(tmp_path):
    history = [np.array([[0, 1], [1, 0]]), np.array([[1, 1], [0, 0]])]
    path = save_simulation(history=history, automaton="Game of Life", rule="game_of_life",
                           states=["dead", "alive"], metadata={"source": "test"}, path=tmp_path / "run.json")
    loaded = load_simulation(path)
    assert loaded["automat"] == "Game of Life"
    assert loaded["generatie"] == 1
    assert np.array_equal(loaded["stare"], history[-1])
    assert all(np.array_equal(a, b) for a, b in zip(loaded["istoric"], history))
    assert loaded["dimensiuni"] == [2, 2]
