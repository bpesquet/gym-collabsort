"""
Configuration values.
"""

from dataclasses import dataclass


@dataclass
class Config:
    """Configuratiov class with default values"""

    # Grid shape
    n_rows = 4
    n_cols = 9

    # Size in pixels of a (square) grid cell
    cell_size = 50

    # Background color of the grid
    background_color = "white"

    # Width of seperation lines
    line_width = 1

    # Number of pickable objects on the grid
    n_objects = 10
