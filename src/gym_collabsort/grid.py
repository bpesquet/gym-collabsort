"""
The 2D grid containing objects and agents.
"""

import numpy as np
import pygame
from pygame.math import Vector2
from pygame.sprite import Group

from .arm import Arm
from .board import BoardElement, Color, Object, Shape
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

        # Create agent and robot arms as empty groups of parts
        self.agent_arm: Arm = Arm(grid=self, config=self.config)
        self.robot_arm: Arm = Arm(grid=self, config=self.config)

    @property
    def window_size(self) -> tuple[int, int]:
        """Get the size of the grid window"""

        window_width = self.config.n_cols * self.config.object_size
        window_height = self.config.n_rows * self.config.object_size
        return (window_width, window_height)

    def populate(
        self,
        rng: np.random.Generator,
    ) -> None:
        """Populate the grid"""

        # Check that the grid is big enough to accomodate all elements
        assert self.config.n_rows >= 2, (
            "Grid should have at least two rows to include agent and robot"
        )
        assert self.config.n_objects <= self.config.n_rows * self.config.n_cols - 2, (
            f"Not enough space on the grid for {self.config.n_objects} objects"
        )

        # Init agent arm at the center of the bottom row
        self.agent_arm.reset(
            starting_location=Vector2(x=(self.config.n_cols - 1) // 2, y=0)
        )

        # Init robot arm at the center of the top row
        self.robot_arm.reset(
            starting_location=Vector2(
                x=(self.config.n_cols - 1) // 2, y=self.config.n_rows - 1
            )
        )

        # Add objects to the grid in an available location
        self.objects.empty()
        remaining_objects = self.config.n_objects
        while remaining_objects > 0:
            obj_location = Vector2(
                x=rng.integers(low=0, high=self.config.n_cols),
                y=rng.integers(low=0, high=self.config.n_rows),
            )
            if self.get_element(location=obj_location) is None:
                # Randomly define object properties
                color = rng.choice(a=self.config.object_colors)
                shape = rng.choice(a=self.config.object_shapes)

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

    def get_element(self, location: Vector2) -> BoardElement | None:
        # Check for existing objects
        for obj in self.objects:
            if obj.location == location:
                return obj

        # Check for agent arm
        agent_arm_part = self.agent_arm.get_part(location=location)
        if agent_arm_part is not None:
            return agent_arm_part

        # Check for robot arm
        robot_arm_part = self.robot_arm.get_part(location=location)
        if robot_arm_part is not None:
            return robot_arm_part

        return None

    def get_objects(self, colors: tuple[Color], shapes: tuple[Shape]) -> list[Object]:
        """Get the ordered list of objects with compatible colors and shapes"""

        shape_compatible_objects: list[Object] = []
        compatible_objects: list[Object] = []

        for shape in shapes:
            for obj in self.objects:
                if obj.shape == shape:
                    shape_compatible_objects.append(obj)

        for color in colors:
            for obj in shape_compatible_objects:
                if obj.color == color:
                    compatible_objects.append(obj)

        return compatible_objects

    def draw(self) -> pygame.Surface:
        """Draw the grid"""

        # fill the surface with background color to wipe away anything previously drawed
        self.canvas.fill(self.config.background_color)

        # Draw objects
        self.objects.update()
        self.objects.draw(surface=self.canvas)

        # Draw agent and robot arms
        self.agent_arm.draw(surface=self.canvas)
        self.robot_arm.draw(surface=self.canvas)

        # Draw separation lines between grid cells.
        # Draw vertical lines
        for x in range(self.config.n_cols + 1):
            x_line = self.config.object_size * x
            pygame.draw.line(
                surface=self.canvas,
                color="black",
                start_pos=(x_line, 0),
                end_pos=(x_line, self.canvas.get_height()),
            )
        # Draw horizontal lines
        for y in range(self.config.n_rows + 1):
            y_line = self.config.object_size * y
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

        return grid_str
