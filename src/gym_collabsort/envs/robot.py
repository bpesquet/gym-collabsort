"""
Implementation of robot logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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
            return (0, 1)
        else:
            return (0, -1)
