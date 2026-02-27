"""
Package definition file.
"""

import importlib.metadata

from gymnasium.envs.registration import register

# Register the environment with Gymnasium
register(
    id="CollabSort-v0",
    entry_point="gym_collabsort.envs.env:CollabSortEnv",
    # Since env.reset() doesn't clear the board, this env is non-deterministic:
    # an observation cannot be repeated with the same initial state, random number generator state and actions
    nondeterministic=True,
)


# Make the version accessible within the package
try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"  # Fallback for development mode
