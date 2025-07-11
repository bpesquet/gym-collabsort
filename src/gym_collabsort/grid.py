"""
The 2D grid used by the environment.

Inspired by https://github.com/koulanurag/ma-gym/blob/master/ma_gym/envs/utils/draw.py
"""

from dataclasses import dataclass
from enum import StrEnum
from random import choice
from typing import Tuple

from PIL import Image, ImageDraw


class Color(StrEnum):
    """Possible colors for a grid cell"""

    WHITE = "white"
    RED = "red"
    BLUE = "blue"


@dataclass
class Cell:
    """A grid cell"""

    color: Color = Color.WHITE


class Grid:
    """A 2D grid"""

    def __init__(self, shape: Tuple[int, int] = (3, 7), cell_size: int = 50):
        self.shape = shape
        self.cell_size = cell_size

        # Init an empty grid
        self.cells = [[Cell() for col in range(shape[1])] for row in range(shape[0])]

        # Define random colors for grid cells
        for row in range(self.shape[0]):
            for col in range(self.shape[1]):
                color = choice([Color.RED, Color.BLUE])
                self.cells[row][col].color = color

    def draw(self) -> Image:
        """Draw grid as an image"""

        height: int = self.cell_size * self.shape[0]
        width: int = self.cell_size * self.shape[1]

        grid_img = Image.new(mode="RGB", size=(width, height), color="white")
        grid_img = self._fill_cells(image=grid_img)
        grid_img = self._draw_lines(image=grid_img)

        return grid_img

    def _fill_cells(self, image: Image) -> Image:
        """Add cell colors to grid image"""

        for row in range(self.shape[0]):
            for col in range(self.shape[1]):
                x: int = self.cell_size * col
                y: int = self.cell_size * row
                x_dash, y_dash = (
                    x + self.cell_size,
                    y + self.cell_size,
                )
                ImageDraw.Draw(image).rectangle(
                    [(x, y), (x_dash, y_dash)], fill=self.cells[row][col].color
                )

        return image

    def _draw_lines(self, image: Image) -> Image:
        """Add separation lines to grid image"""

        line_color = "black"
        draw = ImageDraw.Draw(image)
        y_start = 0
        y_end = image.height

        for x in range(0, image.width, self.cell_size):
            line = ((x, y_start), (x, y_end))
            draw.line(line, fill=line_color)

        x = image.width - 1
        line = ((x, y_start), (x, y_end))
        draw.line(line, fill=line_color)

        x_start = 0
        x_end = image.width

        for y in range(0, image.height, self.cell_size):
            line = ((x_start, y), (x_end, y))
            draw.line(line, fill=line_color)

        y = image.height - 1
        line = ((x_start, y), (x_end, y))
        draw.line(line, fill=line_color)

        del draw
        return image

    def __str__(self) -> str:
        grid_str: str = f"{self.shape}\n"

        for row in range(self.shape[0]):
            for col in range(self.shape[1]):
                grid_str += self.cells[row][col].color.name[0] + " "
            grid_str += "\n"

        return grid_str
