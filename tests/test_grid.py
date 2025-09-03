"""
Unit tests for grid.
"""

from gym_collabsort.envs.grid import Grid


def test_grid():
    grid = Grid(shape=(3, 7))
    print(grid)

    img = grid.draw()
    img.show()
