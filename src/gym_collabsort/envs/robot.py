"""
Implementation of robot policy.
"""

from ..arm import Arm
from ..config import Config
from .action import Action


class Robot:
    def __init__(self, arm: Arm, config: Config):
        self.arm = arm
        self.config = config

    def choose_action(self) -> dict:
        """Choose action"""

        if self.arm.target_coords is not None:
            if self.arm.board.get_object_at(self.arm.target_coords) is None:
                self.arm.target_coords = self.arm.base.rect.center
            return {"action_value": Action.MOVE.value, "target": None}
        else:
            # Aim for a compatible object
            compatible_objects = self.arm.board.get_compatible_objects(
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
