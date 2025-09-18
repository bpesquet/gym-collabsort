"""
Unit tests for environment.
"""

from gym_collabsort.envs.env import CollabSortEnv, RenderMode


def test_reset() -> None:
    env = CollabSortEnv()

    _, info = env.reset()
    assert info == {}


def test_random_actions() -> None:
    env = CollabSortEnv(render_mode=RenderMode.HUMAN)
    env.reset()

    ep_reward = 0
    for _ in range(50):
        _, reward, _, _, _ = env.step(env.action_space.sample())

        ep_reward += reward

    env.close()
    print(f"Episode over, reward={ep_reward:.02f}")


def test_render_rgb() -> None:
    env = CollabSortEnv(render_mode=RenderMode.RGB_ARRAY)
    env.reset()

    env.step(env.action_space.sample())

    frame = env.render()
    assert frame.ndim == 3
    assert frame.shape[0] == env.config.board_width
    assert frame.shape[1] == env.config.board_height
