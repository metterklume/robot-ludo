from state import makemove
from match import halfshift
import numpy as np


def getOppNextMoveProb(turn, b, defenseScr=0.0):
    L = b.length
    nextMoveProb = [0] * L

    if turn == 0:
        oppPos = b.blue[L // 2:L] + b.blue[0:L // 2]
        selfPos = b.red
    else:
        oppPos = b.red
        selfPos = b.blue

    for i, c in enumerate(oppPos):
        if c:
            for j in range(i + 1, min(i + 7, L)):
                nextMoveProb[j] += defenseScr

    if turn == 0:
        nextMoveProb = nextMoveProb[L // 2:L] + nextMoveProb[0:L // 2]

    for i, c in enumerate(selfPos):
        if c:
            nextMoveProb[i] = c * nextMoveProb[i]

    for i, s in enumerate(b.safe):
        if s:
            nextMoveProb[i] = 0

    return nextMoveProb


def getBestMove(b,
                moves,
                newCtrScr=1,
                cutScrMult=11,
                homeRunScr=20,
                normalMoveScr=0.0,
                randomMoveProb=0.0,
                defenseScr=0.0):
    # null move
    turn, pos, steps = moves[0]
    if (pos, steps) == (-1, -1):
        return moves[0]

    # random move
    if np.random.uniform() < randomMoveProb:
        return moves[np.random.randint(0, len(moves))]

    rp, bp = b.redpen, b.bluepen
    L = b.length
    scores = []

    if turn == 1:
        moves = sorted(moves, key=lambda triple: halfshift(triple[1], L))

    oppNextMoveProb = getOppNextMoveProb(turn, b, defenseScr=defenseScr)

    for move in moves:
        _, pos, steps = move
        nextPos = pos + steps

        # new ctr move
        if (pos, steps) == (0, 0):
            scores.append(newCtrScr + 1 - [sum(b.red) / b.counters, sum(b.blue) / b.counters][turn])
            continue

        b_temp = makemove(b, move, copyboard=True)

        if turn == 0:
            # cut move
            if b_temp.bluepen > bp:
                scores.append((b_temp.bluepen - bp) * cutScrMult +
                              [nextPos - L // 2, nextPos + L // 2][nextPos < L // 2] / L)

            # home run move
            elif nextPos == L:
                scores.append(homeRunScr)

            # normal move
            else:
                scores.append(pos * normalMoveScr - oppNextMoveProb[nextPos] + oppNextMoveProb[pos])

        if turn == 1:
            # cut move
            if b_temp.redpen > rp:
                scores.append((b_temp.redpen - rp) * cutScrMult + (nextPos % L) / L)

            # home run move
            elif nextPos == L // 2:
                scores.append(homeRunScr)

            # normal move
            else:
                if pos < (L // 2):
                    scores.append((pos + L // 2) * normalMoveScr - oppNextMoveProb[nextPos] +
                                  oppNextMoveProb[pos])
                else:
                    scores.append((pos - L // 2) * normalMoveScr - oppNextMoveProb[nextPos % L] +
                                  oppNextMoveProb[pos])

    return moves[np.argmax(scores)]
