"""
Package definition file.
"""

from gymnasium.envs.registration import register

# Register the environment with Gymnasium
register(id="CollabSort-v0", entry_point="gym_collabsort.envs.env:CollabSortEnv")
