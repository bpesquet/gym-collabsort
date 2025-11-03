"""
Gym environment for a collaborative sorting task.
"""

from enum import StrEnum
from typing import Any

import gymnasium as gym
import numpy as np
import pygame

from ..action import Action
from ..board.board import Board
from ..board.object import Color, Object, Shape
from ..config import Config
from .robot import Robot, get_color_priorities, get_shape_priorities


class RenderMode(StrEnum):
    """Possible render modes for the environment"""

    HUMAN = "human"
    RGB_ARRAY = "rgb_array"
    NONE = "None"


class CollabSortEnv(gym.Env):
    """Gym environment implementing a collaborative sorting task"""

    # Supported render modes
    metadata = {"render_modes": [rm.value for rm in RenderMode]}

    def __init__(
        self,
        render_mode: RenderMode = RenderMode.NONE,
        config: Config | None = None,
    ) -> None:
        """Initialize the environment"""

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        if config is None:
            # Use default configuration values
            config = Config()

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

        # Create board
        self.board = Board(rng=self.np_random, config=self.config)

        # Create robot
        self.robot = Robot(
            board=self.board,
            arm=self.board.robot_arm,
            color_priorities=get_color_priorities(config.robot_color_rewards),
            shape_priorities=get_shape_priorities(config.robot_shape_rewards),
        )

        # Define action format
        self.action_space = gym.spaces.Discrete(len(Action))

        # Define observation format. See _get_obs() method for details
        self.observation_space = gym.spaces.Dict(
            {
                "self": self._get_coords_space(),
                "objects": gym.spaces.Sequence(
                    gym.spaces.Dict(
                        {
                            "coords": self._get_coords_space(),
                            # max_length is the maximum number of characters in a color
                            "color": gym.spaces.Text(max_length=10),
                            "shape": gym.spaces.Discrete(n=len(Shape)),
                        }
                    )
                ),
                "robot": self._get_coords_space(),
            }
        )

    def _get_coords_space(self) -> gym.spaces.Space:
        """Helper method to create a Box space for the 2D coordinates (row, col) of a board element"""

        return gym.spaces.Box(
            # Coordonates are 1-based
            low=np.array([1, 1]),
            # Maximum values are bounded by board dimensions
            high=np.array(
                [
                    self.config.n_rows,
                    self.config.n_cols,
                ]
            ),
            dtype=int,
        )

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict, dict]:
        # Init the RNG
        super().reset(seed=seed, options=options)

        self.board.add_object()

        if self.render_mode == RenderMode.HUMAN:
            self._render_frame()

        return (self._get_obs(), self._get_info())

    def _get_obs(self) -> dict:
        """
        Return an observation given to the agent.

        An observation is a dictionary containing:
        - the coordinates of agent arm gripper
        - the properties of all objects
        - the coordinates of robot arm gripper
        """

        objects = tuple(
            self._get_object_props(object=obj) for obj in self.board.objects
        )

        return {
            "self": self.board.agent_arm.gripper.coords.as_vector(),
            "objects": objects,
            "robot": self.board.robot_arm.gripper.coords.as_vector(),
        }

    def _get_info(self) -> dict:
        """Return additional information given to the agent"""

        # No additional info
        return {}

    def _get_object_props(self, object: Object) -> dict:
        """Return properties for a specific object"""

        return {
            "coords": object.coords.as_vector(),
            "color": object.color,
            "shape": object.shape.value,
        }

    def step(self, action: Action) -> tuple[dict, float, bool, bool, dict]:
        # Init reward with a small time penalty
        reward: float = self.config.reward__time_penalty

        self.board.animate()

        # Handle robot action
        _, placed_object = self.board.robot_arm.act(
            action=self.robot.choose_action(),
            objects=self.board.objects,
            other_arm=self.board.agent_arm,
        )
        if placed_object is not None:
            self._move_to_scorebar(object=placed_object, is_agent=False)

            # Compute robot reward
            reward += self._compute_reward(
                object=placed_object,
                color_rewards=self.config.robot_color_rewards,
                shape_rewards=self.config.robot_shape_rewards,
            )

        # Handle agent action
        _, placed_object = self.board.agent_arm.act(
            action=action, objects=self.board.objects, other_arm=self.board.robot_arm
        )
        if placed_object is not None:
            self._move_to_scorebar(object=placed_object, is_agent=True)

            # Compute agent reward
            reward += self._compute_reward(
                object=placed_object,
                color_rewards=self.config.agent_color_rewards,
                shape_rewards=self.config.agent_shape_rewards,
            )

        observation = self._get_obs()
        info = self._get_info()

        # Episode is terminated when all objects have been picked up
        terminated = (
            len(self.board.objects) == 0
            and self.board.agent_arm.picked_object is None
            and self.board.robot_arm.picked_object is None
        )

        if self.render_mode == RenderMode.HUMAN:
            self._render_frame()

        return observation, reward, terminated, False, info

    def _move_to_scorebar(self, object: Object, is_agent=True) -> None:
        """Move a placed object to the agent or robot score bar"""

        if is_agent:
            placed_objects = self.board.agent_placed_objects
            # Agent score bar is located below the board
            y_placed_object = (
                self.board.agent_arm.base.location_abs[1] + self.config.scorebar_height
            )
        else:
            placed_objects = self.board.robot_placed_objects
            # Robot score bar is located above the board
            y_placed_object = (
                self.board.robot_arm.base.location_abs[1] - self.config.scorebar_height
            )
        x_placed_object = (
            len(placed_objects)
            * (self.config.board_cell_size + self.config.scorebar_margin)
            + self.config.board_cell_size // 2
            + self.config.scorebar_margin
        )

        # Move placed object to appropriate score bar
        object.location_abs = (x_placed_object, y_placed_object)

        # Update objects lists
        placed_objects.add(object)

    def _compute_reward(
        self,
        object: Object,
        color_rewards: dict[Color, float],
        shape_rewards: dict[Shape, float],
    ) -> float:
        """Compute the reward for a placed object"""

        return color_rewards[object.color] + shape_rewards[object.shape]

    def render(self) -> np.ndarray | None:
        if self.render_mode == RenderMode.RGB_ARRAY:
            return self._render_frame()

    def _render_frame(self) -> np.ndarray | None:
        if self.window is None and self.render_mode == RenderMode.HUMAN:
            # Init pygame display
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(size=self.config.window_dimensions)
            pygame.display.set_caption(self.config.window_title)

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
        if self.window:
            pygame.display.quit()
            pygame.quit()
            pygame.quit()
