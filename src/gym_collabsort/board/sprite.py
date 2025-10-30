"""
Base class for board elements.
"""

import pygame
from pygame.math import Vector2

from ..config import Config


class Sprite(pygame.sprite.Sprite):
    """Base class for board elements"""

    def __init__(
        self,
        location: Vector2,
        size: int,
        config: Config,
        transparent_background: bool = False,
    ):
        super().__init__()

        self.config = config

        # Init sprite image
        self.image = pygame.Surface(size=(size, size))
        self.image.fill(color=config.background_color)

        if transparent_background:
            # Make the rect pixels around the object shape transparent
            self.image.set_colorkey(config.background_color)

        # Define initial sprite location.
        self.location = location

    @property
    def location(self) -> tuple[int, int]:
        """Get location of sprite center, relative to board"""

        # Y is offsetted to take into account the placed objects line above the board
        return (
            self.rect.center[0],
            self.rect.center[1] - self.config.scorebar_height,
        )

    @location.setter
    def location(self, value: Vector2 | tuple[int, int]) -> None:
        """Center sprite around given relative location"""

        # Sprite location is relative to board.
        # Two lines above and below the board display the placed objects for each arm.
        # X is the same for relative and absolute locations.
        # Y is offsetted by the height of the drooped objects line + a thin margin
        self.rect = self.image.get_rect(
            center=(value[0], value[1] + self.config.scorebar_height)
        )

    @property
    def location_abs(self) -> tuple[int, int]:
        """Get absolute location of sprite center"""

        return self.rect.center

    @location_abs.setter
    def location_abs(self, value: Vector2 | tuple[int, int]) -> None:
        """Center sprite around given absolute location"""

        self.rect = self.image.get_rect(center=value)

    def move(self, x_offset: int = 0, y_offset: int = 0) -> None:
        """Move sprite by the specified x (horizontal) and y (vertical) offsets"""

        # Compute location of new sprite center
        new_center = Vector2(
            x=self.rect.center[0] + x_offset * self.config.board_cell_size,
            y=self.rect.center[1] + y_offset * self.config.board_cell_size,
        )
        self.location_abs = new_center
