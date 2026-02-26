"""
Score bar definitions.
"""

import pygame.freetype as freetype
from pygame import Surface
from pygame.sprite import Group

from ..config import Color, Config
from .object import Object


class ScoreBar:
    """A score bar displaying the list of placed objects for an arm"""

    def __init__(self, config: Config, y_object: int) -> None:
        self.config = config

        # Absolute y-coordinate of placed objects on this score bar
        self.y_object = y_object

        # Create an empty group containing placed objects
        self.objects: Group[Object] = Group()

        # Number of identical objects. Order matches the one of objects group
        self.n_identical_objects: list[int] = []

    def reset(self) -> None:
        """Reset the score bar"""

        # Reset lists
        self.objects.empty()
        self.n_identical_objects.clear()

    def add(self, placed_object: Object) -> None:
        """Add a placed object"""

        # Look for an already placed object with same properties as the new one
        same_obj_idx = -1
        for idx, obj in enumerate(self.objects):
            if obj.color == placed_object.color and obj.shape == placed_object.shape:
                # Same object found: stop search
                same_obj_idx = idx
                break

        if same_obj_idx >= 0:
            # An object with identical properties was found.
            # Increment the number of identical objects
            self.n_identical_objects[same_obj_idx] += 1
        else:
            # No object with same properties was found

            # Move placed object to appropriate location in score bar
            x_object: int = (
                len(self.objects)
                * (self.config.board_cell_size + self.config.scorebar_margin)
                + self.config.board_cell_size // 2
                + self.config.scorebar_margin
            )
            placed_object.location_abs = (x_object, self.y_object)

            # Add the placed object to the group
            self.objects.add(placed_object)
            self.n_identical_objects.append(1)

    def draw(self, surface: Surface) -> None:
        """Draw the score bar to a surface"""

        # Draw objects
        self.objects.draw(surface=surface)

        obj_count_text = freetype.Font(None)
        for idx, obj in enumerate(self.objects):
            obj_count = self.n_identical_objects[idx]

            # Get size and offset of rendered text in order to center it inside the object symbol
            text_rect = obj_count_text.get_rect(
                text=str(obj_count), size=self.config.metric_text_size
            )
            obj_count_text.render_to(
                surface,
                # Adjust text position at the center of the containing object
                dest=(
                    obj.location_abs[0] - text_rect.centerx,
                    obj.location_abs[1] - text_rect.centery // 3,
                ),
                text=str(obj_count),
                # Adapt text color to object for better lisibility
                fgcolor="black" if obj.color == Color.YELLOW else "white",
                size=self.config.metric_text_size,
            )
