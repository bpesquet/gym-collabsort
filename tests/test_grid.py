"""
Unit tests for grid.
"""

from gym_collabsort.envs.grid import Grid


def test_grid():
    grid = Grid()
    print(grid)

    img = grid.draw()
    img.show()
