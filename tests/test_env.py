"""
Unit tests for environment.
"""

from gym_collabsort.envs.collabsort import CollabSortEnv, RenderMode


def test_reset() -> None:
    env = CollabSortEnv()

    _, info = env.reset()
    assert info == {}


def test_render_human() -> None:
    """Test environment rendering for humans"""

    env = CollabSortEnv(render_mode=RenderMode.HUMAN)
    env.reset()

    ep_over = False
    ep_reward = 0
    while not ep_over:
        _, reward, terminated, truncated, _ = env.step(env.action_space.sample())

        ep_reward += reward
        ep_over = terminated or truncated

    env.close()
    print(f"Episode over, reward={ep_reward:.02f}")


def test_render_rgb() -> None:
    """Test environment rendering as rgb frame"""

    env = CollabSortEnv(render_mode=RenderMode.RGB_ARRAY)
    env.reset()

    env.step(env.action_space.sample())
    frame = env.render()
    assert frame.ndim == 3
