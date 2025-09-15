"""
Arm-related definitions.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from pygame.sprite import Group, GroupSingle
from pygame.surface import Surface

from .cell import ArmPart, Clamp, Location, Object
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

        self.starting_location: Location = None
        self._clamp: GroupSingle[ArmPart] = GroupSingle()
        self.parts: Group[ArmPart] = Group()
        self.picked_object: Object = None

    @property
    def clamp(self) -> Clamp:
        """Return the arm clamp"""

        return self._clamp.sprite

    def reset(self, starting_location: Location):
        """Reset the arm to starting position"""

        self.starting_location = starting_location
        self._clamp.add(
            Clamp(location=starting_location, config=Config, is_agent=self.is_agent)
        )
        self.picked_object = None
        self.parts.empty()

    def move(self, direction: tuple[int, int]) -> Object | None:
        """Move the arm in a given direction"""

        new_clamp_location = copy.deepcopy(self.clamp.location)
        new_clamp_location.add_(
            direction=direction, clip=(self.config.n_rows - 1, self.config.n_cols - 1)
        )

        self._move_clamp(location=new_clamp_location)

    def _move_clamp(self, location: Location) -> Object | None:
        """Move the arm clamp to a given location"""

        if location != self.clamp.location:
            cell_at_new_location = self.grid._get_cell(location=Location)

            if cell_at_new_location is None:
                # New location is empty
                self._extend(location=location)

            elif isinstance(cell_at_new_location, Object) and self.clamp.is_empty:
                # New location contains an object and arm clamp is empty

                self._extend(location=location)

                # Pick object into clamp
                self.clamp.is_empty = False
                self.picked_object = cell_at_new_location

            elif isinstance(cell_at_new_location, ArmPart):
                # New location contains an arm part (agent or robot)

                arm_part: ArmPart = cell_at_new_location
                if arm_part.is_agent:
                    # Part belong to agent arm: retract the arm to new location
                    self._retract(location=location)

                    # If the arm is retracted to its starting position, drop the picked object
                    if location == self.starting_location:
                        dropped_object = copy.deepcopy(self.picked_object)

                        # Drop previously picked object
                        self.grid.objects.remove(self.picked_object)
                        self.clamp.is_empty = True
                        self.picked_object = None

                        return dropped_object

        return None

    def draw(self, surface: Surface) -> None:
        """Draw the arm to a surface"""

        # Draw the clamp
        self._clamp.update()
        self._clamp.draw(surface=surface)

        # Draw the arm parts
        self.parts.update()
        self.parts.draw(surface=surface)

    def get_part(self, location: Location) -> ArmPart | None:
        """Check if a grid location is occupied by a part of the arm"""

        for arm_part in self.parts:
            if arm_part.location == location:
                return arm_part

        if self.clamp.location == location:
            return self.clamp

        return None

    def _extend(self, location: Location):
        """Extend the arm to a new location"""

        # Add a part at current location of clamp
        self.parts.add(
            ArmPart(
                location=self.clamp.location,
                config=self.config,
                is_agent=self.is_agent,
            )
        )
        # Move clamp to new location
        self.clamp.location = location

    def _retract(self, location: Location):
        """Retract the arm to a new location"""

        # Remove the existing part at new location
        self.parts.remove(
            ArmPart(
                location=location,
                config=self.config,
                is_agent=self.is_agent,
            )
        )
        # Move clamp to new location
        self.clamp.location = location

        if self.picked_object is not None and self.picked_object.location == location:
            # Move picked object alongside arm clamp
            self.picked_object.location = location
