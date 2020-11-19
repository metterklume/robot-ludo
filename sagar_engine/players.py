import os
from state import getmoves
from match import judge
from .ludoenv import LudoEnv
from .model import TDLudo
from .agents import TDAgent
from .ludo_utils import getBestMove
from copy import deepcopy

script_path = os.path.abspath(__file__)
script_dir = os.path.split(script_path)[0]


def myPlayer1(board, turn, roll):
    return getBestMove(board,
                       getmoves(board, turn, roll),
                       newCtrScr=board.length,
                       cutScrMult=board.length,
                       homeRunScr=board.length + 0.75,
                       normalMoveScr=1 / board.length,
                       defenseScr=1)


def myPlayer2(board, turn, roll):
    return getBestMove(board,
                       getmoves(board, turn, roll),
                       newCtrScr=board.length * 3,
                       cutScrMult=board.length,
                       homeRunScr=board.length + 0.75,
                       normalMoveScr=1 / board.length,
                       defenseScr=1)


class TDPlayer:
    def __init__(self, counters=12, length=36, safe_squares=(9, 27), color=0, starting=0,
                 agent_loc=f'{script_dir}/model_len36_65k.tar'):
        self.net = TDLudo(hidden_units=40, input_units=123, lr=0.1, lamda=None, init_weights=False)
        self.env = LudoEnv(counters=counters, length=length, safe_squares=safe_squares,
                           starting=starting)
        self.net.load(checkpoint_path=agent_loc, optimizer=None, eligibility_traces=False)
        self.agent = TDAgent(color, net=self.net)

    def make_a_move(self, board, turn, roll):
        self.env.board = board.__copy__()
        self.env.turn = deepcopy(turn)
        self.env.updateState()
        actions = self.env.get_valid_actions(turn, roll)
        action = self.agent.choose_best_action(actions, self.env)
        return action


if __name__ == "__main__":
    td_player_red = TDPlayer(color=0)
    td_player_blue = TDPlayer(color=1)
    print(judge(12, 36, (9, 27), td_player_red.make_a_move, td_player_blue.make_a_move, games=10))
    # match(10, 20, (5, 15), myPlayer1, myPlayer2, maxiters=1000, starting=0, seed=2, verbose=True)
