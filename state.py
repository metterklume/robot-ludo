"""
Created on Mon Oct 12 14:30:00 2020

@author: abhishekroy
"""

from dataclasses import dataclass
import numpy as np
import copy

@dataclass
class Board:
    counters: int #total counters for each side to start
    length: int   #length of the track
    
    # Next 3 arrays have size = *length*
    safe: list    # 1 if square is safe else 0  
    red: list     # Red and Blue counters on each square
    blue: list    

    redpen: int   # number of counters that are in the 'pen' 
    bluepen: int  # waiting to come into play

    def __copy__(self):
        return Board(counters=self.counters,length=self.length,safe=list(self.safe),red=list(self.red),blue=list(self.blue),
        redpen=self.redpen,bluepen=self.bluepen)

# move is in the form (turn, pos, steps)
# turn = 0 for red, 1 for blue
# Two special moves:
# (turn, 0, 0) --> counter moves home from pen
# (turn, -1, -1) --> Pass

def makemove(board, move, copyboard=True):
    '''
    Make a move on the board. If *copy* then returns copy,
    else mutates current board.
    '''
    if not isvalidmove(board, move):
        print("Invalid move")
        return board
    
    if copyboard:
        newboard = copy.copy(board)
    else:
        newboard = board

    turn, pos, steps = move
    L = board.length 

    # Null move
    if (pos,steps) == (-1,-1):
        return newboard

    # Special move --> new counter enters from pen    
    if (pos,steps) == (0,0):
        if turn == 0:
            newboard.red[0] += 1
            newboard.redpen -= 1
        if turn == 1:
            newboard.blue[L//2] += 1
            newboard.bluepen -= 1

    # Regular move --> advance counter by *steps* and cut 
    # opposite coloured counters at destination unless at safe square.
    # If home is reached, remove counter from board 
    elif turn == 0:
        newpos = pos + steps
        newboard.red[pos] -= 1

        if newpos != L:
            newboard.red[newpos] += 1
        
            if not newboard.safe[newpos]:
                newboard.bluepen += newboard.blue[newpos]
                newboard.blue[newpos] = 0
    
    elif turn == 1:
        newpos = (pos + steps) % L
        newboard.blue[pos] -= 1

        if newpos != L//2:
            newboard.blue[newpos] += 1
        
            if not newboard.safe[newpos]:
                newboard.redpen += newboard.red[newpos]
                newboard.red[newpos] = 0
        
    return newboard


def isvalidmove(board, move, maxroll=6):
    '''
    True if move is valid
    '''
    turn, pos, steps = move
    L, newpos = board.length, pos + steps

    # Null move
    if (pos,steps) == (-1,-1):
        return True

    # Special move --> new counter enters from pen    
    if (pos,steps) == (0,0):
        if turn == 0 and board.redpen:
            return True
        if turn == 1 and board.bluepen:
            return True
    
    # Check if counter present at *pos* and moving will not cross home
    if turn == 0:
        if not board.red[pos] or newpos > L:
            return False
        
    if turn == 1:
        if not board.blue[pos] or (pos < L//2 and pos+steps > L//2) or\
            (pos > L//2 and newpos > L + L//2):
            return False

    if pos < 0 or pos >= L or steps<=0 or steps>maxroll:
        return False
    
    return True


def isvalidboard(board):
    '''
    True if board passes consistency checks
    '''
    L,r,b,s = board.length,len(board.red),len(board.blue),len(board.safe)

    if (r,b,s) != (L,L,L):
        return False

    if sum(board.red)>board.counters-board.redpen or \
        sum(board.blue)>board.counters-board.bluepen:
        return False

    return True


def getmoves(board, turn, roll, maxroll=6):
    '''
    Get list of legal moves for the board, given a turn and roll of the die
    '''
    moves = []
    if roll == maxroll and \
        ((turn == 0 and board.redpen) or (turn == 1 and board.bluepen)):
        moves += [(turn,0,0)]
    
    if turn == 0:
        for pos,ctrs in enumerate(board.red):
            if ctrs and isvalidmove(board,(turn, pos, roll)):
                moves += [(turn,pos,roll)]
        
    if turn == 1:
        for pos,ctrs in enumerate(board.blue):
            if ctrs and isvalidmove(board,(turn, pos, roll)):
                moves += [(turn,pos,roll)]

    if not moves:
        moves = [(turn,-1,-1)]

    return moves
