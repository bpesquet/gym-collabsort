"""
Implementation of robot policy.
"""

from ..action import Action
from ..board.arm import Arm
from ..board.board import Board
from ..board.object import Object
from ..config import Color, Shape


def get_color_priorities(color_rewards: dict[Color, float]) -> list[Color]:
    """Return the ordered list of color priorities based on rewards"""

    # Sort colors by descending reward
    return list(
        color
        for color, _ in sorted(
            color_rewards.items(), key=lambda item: item[1], reverse=True
        )
    )


def get_shape_priorities(shape_rewards: dict[Shape, float]) -> list[Shape]:
    """Return the ordered list of shape priorities based on rewards"""

    # Sort shapes by descending reward
    return list(
        shape
        for shape, _ in sorted(
            shape_rewards.items(), key=lambda item: item[1], reverse=True
        )
    )


class Robot:
    def __init__(
        self,
        board: Board,
        arm: Arm,
        color_priorities: tuple[Color],
        shape_priorities: tuple[Shape],
    ) -> None:
        self.board = board
        self.arm = arm
        self.color_priorities = color_priorities
        self.shape_priorities = shape_priorities

        # Location of current target (an object or the arm base)
        self.target_location: tuple[int, int] = None

    def choose_action(self) -> Action:
        """Return the chosen action"""

        action = Action.NONE

        if self.arm.is_retracted():
            # Search for reachable objects compatible with picking priorities
            pickable_objects = self._get_pickable_objects(
                colors=self.color_priorities,
                shapes=self.shape_priorities,
            )
            if len(pickable_objects) > 0:
                # Select the first pickable object as possible target
                target = pickable_objects[0].coords

                if (target.col - self.arm.gripper.coords.col) == abs(
                    target.row - self.arm.gripper.coords.row
                ):
                    # Target is pickable if movement starts now
                    action = (
                        Action.PICK_LOWER
                        if target.row == self.board.config.lower_treadmill_row
                        else Action.PICK_UPPER
                    )

        return action

    def _get_pickable_objects(
        self, colors: tuple[Color], shapes: tuple[Shape]
    ) -> list[Object]:
        """
        Get the ordered list of board objects with listed colors and shapes.

        Desired colors and shapes are given by descending order of priority.
        Selected objects (if any) are returned by descending order or compatibility.
        Color is used as first selection criterion, shape as second.
        """

        shape_compatible_objects: list[Object] = []
        pickable_objects: list[Object] = []

        # Exclude objects impossible to pick because they are already too close to the arm column
        reachable_objects = [
            obj
            for obj in self.board.objects
            if (obj.coords.col - self.arm.gripper.coords.col)
            >= abs(obj.coords.row - self.arm.gripper.coords.row)
        ]

        # Select available objects that are shape-compatible.
        # They are sorted by descending order of shape priority
        for shape in shapes:
            for obj in reachable_objects:
                if obj.shape == shape:
                    shape_compatible_objects.append(obj)

        # Select shape-compatible objects that are also color-compatible.
        # They are sorted by descending order of color priority
        for color in colors:
            for obj in shape_compatible_objects:
                if obj.color == color:
                    pickable_objects.append(obj)

        return pickable_objects
