import numpy as np


def count_cells(generation, state=1):
    """Numără celulele cu starea cerută, pentru grile 1D sau 2D."""
    return int(np.count_nonzero(np.asarray(generation) == state))
