"""
Unit tests for environment.
"""

from gym_collabsort.config import Color, Config
from gym_collabsort.envs.collabsort import Action, CollabSortEnv, RenderMode


def test_reset() -> None:
    env = CollabSortEnv()

    _, info = env.reset()
    assert info == {}


def test_robot() -> None:
    # Define a very basic config in order to shorten episode
    config = Config(n_objects=20, object_colors=(Color.BLUE,))

    env = CollabSortEnv(render_mode=RenderMode.HUMAN, config=config)
    env.reset()

    ep_over = False
    ep_reward = 0
    while not ep_over:
        # Agent is never moving, only robot is picking objects
        _, reward, terminated, truncated, _ = env.step(
            action=Action.WAIT.value
        )  # env.action_space.sample())

        ep_reward += reward
        ep_over = terminated or truncated

    env.close()
    print(f"Episode over, reward={ep_reward:.02f}")


def test_render_rgb() -> None:
    env = CollabSortEnv(render_mode=RenderMode.RGB_ARRAY)
    env.reset()

    env.step(env.action_space.sample())
    frame = env.render()
    assert frame.ndim == 3
    assert frame.ndim == 3
    assert frame.ndim == 3
