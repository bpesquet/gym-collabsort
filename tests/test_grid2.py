"""
Unit tests for grid.
"""

import numpy as np
from matplotlib import pyplot as plt

from gym_collabsort.grid2 import Grid


def test_reset_and_draw():
    grid = Grid()

    grid.reset(rng=np.random.default_rng())
    print(grid)
    assert len(grid.objects) == grid.config.n_objects

    frame = grid.draw()
    plt.imshow(frame)
    plt.show()
