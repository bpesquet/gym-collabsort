"""
Implementation of robot logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config import Config
from .action import Action

if TYPE_CHECKING:
    # Only import the below statements during type checking to avoid a circular reference
    # https://stackoverflow.com/a/67673741
    from ..board import Board


class Robot:
    def __init__(self, board: Board, config: Config):
        self.board = board
        self.config = config

    def choose_actiob(self, board: Board) -> dict:
        """Choose robot action"""

        if board.robot_arm.picked_object is not None:
            return {"action_value": Action.RETRACT.value, "target": None}
        elif board.robot_arm.target_coords is not None:
            return {"action_value": Action.EXTEND.value, "target": None}
        else:
            # Aim for a compatible object
            compatible_objects = self.board.get_compatible_objects(
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
