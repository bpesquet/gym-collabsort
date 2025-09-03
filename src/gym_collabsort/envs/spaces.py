"""
Action and observation spaces
"""

from collections.abc import Sequence

import gymnasium as gym
from gymnasium.spaces.space import Space

# ActionSpace: TypeAlias = gym.spaces.Dict[
#     {
#         "agent": gym.spaces.Box(
#             0, size - 1, shape=(2,), dtype=int
#         ),  # [x, y] coordinates
#         "target": gym.spaces.Box(
#             0, size - 1, shape=(2,), dtype=int
#         ),  # [x, y] coordinates
#     }
# ]


class MultiAgentActionSpace(list):
    """Container for a set of action spaces"""

    def __init__(self, action_spaces: Sequence[Space]):
        for action_space in action_spaces:
            assert isinstance(action_space, gym.spaces.space.Space)

        super().__init__(action_spaces)
        self.action_spaces = action_spaces

    def sample(self):
        """Sample an action for each agent"""

        return [action_space.sample() for action_space in self.action_spaces]


class MultiAgentObservationSpace(list):
    """Container for a set of observation spaces"""

    def __init__(self, observation_spaces: Sequence[Space]):
        for observation_space in observation_spaces:
            assert isinstance(observation_space, gym.spaces.space.Space)

        super().__init__(observation_spaces)
        self.observation_spaces = observation_spaces

    def sample(self):
        """Sample an observation for each agent"""

        return [
            observation_space.sample() for observation_space in self.observation_spaces
        ]
