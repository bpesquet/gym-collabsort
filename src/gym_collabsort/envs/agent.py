"""
Agent definitions.
"""

from dataclasses import dataclass

from PIL import Image, ImageDraw

from gym_collabsort.typing import Area


@dataclass
class Agent:
    """An agent picking up objects"""

    number: int
    row: int
    col: int

    def draw(self, xy: Area, image: Image) -> Image:
        """Draw the agent as a PIL image"""

        # The agent is drawn as a smaller circle with its number inside
        radius = (xy[1][0] - xy[0][0]) / 3
        offset = (xy[1][0] - xy[0][0]) / 2
        center = (xy[0][0] + offset, xy[0][1] + offset)
        ImageDraw.Draw(image).circle(xy=center, radius=radius, fill="black")
