"""
Classic gridworld for RL
"""

from typing import List, Tuple

import gym
from gym import spaces
import numpy as np

from GridWorld import GridWorld


class GridWorldEnv(gym.Env):
    """
    Description:
        A small randomly generated maze.
    Source:
        Classic gridworld
    Observation:
        4 x n x n array
        n is the grid size
        The 4 layers are [Player, Goal, Walls, Holes]
        0 is empty, 1 has piece
    Actions:
        Type: MultiBinary(4)
        [up, down, left, right]
        Note: It takes the first 1 it see's and ignores the other movements
        i.e. [1,0,1,0] would just take up and ignore left.
    Reward:
        -1 for every step (including failed move such as hitting a wall)
        -10 for moving to a hole
        +10 for moving to goal
    Starting State:
        Random
    Episode Termination:
        Player has moved to goal
        TODO: does this need a max steps?
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, size=6, holes=1, walls=1, use_random=True, rand_seed=42):
        self.g = GridWorld(size=size, holes=holes, walls=walls,
                           use_random=use_random, rand_seed=rand_seed)
        self.action_space = spaces.MultiBinary(4)

    def step(self, action: List[int]) -> Tuple[np.ndarray, int, bool, dict]:
        """ Take a single action in the game and return the new state

        :param action: array [up, down, left, right]
        :return: obs, rew, done, info
        """
        rew, done = self.g.move_player(action)
        obs = self.g.get_state()
        info = {}
        return obs, rew, done, info

    def reset(self) -> np.ndarray:
        """ Reset grid
        Reset grid to start positions (or random)

        :return: np.ndarray, game state
        """
        return self.g.reset()

    def render(self, mode='human') -> None:
        """
        Render the grid to the console
        :param mode: Ignore
        :return: None
        """
        print(self.g.render())

    def close(self) -> None:
        """Close environment
        Not needed
        :return: None
        """
        pass


def create_world():
    env = GridWorldEnv(size=6, holes=1, walls=1, use_random=True, rand_seed=11)
    obs = env.reset()
    env.render()

    cur_step = 0
    max_steps = 100
    done = False
    tot_rew = 0
    while not done and cur_step < max_steps:
        cur_step += 1
        obs, rew, done, info = env.step(env.action_space.sample())
        tot_rew += rew
    print(f"Done in {cur_step}")
    print(f"Total Reward {tot_rew}")


if __name__ == '__main__':
    create_world()
