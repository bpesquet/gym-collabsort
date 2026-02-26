"""
Unit test for score bars.
"""

from pygame.math import Vector2

from gym_collabsort.board.object import Object
from gym_collabsort.board.scorebar import ScoreBar
from gym_collabsort.config import Color, Config, Shape


def test_add_object() -> None:
    """Test the addition of an object"""

    config = Config()

    scorebar = ScoreBar(config=config, y_object=10)

    # Assert emptiness
    assert len(scorebar.objects) == 0
    assert scorebar.n_identical_objects == []

    # Assert addition of new object
    scorebar.add(
        placed_object=Object(
            location=Vector2(0, 0), color=Color.BLUE, shape=Shape.SQUARE, config=config
        )
    )
    assert len(scorebar.objects) == 1
    assert scorebar.n_identical_objects == [1]

    # Assert addition of object with same properties as existing one
    scorebar.add(
        placed_object=Object(
            location=Vector2(1, 1), color=Color.BLUE, shape=Shape.SQUARE, config=config
        )
    )
    assert len(scorebar.objects) == 1
    assert scorebar.n_identical_objects == [2]

    # Assert addition of yet another new object
    scorebar.add(
        placed_object=Object(
            location=Vector2(2, 2),
            color=Color.BLUE,
            shape=Shape.TRIANGLE,
            config=config,
        )
    )
    assert len(scorebar.objects) == 2
    assert scorebar.n_identical_objects == [2, 1]
