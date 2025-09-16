"""
Content of grid cells.
"""

import pygame
from pygame.math import Vector2

from gym_collabsort.config import Color, Config, Shape


class GridElement(pygame.sprite.Sprite):
    """Base class for all grid elements"""

    def __init__(self, location: Vector2, config: Config) -> None:
        super().__init__()

        self.location = location
        self.config = config

        # Init element image
        self.image = pygame.Surface(size=(config.cell_size, config.cell_size))
        self.image.fill(color=config.background_color)

    def update(self) -> None:
        """Update the cell image"""

        # Update the centered rectangular area of the element's image
        self.rect = self.image.get_rect(center=self._get_center_coords())

    def _get_center_coords(self) -> Vector2:
        """Compute the coordinates of the center of this element"""

        return Vector2(
            x=self.config.cell_size * (self.location.x + 0.5),
            y=self.config.cell_size * (self.config.n_rows - 0.5 - self.location.y),
        )

    def __str__(self) -> str:
        """Return a string representation of the element"""

        return f"Location: {self.location}"


class Object(GridElement):
    """A pickable object"""

    def __init__(
        self,
        location: Vector2,
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

        # Define the centered rectangular area of the image
        self.rect = self.image.get_rect(center=self._get_center_coords())

    def __str__(self) -> str:
        return super().__str__() + f". Color={self.color}. Shape={self.shape}"


class ArmPart(GridElement):
    """Part of the agent or robot arm"""

    def __init__(self, location: Vector2, config: Config, is_agent: bool) -> None:
        super().__init__(location=location, config=config)

        self.is_agent = is_agent
        self.picked_object = None

        self._draw()

    @property
    def picked_object(self) -> Object:
        return self._picked_object

    @picked_object.setter
    def picked_object(self, value) -> None:
        self._picked_object = value
        self._draw()

    def _draw(self) -> None:
        if self.picked_object is not None:
            self.image = self.picked_object.image.copy()

        if self.is_agent:
            # Draw part of agent arm as a "+" sign.
            # Draw vertical line
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(self.config.cell_size // 2, 0),
                end_pos=(self.config.cell_size // 2, self.config.cell_size),
                width=3,
            )
            # Draw horizontal line
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, self.config.cell_size // 2),
                end_pos=(self.config.cell_size, self.config.cell_size // 2),
                width=3,
            )
        else:
            # Draw part of robot arm as a "x" sign
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, 0),
                end_pos=(self.config.cell_size, self.config.cell_size),
                width=3,
            )
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, self.config.cell_size),
                end_pos=(self.config.cell_size, 0),
                width=3,
            )

        # Define the centered rectangular area of the agent image
        self.rect = self.image.get_rect(center=self._get_center_coords())
