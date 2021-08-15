"""
Gridworld implementation
"""

import random
from typing import Tuple, Set, List, Optional, Union

import numpy as np

render_map = {
    0: '.',  # Empty
    1: 'P',  # Player
    2: '#',  # Wall
    3: 'O',  # Hole
    4: 'G',  # Goal
}


class GridWorld:

    pieces = {
        'Player': (-1, -1),
        'Goal': (-1, -1),
        'Walls': [],
        'Holes': []
    }

    def __init__(self, size=4, holes=1, walls=1, use_random=False,
                 rand_seed=42) -> None:
        assert (size >= 4), "Size needs to be >= 4"

        if not use_random:
            random.seed(rand_seed)
        self.size = size
        self.walls = walls
        self.holes = holes

    def clear_grid(self):
        """Create an empty grid state"""
        self.pieces = {
            'Player': (-1, -1),
            'Goal': (-1, -1),
            'Walls': [],
            'Holes': []
        }

    def reset(self):
        """ Reset grid
        Reset grid to start positions (or random)
        :return: np.ndarray, game state
        """
        self.clear_grid()
        self.add_walls(self.walls)
        self.add_holes(self.holes)
        self.add_goal()
        self.set_player()
        return self.get_state()

    def _filled_pos(self, include_player: bool = False) -> Set[Tuple[int, int]]:
        """ Get a list of filled positions

        :param include_player: bool, wether to include the player in the check
        :return: Set[Tuple[int, int]], set of filled positions
        """
        filled = set()
        if include_player and self.pieces['Player']:
            filled.add(self.pieces['Player'])
        for w in self.pieces['Walls']:
            filled.add(w)
        for h in self.pieces['Holes']:
            filled.add(h)
        return filled

    def _is_empty(self, pos: Tuple[int, int]) -> bool:
        """ Is a position empty

        :param pos: Tuple[int, int], the position to check
        :return: bool, whether the position is empty
        """
        return pos not in self._filled_pos(include_player=True)

    def _get_pos(self) -> Tuple[int, int]:
        """ Generate a random position
        Does no check on the validity of the position

        :return: Tuple[int, int], new position
        """
        return (
            random.randint(0, self.size - 1),
            random.randint(0, self.size - 1))

    def _get_empty_pos(self) -> Tuple[int, int]:
        """ Find an empty position
        After 10 failed attempts an exception is raised.

        :return: Tuple[int, int], new empty position
        """
        attempts = 0
        pos = self._get_pos()
        while attempts <= 100 and not self._is_empty(pos):
            attempts += 1
            pos = self._get_pos()
        if attempts > 100:
            raise Exception('Too many attempts looking for empty position')
        return pos

    def set_player(self, pos: Optional[Tuple[int, int]] = None) -> None:
        """ Set player position
        If no position is sent a random empty position is used.

        :param pos: Tuple[int, int], Option the position to move the player to
        """
        if not pos:
            pos = self._get_empty_pos()
        self.pieces['Player'] = pos

    def add_goal(self) -> None:
        """ Add goal position
        Uses random empty position
        """
        pos = self._get_empty_pos()
        self.pieces['Goal'] = pos

    def add_walls(self, count: int) -> None:
        """ Add a number of wall positions
        Uses random empty position

        :param: count, number of walls to add
        """
        for _ in range(count):
            pos = self._get_empty_pos()
            self.pieces['Walls'].append(pos)

    def add_holes(self, count: int) -> None:
        """ Add a number of hole positions
        Uses random empty position

        :param: count, number of holes to add
        """
        for _ in range(count):
            pos = self._get_empty_pos()
            self.pieces['Holes'].append(pos)

    def to_array(self) -> np.ndarray:
        """ Return the grid as a numpy array
        n x n grid filled with zeros except-
        Player: 1
        Walls: 2
        Holes: 3
        Goal: 4

        :return: numpy array of grid
        """
        a = np.zeros((self.size, self.size))

        a[self.pieces['Player']] = 1
        a[self.pieces['Goal']] = 4
        for w in self.pieces['Walls']:
            a[w] = 2
        for w in self.pieces['Holes']:
            a[w] = 3
        return a

    def render(self, raw: bool = False) -> Union[np.ndarray, str]:
        """ Output a render of the grid for printing (to console)
        Output is either an ndarray or string
        If string the grid uses the mappings from render_map

        :param: raw, if to output formatted as the raw ndarray
        :return: Either an ndarray of pretty format of grid as string
        """
        a = self.to_array()
        if raw:
            return a

        output = ''
        for row in a:
            row_str = ''
            for column in row:
                row_str += render_map[column]
            row_str += '\n'
            output += row_str
        return output

    def _pos_out_of_bounds(self, pos: Tuple[int, int]) -> bool:
        """  Check if a position is outside the grid

        :param pos: Tuple[int, int] position to check
        :return: bool, whether the position is outside of the grid
        """
        y, x = pos
        return not (0 <= y < self.size) or not (0 <= x < self.size)

    def get_reward(self) -> Tuple[int, bool]:
        """ Get the reward for the current state and if game is over
        -1 for normal/no move (or bounce off wall) (game continues)
        -10 for player in hole (game ends)
        +10 for player at goal (game ends)

        :return: Tuple[int, bool], reward, is end state
        """
        p_pos = self.pieces['Player']
        # Goal
        if p_pos == self.pieces['Goal']:
            return 10, True
        # Hole
        for h in self.pieces['Holes']:
            if p_pos == h:
                return -10, True
        # Other Move
        return -1, False

    def move_player(self, action: List) -> Tuple[int, bool]:
        """ Move the player piece and return [reward, gameover]
        Action is sent as an array of
        [up, down, left, right]
        Only the first seen 1 in the array is used

        :param action: list, move to take
        :return: Tuple[int, bool], reward, is end state
        """
        p_pos = self.pieces['Player']
        y, x = p_pos
        if action[0] == 1:  # up
            y = y - 1
        elif action[1] == 1:  # down
            y = y + 1
        elif action[2] == 1:  # left
            x = x - 1
        elif action[3] == 1:  # right
            x = x + 1
        new_pos = (y, x)
        if not (self._pos_out_of_bounds(new_pos) or self.pos_on_wall(new_pos)):
            # Bounce player back
            self.set_player(new_pos)
        # TODO: player move to hole
        return self.get_reward()

    def pos_on_wall(self, pos: Tuple[int, int]) -> bool:
        """ Is the position on a wall?

        :param pos: position to check
        :return: bool, whether the position is a wall position
        """
        for h in self.pieces['Walls']:
            if pos == h:
                return True
        return False

    def get_state(self) -> np.ndarray:
        """ Get the state of the game as a stacked np array
        Used for representation passed to Neural Network

        4 x n x n layers,
        0s as defaults
        1s where the item of the layer exists

        Layers are stacked [Player, Goal, Walls, Holes]

        :return: np.ndarray, stacked array of layers
        """
        # [Player, Goal, Walls, Holes]
        state = np.zeros((4, self.size, self.size))

        # Player
        y, x = self.pieces['Player']
        state[0, y, x] = 1.0

        # Goal
        y, x = self.pieces['Goal']
        state[1, y, x] = 1.0

        # Walls
        for y, x in self.pieces['Walls']:
            state[2, y, x] = 1.0

        # Holes
        for y, x in self.pieces['Holes']:
            state[3, y, x] = 1.0

        return state


def create_world():
    """ Dev stuff """
    g = GridWorld(size=6, holes=1, walls=1, use_random=False)
    g.reset()
    print(g.render())
    _, _ = g.move_player([1, 0, 0, 0])

    rew, done = g.move_player([0, 1, 0, 0])
    print(g.render())
    print(rew, done)
    print()
    # print(g.get_state())


if __name__ == '__main__':
    create_world()
