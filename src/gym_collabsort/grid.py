"""
The 2D grid used by the environment.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class Color(Enum):
    """Possible colors for a grid cell"""

    WHITE = 0
    RED = 1
    BLUE = 2


@dataclass
class Cell:
    """A grid cell"""

    color: Color


class Grid:
    """A 2D grid"""

    def __init__(self, shape: Tuple = (3, 7)):
        self.shape = shape
        self.cells = [
            [Cell(color=Color.WHITE) for col in range(shape[1])]
            for row in range(shape[0])
        ]

    def __str__(self):
        grid_str: str = f"{self.shape}\n"

        for row in range(self.shape[0]):
            for col in range(self.shape[1]):
                grid_str += self.cells[row][col].color.name[0] + " "
            grid_str += "\n"

        return grid_str
