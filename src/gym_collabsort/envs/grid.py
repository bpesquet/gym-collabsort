"""
The 2D grid used by the environment.

Inspired by https://github.com/koulanurag/ma-gym/blob/master/ma_gym/envs/utils/draw.py
"""

import random
from dataclasses import dataclass
from enum import Enum, StrEnum

from PIL import Image, ImageDraw


class Color(StrEnum):
    """Possible colors for an object"""

    RED = "red"
    BLUE = "blue"
    YELLOW = "yellow"


class Shape(Enum):
    """Possible shapes for an object"""

    SQUARE = 1
    RECTANGLE = 2
    TRIANGLE = 3


@dataclass
class Object:
    """An object to be picked up by the agents"""

    color: Color
    shape: Shape


class Grid:
    """A 2D grid containing the objects to be picked"""

    def __init__(self, shape: tuple[int, int] = (3, 7), cell_size: int = 50):
        self.n_rows = shape[0]
        self.n_cols = shape[1]
        self.cell_size = cell_size

        # Init base grid image used for rendering
        height: int = self.cell_size * self.n_rows
        width: int = self.cell_size * self.n_cols
        self.base_img: Image = Image.new(
            mode="RGB", size=(width, height), color="white"
        )

        self.cells = self.init_cells()

    def init_cells(self, n_objects: int = 10) -> list[list[Object | None]]:
        """Init grid cells"""

        assert n_objects <= self.n_rows * self.n_cols, (
            f"Too many objects ({n_objects}) for a {self.n_rows}x{self.n_cols} grid"
        )

        # Init a list of empty cells
        cells: list[list[Object | None]] = [
            [None for col in range(self.n_cols)] for row in range(self.n_rows)
        ]

        # Place objects randomly on the grid.
        # Each cell can only contain one object
        remaining_objects = n_objects
        while remaining_objects > 0:
            color = random.choice(list(Color))
            shape = random.choice(list(Shape))
            row, col = (
                random.randint(0, self.n_rows - 1),
                random.randint(0, self.n_cols - 1),
            )
            if cells[row][col] is None:
                cells[row][col] = Object(color=color, shape=shape)
                remaining_objects -= 1

        return cells

    def draw(self) -> Image:
        """Draw grid as an image"""

        grid_img = self._draw_cells(image=self.base_img)
        grid_img = self._draw_lines(image=grid_img)

        return grid_img

    def _draw_cells(self, image: Image) -> Image:
        """Draw grid cells"""

        for row in range(self.n_rows):
            for col in range(self.n_cols):
                if self.cells[row][col] is not None:
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
        grid_str: str = f"{self.n_rows, self.n_cols}\n"

        for row in range(self.n_rows):
            for col in range(self.n_cols):
                if self.cells[row][col] is not None:
                    grid_str += self.cells[row][col].color.name[0] + " "
                else:
                    grid_str += "_ "
            grid_str += "\n"

        return grid_str
