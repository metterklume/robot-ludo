import os
import sys
from .agents import TDAgent, RandomAgent, CustomAgent, evaluate_agents, RED, BLUE
from .model import TDLudo
from .ludoenv import LudoEnv


def write_file(path, **kwargs):
    with open('{}/parameters.txt'.format(path), 'w+') as file:
        print("Parameters:")
        for key, value in kwargs.items():
            file.write("{}={}\n".format(key, value))
            print("{}={}".format(key, value))
        print()


def path_exists(path):
    if os.path.exists(path):
        return True
    else:
        print("The path {} doesn't exists".format(path))
        sys.exit()


# ==================================== TRAINING PARAMETERS ===================================
def args_train(args):
    save_step = args.save_step
    save_path = None
    n_episodes = args.episodes
    init_weights = args.init_weights
    lr = args.lr
    hidden_units = args.hidden_units
    lamda = args.lamda
    name = args.name
    model_type = args.type
    seed = args.seed

    counters = args.counters
    length = args.length
    safe_squares = args.ss
    starting = args.starting

    eligibility = False
    optimizer = None

    net = TDLudo(hidden_units=hidden_units, lr=lr, lamda=lamda, init_weights=init_weights, seed=seed)
    eligibility = True
    env = LudoEnv(counters=counters, length=length, safe_squares=safe_squares, starting=starting)

    if args.model and path_exists(args.model):
        # assert os.path.exists(args.model), print("The path {} doesn't exists".format(args.model))
        net.load(checkpoint_path=args.model, optimizer=optimizer, eligibility_traces=eligibility)
        print(f'Checkpoint loaded : {args.model}')

    if args.save_path and path_exists(args.save_path):
        # assert os.path.exists(args.save_path), print("The path {} doesn't exists".format(args.save_path))
        save_path = args.save_path

        write_file(
            save_path, save_path=args.save_path, command_line_args=args, type=model_type, hidden_units=hidden_units,
            init_weights=init_weights, alpha=net.lr, lamda=net.lamda,
            n_episodes=n_episodes, save_step=save_step, start_episode=net.start_episode, name_experiment=name,
            env="env_id", restored_model=args.model, seed=seed,
            eligibility=eligibility, optimizer=optimizer, modules=[module for module in net.modules()]
        )

    net.train_agent(env=env, n_episodes=n_episodes, save_path=save_path, save_step=save_step, eligibility=eligibility,
                    name_experiment=name)


def args_evaluate(args):
    model_agent0 = args.model_agent0
    # model_agent1 = args.model_agent1
    model_type = args.type
    hidden_units_agent0 = args.hidden_units_agent0
    # hidden_units_agent1 = args.hidden_units_agent1
    n_episodes = args.episodes

    counters = args.counters
    length = args.length
    safe_squares = args.ss
    starting = args.starting

    # if path_exists(model_agent0) and path_exists(model_agent1):
    if path_exists(model_agent0):
        # assert os.path.exists(model_agent0), print("The path {} doesn't exists".format(model_agent0))
        # assert os.path.exists(model_agent1), print("The path {} doesn't exists".format(model_agent1))

        # if model_type == 'nn':
        net0 = TDLudo(hidden_units=hidden_units_agent0, lr=0.1, lamda=None, init_weights=False)
        # net1 = TDLudo(hidden_units=hidden_units_agent1, lr=0.1, lamda=None, init_weights=False)
        env = LudoEnv(counters=counters, length=length, safe_squares=safe_squares, starting=starting)

        net0.load(checkpoint_path=model_agent0, optimizer=None, eligibility_traces=False)
        # net1.load(checkpoint_path=model_agent1, optimizer=None, eligibility_traces=False)

        agents = {RED: TDAgent(RED, net=net0), BLUE: CustomAgent(BLUE)}

        evaluate_agents(agents, env, n_episodes)
