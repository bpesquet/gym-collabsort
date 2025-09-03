"""
The 2D grid containing objects and agents.
"""

from .config import Config
from .elements import Location, Object


class Grid:
    """The 2D grid containing objects and agents"""

    def __init__(self, rng, config: Config | None = None):
        if config is None:
            # Use default configuration values
            config = Config()

        self.config = config
        self.rng = rng
        self.objects: list[Object] = []

    def reset(self) -> None:
        """Reset the grid"""

        self.objects = []
        self._add_objects()

    def _add_objects(self) -> None:
        """Add objects to the grid"""

        # Put each object in an available location
        remaining_objects = self.config.n_objects
        while remaining_objects > 0:
            location = Location(
                row=self.rng.integers(low=0, high=self.config.n_rows - 1),
                col=self.rng.integers(low=0, high=self.config.n_cols - 1),
            )
            if self._is_location_available(location=location):
                self.objects.append(Object(location=location, config=self.config))
                remaining_objects -= 1

    def _is_location_available(self, location: Location) -> bool:
        """Check if a grid location is available or already taken by an element"""

        for obj in self.objects:
            if obj.location == location:
                return False
        return True

    def __str__(self):
        n_objects: int = len(self.objects)
        grid_str: str = f"n_objects={n_objects} "

        if n_objects > 0:
            grid_str += "\n["
            grid_str += " ".join(map(str, self.objects))
            grid_str += "]"

        return grid_str
