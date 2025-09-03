"""
Unit tests for grid.
"""

import numpy as np

from gym_collabsort.grid2 import Grid


def test_reset():
    rng = np.random.default_rng()

    grid = Grid(rng=rng)
    grid.reset()

    print(grid)
