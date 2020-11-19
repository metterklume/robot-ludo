from state import getmoves, makemove
from match import make_start_board
import numpy as np
from copy import deepcopy


class LudoEnv:
    def __init__(self, counters=12, length=36, safe_squares=[9, 27], starting=0):
        self.counters = counters
        self.length = length
        self.safe_squares = safe_squares
        self.board = make_start_board(self.counters, self.length, self.safe_squares)
        self.board_copy = self.board.__copy__()
        self.state = []
        self.turn = starting
        self.turn_copy = starting

    def updateState(self):
        self.state = self.board.red + \
                     self.board.blue + \
                     self.board.safe + \
                     [int(i) for i in np.binary_repr(self.board.bluepen, 7)] + \
                     [int(i) for i in np.binary_repr(self.board.redpen, 7)] + \
                     [self.turn]

    def get_valid_actions(self, turn, roll):
        return getmoves(self.board, turn, roll)

    def __copy_state(self):
        self.board_copy = self.board.__copy__()
        self.turn_copy = deepcopy(self.turn)

    def step(self, move):
        reward = None
        self.__copy_state()
        self.board = makemove(self.board, move, copyboard=False)
        self.turn = int(not move[0])

        self.updateState()

        if self.board.redpen == 0 and sum(self.board.red) == 0:
            result = 0
            reward = 1
            done = True
        elif self.board.bluepen == 0 and sum(self.board.blue) == 0:
            result = 1
            reward = 0
            done = True
        else:
            result = None
            done = False

        return self.state, reward, done, result

    def reset(self):
        self.board = make_start_board(self.counters, self.length, self.safe_squares)
        self.updateState()
        self.turn = 0
        return self.turn, self.state

    def restore_last_state(self):
        self.board = self.board_copy.__copy__()
        self.turn = deepcopy(self.turn_copy)
        self.updateState()
