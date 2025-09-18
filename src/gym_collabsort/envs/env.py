"""
Gym environment for a collaborative sorting task.
"""

from enum import Enum, StrEnum
from typing import Any

import gymnasium as gym
import numpy as np
import pygame

from gym_collabsort.board import Board, Object, Shape
from gym_collabsort.config import Config


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
        config: Config | None = None,
    ):
        """Initialize the environment"""

        if config is None:
            # Use default configuration values
            config = Config()

        self.render_mode = render_mode
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

        self.board = Board(config=self.config)

        # Define action format
        self.action_space = gym.spaces.Dict(
            {
                "action": gym.spaces.Discrete(n=len(Action)),
                "target_coords": self._get_coords_space(),
            }
        )

        # Define observation format. See _get_obs() method for details
        self.observation_space = gym.spaces.Dict(
            {
                "coords": self._get_coords_space(),
                "objects": gym.spaces.Tuple(
                    tuple(
                        gym.spaces.Dict(
                            {
                                "coords": self._get_coords_space(),
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

    def _get_coords_space(self) -> gym.spaces.Space:
        """Helper method to create a Box space for the coordinates of a board element"""

        return gym.spaces.Box(
            low=np.array([0, 0]),
            # Maximum values are bounded by board dimensions
            high=np.array(
                [
                    self.config.board_width,
                    self.config.board_height,
                ]
            ),
            dtype=int,
        )

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict, dict]:
        # Init the RNG
        super().reset(seed=seed, options=options)

        self.board.populate(rng=self.np_random)

        if self.render_mode == RenderMode.HUMAN:
            self._render_frame()

        return (self._get_obs(), {})

    def _get_obs(self) -> dict:
        """Return an observation given to the agent"""

        # An observation is a dictionary containing:
        # - the coordinates of agent arm claw
        # - properties for all objects
        objects = [self._get_object_props(object=obj) for obj in self.board.objects]
        return {
            "coords": None,  # TODO
            "objects": objects,
        }

    def _get_object_props(self, object: Object) -> dict:
        """Return properties for a aspecific object"""

        return {
            "coords": object.coords,
            "color": object.color,
            "shape": object.shape,
        }

    def step(self, action: dict) -> tuple[dict, int, bool, bool, dict]:
        if action["action"] == Action.AIM.value:
            pass
        elif action == Action.EXTEND.value:
            pass

        reward = 0

        observation = self._get_obs()

        # Episode is terminated when all objects have been picked up
        terminated = len(self.board.objects) == 0

        if self.render_mode == RenderMode.HUMAN:
            self._render_frame()

        return observation, reward, terminated, False, {}

    def render(self) -> np.ndarray | None:
        if self.render_mode == RenderMode.RGB_ARRAY:
            return self._render_frame()

    def _render_frame(self) -> np.ndarray | None:
        if self.window is None and self.render_mode == RenderMode.HUMAN:
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(size=self.config.window_size)

        if self.clock is None and self.render_mode == RenderMode.HUMAN:
            self.clock = pygame.time.Clock()

        canvas = self.board.draw()

        if self.render_mode == RenderMode.HUMAN:
            # The following line copies our drawings from canvas to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.config.render_fps)

        else:  # rgb_array
            return self.board.get_frame()

    def close(self) -> None:
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            pygame.quit()
