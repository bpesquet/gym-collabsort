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

    # Board dimensions in pixels
    board_height: int = 500
    board_width: int = 800

    # Width of board delimitation line in pixels
    board_line_width: int = 3

    # Margin in pixels around dropped objects
    dropped_object_margin: int = 3

    @property
    def window_dimensions(self) -> tuple[int, int]:
        """Return the dimensions (width, height) of the main window in pixels"""

        # Add heights of both dropped objects lines
        return (
            self.board_width,
            self.board_height + self.y_offset * 2,
        )

    @property
    def y_offset(self) -> int:
        """Return the offset for vertical coordinate (height of dropped objects line)"""

        return self.object_size + self.dropped_object_margin

    # Title of the main window
    window_title = "gym-collabsort - Collaborative sorting task"

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

    # Time penalty used as based reward
    reward__time_penalty: float = -0.1

    # Robot rewards linked to dropped objects' colors
    robot_color_rewards = {
        Color.RED: 5,
        Color.YELLOW: 0,
        Color.BLUE: -5,
    }

    # Robot rewards linked to dropped objects' shapes
    robot_shape_rewards = {
        Shape.SQUARE: 2,
        Shape.CIRCLE: 1,
        Shape.TRIANGLE: 0,
    }

    # Agent rewards linked to dropped objects' colors
    agent_color_rewards = {
        Color.BLUE: 5,
        Color.RED: 0,
        Color.YELLOW: -5,
    }

    # Agent rewards linked to dropped objects' shapes
    agent_shape_rewards = {
        Shape.CIRCLE: 1,
        Shape.SQUARE: 1,
        Shape.TRIANGLE: 0,
    }
