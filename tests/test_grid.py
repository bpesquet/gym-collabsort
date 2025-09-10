"""
Unit tests for grid.
"""

import numpy as np

from gym_collabsort.grid import Grid


def test_populate() -> None:
    grid = Grid()
    assert len(grid.objects) == 0

    grid.populate(rng=np.random.default_rng())
    print(grid)
    assert len(grid.objects) == grid.config.n_objects


def test_draw() -> None:
    grid = Grid()

    grid.draw()
    frame = grid.get_frame()
    assert frame.shape[0] == grid.window_size[1]
    assert frame.shape[1] == grid.window_size[0]
