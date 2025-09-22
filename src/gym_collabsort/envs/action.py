from enum import Enum


class Action(Enum):
    """Possible actions for an agent"""

    # Do nothing
    WAIT = 0
    # Move arm
    MOVE = 1
