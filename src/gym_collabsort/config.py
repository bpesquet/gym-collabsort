"""
Configuration values.
"""

import math
from dataclasses import dataclass
from enum import Enum, StrEnum


class Color(StrEnum):
    """Possible colors for an object"""

    RED = "red"
    BLUE = "blue"
    YELLOW = "yellow"


class Shape(Enum):
    """Possible shapes for an object"""

    SQUARE = 0
    CIRCLE = 1
    TRIANGLE = 2


@dataclass
class Config:
    """Configuration class with default values"""

    # Frames Per Second for environment rendering
    render_fps: int = 2

    # ---------- Window and board ----------

    # Number of board rows
    n_rows: int = 10

    # Number of board columns
    n_cols: int = 16

    # Size of a square board cell in pixels
    board_cell_size: int = 50

    @property
    def board_height(self) -> int:
        """Return the height of the board in pixels"""

        return self.n_rows * self.board_cell_size

    @property
    def board_width(self) -> int:
        """Return the width of the board in pixels"""

        return self.n_cols * self.board_cell_size

    # Width in pixels of delimitation line between score bar and board
    scorebar_line_thickness: int = 3

    # Margin around score bar content in pixels
    scorebar_margin: int = 3

    @property
    def scorebar_height(self) -> int:
        """Return the height of the score bar (which is an offset for vertical coordinate)"""

        return self.board_cell_size + self.scorebar_margin

    @property
    def window_dimensions(self) -> tuple[int, int]:
        """Return the dimensions (width, height) of the main window in pixels"""

        # Add heights of both dropped objects lines
        return (
            self.board_width,
            self.board_height + self.scorebar_height * 2,
        )

    # Title of the main window
    window_title = "gym-collabsort - Collaborative sorting task"

    # Background color of the window
    background_color: str = "white"

    # ---------- Treadmills ----------

    # Board row for the uppoer treadmill
    upper_treadmill_row = 4

    # Board row for the lower treadmill
    lower_treadmill_row = 7

    # ---------- Objects ----------

    # Maximum number of objects. If 0, new objects will be added indefinitely
    n_objects: float = math.inf

    # Possible colors for board objects
    object_colors: tuple[Color] = (Color.RED, Color.BLUE, Color.YELLOW)

    # Possible shapes for board objects
    object_shapes: tuple[Shape] = (Shape.SQUARE, Shape.CIRCLE, Shape.TRIANGLE)

    # Probability of adding a new object at each time step
    new_object_proba = 0.25

    # ---------- Agent and robot arms ----------

    # Board column where arm bases are placed
    arm_base_col: int = 4

    # Thickness of arm base lines in pixels
    arm_base_line_thickness: int = 5

    # Thickness of the line between arm base and claw in pixels
    arm_line_thickness: int = 7

    # Size (height & width) of the agent and robot claws in pixels
    arm_claw_size: int = board_cell_size / 2

    # Arm claw movement speed in pixels
    arm_claw_speed: int = 20

    # ---------- Rewards ----------

    # Factor by which the arm speed is reduced after a collision
    collision_speed_reduction_factor: int = 4

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
