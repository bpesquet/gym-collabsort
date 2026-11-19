"""
Unit tests for environment.
"""

from unittest.mock import patch

import gymnasium as gym
import numpy as np
import pygame
import pytest
from gymnasium.utils.env_checker import check_env

import gym_collabsort
from gym_collabsort.board.arm import Arm
from gym_collabsort.board.object import Object
from gym_collabsort.config import Action, Color, Config, RenderMode, Shape
from gym_collabsort.envs.env import CollabSortEnv
from gym_collabsort.envs.robot import Robot


def test_version() -> None:
    """Test environment version"""

    # Check that version string is not empty
    assert gym_collabsort.__version__


def test_check_env() -> None:
    """Test compatibility with Gymnasium API"""

    check_env(CollabSortEnv())


def test_api() -> None:
    """Test environment API"""

    env = CollabSortEnv()
    _, info = env.reset()

    assert info["n_collisions"] == 0
    assert info["n_agent_placed_objects"] == 0
    assert info["n_robot_placed_objects"] == 0
    assert info["n_dropped_objects"] == 0

    # TODO test observation format


def test_render_rgb() -> None:
    """Test RGB rendering"""

    env = CollabSortEnv(config=Config(render_mode=RenderMode.RGB_ARRAY))
    env.reset()

    env.step(action=env.action_space.sample())

    frame = env.render()
    assert frame is not None
    assert frame.ndim == 3
    assert frame.shape[0] == env.config.window_dimensions[1]
    assert frame.shape[1] == env.config.board_width


def test_random_agent() -> None:
    """Test an agent choosing random actions"""

    env = gym.make("CollabSort-v2")
    env.reset()

    for _ in range(60):
        _, _, _, _, _ = env.step(action=env.action_space.sample())

    env.close()


def test_reward_noise_is_applied() -> None:
    """Test that configured reward noise affects the returned reward"""

    config = Config(
        reward_noise_std=1.0,
        render_mode=RenderMode.RGB_ARRAY,
        robot_enabled=False,
    )
    env = CollabSortEnv(config=config)
    env.reset(seed=0)

    rewards = [env.step(action=Action.NONE.value)[1] for _ in range(100)]

    assert np.std(rewards) > 0.5


def test_reward_noise_not_applied_when_zero() -> None:
    """Test that no reward noise is applied when std is 0"""

    config = Config(
        reward_noise_std=0.0,
        render_mode=RenderMode.RGB_ARRAY,
        robot_enabled=False,
    )
    env = CollabSortEnv(config=config)
    env.reset(seed=0)

    rewards = [env.step(action=Action.NONE.value)[1] for _ in range(100)]

    assert np.isclose(np.std(rewards), 0.0)


def test_reward_change_step_switches_matrices() -> None:
    """Test that the agent reward matrix changes after the configured step threshold."""

    agent_rewards_after = np.array(
        [[10.0, 10.0, 10.0], [10.0, 10.0, 10.0], [10.0, 10.0, 10.0]]
    )

    config = Config(
        render_mode=RenderMode.RGB_ARRAY,
        robot_enabled=False,
        enable_reward_change=True,
        reward_change_step=5,
        agent_rewards_after=agent_rewards_after,
    )
    env = CollabSortEnv(config=config)
    env.reset(seed=0)

    assert np.array_equal(env.current_agent_rewards, config.agent_rewards)

    for _ in range(5):
        env.step(action=Action.NONE.value)

    assert env.total_steps == 5
    assert np.array_equal(env.current_agent_rewards, agent_rewards_after)

    env.step(action=Action.NONE.value)
    assert env.total_steps == 6
    assert np.array_equal(env.current_agent_rewards, agent_rewards_after)


def test_reward_change_flip_best() -> None:
    """Test that the "flip_best" reward change negates the most valuable object color."""

    config = Config(
        render_mode=RenderMode.RGB_ARRAY,
        robot_enabled=False,
        enable_reward_change=True,
        reward_change_step=3,
        reward_change_type="flip_best",
    )
    env = CollabSortEnv(config=config)
    env.reset(seed=0)

    for _ in range(2):
        _, _, _, _, info = env.step(action=Action.NONE.value)
    assert not info["reward_changed"]
    assert np.array_equal(env.current_agent_rewards, config.agent_rewards)

    _, _, _, _, info = env.step(action=Action.NONE.value)
    assert info["reward_changed"]

    # Best color (highest row sum) is negated, other colors are unchanged
    rewards_before = config.agent_rewards
    best_color = np.argmax(rewards_before.sum(axis=1))
    rewards_after = env.current_agent_rewards
    for color in range(rewards_before.shape[0]):
        expected = rewards_before[color] * (-1 if color == best_color else 1)
        assert np.array_equal(rewards_after[color], expected)
    assert np.all(rewards_after[best_color] < 0)


