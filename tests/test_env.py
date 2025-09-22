"""
Unit tests for environment.
"""

from gym_collabsort.envs.env import CollabSortEnv, RenderMode
from gym_collabsort.envs.robot import Robot


def test_reset() -> None:
    env = CollabSortEnv()

    _, info = env.reset()
    assert info == {}


def test_robot_vs_robot() -> None:
    env = CollabSortEnv(render_mode=RenderMode.HUMAN)
    env.reset()

    agent = Robot(arm=env.board.agent_arm, config=env.config)

    ep_over: bool = False
    ep_reward = 0
    while not ep_over:
        _, ep_reward, terminated, trucanted, _ = env.step(
            action=agent.choose_action(board=env.board)
        )
        ep_over = terminated or trucanted


def test_render_rgb() -> None:
    env = CollabSortEnv(render_mode=RenderMode.RGB_ARRAY)
    env.reset()

    env.step(env.action_space.sample())

    frame = env.render()
    assert frame.ndim == 3
    assert frame.shape[0] == env.config.board_height
    assert frame.shape[1] == env.config.board_width
