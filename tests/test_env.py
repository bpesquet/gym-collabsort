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

    for _ in range(60):
        env.step(env.action_space.sample())

    env.close()


def test_render_rgb() -> None:
    """Test environment rendering as rgb frame"""

    env = CollabSortEnv(render_mode=RenderMode.RGB_ARRAY)
    env.reset()

    env.step(env.action_space.sample())
    frame = env.render()
    assert frame.ndim == 3
