"""
Implementation of robot policy.
"""

import numpy as np

from ..board.arm import Arm
from ..board.board import Board
from ..board.object import Object
from ..config import Action


class Robot:
    def __init__(
        self,
        board: Board,
        arm: Arm,
        rewards: np.ndarray,
    ) -> None:
        self.board = board
        self.arm = arm
        self.rewards = rewards

    def choose_action(self) -> Action:
        """Return the chosen action"""

        # Wait by default
        action: Action = Action.NONE

        # Search for the best object to aim for
        best_object = self._choose_best_object()

        if best_object is not None:
            if best_object.coords == self.arm.gripper.coords:
                # The best object is pickable now
                action = Action.PICK
            elif (
                best_object.coords.col - self.arm.base.coords.col
                == best_object.coords.row - self.arm.gripper.coords.row
            ):
                # The best object will be pickable if a downward movement starts now
                action = Action.DOWN
            elif (
                best_object.coords.col - self.arm.base.coords.col
                == self.arm.gripper.coords.row - best_object.coords.row
            ):
                # The best object will be pickable if an upward movement starts now
                action = Action.UP

        return action

    def _choose_best_object(self) -> Object | None:
        """Return the best object to aim for (the most rewarding of the objects reachable in the future)"""

        reachable_objects: list[Object] = []

        # Exclude objects impossible to pick because they are already too close to the arm column
        reachable_objects = [
            obj
            for obj in self.board.objects
            if (obj.coords.col - self.arm.gripper.coords.col)
            >= abs(obj.coords.row - self.arm.gripper.coords.row)
        ]

        if len(reachable_objects) > 0:
            # Sort reachable objects by descending reward
            reachable_objects.sort(
                key=lambda o: o.get_reward(rewards=self.rewards), reverse=True
            )

            # Return the reachable object with the highest reware
            return reachable_objects[0]

        # No reachable object
        return None
