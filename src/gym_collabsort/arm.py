"""
Arm-related definitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pygame
from pygame.math import Vector2
from pygame.sprite import GroupSingle, Sprite, spritecollide

from .config import Config

if TYPE_CHECKING:
    # Only import the below statements during type checking to avoid a circular reference
    # https://stackoverflow.com/a/67673741
    from .board import Board, Object, ObjectProps

# Drawing constants
ARM_BASE_LINE_WIDTH: int = 5
ARM_LINE_WIDTH: int = 7


class ArmBase(Sprite):
    """Base of the agent or robot arm"""

    def __init__(self, coords: Vector2, config: Config) -> None:
        super().__init__()

        # Init image
        self.image = pygame.Surface(size=(config.arm_base_size, config.arm_base_size))
        self.image.fill(color=config.background_color)

        # Draw an empty square box
        # Draw vertical lines
        for x in (0, config.arm_base_size - 1):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(x, 0),
                end_pos=(x, config.arm_base_size),
                width=ARM_BASE_LINE_WIDTH,
            )
        # Draw horizontal lines
        for y in (0, config.arm_base_size - 1):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, y),
                end_pos=(config.arm_base_size, y),
                width=ARM_BASE_LINE_WIDTH,
            )

        # Define initial location
        self.rect = self.image.get_rect(center=coords)


class ArmClaw(Sprite):
    """Claw of the agent or robot arm"""

    def __init__(self, coords: Vector2, config: Config) -> None:
        super().__init__()

        self.config = config

        # Init image
        self.image = pygame.Surface(size=(config.arm_claw_size, config.arm_claw_size))
        self.image.fill(color=config.background_color)

        # Make the rect pixels around the claw shape transparent
        self.image.set_colorkey(config.background_color)

        pygame.draw.circle(
            surface=self.image,
            color="black",
            center=(config.arm_claw_size // 2, config.arm_claw_size // 2),
            radius=config.arm_claw_size // 2,
        )

        # Define initial location
        self.rect = self.image.get_rect(center=coords)

    def move_towards(self, target_coords: Vector2, speed_penalty: bool = False) -> None:
        """Move the claw towards a specific target"""

        # Update claw location
        coords = Vector2(self.rect.center)
        max_distance = self.config.arm_claw_speed
        if speed_penalty:
            max_distance /= self.config.collision_speed_reduction_factor
        coords.move_towards_ip(target_coords, max_distance)
        self.rect = self.image.get_rect(center=coords)


class Arm:
    def __init__(self, board: Board, config: Config) -> None:
        self.board = board
        self.config = config

        self.target_coords: Vector2 = None
        self.picked_object: Object = None
        self.collision_penalty: bool = False

        self._base: GroupSingle[ArmBase] = GroupSingle()
        self._claw: GroupSingle[ArmClaw] = GroupSingle()

    @property
    def base(self) -> ArmBase:
        return self._base.sprite

    @property
    def claw(self) -> ArmClaw:
        return self._claw.sprite

    def reset(self, coords: Vector2) -> None:
        """Reset the arm to its starting location"""

        self._base.empty()
        self._claw.empty()

        # Put robot arm base and claw at the center of the bottom row
        self._base.add(ArmBase(coords=coords, config=self.config))
        self._claw.add(ArmClaw(coords=coords, config=self.config))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the arm on a surface"""

        # Draw arm base and claw
        self._base.draw(surface=surface)
        self._claw.draw(surface=surface)

        # Draw line between arm base and claw
        pygame.draw.line(
            surface=surface,
            color="black",
            start_pos=self.base.rect.center,
            end_pos=self.claw.rect.center,
            width=ARM_LINE_WIDTH,
        )

    def collide_sprite(self, sprite: Sprite) -> bool:
        """Check if the arm collides with a sprite"""

        return spritecollide(
            sprite=sprite, group=self._base, dokill=False
        ) or spritecollide(sprite=sprite, group=self._claw, dokill=False)

    def collide_arm(self, arm: Arm) -> bool:
        """Check if the arm collides with the other arm"""

        collide_claw: bool = self.collide_sprite(sprite=arm.claw)
        collide_base: bool = self.collide_sprite(sprite=arm.base)
        collide_line: tuple = self.claw.rect.clipline(
            first_coordinate=arm.base.rect.center,
            second_coordinate=arm.claw.rect.center,
        )

        return collide_claw or collide_base or collide_line

    def action_aim(self, target_array: np.ndarray) -> None:
        """Aim arm towards specific coordinates"""

        target_coords = Vector2(target_array[0], target_array[1])
        if self.target_coords is not None:
            print(
                f"Warning: overriding arm target, was {self.target_coords}, now {target_coords}"
            )

        self.target_coords = target_coords

    def action_move(self, other_arm: Arm) -> ObjectProps | None:
        """Move arm claw towards target"""

        if self.target_coords is not None:
            # Move claw towards target
            self.claw.move_towards(
                target_coords=self.target_coords, speed_penalty=self.collision_penalty
            )

            if self.picked_object is not None:
                # Move picked object alongside claw
                self.picked_object.rect = self.picked_object.image.get_rect(
                    center=self.claw.rect.center
                )

            if self.collide_arm(arm=other_arm):
                # Collision detected with the other arm
                self.collision_penalty = True
            elif self.picked_object is None:
                # Check if the claw can pick an object at current location
                obj = self.board.get_object_at(coords=self.claw.rect.center)
                if obj is not None:
                    # Pick object and aim towards arm base
                    self.picked_object = obj
                    self.target_coords = self.base.rect.center

            if self.is_retracted():
                # Arm is retracted
                self.target_coords = None
                self.collision_penalty = False

                if self.picked_object is not None:
                    # Drop object
                    dropped_obj_props = self.picked_object.props
                    self.board.objects.remove(self.picked_object)
                    self.picked_object = None

                    return dropped_obj_props

        else:
            print("Error: moving arm without any target")

    def action_extend(self, other_arm: Arm) -> bool:
        """Extend the arm towards the previously defined target, returning collision status"""

        if self.target_coords is None:
            print("Error: trying to extend arm without any target")
        elif self.picked_object is not None:
            print("Warning: trying to extend arm with a picked object")
        else:
            self.claw.move_towards(target_coords=self.target_coords)

            if self.collide_arm(arm=other_arm):
                self.collision_penalty = True
                return True

            if self.picked_object is None:
                # Check if the claw can pick an object
                obj = self.board.get_object_at(coords=self.claw.rect.center)
                if obj is not None:
                    self.picked_object = obj
                    self.target_coords = None

        return False

    def action_retract(self) -> ObjectProps | None:
        """Retract the arm towards its base, returning properties of the dropped object if any"""

        self.claw.move_towards(
            target_coords=self.base.rect.center, speed_penalty=self.collision_penalty
        )

        if self.is_retracted():
            # Arm is retracted after penalty
            self.target_coords = None
            self.collision_penalty = False

        if self.picked_object is not None:
            self.picked_object.rect = self.picked_object.image.get_rect(
                center=self.claw.rect.center
            )

            if self.is_retracted():
                # Drop object
                dropped_obj_props = self.picked_object.props
                self.board.objects.remove(self.picked_object)
                self.picked_object = None

                return dropped_obj_props

        # No dropped object
        return None

    def is_retracted(self) -> bool:
        """Check if th arm claw has returned to its base"""

        return self.claw.rect.center == self.base.rect.center
