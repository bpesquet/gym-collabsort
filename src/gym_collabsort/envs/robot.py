"""
Implementation of robot policy.
"""

from ..arm import Arm
from ..config import Config
from .action import Action


class Robot:
    def __init__(self, arm: Arm, config: Config) -> None:
        self.arm = arm
        self.config = config

        # Coordinates of current target
        self.target: tuple[int, int] = None

    def choose_action(self) -> dict:
        """Choose action"""

        if self.arm.is_retracted():
            # Reset target when arm is fully retracted
            self.target = None
        elif self.arm.collision_penalty or self.arm.picked_object is not None:
            # Retract arm towards its base after a collision or if a object has been picked
            self.target = self.arm.base.rect.center
        elif (
            self.target is not None
            and self.arm.board.get_object_at(self.target) is None
        ):
            # Previously targeted object is no longer there (probably picked by the other arm).
            # Retract arm towards its base
            self.target = self.arm.base.rect.center

        if self.target is None:
            # Search for objects compatible with robot picking priorities
            compatible_objects = self.arm.board.get_compatible_objects(
                colors=self.config.robor_color_priorities,
                shapes=self.config.robor_shape_priorities,
            )
            if len(compatible_objects) > 0:
                # Aim for the first compatible object
                self.target = compatible_objects[0].rect.center

        if self.target is not None:
            # Move arm towards target
            return {"action_value": Action.MOVE.value, "target": self.target}
        else:
            # No possible target => no movement
            return {"action_value": Action.WAIT.value, "target": None}
