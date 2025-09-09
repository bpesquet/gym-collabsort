"""
Gym environment for a collaborative sorting task.
"""

from enum import Enum, StrEnum
from typing import Any

import gymnasium as gym
import numpy as np

from gym_collabsort.config import Config
from gym_collabsort.grid import Grid
from gym_collabsort.object import Object, Shape


class Action(Enum):
    """Possible actions for an agent"""

    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3


class RenderMode(StrEnum):
    """Possible render modes for the environment"""

    HUMAN = "human"
    RGB_ARRAY = "rgb_array"
    NONE = "None"


class CollabSortEnv(gym.Env):
    """Gym multiagent environment implementing a collaborative sorting task"""

    def __init__(
        self,
        render_mode: RenderMode = RenderMode.NONE,
        n_agents: int = 2,
        config: Config | None = None,
    ):
        """Initialize the environment"""

        if config is None:
            # Use default configuration values
            config = Config()

        self.render_mode = render_mode
        self.n_agents = n_agents
        self.config = config

        self.grid = Grid(config=config)

        # Define possible actions for the agent
        self.action_space = gym.spaces.Discrete(n=len(Action))

        # Define observation format. See _get_obs() method for details
        self.observation_space = gym.spaces.Dict(
            {
                "self_location": self._create_location_space(),
                "objects": gym.spaces.Tuple(
                    tuple(
                        gym.spaces.Dict(
                            {
                                "location": self._create_location_space(),
                                # max_length is the maximum number of characters in a color
                                "color": gym.spaces.Text(max_length=10),
                                "shape": gym.spaces.Discrete(n=len(Shape)),
                            }
                        )
                        for _ in range(self.config.n_objects)
                    )
                ),
            }
        )

    def _create_location_space(self) -> gym.spaces.Space:
        """Helper method to create a Box space for the location of an element as (row,col) coordinates"""

        return gym.spaces.Box(
            low=np.array([0, 0]),
            # Maximum values are bounded by grid dimensions
            high=np.array(
                [
                    self.config.n_rows - 1,
                    self.config.n_cols - 1,
                ]
            ),
            dtype=int,
        )

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict, dict]:
        # Init the RNG
        super().reset(seed=seed, options=options)

        self.grid.populate(rng=self.np_random)

        return (self._get_obs(), {})

    def _get_obs(self) -> dict:
        """Return an observation given to the agent"""

        # An observation is a dictionary containing:
        # - the agent location
        # - properties for all objects
        objects = [self._get_object_props(object=obj) for obj in self.grid.objects]
        return {
            "self_location": self.grid.agent.sprite.location.as_array(),
            "objects": objects,
        }

    def _get_object_props(self, object: Object) -> dict:
        """Return properties for a aspecific object"""

        return {
            "location": object.location.as_array(),
            "color": object.color,
            "shape": object.shape,
        }
