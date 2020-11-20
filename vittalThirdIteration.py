from state import Board, makemove, getmoves, isvalidboard, isvalidmove
# from draw import drawboard
from match import make_start_board, match, judge
import numpy as np
import random

def dieRolldiev3(board, turn, roll):
    validMoves = getmoves(board,turn,roll)
    scores = dict(zip(validMoves, [scoreMovev3(board, move, turn) for move in validMoves]))
    bestMoves = [key for key in scores.keys() if scores[key] == max(scores.values())]
    return random.choice(bestMoves)
def scoreMovev3(board, move, turn):
    nextBoard = makemove(board, move, copyboard=True)
    #wt1: player tokens under attack. -ve
    #wt2: send piece to home square. +ve
    #wt3: get piece from pen to board. +ve
    #wt4: cut opponent pieces. +ve
    #wt5: opponent tokens under attack. +ve
    #wt6: incentivise token movement closer to home. +ve
    wt1, wt2, wt3,wt4,wt5,wt6 = (-10, 70, 10, 90, 5, 0.01)
    redPositionStrength = [np.sum([i for i in range(a+1)]) for a in range(nextBoard.length)]
    redPositionsUnderAttack = (1-np.array(nextBoard.safe))*nextBoard.red
    bluePositionsUnderAttack = (1-np.array(nextBoard.safe))*nextBoard.blue
    redUnderAttack = np.sum([np.sum(redPositionsUnderAttack[ix+1:min(ix+7,nextBoard.length//2+1)]) if ix < nextBoard.length//2 else np.sum(redPositionsUnderAttack[ix+1:min(ix+7,nextBoard.length)]) + np.sum(redPositionsUnderAttack[0:max(0,ix+7-nextBoard.length)]) for ix in np.nonzero(nextBoard.blue)[0]])
    blueUnderAttack = np.sum([np.sum(bluePositionsUnderAttack[ix+1:ix+7]) for ix in np.nonzero(nextBoard.red)[0]])
    if turn ==0:
        if (np.sum(nextBoard.blue) + nextBoard.bluepen <= 0.25*nextBoard.counters)&(np.sum(nextBoard.red) + nextBoard.redpen > 0.5*nextBoard.counters): # play aggressively
            score = wt1*redUnderAttack+wt2*(nextBoard.counters - np.sum(nextBoard.red) - nextBoard.redpen)+wt3*np.sum(nextBoard.red)+1.5*wt4*nextBoard.bluepen+1.5*wt5*blueUnderAttack+wt6*np.dot(redPositionStrength,nextBoard.red)
        else: #play normally. 
            score = wt1*redUnderAttack+wt2*(nextBoard.counters - np.sum(nextBoard.red) - nextBoard.redpen)+wt3*np.sum(nextBoard.red)+wt4*nextBoard.bluepen+wt5*blueUnderAttack+wt6*np.dot(redPositionStrength,nextBoard.red)
    elif turn ==1:
        bluePositionStrength = redPositionStrength[nextBoard.length//2:] + redPositionStrength[:nextBoard.length//2]
        if (np.sum(nextBoard.red) + nextBoard.redpen <= 0.25*nextBoard.counters)&(np.sum(nextBoard.blue) + nextBoard.bluepen > 0.5*nextBoard.counters): # play aggressively
            score = wt1*blueUnderAttack+wt2*(nextBoard.counters - np.sum(nextBoard.blue) - nextBoard.bluepen)+wt3*np.sum(nextBoard.blue)+1.5*wt4*nextBoard.redpen+1.5*wt5*redUnderAttack+wt6*np.dot(bluePositionStrength,nextBoard.blue)
        else: # play normally
            score = wt1*blueUnderAttack+wt2*(nextBoard.counters - np.sum(nextBoard.blue) - nextBoard.bluepen)+wt3*np.sum(nextBoard.blue)+wt4*nextBoard.redpen+wt5*redUnderAttack+wt6*np.dot(bluePositionStrength,nextBoard.blue)
    return score
