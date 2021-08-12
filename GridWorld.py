import random
from typing import Tuple, Set, List, Optional

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
        self.reset()

    def reset(self):
        self.add_walls(self.walls)
        self.add_holes(self.holes)
        self.add_goal()
        self.set_player()
        return self.get_state()

    def _filled_pos(self, include_player: bool = False) -> Set[Tuple[int, int]]:
        filled = set()
        if include_player and self.pieces['Player']:
            filled.add(self.pieces['Player'])
        for w in self.pieces['Walls']:
            filled.add(w)
        for h in self.pieces['Holes']:
            filled.add(h)
        return filled

    def _is_empty(self, pos: Tuple[int, int]) -> bool:
        return pos not in self._filled_pos(include_player=True)

    def _get_pos(self) -> Tuple[int, int]:
        return (
            random.randint(0, self.size - 1),
            random.randint(0, self.size - 1))

    def _get_empty_pos(self) -> Tuple[int, int]:
        attempts = 0
        pos = self._get_pos()
        while attempts <= 100 and not self._is_empty(pos):
            attempts += 1
            pos = self._get_pos()
        if attempts > 100:
            raise Exception('Too many attempts looking for empty position')
        return pos

    def set_player(self, pos: Optional[Tuple[int, int]] = None) -> None:
        if not pos:
            pos = self._get_empty_pos()
        self.pieces['Player'] = pos

    def add_goal(self) -> None:
        pos = self._get_empty_pos()
        self.pieces['Goal'] = pos

    def add_walls(self, count: int) -> None:
        for _ in range(count):
            pos = self._get_empty_pos()
            self.pieces['Walls'].append(pos)

    def add_holes(self, count: int) -> None:
        for _ in range(count):
            pos = self._get_empty_pos()
            self.pieces['Holes'].append(pos)

    def to_array(self) -> np.ndarray:
        a = np.zeros((self.size, self.size))

        a[self.pieces['Player']] = 1
        a[self.pieces['Goal']] = 4
        for w in self.pieces['Walls']:
            a[w] = 2
        for w in self.pieces['Holes']:
            a[w] = 3
        return a

    def render(self, raw=False) -> str:
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
        y, x = pos
        return not (0 <= y < self.size) or not (0 <= x < self.size)

    def move_player(self, action: List) -> int:
        # [up, down, left, right]
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
        if self._pos_out_of_bounds(new_pos):
            return 0
        self.set_player(new_pos)
        return -1

    def get_state(self) -> np.ndarray:
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
    g = GridWorld(size=6, holes=1, walls=1, use_random=True)
    print(g.render())
    g.move_player([1, 0, 0, 0])
    print(g.render())
    print(g.get_state())


if __name__ == '__main__':
    create_world()
