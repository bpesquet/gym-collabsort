"""
The 2D grid containing objects and agents.
"""

import numpy as np
import pygame
from pygame.sprite import Group

from .config import Config
from .elements import Location, Object


class Grid:
    """The 2D grid containing objects and agents"""

    def __init__(self, config: Config | None = None):
        if config is None:
            # Use default configuration values
            config = Config()

        self.config = config

        # Define the surface to draw upon
        window_width = self.config.n_cols * self.config.cell_size
        window_height = self.config.n_rows * self.config.cell_size
        self.canvas = pygame.Surface(size=(window_width, window_height))

        self.agent_location = Location(row=-1, col=-1)

    def reset(
        self,
        rng: np.random.Generator,
    ) -> None:
        """Reset the grid"""

        # Put agent at the center of the last row
        self.agent_location = Location(
            row=self.config.n_rows - 1, col=round((self.config.n_cols - 1) / 2)
        )

        assert self.config.n_objects <= self.config.n_rows * self.config.n_cols - 2, (
            f"Not enough space on the grid for {self.config.n_objects} objects"
        )

        # Put each object in an available location
        self.objects: Group[Object] = Group()
        remaining_objects = self.config.n_objects
        while remaining_objects > 0:
            location = Location(
                row=rng.integers(low=0, high=self.config.n_rows - 1),
                col=rng.integers(low=0, high=self.config.n_cols - 1),
            )
            if self._is_location_available(location=location):
                self.objects.add(Object(location=location, config=self.config))
                remaining_objects -= 1

    def _is_location_available(self, location: Location) -> bool:
        """Check if a grid location is available or already taken by an element"""

        # Check for existing objects
        for obj in self.objects:
            if obj.location == location:
                return False

        # Check for agent
        if location == self.agent_location:
            return False

        return True

    def draw(self):
        """Draw the grid"""

        # fill the surface with background color to wipe away anything
        self.canvas.fill(self.config.background_color)

        # Draw objects
        self.objects.draw(self.canvas)

        # Return grid as a frame
        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.canvas)), axes=(1, 0, 2)
        )

    def __str__(self) -> str:
        """Return a string description of a grid"""

        n_objects: int = len(self.objects)
        grid_str: str = f"Grid dimensions: ({self.config.n_rows}, {self.config.n_cols}). {n_objects} objects"

        if n_objects > 0:
            grid_str += ": "
            grid_str += " ".join(map(str, self.objects))
            grid_str += "]"

        grid_str += f". Agent: {self.agent_location}"

        return grid_str
