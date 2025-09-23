"""
Unit tests for environment.
"""

from gym_collabsort.envs.env import CollabSortEnv, RenderMode
from gym_collabsort.envs.robot import Robot


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
    assert frame.shape[0] == env.config.board_height
    assert frame.shape[1] == env.config.board_width


def test_random_agent() -> None:
    env = CollabSortEnv(render_mode=RenderMode.NONE)
    env.reset()

    for _ in range(60):
        _, _, _, _, _ = env.step(action=env.action_space.sample())

    env.close()


def test_robot_vs_robot() -> None:
    env = CollabSortEnv(render_mode=RenderMode.HUMAN)
    env.reset()

    # Use robot policy for agent
    robotic_agent = Robot(board=env.board, arm=env.board.agent_arm, config=env.config)

    ep_over: bool = False
    while not ep_over:
        _, _, terminated, trucanted, _ = env.step(action=robotic_agent.choose_action())
        ep_over = terminated or trucanted

    env.close()
