import random
from state import makemove, getmoves

def ssb_engine(board,turn,roll):
    moves = getmoves(board,turn,roll)
    bp_before, rp_before = board.bluepen, board.redpen
    hbl = int(board.length/2)
    move_type = {}

    if len(moves) == 1:
        return moves[0]

    for k in moves:
        b2 = makemove(board, k)
        move_type[k] = ("GM",0.8)
        pos = k[1]
        new_pos = k[1] + k[2]
        pre_vuln_status,post_vuln_status = 0,0
        bp_now, rp_now = b2.bluepen, b2.redpen

        if turn == 1:

            new_pos = abs(new_pos - board.length) if new_pos >= board.length else new_pos
            if  pos > hbl:
                gap = pos - hbl
                pre_vuln_status = sum(board.red[gap : pos]) 
                post_vuln_status = sum(b2.red[gap : pos])
            else:
                pre_vuln_status = sum(board.red[0:pos])
                post_vuln_status = sum(b2.red[0:pos])

            #if (pos < hbl) and (pre_vuln_status > post_vuln_status):
            if pre_vuln_status > post_vuln_status:                
                move_type[k] = ("GM",1.6)
                
            if k == (turn,0,0):
                move_type[k] = ("EB",1.4) #Enter Board

            if rp_now > rp_before:
                move_type[k] = ("CP",1.6) #Cut Piece
                    
            if sum(board.blue) > sum(b2.blue):
                move_type[k] = ("RH",1.2) #Reach Home
               
        else: #turn = 0

            if pos < hbl:
                gap = pos - hbl
                pre_vuln_status = sum(board.blue[0 : pos]) + sum(board.blue[gap:])
                post_vuln_status = sum(b2.blue[0 : pos]) + sum(b2.blue[gap:])
            else:
                pre_vuln_status = sum(board.blue[pos-hbl : pos])
                post_vuln_status = sum(b2.blue[pos-hbl : pos])

            #if (pos > hbl) and (pre_vuln_status > post_vuln_status):
            if pre_vuln_status > post_vuln_status:
                move_type[k] = ("GM",1.6)

            if k == (turn,0,0):
                move_type[k] = ("EB",1.4) #Enter Board

            if bp_now > bp_before:
                move_type[k] = ("CP",1.6) #Cut Piece
                    
            if sum(board.red) > sum(b2.red):
                move_type[k] = ("RH",1.2) #Reach Home
                
            
    
    sorted_score = sorted(move_type.items(), key = lambda x: x[1][1], reverse=True)
    #print("score : ", sorted_score)
    max_score = sorted_score[0][1][1]
    #print('max score ',max_score)
    sorted_max_scores = []
    for k in sorted_score:
        if k[1][1] == max_score:
            sorted_max_scores.append(k[0])
        else:
            break

    return random.choice(sorted_max_scores)