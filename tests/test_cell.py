"""
Unit tests for cell elements.
"""

from pygame.math import Vector2

from gym_collabsort.cell import Color, Object, Shape
from gym_collabsort.config import Config


def test_object() -> None:
    obj_loc = Vector2(x=1, y=6)
    color = Color.BLUE
    shape = Shape.TRIANGLE

    obj = Object(location=obj_loc, config=Config(), color=color, shape=shape)
    print(obj)

    assert obj.location == obj_loc
    assert obj.image is not None
    assert obj.rect is not None
