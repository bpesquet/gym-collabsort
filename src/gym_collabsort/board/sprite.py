"""
Base class for board elements.
"""

import pygame
from pygame.math import Vector2


class Sprite(pygame.sprite.Sprite):
    """Base class for board elements"""

    def __init__(
        self,
        coords: Vector2,
        size: int,
        background_color: str,
        transparent_background: bool = False,
    ):
        super().__init__()

        # Init sprite image
        self.image = pygame.Surface(size=(size, size))
        self.image.fill(color=background_color)

        if transparent_background:
            # Make the rect pixels around the object shape transparent
            self.image.set_colorkey(background_color)

        # Define initial sprite location
        self.coords = coords

    @property
    def coords(self) -> tuple[int, int]:
        """Get coordinates of sprite center"""

        return self.rect.center

    @coords.setter
    def coords(self, value: Vector2 | tuple[int, int]) -> None:
        """Center sprite image around coordinates"""

        self.rect = self.image.get_rect(center=value)
