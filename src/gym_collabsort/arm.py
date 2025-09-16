"""
Arm-related definitions.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import numpy as np
from pygame.math import Vector2
from pygame.sprite import Group, GroupSingle
from pygame.surface import Surface

from .cell import ArmPart, Object
from .config import Config

if TYPE_CHECKING:
    # Only import the below statements during type checking to avoid a circular reference
    # https://stackoverflow.com/a/67673741
    from .grid import Grid


class Arm:
    def __init__(self, grid: Grid, config: Config, is_agent: bool):
        self.grid = grid
        self.config = config
        self.is_agent = is_agent

        self.starting_location: Vector2 = None
        self._claw: GroupSingle[ArmPart] = GroupSingle()
        self.parts: Group[ArmPart] = Group()

    @property
    def claw(self) -> ArmPart:
        """Return the arm claw"""

        return self._claw.sprite

    def reset(self, starting_location: Vector2):
        """Reset the arm to starting position"""

        self.starting_location = starting_location
        self._claw.add(
            ArmPart(location=starting_location, config=Config, is_agent=self.is_agent)
        )
        self.parts.empty()

    def move(self, direction: tuple[int, int]) -> Object | None:
        """Move the arm in a given direction"""

        new_claw_location = Vector2(
            x=np.clip(
                a=self.claw.location.x + direction[0],
                a_min=0,
                a_max=self.config.n_cols - 1,
            ),
            y=np.clip(
                a=self.claw.location.y + direction[1],
                a_min=0,
                a_max=self.config.n_rows - 1,
            ),
        )

        self._move_claw(location=new_claw_location)

    def _move_claw(self, location: Vector2) -> Object | None:
        """Move the arm claw to a given location"""

        if location != self.claw.location:
            cell_at_new_location = self.grid._get_cell(location=location)

            if cell_at_new_location is None:
                # New location is empty
                self._extend(location=location)

            elif (
                isinstance(cell_at_new_location, Object)
                and self.claw.picked_object is None
            ):
                # New location contains an object and arm claw is empty:
                # move claw to pick the object
                self._extend(location=location, picked_object=cell_at_new_location)

            elif isinstance(cell_at_new_location, ArmPart):
                # New location contains an arm part (agent or robot)

                arm_part: ArmPart = cell_at_new_location
                if arm_part.is_agent == self.is_agent:
                    # Part belong to this arm: retract the arm to new location
                    self._retract(location=location)

                    # If the arm is retracted to its starting position, drop the picked object
                    if location == self.starting_location:
                        dropped_object = copy.deepcopy(self.claw.picked_object)

                        # Drop previously picked object
                        self.grid.objects.remove(self.claw.picked_object)
                        self.claw.picked_object = None

                        return dropped_object

        return None

    def draw(self, surface: Surface) -> None:
        """Draw the arm to a surface"""

        # Draw the claw
        self._claw.update()
        self._claw.draw(surface=surface)

        # Draw the arm parts
        self.parts.update()
        self.parts.draw(surface=surface)

    def get_part(self, location: Vector2) -> ArmPart | None:
        """Check if a grid location is occupied by a part of the arm"""

        for arm_part in self.parts:
            if arm_part.location == location:
                return arm_part

        if self.claw.location == location:
            return self.claw

        return None

    def _extend(self, location: Vector2, picked_object: Object | None = None):
        """Extend the arm to a new location"""

        # Add a part at current location of claw
        self.parts.add(
            ArmPart(
                location=self.claw.location,
                config=self.config,
                is_agent=self.is_agent,
            )
        )

        # Move claw to new location
        self.claw.location = location

        if picked_object is not None:
            self.claw.picked_object = picked_object
            # Move picked object alongside arm claw
            self.claw.picked_object.location = location

    def _retract(self, location: Vector2):
        """Retract the arm to a new location"""

        # Remove the existing part at new location
        self.parts.remove(
            ArmPart(
                location=location,
                config=self.config,
                is_agent=self.is_agent,
            )
        )
        # Move claw to new location
        self.claw.location = location

        if self.claw.picked_object is not None:
            # Move picked object alongside arm claw
            self.claw.picked_object.location = location
