"""
Unit tests for environment.
"""

import gymnasium as gym
import pygame

from gym_collabsort.envs.env import CollabSortEnv, RenderMode
from gym_collabsort.envs.robot import Robot, get_color_priorities, get_shape_priorities


def test_registration() -> None:
    """Test registering the environment through Gymnasium"""

    env = gym.make("CollabSort-v0")
    assert env is not None


def test_reset() -> None:
    env = CollabSortEnv()

    _, info = env.reset()
    assert info == {}


def test_render_rgb() -> None:
    env = CollabSortEnv(render_mode=RenderMode.RGB_ARRAY)
    env.reset()

    env.step(action=env.action_space.sample())

    frame = env.render()
    assert frame.ndim == 3
    assert frame.shape[0] == env.config.window_dimensions[1]
    assert frame.shape[1] == env.config.board_width


def test_random_agent() -> None:
    """Test an agent using random actions"""

    env = CollabSortEnv(render_mode=RenderMode.NONE)
    env.reset()

    for _ in range(60):
        _, _, _, _, _ = env.step(action=env.action_space.sample())

    env.close()


def test_robotic_agent(pause_at_end: bool = False) -> None:
    """Test an agent using the same behavior as the robot, but with specific rewards"""

    env = CollabSortEnv(render_mode=RenderMode.HUMAN)
    env.reset()

    # Use robot policy with agent rewards
    robotic_agent = Robot(
        board=env.board,
        arm=env.board.agent_arm,
        color_priorities=get_color_priorities(env.config.agent_color_rewards),
        shape_priorities=get_shape_priorities(env.config.agent_shape_rewards),
    )

    ep_over: bool = False
    while not ep_over:
        _, _, terminated, trucanted, _ = env.step(action=robotic_agent.choose_action())
        ep_over = terminated or trucanted

    if pause_at_end:
        # Wait for any user input to exit enrironment
        pygame.event.clear()
        _ = pygame.event.wait()

    env.close()


if __name__ == "__main__":
    # Standalone execution with pause at end
    test_robotic_agent(pause_at_end=True)
