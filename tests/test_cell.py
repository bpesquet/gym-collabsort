"""
Unit tests for cell elements.
"""

import numpy as np

from gym_collabsort.cell import Color, Location, Object, Shape
from gym_collabsort.config import Config


def test_location() -> None:
    row, col = 2, 3
    loc = Location(row=row, col=col)

    loc_array = loc.as_array()
    assert loc_array[0] == row
    assert loc_array[1] == col

    direction = np.array([1, 1])
    loc.add(direction=direction)
    assert loc.row == row + 1
    assert loc.col == col + 1

    clip = (5, 7)
    loc.add(direction=(10, 10), clip=clip)
    assert loc.row == clip[0]
    assert loc.col == clip[1]

    loc.add(direction=(-10, -10), clip=clip)
    assert loc.row == 0
    assert loc.col == 0


def test_object() -> None:
    obj_loc = Location(1, 6)
    color = Color.BLUE
    shape = Shape.TRIANGLE

    obj = Object(location=obj_loc, config=Config(), color=color, shape=shape)
    print(obj)

    assert obj.location == obj_loc
    assert obj.image is not None
    assert obj.rect is not None
