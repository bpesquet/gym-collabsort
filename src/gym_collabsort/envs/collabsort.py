"""
Gym environment for a collaborative sorting task.
"""

from enum import Enum, StrEnum
from typing import Any

import gymnasium as gym
import numpy as np
import pygame

from gym_collabsort.cell import Object, Shape
from gym_collabsort.config import Config
from gym_collabsort.grid import Grid


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

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

        self.grid = Grid(config=config)

        """
        The following dictionary maps abstract actions from `self.action_space` to
        the direction we will walk in if that action is taken.
        i.e. 0 corresponds to "right", 1 to "up" etc.
        """
        self._action_to_direction = {
            Action.RIGHT.value: (1, 0),
            Action.UP.value: (0, 1),
            Action.LEFT.value: (-1, 0),
            Action.DOWN.value: (0, -1),
        }

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

        if self.render_mode == RenderMode.HUMAN:
            self._render_frame()

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

    def step(self, action) -> tuple[dict, int, bool, bool, dict]:
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        direction = self._action_to_direction[action]
        # Update agent location
        self.grid.agent.sprite.location.add(
            direction=direction, clip=(self.config.n_rows - 1, self.config.n_cols - 1)
        )

        observation = self._get_obs()

        if self.render_mode == RenderMode.HUMAN:
            self._render_frame()

        return observation, 0, False, False, {}

    def render(self) -> np.ndarray | None:
        if self.render_mode == RenderMode.RGB_ARRAY:
            return self._render_frame()

    def _render_frame(self) -> np.ndarray | None:
        if self.window is None and self.render_mode == RenderMode.HUMAN:
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(size=self.grid.window_size)

        if self.clock is None and self.render_mode == RenderMode.HUMAN:
            self.clock = pygame.time.Clock()

        canvas = self.grid.draw()

        if self.render_mode == RenderMode.HUMAN:
            # The following line copies our drawings from canvas to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.config.render_fps)

        else:  # rgb_array
            return self.grid.get_frame()

    def close(self) -> None:
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