def test_reward_change_period_alternates_matrices() -> None:
    """Test that rewards alternate between changed and initial matrices when a period is set."""

    config = Config(
        render_mode=RenderMode.RGB_ARRAY,
        robot_enabled=False,
        enable_reward_change=True,
        reward_change_step=2,
        reward_change_type="flip_best",
        reward_change_period=3,
    )
    env = CollabSortEnv(config=config)
    env.reset(seed=0)

    # total_steps after each step: 1..11
    # Initial until step 2, then changed for 3 steps, initial for 3 steps, and so on
    expected = [False, True, True, True, False, False, False, True, True, True, False]
    observed = []
    for _ in expected:
        _, _, _, _, info = env.step(action=Action.NONE.value)
        observed.append(info["reward_changed"])
        expected_rewards = (
            config.agent_rewards_flipped if observed[-1] else config.agent_rewards
        )
        assert np.array_equal(env.current_agent_rewards, expected_rewards)

    assert observed == expected


def test_reward_changed_info_without_reward_change() -> None:
    """Test that rewards are never reported as changed when reward change is disabled."""

    config = Config(render_mode=RenderMode.RGB_ARRAY, robot_enabled=False)
    env = CollabSortEnv(config=config)
    env.reset(seed=0)

    for _ in range(3):
        _, _, _, _, info = env.step(action=Action.NONE.value)
        assert not info["reward_changed"]


def test_robotic_agent(pause_at_end: bool = False) -> None:
    """Test an agent using the same behavior as the robot, but with specific rewards"""

    config = Config(render_mode=RenderMode.HUMAN, n_objects=10)

    env = CollabSortEnv(config=config)
    env.reset()

    # Use robot policy with agent rewards
    robotic_agent = Robot(
        board=env.board,
        arm=env.board.agent_arm,
        rewards=config.agent_rewards,
    )

    ep_over: bool = False
    while not ep_over:
        _, _, terminated, truncated, _ = env.step(
            action=robotic_agent.choose_action().value
        )
        ep_over = terminated or truncated

    if pause_at_end:
        # Wait for any user input to exit environment
        pygame.event.clear()
        _ = pygame.event.wait()

    env.close()


def test_disabled_robot_env() -> None:
    """Test environment with robot arm disabled"""

    config = Config(robot_enabled=False, render_mode=RenderMode.RGB_ARRAY)
    env = CollabSortEnv(config=config)
    obs, info = env.reset()

    assert info["n_collisions"] == 0
    assert info["n_agent_placed_objects"] == 0
    assert info["n_robot_placed_objects"] == 0
    assert env.robot is None

    # Check observation format
    assert "self" in obs
    assert "robot" in obs
    assert "moving_objects" in obs

    # Robot coordinates should still be returned, corresponding to robot retracted base location [1, 4]
    assert (obs["robot"]["coords"] == [1, 4]).all()

    # Step the environment
    for _ in range(20):
        obs, _, _, _, info = env.step(action=env.action_space.sample())
        # Robot position must remain retracted
        assert (obs["robot"]["coords"] == [1, 4]).all()
        # No collisions should ever occur because the robot arm is not active
        assert info["n_collisions"] == 0

    frame = env.render()
    assert frame is not None
    assert frame.ndim == 3

    env.close()


def test_configurable_treadmills() -> None:
    """Test environment with various treadmill configurations"""

    treadmill_configs = [
        ("upper",),
        ("middle",),
        ("lower",),
        ("upper", "middle"),
        ("upper", "lower"),
        ("middle", "lower"),
        ("upper", "middle", "lower"),
    ]

    for active in treadmill_configs:
        config = Config(
            active_treadmills=active,
            render_mode=RenderMode.RGB_ARRAY,
            n_objects=20,
        )
        env = CollabSortEnv(config=config)
        env.reset()

        # Run enough steps to spawn several objects
        for _ in range(100):
            env.step(action=env.action_space.sample())

        # All spawned objects should be on an active treadmill row
        active_rows = set(config.treadmill_rows)

        held_objects = []
        if env.board.agent_arm.picked_object:
            held_objects.append(env.board.agent_arm.picked_object)
        if env.board.robot_arm.picked_object:
            held_objects.append(env.board.robot_arm.picked_object)

        for obj in env.board.objects:
            if obj in held_objects:
                continue

            assert obj.coords.row in active_rows, (
                f"Object at row {obj.coords.row} not in active rows {active_rows} "
                f"for config active_treadmills={active}"
            )

        env.close()


