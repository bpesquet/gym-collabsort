"""
Unit tests for environment.
"""

from gym_collabsort.envs.collabsort import CollabSortEnv


def test_reset() -> None:
    env = CollabSortEnv()

    obs, info = env.reset()
    print(obs)
    assert info == {}
