"""
The agent.
"""

import pygame

from .config import Config
from .object import Location


class Agent(pygame.sprite.Sprite):
    """The agent"""

    def __init__(self, location: Location, config: Config) -> None:
        super().__init__()

        self.config = config
        self.location = location

        # Init agent image
        self.image = pygame.Surface(size=(config.cell_size, config.cell_size))
        self.image.fill(color=config.background_color)

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

        # Get the centered rectangular area of the agent image
        self.rect = self.image.get_rect(center=self._get_center())

    def update(self):
        """Update agent location"""

        # Update the centered rectangular area of the agent image
        self.rect = self.image.get_rect(center=self._get_center())

    def _get_center(self) -> tuple[int, int]:
        """Compute coordinates of center of agent location"""

        # X and Y axes resp. correspond to col and row values
        x_center = self.config.cell_size * (self.location.col + 0.5)
        y_center = self.config.cell_size * (self.location.row + 0.5)

        return (x_center, y_center)
