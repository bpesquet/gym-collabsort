"""
The environment board and its content.
"""

from dataclasses import dataclass

import numpy as np
import pygame
from pygame.math import Vector2
from pygame.sprite import Group, Sprite, spritecollide

from gym_collabsort.arm import Arm
from gym_collabsort.config import Color, Config, Shape


@dataclass
class ObjectProps:
    """Properties of an object"""

    color: Color
    shape: Shape


class Object(Sprite):
    """A pickable object"""

    def __init__(
        self,
        coords: Vector2,
        config: Config,
        color: Color,
        shape: Shape,
    ) -> None:
        super().__init__()

        # Init object image
        self.image = pygame.Surface(size=(config.object_size, config.object_size))
        self.image.fill(color=config.background_color)

        self.color = color
        self.shape = shape

        # Draw object on the image
        if self.shape == Shape.SQUARE:
            self.image.fill(color=color)
        elif self.shape == Shape.CIRCLE:
            pygame.draw.circle(
                surface=self.image,
                color=self.color,
                center=(config.object_size // 2, config.object_size // 2),
                radius=config.object_size // 2,
            )
        elif self.shape == Shape.TRIANGLE:
            # Compute coordinates of 3 vectices
            top = (config.object_size // 2, 0)
            bl = (0, config.object_size)
            br = (config.object_size, config.object_size)

            # Draw the triangle
            pygame.draw.polygon(
                surface=self.image, color=self.color, points=(top, bl, br)
            )

        # Define initial location
        self.rect = self.image.get_rect(center=coords)

    @property
    def props(self) -> ObjectProps:
        return ObjectProps(color=self.color, shape=self.shape)


class Board:
    """The environment board"""

    def __init__(self, config: Config | None = None) -> None:
        if config is None:
            # Use default configuration values
            config = Config()

        self.config = config

        # Define the surface to draw upon
        self.canvas = pygame.Surface(size=self.config.window_size)

        # Create an empty group for objects
        self.objects: Group[Object] = Group()

        # Create agent and robot arms
        self.agent_arm = Arm(board=self, config=config)
        self.robot_arm = Arm(board=self, config=config)

    def populate(
        self,
        rng: np.random.Generator,
    ) -> None:
        """Populate the board"""

        # Put robot arm at the center of the top row
        self.robot_arm.reset(
            coords=Vector2(
                x=self.config.board_width // 2,
                y=self.config.arm_base_size // 2,
            )
        )

        # Put agent arm at the center of the bottom row
        self.agent_arm.reset(
            coords=Vector2(
                x=self.config.board_width // 2,
                y=self.config.board_height - self.config.arm_base_size // 2,
            )
        )

        # Add objects to the board in an available location
        self.objects.empty()
        remaining_objects = self.config.n_objects
        while remaining_objects > 0:
            # Randoml generate coordinates compatible with board dimensions
            obj_coords = Vector2(
                x=rng.integers(
                    low=self.config.object_size // 2,
                    high=self.config.board_width - self.config.object_size // 2,
                ),
                y=rng.integers(
                    low=self.config.object_size // 2,
                    high=self.config.board_height - self.config.object_size // 2,
                ),
            )
            # Randomly generate object properties
            obj_color = rng.choice(a=self.config.object_colors)
            obj_shape = rng.choice(a=self.config.object_shapes)

            new_obj = Object(
                coords=obj_coords,
                color=obj_color,
                shape=obj_shape,
                config=self.config,
            )
            if (
                not self.agent_arm.collide_sprite(sprite=new_obj)
                and not self.robot_arm.collide_sprite(sprite=new_obj)
                and not spritecollide(sprite=new_obj, group=self.objects, dokill=False)
            ):
                # Add new object if it doesn't collide with anything already present on the board
                self.objects.add(new_obj)
                remaining_objects -= 1

    def get_object_at(self, coords: Vector2) -> Object | None:
        """Return the object at a given location, if any"""

        for obj in self.objects:
            if obj.rect.center == coords:
                return obj

    def get_compatible_objects(
        self, colors: tuple[Color], shapes: tuple[Shape]
    ) -> list[Object]:
        """Get the ordered list of board objects with compatible colors and shapes"""

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
        """Draw the board"""

        # fill the surface with background color to wipe away anything previously drawed
        self.canvas.fill(self.config.background_color)

        # Draw objects
        self.objects.update()
        self.objects.draw(surface=self.canvas)

        # Draw arms
        self.agent_arm.draw(surface=self.canvas)
        self.robot_arm.draw(surface=self.canvas)

        return self.canvas

    def get_frame(self) -> np.ndarray:
        """Return the board as a NumPy array"""

        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.canvas)), axes=(1, 0, 2)
        )
