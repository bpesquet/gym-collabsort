"""
Unit tests for grid.
"""

import numpy as np
from matplotlib import pyplot as plt

from gym_collabsort.grid import Grid


def test_populate():
    grid = Grid()
    assert len(grid.objects) == 0

    grid.populate(rng=np.random.default_rng())
    print(grid)
    assert len(grid.objects) == grid.config.n_objects

    frame = grid.draw()
    plt.imshow(frame)
    plt.show()
