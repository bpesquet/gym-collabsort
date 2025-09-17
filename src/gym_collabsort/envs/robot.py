"""
Implementation of robot logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..config import Config

if TYPE_CHECKING:
    # Only import the below statements during type checking to avoid a circular reference
    # https://stackoverflow.com/a/67673741
    from ..grid import Grid


class Robot:
    def __init__(self, grid: Grid, config: Config):
        self.grid = grid
        self.config = config

    def choose_direction(self) -> tuple[int, int]:
        if self.grid.robot_arm.claw.picked_object is not None:
            # Retract arm: aim for previous claw position
            target_location = self.grid.robot_arm.previous_claw_locations[-1]
        else:
            # Aim for a compatible object
            compatible_objects = self.grid.get_objects(
                colors=self.config.robor_color_priorities,
                shapes=self.config.robor_shape_priorities,
            )
            if len(compatible_objects) > 0:
                # Aim for the first compatible object
                target_obj = compatible_objects[0]
                target_location = target_obj.location
            else:
                # No possible target: no movement
                target_location = self.grid.robot_arm.claw.location

        delta_array = np.clip(
            a=target_location - self.grid.robot_arm.claw.location,
            a_min=(-1, -1),
            a_max=(1, 1),
        )

        return (delta_array[0], delta_array[1])
