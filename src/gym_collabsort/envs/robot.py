"""
Implementation of robot policy.
"""

from ..board.arm import Arm
from ..board.board import Board
from ..config import Config


class Robot:
    def __init__(self, board: Board, arm: Arm, config: Config) -> None:
        self.board = board
        self.arm = arm
        self.config = config

        # Coordinates of current target
        self.target_coords: tuple[int, int] = None

    def choose_action(self) -> tuple[int, int]:
        """Return the coordinates of the chosen target"""

        if self.arm.is_retracted():
            # Reset target when arm is fully retracted
            self.target_coords = None
        elif self.arm.collision_penalty or self.arm.picked_object is not None:
            # Retract arm towards its base after a collision or if a object has been picked
            self.target_coords = self.arm.base.coords
        elif (
            self.target_coords is not None
            and self.board.get_object_at(self.target_coords) is None
        ):
            # Previously targeted object is no longer there (probably picked by the other arm).
            # Retract arm towards its base
            self.target_coords = self.arm.base.coords

        if self.target_coords is None:
            # Search for objects compatible with robot picking priorities
            compatible_objects = self.board.get_compatible_objects(
                colors=self.config.robor_color_priorities,
                shapes=self.config.robor_shape_priorities,
            )
            if len(compatible_objects) > 0:
                # Aim for the first compatible object
                self.target_coords = compatible_objects[0].coords

        if self.target_coords is not None:
            # Move arm towards target
            return self.target_coords
        else:
            # No possible target => stay still
            return self.arm.claw.coords
