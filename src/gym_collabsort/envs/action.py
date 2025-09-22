from enum import Enum


class Action(Enum):
    """Possible actions for an agent"""

    # Do nothing
    WAIT = 0
    # Aim arm towards specific coordinates
    AIM = 1
    # Extend arm
    EXTEND = 2
    # Retract arm
    RETRACT = 3
