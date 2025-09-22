"""
Implementation of robot policy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..arm import Arm
from ..config import Config
from .action import Action

if TYPE_CHECKING:
    # Only import the below statements during type checking to avoid a circular reference
    # https://stackoverflow.com/a/67673741
    from ..board import Board


class Robot:
    def __init__(self, arm: Arm, config: Config):
        self.arm = arm
        self.config = config

    def choose_action(self, board: Board) -> dict:
        """Choose action"""

        if self.arm.picked_object is not None or self.arm.collision_penalty:
            return {"action_value": Action.RETRACT.value, "target": None}
        elif (
            self.arm.target_coords is not None
            and board.get_object_at(self.arm.target_coords) is not None
        ):
            # Keep extending arm towards previously selected object
            return {"action_value": Action.EXTEND.value, "target": None}
        else:
            # Aim for a compatible object
            compatible_objects = board.get_compatible_objects(
                colors=self.config.robor_color_priorities,
                shapes=self.config.robor_shape_priorities,
            )
            if len(compatible_objects) > 0:
                # Aim for the first compatible object
                target = compatible_objects[0].rect.center
                return {"action_value": Action.AIM.value, "target": target}
            else:
                # No possible target => no movement
                return {"action_value": Action.WAIT.value, "target": None}
