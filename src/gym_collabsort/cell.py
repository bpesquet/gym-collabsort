"""
Content of grid cells.
"""

from dataclasses import dataclass
from enum import Enum, StrEnum

import numpy as np
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
    """A location as zero-based (row,col) grid coordinates"""

    row: int = -1
    col: int = -1

    def __str__(self) -> str:
        return f"({self.row},{self.col})"

    def as_array(self) -> np.ndarray:
        """Return the location as a 2D NumPy array"""

        return np.array([self.row, self.col], dtype=int)

    def add(
        self, direction: tuple[int, int], clip: tuple[int, int] | None = None
    ) -> None:
        """Update location according to a given direction"""

        loc_array = self.as_array() + np.array(direction, dtype=int)

        if clip is not None:
            loc_array = np.clip(loc_array, a_min=[0, 0], a_max=clip)

        self.row = loc_array[0]
        self.col = loc_array[1]


class GridElement(pygame.sprite.Sprite):
    """Base class for grid elements"""

    def __init__(self, location: Location, config: Config) -> None:
        super().__init__()

        self.location = location
        self.config = config

        # Init object image
        self.image = pygame.Surface(size=(config.cell_size, config.cell_size))
        self.image.fill(color=config.background_color)

    def _get_center(self) -> tuple[int, int]:
        """Compute coordinates of center of agent location"""

        # X and Y axes resp. correspond to col and row values
        x_center = self.config.cell_size * (self.location.col + 0.5)
        y_center = self.config.cell_size * (self.location.row + 0.5)

        return (x_center, y_center)

    def __str__(self) -> str:
        """Return a string representation of the element"""

        return f"Location: {self.location}"


class Object(GridElement):
    """A pickable object"""

    def __init__(
        self,
        location: Location,
        config: Config,
        color: Color,
        shape: Shape,
    ) -> None:
        super().__init__(location=location, config=config)

        self.color = color
        self.shape = shape

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

        # Define the centered rectangular area of the object image
        self.rect = self.image.get_rect(center=self._get_center())

    def __str__(self) -> str:
        return super().__str__() + f". Color={self.color}. Shape={self.shape}"


class Agent(GridElement):
    """The agent"""

    def __init__(self, location: Location, config: Config) -> None:
        super().__init__(location=location, config=config)

        # Draw agent on the image as a "+" sign.
        # Draw vertical line
        pygame.draw.line(
            surface=self.image,
            color="black",
            start_pos=(config.cell_size // 2, 0),
            end_pos=(config.cell_size // 2, config.cell_size),
            width=3,
        )
        # Draw horizontal line
        pygame.draw.line(
            surface=self.image,
            color="black",
            start_pos=(0, config.cell_size // 2),
            end_pos=(config.cell_size, config.cell_size // 2),
            width=3,
        )

        # Define the centered rectangular area of the agent image
        self.rect = self.image.get_rect(center=self._get_center())

    def update(self) -> None:
        """Move the agent image"""

        # Update the centered rectangular area of the agent image
        self.rect = self.image.get_rect(center=self._get_center())
