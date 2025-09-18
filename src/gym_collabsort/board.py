"""
The environment board and its content.
"""

import numpy as np
import pygame
from pygame.math import Vector2
from pygame.sprite import Group, Sprite, spritecollide

from gym_collabsort.config import Color, Config, Shape


class BoardElement(Sprite):
    """Base class for all board elements"""

    def __init__(self, coords: Vector2, size: tuple[int, int], config: Config) -> None:
        super().__init__()

        self.coords = coords

        # Init element image
        self.image = pygame.Surface(size=size)
        self.image.fill(color=config.background_color)

    def update(self) -> None:
        # Move the element, centering it around its coordinates
        self.rect = self.image.get_rect(center=self.coords)


class Object(BoardElement):
    """A pickable object"""

    def __init__(
        self,
        coords: Vector2,
        config: Config,
        color: Color,
        shape: Shape,
    ) -> None:
        super().__init__(
            coords=coords, size=(config.object_size, config.object_size), config=config
        )

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
        self.update()


class ArmBase(BoardElement):
    """Base of the agent or robot arm"""

    def __init__(self, coords: Vector2, config: Config) -> None:
        super().__init__(
            coords=coords,
            size=(config.arm_base_size, config.arm_base_size),
            config=config,
        )

        # Draw an empty square box
        # Draw vertical lines
        for x in (0, config.arm_base_size):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(x, 0),
                end_pos=(x, config.arm_base_size),
                width=1,
            )
        # Draw horizontal lines
        for y in (0, config.arm_base_size):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, y),
                end_pos=(config.arm_base_size, y),
                width=1,
            )

        # Define initial location
        self.update()


class ArmClaw(BoardElement):
    """Claw of the agent or robot arm"""

    def __init__(self, coords: Vector2, config: Config, is_agebt: bool):
        super().__init__(
            coords=coords,
            size=(config.arm_claw_size, config.arm_claw_size),
            config=config,
        )

        if self.is_agent:
            # Draw agent claw arm as a "+" sign.
            # Draw vertical line
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(config.arm_claw_size // 2, 0),
                end_pos=(config.arm_claw_size // 2, config.arm_claw_size),
                width=3,
            )
            # Draw horizontal line
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, config.arm_claw_size // 2),
                end_pos=(config.arm_claw_size, config.arm_claw_size // 2),
                width=3,
            )
        else:
            # Draw base of robot arm as a "x" sign
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, 0),
                end_pos=(config.arm_claw_size, config.arm_claw_size),
                width=3,
            )
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, config.arm_claw_size),
                end_pos=(config.arm_claw_size, 0),
                width=3,
            )

        # Define initial location
        self.update()


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

        # Create an empty group for agent and robot arm bases
        self.arm_bases: Group[ArmBase] = Group()

    def populate(
        self,
        rng: np.random.Generator,
    ) -> None:
        """Populate the board"""

        # Put base of agent arm at the center of the bottom row
        robot_arm_base = ArmBase(
            coords=Vector2(
                x=self.config.board_width // 2,
                y=self.config.arm_base_size,
            ),
            config=self.config,
        )
        self.arm_bases.add(robot_arm_base)

        # Put base of agent arm at the center of the bottom row
        agent_arm_base = ArmBase(
            coords=Vector2(
                x=self.config.board_width // 2,
                y=self.config.board_height - self.config.arm_base_size,
            ),
            config=self.config,
        )
        self.arm_bases.add(agent_arm_base)

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
            if not spritecollide(
                sprite=new_obj, group=self.objects, dokill=False
            ) and not spritecollide(sprite=new_obj, group=self.arm_bases, dokill=False):
                # Add new object if it doesn't collide with anything already present on the board
                self.objects.add(new_obj)
                remaining_objects -= 1

    def draw(self) -> pygame.Surface:
        """Draw the board"""

        # fill the surface with background color to wipe away anything previously drawed
        self.canvas.fill(self.config.background_color)

        # Draw objects
        self.objects.update()
        self.objects.draw(surface=self.canvas)

        # Draw (static) arm bases
        self.arm_bases.draw(surface=self.canvas)

        return self.canvas

    def get_frame(self) -> np.ndarray:
        """Return the board as a NumPy array"""

        return np.transpose(
            np.array(pygame.surfarray.pixels3d(self.canvas)), axes=(1, 0, 2)
        )
