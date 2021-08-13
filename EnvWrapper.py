from typing import List, Tuple

import gym
from gym import spaces
import numpy as np

from GridWorld import GridWorld


class GridWorldEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, size=6, holes=1, walls=1, use_random=True, rand_seed=42):
        self.g = GridWorld(size=size, holes=holes, walls=walls,
                           use_random=use_random, rand_seed=rand_seed)
        self.action_space = spaces.MultiBinary(4)

    def step(self, action: List[int]) -> Tuple[np.ndarray, int, bool, dict]:
        # action [up, down, left, right]
        rew, done = self.g.move_player(action)
        obs = self.g.get_state()
        info = {}
        return obs, rew, done, info

    def reset(self) -> np.ndarray:
        return self.g.reset()

    def render(self, mode='human') -> None:
        print(self.g.render())

    def close(self) -> None:
        pass


def create_world():
    env = GridWorldEnv(size=6, holes=1, walls=1, use_random=False, rand_seed=11)
    obs = env.reset()
    env.render()

    cur_step = 0
    max_steps = 100
    done = False
    while not done and cur_step < max_steps:
        cur_step += 1
        obs, rew, done, info = env.step(env.action_space.sample())
        # print(rew, done)
    print(f"Done in {cur_step}")


if __name__ == '__main__':
    create_world()
