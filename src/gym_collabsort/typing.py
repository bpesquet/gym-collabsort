"""
Type definitions.
"""

from typing import TypeAlias

# A rectangular area of the screen.
# First tuple is the cartesian coordinates of the upper left corner point.
# Second tuple is the cartesian coordinates of the bottom right corner point
Area: TypeAlias = tuple[tuple[int, int], tuple[int, int]]
