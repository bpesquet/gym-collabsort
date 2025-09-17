"""
Arm-related definitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from pygame.math import Vector2
from pygame.sprite import Group, GroupSingle
from pygame.surface import Surface

from .cell import ArmPart, Color, Object, Shape
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
        self.previous_claw_locations: list[Vector2] = []

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

    def move(self, direction: tuple[int, int]) -> tuple[Color, Shape] | None:
        """Move the arm in a given direction"""

        # Clip the new location to grid dimensions
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

        return self._move_claw(location=new_claw_location)

    def _move_claw(self, location: Vector2) -> tuple[Color, Shape] | None:
        """Move the arm claw to a given location"""

        if location != self.claw.location:
            cell_at_new_location = self.grid.get_element(location=location)

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
                if (
                    arm_part.is_agent == self.is_agent
                    and location == self.previous_claw_locations[-1]
                ):
                    # Part belong to this arm: retract the arm to new location
                    return self._retract(location=location)

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

    def _extend(self, location: Vector2, picked_object: Object | None = None) -> None:
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
        self.previous_claw_locations.append(self.claw.location.copy())
        self.claw.location = location

        if picked_object is not None:
            self.claw.picked_object = picked_object
            # Move picked object alongside arm claw
            self.claw.picked_object.location = location

    def _retract(self, location: Vector2) -> tuple[Color, Shape] | None:
        """Retract the arm to a new location"""

        # Remove the existing part at new location
        self.get_part(location=location).kill()

        # Move claw to new location
        self.previous_claw_locations.pop()
        self.claw.location = location

        if self.claw.picked_object is not None:
            # If the arm is retracted to its starting position, drop the picked object
            if location == self.starting_location:
                dropped_object_props = (
                    self.claw.picked_object.color,
                    self.claw.picked_object.shape,
                )

                # Drop the picked object
                self.grid.objects.remove(self.claw.picked_object)
                self.claw.picked_object = None

                # Return it for reward computation
                return dropped_object_props
            else:
                # Otherwise, move the picked object alongside arm claw
                self.claw.picked_object.location = location

        return None