def test_empty_treadmills_raises() -> None:
    """Test that an empty treadmill configuration raises an error"""

    with pytest.raises((ValueError, AssertionError)):
        config = Config(active_treadmills=())
        env = CollabSortEnv(config=config)
        env.reset()


def _make_collision_env() -> CollabSortEnv:
    """Create an environment with a single object and no automatic object spawning"""

    config = Config(render_mode=RenderMode.RGB_ARRAY, n_objects=1, new_object_proba=0)
    env = CollabSortEnv(config=config)
    env.reset(seed=0)

    return env


def _give_object(env: CollabSortEnv, arm: Arm) -> Object:
    """Add an object to the board and make it picked by the given arm"""

    obj = Object(
        location=arm.gripper.location,
        config=env.config,
        color=Color.RED,
        shape=Shape.SQUARE,
    )
    env.board.objects.add(obj)
    arm._picked_object.add(obj)
    env.board.n_added_objects += 1

    return obj


def _assert_dropped(env: CollabSortEnv, arm: Arm, obj: Object) -> None:
    """Assert that the object picked by the arm was dropped and counted once"""

    assert env.n_collisions == 1
    assert arm.picked_object is None
    assert obj not in env.board.objects
    assert arm.n_dropped_objects == 1
    assert arm.n_placed_objects == 0
    assert env.n_removed_objects == 1
    assert env._get_info()["n_dropped_objects"] == 1


def test_collision_drops_object_of_moving_arm() -> None:
    """Test that an arm colliding while carrying an object drops it, removing it from the board"""

    env = _make_collision_env()
    agent_arm, robot_arm = env.board.agent_arm, env.board.robot_arm

    # Agent gripper on row 6 carrying an object back down to its base, robot gripper just below on row 7
    agent_arm.gripper.move(row_offset=-5)
    robot_arm.gripper.move(row_offset=6)
    obj = _give_object(env=env, arm=agent_arm)

    with patch.object(env.robot, "choose_action", return_value=Action.NONE):
        _, _, terminated, _, info = env.step(action=Action.NONE.value)

        _assert_dropped(env=env, arm=agent_arm, obj=obj)
        # The only object has been removed: episode is over
        assert terminated

        # The dropped object must not be counted again later
        for _ in range(20):
            _, _, _, _, info = env.step(action=Action.NONE.value)
        assert env.n_removed_objects == 1
        assert info["n_fallen_objects"] == 0

    env.close()


def test_collision_drops_object_of_hit_arm() -> None:
    """Test that an arm hit by the other arm drops its object, removing it from the board"""

    env = _make_collision_env()
    agent_arm, robot_arm = env.board.agent_arm, env.board.robot_arm

    # Agent gripper on row 6 carrying an object, robot gripper just above on row 5 and moving down
    agent_arm.gripper.move(row_offset=-5)
    robot_arm.gripper.move(row_offset=4)
    obj = _give_object(env=env, arm=agent_arm)

    with patch.object(env.robot, "choose_action", return_value=Action.DOWN):
        _, _, terminated, _, _ = env.step(action=Action.NONE.value)

    _assert_dropped(env=env, arm=agent_arm, obj=obj)
    assert terminated

    env.close()


def test_collision_prevents_placement() -> None:
    """Test that an object is dropped, not placed, when moving back to the base ends in a collision"""

    env = _make_collision_env()
    agent_arm, robot_arm = env.board.agent_arm, env.board.robot_arm

    # Agent gripper inside the robot base on row 1, robot gripper carrying an object just below on row 2
    agent_arm.gripper.move(row_offset=-10)
    robot_arm.gripper.move(row_offset=1)
    obj = _give_object(env=env, arm=robot_arm)

    env.step(action=Action.NONE.value)

    _assert_dropped(env=env, arm=robot_arm, obj=obj)
    assert len(env.board.robot_scorebar.objects) == 0

    env.close()


def test_config_fields() -> None:
    """Test configuration values that can be overridden or are derived from other ones"""

    config = Config(new_object_proba=0.5, board_cell_size=100)

    assert config.new_object_proba == 0.5
    assert config.arm_gripper_size == 50


