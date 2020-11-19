from dataclasses import dataclass
from state import isvalidboard, getmoves, isvalidmove, makemove
import numpy as np
from copy import deepcopy
import random


def engine_kevin(board, turn, roll):
    weights = [
        9.7700e02,
        9.9983e04,
        8.6000e01,
        6.0000e00,
        6.9282e04,
        1.5159e04,
        9.9731e04,
        3.8300e02,
    ]
    moves = getmoves(board, turn, roll)
    scores = [
        (get_score3(board, move, weights, "calculated", True), move) for move in moves
    ]
    bestscore, bestmove = max(scores)
    if bestscore == 0:
        return random.choice(moves)
    return bestmove


def is_near_home(board, move, home_nearness_threshold, end):
    L = board.length
    nearness_factor = int(home_nearness_threshold * L)
    turn, pos = move[0], move[1]
    if turn == 0:
        return pos >= (L - nearness_factor) and pos <= (L - end)
    return pos >= (L // 2 - nearness_factor) and pos <= L // 2 - end


def get_threat_count(board, enemies, line, turn, pos, calc_type):
    present_last_enemy_move = (int(not turn), pos, 6)
    if calc_type == "calculated":
        enemy_line_current = pos if isvalidmove(board, present_last_enemy_move) else line
    if calc_type == "simple_calculated":
        enemy_line_current = pos

    if pos > enemy_line_current:
        current_enemies = enemies[enemy_line_current:pos]
    else:
        current_enemies = enemies[enemy_line_current:] + enemies[:pos]
    current_threat = 0 if board.safe[pos] else sum(current_enemies)
    return current_threat


def get_opponenets_ahead(board, line, turn, pos, calc_type):
    if turn == 0:
        players = board.red
    else:
        players = board.blue

    enemy_move = (int(not turn), pos, 6)

    # enemy_line_ahead = (
    #     (pos + 6) % board.length if isvalidmove(board, enemy_move) else line
    # )
    if calc_type == "calculated":
        enemy_line_ahead = (
            (pos + 6) % board.length if isvalidmove(board, enemy_move) else line
        )
    if calc_type == "simple_calculated":
        enemy_line_ahead = (pos + 6) % board.length

    safe_zones = []
    if (pos) < enemy_line_ahead:
        current_enemies = players[pos:enemy_line_ahead]
        safe_zones = board.safe[pos:enemy_line_ahead]
    else:
        current_enemies = players[:enemy_line_ahead] + players[pos:]
        safe_zones = board.safe[:enemy_line_ahead] + board.safe[pos:]
    current_threat = sum(
        [
            current_enemies[i] if not safe_zones[i] else 0
            for i in range(len(current_enemies))
        ]
    )

    return current_threat


def get_last_mile_enemies(board, newboard, turn):
    L = board.length
    if turn == 0:
        return sum(board.blue[0 : L // 2]) - sum(newboard.blue[0 : L // 2])

    return sum(board.red[L // 2 : L]) - sum(newboard.red[0 : L // 2])


def get_enemy_stats(board, move, enemy_line):
    turn, pos, roll = move[0], move[1], move[2]
    L = board.length
    nextpos = (pos + roll) % board.length

    enemies = board.red
    enemy_start_line = 0

    if turn == 0:
        enemies = board.blue
        enemy_start_line = L // 2

    if enemy_line == "safe_jump":
        current_threat = 0 if board.safe[pos] else 1
        future_threat = 0 if board.safe[nextpos] else 1
        return current_threat, future_threat, enemies[nextpos]

    present_last_enemy_move = (int(not turn), (pos - 6) % board.length, 6)
    future_last_enemy_move = (int(not turn), (nextpos - 6) % board.length, 6)
    enemy_line_current = (
        (pos - 6)
        % board.length
        # if isvalidmove(board, present_last_enemy_move)
        # else enemy_start_line
    )
    enemy_line_future = (
        (nextpos - 6)
        % board.length
        # if isvalidmove(board, future_last_enemy_move)
        # else enemy_start_line
    )

    if pos > enemy_line_current:
        current_enemies = enemies[enemy_line_current:pos]
    else:
        current_enemies = enemies[enemy_line_current:] + enemies[:pos]
    if nextpos > enemy_line_future:
        future_enemies = enemies[enemy_line_future:nextpos]
    else:
        future_enemies = enemies[enemy_line_future:] + enemies[:nextpos]

    current_threat = 0 if board.safe[pos] else sum(current_enemies)
    future_threat = 0 if board.safe[nextpos] else sum(future_enemies)
    future_striks = 0 if board.safe[nextpos] else enemies[nextpos]

    return current_threat, future_threat, future_striks


def get_score3(board, move, weight, enemy_line="calcluated", proactive=True):
    """Assumption : moves are validated
    TODO: Take the best of all strategy wise and check time of action.
    """
    defensive_weight = weight[0]
    aggressive_weight = weight[1]
    safety_weight = weight[2]
    home_weight = weight[3]
    victory_weight = weight[4]
    nearness = 0.55
    end = 1
    proactive_weight = weight[5]
    start_weight = weight[6]
    last_enemy_weight = weight[7]

    # TODO : Removek
    made_tag = False

    top_score = 0
    turn, pos, roll = move[0], move[1], move[2]
    nextpos = (pos + roll) % board.length

    if (turn, 0, 0) != move and (turn, -1, -1) != move:
        current_threat, future_threat, future_strikes = get_enemy_stats(
            board, move, enemy_line
        )
        enemy_end_line = board.length // 2 if turn == 0 else board.length
        proactive_threat_elim = get_opponenets_ahead(
            board,
            enemy_end_line,
            turn,
            nextpos,
            enemy_line,
        )
        is_safety_jump = board.safe[nextpos]
        nboard = makemove(board, move)
        pen = nboard.redpen if turn == 0 else nboard.bluepen
        counters = nboard.red if turn == 0 else nboard.blue
        if pen == 0 and sum(counters) == 0:
            top_score += victory_weight

        last_mile_enemy_strikes = get_last_mile_enemies(
            board, makemove(board, move), turn
        )

        if not proactive:
            proactive_threat_elim = 0

        if current_threat and not future_threat:
            top_score += (
                current_threat
            ) * defensive_weight + proactive_threat_elim * proactive_weight
            made_tag = True

        if not future_threat and future_strikes:
            top_score += (
                future_strikes
            ) * aggressive_weight + proactive_threat_elim * proactive_weight
            if last_mile_enemy_strikes > 0:
                top_score += (
                    last_mile_enemy_strikes * proactive_weight * last_enemy_weight
                )
            made_tag = True

        elif future_strikes and future_threat:
            top_score += (
                future_strikes * aggressive_weight
                + proactive_threat_elim * proactive_weight
            )
            if last_mile_enemy_strikes > 0:
                top_score += (
                    last_mile_enemy_strikes
                    * (proactive_weight - safety_weight)
                    * last_enemy_weight
                )
            made_tag = True

        top_score -= future_threat * safety_weight

        if is_near_home(board, move, nearness, end):
            top_score += home_weight

        if is_safety_jump:
            top_score += safety_weight
            made_tag = True

    elif (turn, 0, 0) == move:
        top_score += start_weight

    return top_score


def get_score2(board, move, weight, enemy_line="calcluated", proactive=True):
    """Assumption : moves are validated
    TODO: Take the best of all strategy wise and check time of action.
    """
    defensive_weight = weight[0]
    aggressive_weight = weight[1]
    safety_weight = weight[2]
    home_weight = weight[3]
    victory_weight = weight[4]
    nearness = weight[5]
    end = weight[6]
    proactive_weight = weight[7]

    # TODO : Removek
    made_tag = False

    top_score = 0
    turn, pos, roll = move[0], move[1], move[2]
    nextpos = (pos + roll) % board.length

    if (turn, 0, 0) != move and (turn, -1, -1) != move:
        current_threat, future_threat, future_strikes = get_enemy_stats(
            board, move, enemy_line
        )
        enemy_end_line = board.length // 2 if turn == 0 else board.length
        proactive_threat_elim = get_opponenets_ahead(
            board,
            enemy_end_line,
            turn,
            nextpos,
            enemy_line,
        )
        is_safety_jump = board.safe[nextpos]
        nboard = makemove(board, move)
        pen = nboard.redpen if turn == 0 else nboard.bluepen
        counters = nboard.red if turn == 0 else nboard.blue
        if pen == 0 and sum(counters) == 0:
            top_score += victory_weight

        if not proactive:
            proactive_threat_elim = 0

        if current_threat and not future_threat:
            top_score += (
                current_threat
            ) * defensive_weight + proactive_weight * proactive_weight
            made_tag = True

        if not future_threat and future_strikes:
            top_score += (
                future_strikes
            ) * aggressive_weight + proactive_threat_elim * proactive_weight
            made_tag = True

        elif future_strikes and future_threat:
            top_score += (
                future_strikes * aggressive_weight
                - future_threat * safety_weight
                + proactive_threat_elim * proactive_weight
            )
            made_tag = True

        if is_near_home(board, move, nearness, end):
            top_score += home_weight

        if is_safety_jump:
            top_score += safety_weight
            made_tag = True

    elif (turn, 0, 0) == move:
        top_score += home_weight

    return top_score


def get_score(board, move, weight, enemy_line="calcluated", proactive=True):
    """Assumption : moves are validated
    TODO: Take the best of all strategy wise and check time of action.
    """
    defensive_weight = weight[0]
    aggressive_weight = weight[1]
    safety_weight = weight[2]
    home_weight = weight[3]
    victory_weight = weight[4]
    nearness = 0.55
    end = 1
    proactive_weight = weight[5]
    start_weight = weight[6]

    # TODO : Removek
    made_tag = False

    top_score = 0
    turn, pos, roll = move[0], move[1], move[2]
    nextpos = (pos + roll) % board.length

    if (turn, 0, 0) != move and (turn, -1, -1) != move:
        current_threat, future_threat, future_strikes = get_enemy_stats(
            board, move, enemy_line
        )
        enemy_end_line = board.length // 2 if turn == 0 else board.length
        proactive_threat_elim = get_opponenets_ahead(
            board,
            enemy_end_line,
            turn,
            nextpos,
            enemy_line,
        )
        is_safety_jump = board.safe[nextpos]
        nboard = makemove(board, move)
        pen = nboard.redpen if turn == 0 else nboard.bluepen
        counters = nboard.red if turn == 0 else nboard.blue
        if pen == 0 and sum(counters) == 0:
            top_score += victory_weight

        if not proactive:
            proactive_threat_elim = 0

        if current_threat and not future_threat:
            top_score += (
                current_threat
            ) * defensive_weight + proactive_threat_elim * proactive_weight
            made_tag = True

        if not future_threat and future_strikes:
            top_score += (
                future_strikes
            ) * aggressive_weight + proactive_threat_elim * proactive_weight
            made_tag = True

        elif future_strikes and future_threat:
            top_score += (
                future_strikes * aggressive_weight
                - future_threat * safety_weight
                + proactive_threat_elim * proactive_weight
            )
            made_tag = True

        if is_near_home(board, move, nearness, end):
            top_score += home_weight

        if is_safety_jump:
            top_score += safety_weight
            made_tag = True

    elif (turn, 0, 0) == move:
        top_score += start_weight

    return top_score


def get_enemy_stats2(board, move, enemy_line):
    turn, pos, roll = move[0], move[1], move[2]
    L = board.length
    nextpos = (pos + roll) % board.length

    enemies = board.red
    enemy_start_line = 0

    if turn == 0:
        enemies = board.blue
        enemy_start_line = L // 2

    if enemy_line == "safe_jump":
        current_threat = 0 if board.safe[pos] else 1
        future_threat = 0 if board.safe[nextpos] else 1
        return current_threat, future_threat, enemies[nextpos]

    present_last_enemy_move = (int(not turn), (pos - 6) % board.length, 6)
    future_last_enemy_move = (int(not turn), (nextpos - 6) % board.length, 6)
    enemy_line_current = (
        (pos - 6) % board.length
        if isvalidmove(board, present_last_enemy_move)
        else enemy_start_line
    )
    enemy_line_future = (
        (nextpos - 6) % board.length
        if isvalidmove(board, future_last_enemy_move)
        else enemy_start_line
    )

    if pos > enemy_line_current:
        current_enemies = enemies[enemy_line_current:pos]
    else:
        current_enemies = enemies[enemy_line_current:] + enemies[:pos]
    if nextpos > enemy_line_future:
        future_enemies = enemies[enemy_line_future:nextpos]
    else:
        future_enemies = enemies[enemy_line_future:] + enemies[:nextpos]

    current_threat = 0 if board.safe[pos] else sum(current_enemies)
    future_threat = 0 if board.safe[nextpos] else sum(future_enemies)
    future_striks = 0 if board.safe[nextpos] else enemies[nextpos]

    return current_threat, future_threat, future_striks


def kevin_submission_archived(board, turn, roll):
    """DONT CHANGE .996 with simple_player3"""
    # weights = [36.0, 10000.0, 1793.0, 1795.0]
    # weights = [48, 99993, 298, 82660, 6462]
    weights = [
        3.38000000e02,
        9.87160000e04,
        6.87000000e02,
        1.21900000e03,
        9.94370000e04,
        1.15066635e-01,
        1,
        26,
    ]
    # weights = [1000, 500, 10, 10, 10000, 0.3, 4]
    moves = getmoves(board, turn, roll)
    scores = [
        (get_score2(board, move, weights, "calculated", True), move) for move in moves
    ]
    bestscore, bestmove = max(scores)
    if bestscore == 0:
        return random.choice(moves)
    return bestmove


def kevin_submission_archived2(board, turn, roll):
    weights = [
        1000,
        500,
        10,
        10,
        1000,
        0.3,
        4,
        9.92130000e04,
    ]
    moves = getmoves(board, turn, roll)
    scores = [
        (get_score2(board, move, weights, "calculated", True), move) for move in moves
    ]
    bestscore, bestmove = max(scores)
    if bestscore == 0:
        return random.choice(moves)
    return bestmove


# def kevin_submission1(board, turn, roll):
#     """
#     The one to be used
#     """
#     weights = (100, 100, 100, 100)
#     moves = getmoves(board, turn, roll)
#     scores = [(get_score(board, move, weights, "calculated"), move) for move in moves]
#     bestscore, bestmove = max(scores)
#     if bestscore == 0:
#         return random.choice(moves)
#     return bestmove


# def kevin_submission2(board, turn, roll):

#     weights = (10, 500, 100, 10)
#     moves = getmoves(board, turn, roll)
#     scores = [(get_score2(board, move, weights, "calculated"), move) for move in moves]
#     bestscore, bestmove = max(scores)
#     if bestscore == 0:
#         return random.choice(moves)
#     return bestmove


# def kevin_submission4(board, turn, roll, weights):
#     """
#     The one to be used
#     """
#     moves = getmoves(board, turn, roll)
#     scores = [
#         (get_score2(board, move, [0, 0, 0, 0], "calculated", False), move)
#         for move in moves
#     ]
#     bestscore, bestmove = max(scores)
#     if bestscore == 0:
#         return random.choice(moves)
#     return bestmove


# def random_player(board, turn, roll):
#     weights = (1000, 500, 100, 10)
#     moves = getmoves(board, turn, roll)
#     mymove = get_tagged_move(board, moves, weights, "simple_calculated")
#     return mymove