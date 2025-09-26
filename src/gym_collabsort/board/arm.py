"""
Arm-related definitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame.math import Vector2
from pygame.sprite import GroupSingle, spritecollide

from ..config import Config
from .object import Object
from .sprite import Sprite

if TYPE_CHECKING:
    # Only import the below statements during type checking to avoid a circular reference
    # https://stackoverflow.com/a/67673741
    from .board import Board


class ArmBase(Sprite):
    """Base of the agent or robot arm"""

    def __init__(self, coords: Vector2, config: Config) -> None:
        super().__init__(
            coords=coords,
            size=config.arm_base_size,
            config=config,
        )

        # Draw an empty square box
        # Draw vertical lines
        for x in (0, config.arm_base_size - 1):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(x, 0),
                end_pos=(x, config.arm_base_size),
                width=config.arm_base_line_width,
            )
        # Draw horizontal lines
        for y in (0, config.arm_base_size - 1):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, y),
                end_pos=(config.arm_base_size, y),
                width=config.arm_base_line_width,
            )


class ArmClaw(Sprite):
    """Claw of the agent or robot arm"""

    def __init__(self, coords: Vector2, config: Config) -> None:
        super().__init__(
            coords=coords,
            size=config.arm_claw_size,
            config=config,
            transparent_background=True,
        )

        self.config = config

        pygame.draw.circle(
            surface=self.image,
            color="black",
            center=(config.arm_claw_size // 2, config.arm_claw_size // 2),
            radius=config.arm_claw_size // 2,
        )

    def move_towards(self, target_coords: Vector2, speed_penalty: bool = False) -> None:
        """Move the claw towards a specific target"""

        # Compute new location, including speed penalty if any
        coords = Vector2(self.coords)
        max_distance = self.config.arm_claw_speed
        if speed_penalty:
            max_distance /= self.config.collision_speed_reduction_factor

        # Move claw to new location
        coords.move_towards_ip(target_coords, max_distance)
        self.coords = coords


class Arm:
    def __init__(self, coords: Vector2, config: Config) -> None:
        self.config = config

        self.collision_penalty: bool = False

        # Create arm base
        self._base: GroupSingle[ArmBase] = GroupSingle(
            ArmBase(coords=coords, config=self.config)
        )

        # Create arm claw
        self._claw: GroupSingle[ArmClaw] = GroupSingle(
            ArmClaw(coords=coords, config=self.config)
        )

        # Create empty single sprite groups for picked and dropped objects.
        # They are used to test if arm has picked or dropped an object
        # without needing to copy Object instances (which is not supported by pygame)
        self._picked_object: GroupSingle[Object] = GroupSingle()
        self._dropped_object: GroupSingle[Object] = GroupSingle()

    @property
    def base(self) -> ArmBase:
        """Return the arm base as a sprite"""

        return self._base.sprite

    @property
    def claw(self) -> ArmClaw:
        """Return the arm claw as a sprite"""

        return self._claw.sprite

    @property
    def picked_object(self) -> Object | None:
        """Return the picked object (if any) as a sprite"""

        return self._picked_object.sprite

    @property
    def dropped_object(self) -> Object | None:
        """Return the dropped object (if any) as a sprite"""

        return self._dropped_object.sprite

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
            first_coordinate=arm.base.coords_abs,
            second_coordinate=arm.claw.coords_abs,
        )

        return collide_claw or collide_base or collide_line

    def move(
        self, board: Board, target_coords: Vector2, other_arm: Arm
    ) -> Object | None:
        """Move arm claw towards target coordinates, returning the dropped object if any"""

        if target_coords != self.claw.coords:
            # Move claw towards target if different from current location
            self.claw.move_towards(
                target_coords=target_coords, speed_penalty=self.collision_penalty
            )

            if self.picked_object is not None:
                # Move the picked object alongside claw
                self.picked_object.coords = self.claw.coords

            if self.collide_arm(arm=other_arm):
                # Drop any previously picked objects
                self._picked_object.empty()
                other_arm._picked_object.empty()

                # Set collision penalty for both arms
                self.collision_penalty = True
                other_arm.collision_penalty = True
            else:
                if self.picked_object is None:
                    # No picked object: check if the arm can pick an object at current location
                    obj = board.get_object_at(coords=self.claw.coords)
                    if obj is not None:
                        # Pick object at current location
                        self._picked_object.add(obj)

                if self.is_retracted():
                    # Arm is entirely retracted: cancel collision penalty if any
                    self.collision_penalty = False

                    if self.picked_object is not None:
                        # Drop the picked object and return it
                        self._dropped_object.add(self.picked_object)
                        self._picked_object.remove(self.picked_object)

                        return self.dropped_object

    def is_retracted(self) -> bool:
        """Check if the arm is entirely retracted (claw has returned to base)"""

        return self.claw.coords == self.base.coords
