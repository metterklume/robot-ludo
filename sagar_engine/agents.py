import random
import time
from itertools import count
from random import randint, choice
from .ludo_utils import getBestMove
import numpy as np

random.seed(0)
RED = 0
BLUE = 1
COLORS = {RED: "Red", BLUE: 'Blue'}


# AGENT ============================================================================================

class Agent:
    def __init__(self, color):
        self.color = color
        self.name = 'Agent({})'.format(COLORS[color])

    def roll_dice(self):
        return randint(1, 6)

    def choose_best_action(self, actions, env):
        raise NotImplementedError


# RANDOM AGENT =======================================================================================

class RandomAgent(Agent):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'RandomAgent({})'.format(COLORS[color])

    def choose_best_action(self, actions, env):
        return choice(list(actions)) if actions else None


# CUSTOM AGENT =======================================================================================

class CustomAgent(Agent):
    def __init__(self, color):
        super().__init__(color)
        self.name = 'HumanAgent({})'.format(COLORS[color])

    def choose_best_action(self, actions=None, env=None):
        return getBestMove(env.board,
                           actions,
                           newCtrScr=env.board.length,
                           cutScrMult=env.board.length,
                           homeRunScr=env.board.length + 0.75,
                           normalMoveScr=1 / env.board.length,
                           defenseScr=1)


class TDAgent(Agent):
    def __init__(self, color, net):
        super().__init__(color)
        self.net = net
        self.name = 'TDAgent({})'.format(COLORS[color])

    def choose_best_action(self, actions, env):
        best_action = None

        if actions:
            values = [0.0] * len(actions)

            # Iterate over all the legal moves and pick the best action
            for i, action in enumerate(actions):
                observation, reward, done, info = env.step(action)
                values[i] = self.net(observation)

                # restore the board and other variables (undo the action)
                env.restore_last_state()

            # practical-issues-in-temporal-difference-learning, pag.3
            # ... the network's output P_t is an estimate of White's probability of winning from board position x_t.
            # ... the move which is selected at each time step is the move which maximizes P_t when White is to play and minimizes P_t when Black is to play.
            best_action_index = int(np.argmax(values)) if self.color == RED else int(np.argmin(values))
            best_action = list(actions)[best_action_index]
            # env.counter = tmp_counter

        return best_action




def evaluate_agents(agents, env, n_episodes):
    wins = {RED: 0, BLUE: 0}

    for episode in range(n_episodes):

        agent_color, observation = env.reset()
        agent = agents[agent_color]

        t = time.time()

        for i in count():

            roll = agent.roll_dice()

            actions = env.get_valid_actions(agent_color, roll)
            action = agent.choose_best_action(actions, env)
            observation_next, reward, done, winner = env.step(action)

            if done:
                if winner is not None:
                    wins[agent.color] += 1
                tot = wins[RED] + wins[BLUE]
                tot = tot if tot > 0 else 1

                print(
                    "EVAL => Game={:<6d} | Winner={} | after {:<4} plays || Wins: {}={:<6}({:<5.1f}%) | {}={:<6}({:<5.1f}%) | Duration={:<.3f} sec".format(
                        episode + 1, winner, i,
                        agents[RED].name, wins[RED], (wins[RED] / tot) * 100,
                        agents[BLUE].name, wins[BLUE], (wins[BLUE] / tot) * 100, time.time() - t))
                break

            agent_color = env.turn
            agent = agents[agent_color]

            observation = observation_next
    return wins
