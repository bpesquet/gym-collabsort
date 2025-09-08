"""
Gym environment for a collaborative sorting task.
"""

from enum import Enum, StrEnum
from typing import Any

import gymnasium as gym
import numpy as np

from gym_collabsort.config import Config
from gym_collabsort.grid2 import Grid


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

        # Each agent has the same possible actions, defined as discrete values
        self.action_space = gym.spaces.Tuple(
            (gym.spaces.Discrete(len(Action)) for _ in range(self.n_agents))
        )

        # Each agent receives a dictionary containing:
        # - its location as (row,col) coordinates
        # - the location of every pickable object as (row,col) coordinates
        self.observation_space = gym.spaces.Tuple(
            (
                gym.spaces.Dict(
                    {
                        "agent": self._create_location_space(),
                        "objects": gym.spaces.Tuple(
                            tuple(
                                self._create_location_space()
                                for _ in range(self.config.n_objects)
                            )
                        ),
                    }
                )
                for _ in range(self.n_agents)
            )
        )

    def _create_location_space(self):
        """Helper method to create a Box space for the location of an element as (row,col) coordinates"""

        return gym.spaces.Box(
            low=np.array([0, 0]),
            # Maximum values are bounded by the dimensions of the grid
            high=np.array(
                [
                    self.config.n_rows - 1,
                    self.config.n_cols - 1,
                ]
            ),
            dtype=int,
        )

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        # Init the RNG
        super().reset(seed=seed, options=options)

        self.grid.reset(rng=self.np_random)

    def _get_obs(self) -> list:
        """Return a list of observations, one for each agent"""

        observations = []
        return observations
