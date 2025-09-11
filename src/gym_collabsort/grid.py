"""
The 2D grid containing objects and agents.
"""

import copy

import numpy as np
import pygame
from pygame.sprite import Group, GroupSingle

from .cell import Agent, Color, GridElement, Location, Object, Shape
from .config import Config


class Grid:
    """The 2D grid containing objects and agents"""

    def __init__(self, config: Config | None = None) -> None:
        if config is None:
            # Use default configuration values
            config = Config()

        self.config = config

        # Define the surface to draw upon
        self.canvas = pygame.Surface(size=self.window_size)

        # Create an empty group for grid objects
        self.objects: Group[Object] = Group()

        # Put the agent in its own group
        self._agent: GroupSingle[Agent] = GroupSingle(
            Agent(location=Location(-1, -1), config=config)
        )

    @property
    def window_size(self) -> tuple[int, int]:
        """Get the size of the grid window"""

        window_width = self.config.n_cols * self.config.cell_size
        window_height = self.config.n_rows * self.config.cell_size
        return (window_width, window_height)

    @property
    def agent(self) -> Agent:
        """Get the agent"""

        return self._agent.sprite

    def populate(
        self,
        rng: np.random.Generator,
    ) -> None:
        """Populate the grid"""

        # Put agent at the center of the bottom row
        agent_location = Location(
            row=self.config.n_rows - 1, col=(self.config.n_cols - 1) // 2
        )
        self.agent.location = agent_location

        assert self.config.n_objects <= self.config.n_rows * self.config.n_cols - 2, (
            f"Not enough space on the grid for {self.config.n_objects} objects"
        )

        # Add objects to the grid in an available location
        self.objects.empty()
        remaining_objects = self.config.n_objects
        while remaining_objects > 0:
            obj_location = Location(
                row=rng.integers(low=0, high=self.config.n_rows),
                col=rng.integers(low=0, high=self.config.n_cols),
            )
            if self._get_element(location=obj_location) is None:
                # Randomly define object properties
                color = rng.choice(list(Color))
                shape = rng.choice(list(Shape))

                # Add new object to group
                self.objects.add(
                    Object(
                        location=obj_location,
                        color=color,
                        shape=shape,
                        config=self.config,
                    )
                )
                remaining_objects -= 1

    def _get_element(self, location: Location) -> GridElement | None:
        # Check for existing objects
        for obj in self.objects:
            if obj.location == location:
                return obj

        # Check for agent
        if self.agent.location == location:
            return self.agent

        return None

    def move_agent(self, direction: tuple[int, int]) -> Object | None:
        """Move agent on the grid, returning the picked object if any"""

        new_location = copy.deepcopy(self.agent.location)
        new_location.add(
            direction=direction, clip=(self.config.n_rows - 1, self.config.n_cols - 1)
        )

        if new_location != self.agent.location:
            element = self._get_element(location=new_location)
            if element is not None and isinstance(element, Object):
                self.objects.remove(element)

            # Update agent location
            self.agent.location = new_location

            return element

        return None

    def draw(self) -> pygame.Surface:
        """Draw the grid"""

        # fill the surface with background color to wipe away anything previously drawed
        self.canvas.fill(self.config.background_color)

        # Draw objects
        self.objects.draw(self.canvas)

        # Draw agent
        self._agent.update()
        self._agent.draw(self.canvas)

        # Draw separation lines between grid cells.
        # Draw vertical lines
        for x in range(self.config.n_cols + 1):
            x_line = self.config.cell_size * x
            pygame.draw.line(
                surface=self.canvas,
                color="black",
                start_pos=(x_line, 0),
                end_pos=(x_line, self.canvas.get_height()),
            )
        # Draw horizontal lines
        for y in range(self.config.n_rows + 1):
            y_line = self.config.cell_size * y
            pygame.draw.line(
                surface=self.canvas,
                color="black",
                start_pos=(0, y_line),
                end_pos=(self.canvas.get_width(), y_line),
            )

        # Return grid as pygame surface
        return self.canvas

    def get_frame(self) -> np.ndarray:
        """Return the grid as a NumPy array"""

        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.canvas)), axes=(1, 0, 2)
        )

    def __str__(self) -> str:
        """Return a string representation of a grid"""

        n_objects: int = len(self.objects)
        grid_str: str = f"Grid dimensions: ({self.config.n_rows}, {self.config.n_cols}). {n_objects} objects"

        if n_objects > 0:
            grid_str += ": "
            grid_str += " ".join(map(str, self.objects))
            grid_str += "]"

        grid_str += f". Agent: {self.agent.location}"

        return grid_str
