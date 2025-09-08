"""
Pickable objects.
"""

from dataclasses import dataclass
from enum import Enum, StrEnum

import pygame

from gym_collabsort.config import Config


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
class Location:
    """A location as zero-based (row,col) coordinates"""

    row: int = -1
    col: int = -1

    def __str__(self):
        return f"({self.row},{self.col})"


class Object(pygame.sprite.Sprite):
    """A pickable object"""

    def __init__(
        self, location: Location, color: Color, shape: Shape, config: Config
    ) -> None:
        super().__init__()

        self.location = location
        self.color = color
        self.shape = shape

        # Init object image
        self.image = pygame.Surface(size=(config.cell_size, config.cell_size))
        self.image.fill(color=config.background_color)

        # Draw object on the image
        if self.shape == Shape.SQUARE:
            self.image.fill(color=color)
        elif self.shape == Shape.CIRCLE:
            pygame.draw.circle(
                surface=self.image,
                color=self.color,
                center=(config.cell_size // 2, config.cell_size // 2),
                radius=config.cell_size // 2,
            )
        elif self.shape == Shape.TRIANGLE:
            # Compute coordinates of 3 vectices
            top = (config.cell_size // 2, 0)
            bl = (0, config.cell_size)
            br = (config.cell_size, config.cell_size)

            # Draw the triangle
            pygame.draw.polygon(
                surface=self.image, color=self.color, points=(top, bl, br)
            )

        # Compute coordinates of image center.
        # X and Y axes resp. correspond to col and row values
        x_center = config.cell_size * (self.location.col + 0.5)
        y_center = config.cell_size * (self.location.row + 0.5)

        # Get the centered rectangular area of the object image
        self.rect = self.image.get_rect(center=(x_center, y_center))

    def __str__(self) -> str:
        return f"Location={self.location}, Color={self.color}, Shape={self.shape}"
