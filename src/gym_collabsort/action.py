"""
Action-related definitions.
"""

from enum import Enum


class Action(Enum):
    """Possible actions for agent and robot"""

    NONE = 0
    PICK_UPPER = 1
    PICK_LOWER = 2