EVENT_KEYS = (
    "agent_picked_object_id",
    "agent_picked_object_value",
    "agent_failed_pick",
    "robot_picked_object_id",
    "robot_picked_object_value",
    "robot_failed_pick",
    "collision",
    "agent_placed_object_id",
    "robot_placed_object_id",
    "dropped_object_ids",
    "fallen_object_ids",
)


def test_registration() -> None:
    """Test environment registration and per-step event info"""

    env = gym.make("CollabSort-v2")
    assert isinstance(env.unwrapped, CollabSortEnv)
    assert env.spec is not None and env.spec.id == "CollabSort-v2"
    direct_spec = CollabSortEnv().spec
    assert direct_spec is not None and direct_spec.id == "CollabSort-v2"

    env.reset(seed=0)
    for _ in range(30):
        obs, _, _, _, info = env.step(Action.NONE.value)
    assert all(key in info for key in EVENT_KEYS)
    assert len(obs["moving_objects"]) > 0
    assert all("id" in obj for obj in obs["moving_objects"])

    env.close()


def test_stable_object_ids() -> None:
    """Test that object IDs are unique and stable while objects move"""

    env = CollabSortEnv(
        config=Config(render_mode=RenderMode.RGB_ARRAY, robot_enabled=False)
    )
    obs, _ = env.reset(seed=0)

    seen_cols: dict[int, int] = {}
    for _ in range(100):
        obs, _, _, _, info = env.step(Action.NONE.value)
        ids = [int(obj["id"]) for obj in obs["moving_objects"]]
        assert len(ids) == len(set(ids))
        for obj in obs["moving_objects"]:
            obj_id, col = int(obj["id"]), int(obj["coords"][1])
            if obj_id in seen_cols:
                # Same object, moved one column left
                assert col == seen_cols[obj_id] - 1
            seen_cols[obj_id] = col
        for obj_id in info["fallen_object_ids"]:
            assert obj_id in seen_cols
            assert obj_id not in ids

    assert len(seen_cols) > 1
    env.close()


def test_pick_and_place_events() -> None:
    """Test pick, failed pick and placement events"""

    config = Config(
        render_mode=RenderMode.RGB_ARRAY,
        robot_enabled=False,
        n_objects=1,
        new_object_proba=0,
    )
    env = CollabSortEnv(config=config)
    env.reset(seed=0)
    agent_arm = env.board.agent_arm

    # Nothing under the gripper: failed pick
    _, _, _, _, info = env.step(Action.PICK.value)
    assert info["agent_failed_pick"]
    assert info["agent_picked_object_id"] is None

    # Put an object just above the gripper, then pick it
    agent_arm.gripper.move(row_offset=-1)
    obj = Object(
        location=agent_arm.gripper.location,
        config=env.config,
        color=Color.RED,
        shape=Shape.SQUARE,
        id=42,
    )
    env.board.objects.add(obj)
    env.board.n_added_objects += 1
    _, _, _, _, info = env.step(Action.PICK.value)
    assert not info["agent_failed_pick"]
    assert info["agent_picked_object_id"] == 42
    assert info["agent_picked_object_value"] == obj.get_reward(config.agent_rewards)
    assert info["agent_placed_object_id"] is None

    # Arm moves back to its base and places the object
    _, _, terminated, _, info = env.step(Action.NONE.value)
    assert info["agent_placed_object_id"] == 42
    assert info["agent_picked_object_id"] is None
    assert info["dropped_object_ids"] == ()
    assert terminated

    env.close()


def test_collision_events() -> None:
    """Test collision and dropped object events"""

    config = Config(render_mode=RenderMode.RGB_ARRAY, n_objects=1, new_object_proba=0)
    env = CollabSortEnv(config=config)
    env.reset(seed=0)
    agent_arm, robot_arm = env.board.agent_arm, env.board.robot_arm

    agent_arm.gripper.move(row_offset=-5)
    robot_arm.gripper.move(row_offset=6)
    obj = _give_object(env=env, arm=agent_arm)
    obj.id = 7

    with patch.object(env.robot, "choose_action", return_value=Action.NONE):
        _, _, _, _, info = env.step(Action.NONE.value)
    assert info["collision"]
    assert info["dropped_object_ids"] == (7,)
    assert info["agent_placed_object_id"] is None

    env.close()


if __name__ == "__main__":
    # Standalone execution with pause at end
    test_robotic_agent(pause_at_end=True)
