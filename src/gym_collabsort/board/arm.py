"""
Arm-related definitions.
"""

from __future__ import annotations

import pygame
from pygame.math import Vector2
from pygame.sprite import Group, GroupSingle, spritecollide

from ..action import Action
from ..config import Config
from .object import Object
from .sprite import Coords, Sprite


class Base(Sprite):
    """Base of the agent or robot arm"""

    def __init__(self, location: Vector2, config: Config) -> None:
        super().__init__(
            location=location,
            size=config.board_cell_size,
            config=config,
        )

        # Draw an empty square box
        # Draw vertical lines
        for x in (0, config.board_cell_size - 1):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(x, 0),
                end_pos=(x, config.board_cell_size),
                width=config.arm_base_line_thickness,
            )
        # Draw horizontal lines
        for y in (0, config.board_cell_size - 1):
            pygame.draw.line(
                surface=self.image,
                color="black",
                start_pos=(0, y),
                end_pos=(config.board_cell_size, y),
                width=config.arm_base_line_thickness,
            )


class Gripper(Sprite):
    """Gripper of the agent or robot arm"""

    def __init__(self, location: Vector2, config: Config) -> None:
        super().__init__(
            location=location,
            size=config.arm_gripper_size,
            config=config,
            transparent_background=True,
        )

        self.config = config

        pygame.draw.circle(
            surface=self.image,
            color="black",
            center=(config.arm_gripper_size // 2, config.arm_gripper_size // 2),
            radius=config.arm_gripper_size // 2,
        )


class Arm:
    def __init__(self, location: Vector2, config: Config) -> None:
        self.config = config

        # Create arm base
        self._base: GroupSingle[Base] = GroupSingle(
            Base(location=location, config=self.config)
        )

        # Create arm gripper
        self._gripper: GroupSingle[Gripper] = GroupSingle(
            Gripper(location=location, config=self.config)
        )

        # Current movement target, if any
        self.current_target: Coords | None = None

        # Create empty single sprite group for picked object
        self._picked_object: GroupSingle[Object] = GroupSingle()

        # Penalty flag after a collision
        self.collision_penalty: bool = False

    @property
    def base(self) -> Base:
        """Return the arm base"""

        return self._base.sprite

    @property
    def gripper(self) -> Gripper:
        """Return the arm gripper"""

        return self._gripper.sprite

    @property
    def picked_object(self) -> Object | None:
        """Return the picked object (if any)"""

        return self._picked_object.sprite

    def collide_arm(self, arm: Arm) -> bool:
        """Check if the arm collides with the other arm"""

        # Only grippers can collide
        return spritecollide(sprite=arm.gripper, group=self._gripper, dokill=False)

    def act(
        self, action: Action, objects: Group[Object], other_arm: Arm
    ) -> Object | None:
        """
        Handle the chosen action for the arm.
        Return the placed object if movement ends in arm base with a picket object
        """

        if action == Action.NONE and self.current_target is not None:
            # Continue movement towards previous target
            return self._move(objects=objects, other_arm=other_arm)

        elif action != Action.NONE and self.current_target is None:
            self.current_target = self._get_target_coords(action=action)

            # Init movement towards new target
            return self._move(objects=objects, other_arm=other_arm)

        return None

    def _get_target_coords(self, action: Action) -> Coords:
        """Convert an action to the coordinates (row, col) of its target"""

        col = self.gripper.coords.col
        row = self.gripper.coords.row

        if action == Action.PICK_UPPER:
            row = self.config.upper_treadmill_row
        elif action == Action.PICK_LOWER:
            row = self.config.lower_treadmill_row

        return Coords(row=row, col=col)

    def _move(self, objects: Group[Object], other_arm: Arm) -> Object | None:
        """
        Move arm gripper towards the current target.
        Return the placed object if movement ends in arm base with a picket object
        """

        placed_object: Object = None

        if self.current_target != self.gripper.coords:
            row_offset = 1 if self.current_target.row > self.gripper.coords.row else -1

            # Move the gripper
            self.gripper.move(row_offset=row_offset)

            if self.collide_arm(arm=other_arm):
                self.handle_collision()
                other_arm.handle_collision()

            elif self.picked_object is not None:
                # Move the picked object alongside gripper
                self.picked_object.move(row_offset=row_offset)

                if self.is_retracted():
                    # The placed object will be returned
                    placed_object = self.picked_object

                    # Arm has finished moving the object to its base
                    self._picked_object.remove(placed_object)
                    objects.remove(placed_object)

                    # Arm has no more target
                    self.current_target = None

            else:
                # No picked object: check if the gripper can pick an object at current location
                for obj in objects:
                    if obj.location == self.gripper.location:
                        # Pick object at current location
                        self._picked_object.add(obj)

                        # Arm base is defined as new target
                        self.current_target = self.base.coords

                if self.is_retracted():
                    # Arm has no more target
                    self.current_target = None

        return placed_object

    def handle_collision(self):
        """Handle a collision involving this arm"""

        self.collision_penalty = True

        # Drop any object picked at this time step
        self._picked_object.empty()

        # Move arm gripper back to its base
        self.current_target = self.base.coords

    def is_retracted(self) -> bool:
        """Check if the arm is entirely retracted (gripper has returned to base)"""

        return self.gripper.location == self.base.location
