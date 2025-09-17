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

    # Grid shape
    n_cols: int = 20
    n_rows: int = 10

    # Size in pixels of a (square) grid cell
    cell_size: int = 50

    # Background color of the grid
    background_color: str = "white"

    # Number of pickable objects on the grid
    n_objects: int = 20

    # Possible colors for grid objects
    object_colors: tuple[Color] = (Color.RED, Color.BLUE, Color.YELLOW)

    # Possible shapes for grid objects
    object_shapes: tuple[Shape] = (Shape.SQUARE, Shape.CIRCLE, Shape.TRIANGLE)

    # Ordered list of robot color priorities for selecting objects to pick
    robor_color_priorities: tuple[Color] = (Color.RED, Color.BLUE, Color.YELLOW)

    # Ordered list of robot shape priorities for selecting objects to pick
    robor_shape_priorities: tuple[Shape] = (Shape.SQUARE, Shape.CIRCLE, Shape.TRIANGLE)
