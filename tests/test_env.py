"""
Unit tests for environment.
"""

from gym_collabsort.envs.collabsort import CollabSortEnv


def test_collabsortenv() -> None:
    env = CollabSortEnv()
    env.reset()
