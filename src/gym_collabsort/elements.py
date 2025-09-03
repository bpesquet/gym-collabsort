"""
Elements of the environment: agents and pickable objects.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import pygame

from gym_collabsort.config import Config


@dataclass
class Location:
    """A location as (row,col) coordinates"""

    row: int = -1
    col: int = -1

    def __str__(self):
        return f"({self.row},{self.col})"


@dataclass
class Element(ABC):
    """Base class for elements"""

    # Location as (x,y) coordinates
    location = np.array([-1, -1], dtype=int)

    @abstractmethod
    def draw(self, canvas) -> None:
        """Draw the element on a provided canvas"""


class Object(pygame.sprite.Sprite):
    """A pickable object"""

    def __init__(self, location: Location, config: Config, *groups):
        super().__init__(*groups)

        self.location = location

        self.image = pygame.Surface(size=(config.cell_size, config.cell_size))
        self.image.fill(color="red")

        x_center = config.cell_size * (self.location.row + 0.5)
        y_center = config.cell_size * (self.location.col + 0.5)
        self.rect = self.image.get_rect(center=(x_center, y_center))

    def __str__(self):
        return f"Location={self.location}"
