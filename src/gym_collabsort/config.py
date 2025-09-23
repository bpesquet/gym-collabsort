"""
Configuration values.
"""

from dataclasses import dataclass
from enum import Enum, StrEnum


class Color(StrEnum):
    """Possible colors for an object"""

    RED = "red"
    BLUE = "blue"
    YELLOW = "yellow"


class Shape(Enum):
    """Possible shapes for an object"""

    SQUARE = 1
    CIRCLE = 2
    TRIANGLE = 3


@dataclass
class Config:
    """Configuration class with default values"""

    # Frames Per Second for env rendering
    render_fps: int = 30

    # Board dimensions
    board_height: int = 500
    board_width: int = 800

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.board_width, self.board_height)

    # Size (height & width) of an object in pixels
    object_size: int = 50

    # Size (height & width) of the base of agent and robot arms in pixels
    arm_base_size: int = object_size

    # Width of arm base lines in pixels
    arm_base_line_width: int = 5

    # Width of the line between arm base and claw in pixels
    arm_line_width: int = 7

    # Size (height & width) of the agent and robot claws in pixels
    arm_claw_size: int = arm_base_size / 2

    # Arm claw movement speed in pixels
    arm_claw_speed: int = 20

    # Factor by which the arm speed is reduced after a collision
    collision_speed_reduction_factor: int = 4

    # Background color of the board
    background_color: str = "white"

    # Number of pickable objects on the board
    n_objects: int = 15

    # Possible colors for board objects
    object_colors: tuple[Color] = (Color.RED, Color.BLUE, Color.YELLOW)

    # Possible shapes for board objects
    object_shapes: tuple[Shape] = (Shape.SQUARE, Shape.CIRCLE, Shape.TRIANGLE)

    # Ordered list of robot color priorities for selecting objects to pick
    robor_color_priorities: tuple[Color] = (Color.RED, Color.BLUE, Color.YELLOW)

    # Ordered list of robot shape priorities for selecting objects to pick
    robor_shape_priorities: tuple[Shape] = (Shape.SQUARE, Shape.CIRCLE, Shape.TRIANGLE)
