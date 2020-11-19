import datetime
import random
import time
from itertools import count

import numpy as np
import torch
import torch.nn as nn

from .agents import TDAgent, RandomAgent, evaluate_agents, CustomAgent, RED, BLUE

torch.set_default_tensor_type('torch.DoubleTensor')


class BaseModel(nn.Module):
    def __init__(self, lr, lamda, seed=123):
        super(BaseModel, self).__init__()
        self.lr = lr
        self.lamda = lamda  # trace-decay parameter
        self.start_episode = 0

        self.eligibility_traces = None
        self.optimizer = None

        torch.manual_seed(seed)
        random.seed(seed)

    def update_weights(self, p, p_next):
        raise NotImplementedError

    def forward(self, x):
        raise NotImplementedError

    def init_weights(self):
        raise NotImplementedError

    def init_eligibility_traces(self):
        self.eligibility_traces = [torch.zeros(weights.shape, requires_grad=False) for weights in list(self.parameters())]

    def checkpoint(self, checkpoint_path, step, name_experiment):
        path = checkpoint_path + "/{}_{}_{}.tar".format(name_experiment, datetime.datetime.now().strftime('%Y%m%d_%H%M_%S_%f'), step + 1)
        torch.save({'step': step + 1, 'model_state_dict': self.state_dict(), 'eligibility': self.eligibility_traces if self.eligibility_traces else []}, path)
        print("\nCheckpoint saved: {}".format(path))

    def load(self, checkpoint_path, optimizer=None, eligibility_traces=None):
        checkpoint = torch.load(checkpoint_path)
        self.start_episode = checkpoint['step']

        self.load_state_dict(checkpoint['model_state_dict'])

        if eligibility_traces is not None:
            self.eligibility_traces = checkpoint['eligibility']

        if optimizer is not None:
            self.optimizer.load_state_dict(checkpoint['optimizer'])

    def train_agent(self, env, n_episodes, save_path=None, eligibility=False, save_step=0, name_experiment=''):
        start_episode = self.start_episode
        n_episodes += start_episode

        wins = {RED: 0, BLUE: 0}
        network = self

        agents = {RED: TDAgent(RED, net=network), BLUE: TDAgent(BLUE, net=network)}

        durations = []
        steps = 0
        start_training = time.time()

        for episode in range(start_episode, n_episodes):

            if eligibility:
                self.init_eligibility_traces()

            agent_color, observation = env.reset()
            agent = agents[agent_color]

            t = time.time()

            for i in count():
                roll = agent.roll_dice()

                p = self(observation)

                actions = env.get_valid_actions(agent_color, roll)
                action = agent.choose_best_action(actions, env)
                observation_next, reward, done, winner = env.step(action)
                p_next = self(observation_next)

                if done:
                    if winner is not None:
                        loss = self.update_weights(p, reward)

                        wins[agent.color] += 1

                    tot = sum(wins.values())
                    tot = tot if tot > 0 else 1

                    print("Game={:<6d} | Winner={} | after {:<4} plays || Wins: {}={:<6}({:<5.1f}%) | {}={:<6}({:<5.1f}%) | Duration={:<.3f} sec".format(episode + 1, winner, i,
                        agents[RED].name, wins[RED], (wins[RED] / tot) * 100,
                        agents[BLUE].name, wins[BLUE], (wins[BLUE] / tot) * 100, time.time() - t))

                    durations.append(time.time() - t)
                    steps += i
                    break
                else:
                    loss = self.update_weights(p, p_next)

                agent_color = env.turn
                agent = agents[agent_color]

                observation = observation_next

            if save_path and save_step > 0 and episode > 0 and (episode + 1) % save_step == 0:
                self.checkpoint(checkpoint_path=save_path, step=episode, name_experiment=name_experiment)
                # agents_to_evaluate = {RED: TDAgent(RED, net=network), BLUE: RandomAgent(BLUE)}
                # evaluate_agents(agents_to_evaluate, env, n_episodes=20)
                print()

        print("\nAverage duration per game: {} seconds".format(round(sum(durations) / n_episodes, 3)))
        print("Average game length: {} plays | Total Duration: {}".format(round(steps / n_episodes, 2), datetime.timedelta(seconds=int(time.time() - start_training))))

        if save_path:
            self.checkpoint(checkpoint_path=save_path, step=n_episodes - 1, name_experiment=name_experiment)

            with open('{}/comments.txt'.format(save_path), 'a') as file:
                file.write("Average duration per game: {} seconds".format(round(sum(durations) / n_episodes, 3)))
                file.write("\nAverage game length: {} plays | Total Duration: {}".format(round(steps / n_episodes, 2), datetime.timedelta(seconds=int(time.time() - start_training))))


class TDLudo(BaseModel):
    def __init__(self, hidden_units, lr, lamda, init_weights, seed=123, input_units=123, output_units=1):
        super(TDLudo, self).__init__(lr, lamda, seed=seed)

        self.hidden = nn.Sequential(
            nn.Linear(input_units, hidden_units),
            nn.Sigmoid()
        )

        # self.hidden2 = nn.Sequential(
        #     nn.Linear(hidden_units, hidden_units),
        #     nn.Sigmoid()
        # )

        # self.hidden3 = nn.Sequential(
        #     nn.Linear(hidden_units, hidden_units),
        #     nn.Sigmoid()
        # )

        self.output = nn.Sequential(
            nn.Linear(hidden_units, output_units),
            nn.Sigmoid()
        )

        if init_weights:
            self.init_weights()

    def init_weights(self):
        for p in self.parameters():
            nn.init.zeros_(p)

    def forward(self, x):
        x = torch.tensor(np.array(x), dtype=torch.double)
        x = self.hidden(x)
        # x = self.hidden2(x)
        # x = self.hidden3(x)
        x = self.output(x)
        return x

    def update_weights(self, p, p_next):
        # reset the gradients
        self.zero_grad()

        # compute the derivative of p w.r.t. the parameters
        p.backward()

        with torch.no_grad():

            td_error = p_next - p

            # get the parameters of the model
            parameters = list(self.parameters())

            for i, weights in enumerate(parameters):

                # z <- gamma * lambda * z + (grad w w.r.t P_t)
                self.eligibility_traces[i] = self.lamda * self.eligibility_traces[i] + weights.grad

                # w <- w + alpha * td_error * z
                new_weights = weights + self.lr * td_error * self.eligibility_traces[i]
                weights.copy_(new_weights)

        return td_error
