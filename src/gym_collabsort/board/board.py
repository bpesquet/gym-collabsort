"""
The environment board and its content.
"""

import numpy as np
import pygame
from pygame.math import Vector2
from pygame.sprite import Group

from ..config import Color, Config, Shape
from .arm import Arm
from .object import Object


class Board:
    """The environment board"""

    def __init__(self, rng: np.random.Generator, config: Config | None = None) -> None:
        if config is None:
            # Use default configuration values
            config = Config()

        self.rng = rng
        self.config = config

        # Define the surface to draw upon
        self.canvas = pygame.Surface(size=self.config.window_dimensions)

        # Create an empty group for objects
        self.objects: Group[Object] = Group()

        # Number of added objects since the beginning of the episode
        self.n_added_objects: int = 0

        # Create agent and robot arms
        self.agent_arm = Arm(
            location=Vector2(
                x=(self.config.arm_base_col - 0.5) * self.config.board_cell_size,
                y=self.config.board_height - self.config.board_cell_size // 2,
            ),
            config=config,
        )
        self.robot_arm = Arm(
            location=Vector2(
                x=(self.config.arm_base_col - 0.5) * self.config.board_cell_size,
                y=self.config.board_cell_size // 2,
            ),
            config=config,
        )

        self.agent_dropped_objects: Group[Object] = Group()
        self.robot_dropped_objects: Group[Object] = Group()

    def add_object(
        self,
    ) -> None:
        """Add a new object to the board"""

        # Randomly choose object treadmill
        if self.rng.choice((0, 1)):
            obj_y = (
                self.config.upper_treadmill_row - 0.5
            ) * self.config.board_cell_size
        else:
            obj_y = (
                self.config.lower_treadmill_row - 0.5
            ) * self.config.board_cell_size

        # Randomly generate object attributes
        obj_color = self.rng.choice(a=self.config.object_colors)
        obj_shape = self.rng.choice(a=self.config.object_shapes)

        new_obj = Object(
            location=Vector2(
                x=self.config.board_cell_size * (self.config.n_cols - 0.5), y=obj_y
            ),
            color=obj_color,
            shape=obj_shape,
            config=self.config,
        )
        self.objects.add(new_obj)
        self.n_added_objects += 1

    def animate(self) -> None:
        """Animate the board"""

        # Move all objects from right to left on their treadmill
        for obj in self.objects:
            obj.move(x_offset=-1)

            if obj.location[0] < 0:
                # Object has fallen from the treadmill before being picked
                self.objects.remove(obj)

        # Add a new object according to probability if limite has not been reached yet
        if (
            self.n_added_objects < self.config.n_objects
            and self.rng.random() < self.config.new_object_proba
        ):
            self.add_object()

    def get_object_at(self, location: tuple[int, int]) -> Object | None:
        """Return the object at a given location, if any"""

        for obj in self.objects:
            if obj.location == location:
                return obj

    def get_compatible_objects(
        self, colors: tuple[Color], shapes: tuple[Shape]
    ) -> list[Object]:
        """
        Get the ordered list of board objects with listed colors and shapes.

        Desired colors and shapes are given by descending order of priority.
        Selected objects (if any) are returned by descending order or compatibility.
        Color is used as first selection criterion, shape as second.
        """

        shape_compatible_objects: list[Object] = []
        compatible_objects: list[Object] = []

        # Exclude already picked objects
        available_objects = [
            obj
            for obj in self.objects
            if obj != self.agent_arm.picked_object
            and obj != self.robot_arm.picked_object
        ]

        # Select available object that are shape-compatible.
        # They are sorted by descending order of shape priority
        for shape in shapes:
            for obj in available_objects:
                if obj.shape == shape:
                    shape_compatible_objects.append(obj)

        # Select shape-compatible objects that are also color-compatible.
        # They are sorted by descending order of color priority
        for color in colors:
            for obj in shape_compatible_objects:
                if obj.color == color:
                    compatible_objects.append(obj)

        return compatible_objects

    def draw(self) -> pygame.Surface:
        """Draw the board"""

        # fill the surface with background color to wipe away anything previously drawed
        self.canvas.fill(self.config.background_color)

        # Draw board limits.
        # Y is offsetted to take into account the dropped objects line above the board
        for y in (0, self.config.board_height):
            pygame.draw.line(
                surface=self.canvas,
                color="black",
                start_pos=(0, y + self.config.scorebar_height),
                end_pos=(
                    self.config.board_width,
                    y + self.config.scorebar_height,
                ),
                width=self.config.scorebar_line_thickness,
            )

        # An object just dropped by the agent arm must be moved below the board
        if self.agent_arm._dropped_object:
            # Move dropped object to line above the board
            self.agent_arm.dropped_object.location_abs = (
                len(self.agent_dropped_objects)
                * (self.config.board_cell_size + self.config.scorebar_margin)
                + self.config.board_cell_size // 2
                + self.config.scorebar_margin,
                self.agent_arm.base.location_abs[1] + self.config.scorebar_height,
            )
            # Update objects lists
            self.agent_dropped_objects.add(self.agent_arm.dropped_object)
            self.objects.remove(self.agent_arm.dropped_object)
            self.agent_arm._dropped_object.empty()

        # An object just dropped by the robot arm must be moved above the board
        if self.robot_arm._dropped_object:
            # Move dropped object to line below the board
            self.robot_arm.dropped_object.location_abs = (
                len(self.robot_dropped_objects)
                * (self.config.board_cell_size + self.config.scorebar_margin)
                + self.config.board_cell_size // 2
                + self.config.scorebar_margin,
                self.robot_arm.base.location_abs[1] - self.config.scorebar_height,
            )
            # Update objects lists
            self.robot_dropped_objects.add(self.robot_arm.dropped_object)
            self.objects.remove(self.robot_arm.dropped_object)
            self.robot_arm._dropped_object.empty()

        # Draw dropped objects for each arm
        self.agent_dropped_objects.draw(surface=self.canvas)
        self.robot_dropped_objects.draw(surface=self.canvas)

        # Draw bases for each arm
        self.agent_arm._base.draw(surface=self.canvas)
        self.robot_arm._base.draw(surface=self.canvas)

        # Draw objects
        self.objects.draw(surface=self.canvas)

        # Draw agent arm claw
        self.agent_arm._claw.draw(surface=self.canvas)
        # Draw line between agent arm base and claw
        pygame.draw.line(
            surface=self.canvas,
            color="black",
            start_pos=self.agent_arm.base.location_abs,
            end_pos=self.agent_arm.claw.location_abs,
            width=self.config.arm_line_thickness,
        )

        # Draw robot arm claw
        self.robot_arm._claw.draw(surface=self.canvas)
        # Draw line between robot arm base and claw
        pygame.draw.line(
            surface=self.canvas,
            color="black",
            start_pos=self.robot_arm.base.location_abs,
            end_pos=self.robot_arm.claw.location_abs,
            width=self.config.arm_line_thickness,
        )

        return self.canvas

    def get_frame(self) -> np.ndarray:
        """Return the board as a NumPy array"""

        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.canvas)), axes=(1, 0, 2)
        )
