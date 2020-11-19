"""
Created on Fri Oct 23 14:00:00 2020

@author: abhishekroy
"""
from match import judge

from vittalThirdIteration import dieRolldiev3
from ssb_submission import ssb_engine
from kevins_submission import engine_kevin
from sagar_engine.players import TDPlayer, myPlayer1

td_player_red = TDPlayer(color=0)
td_player_blue = TDPlayer(color=1)
sagar_red = td_player_red.make_a_move
sagar_blue = td_player_blue.make_a_move

red_names = ['Shantanu','Vittal','Kevin','Sagar']
red_engines = [ssb_engine,dieRolldiev3,engine_kevin,sagar_red]
blue_names = ['Shantanu','Vittal','Kevin','Sagar']
blue_engines = [ssb_engine,dieRolldiev3,engine_kevin,sagar_blue]

red_candidates = [{"Name":ename,"Engine":eng} for ename,eng in zip(red_names,red_engines)]
blue_candidates = [{"Name":ename,"Engine":eng} for ename,eng in zip(blue_names,blue_engines)]


def tournament(counters,length,safesquares,candidates1,candidates2,games,outfilename):
    with open(f"{outfilename}","w",buffering=1) as fout:

        fout.write(f"Candidates1: {[c['Name'] for c in candidates1]}\n")
        fout.write(f"Candidates2: {[c['Name'] for c in candidates2]}\n")
        fout.write(f"Games per Match: {games}\n")
        fout.write("-"*50+"\n")
        results = []
        for cand1 in candidates1:
            for cand2 in candidates2:
                name1,name2 = cand1['Name'], cand2['Name']
                if name1 == name2:
                    continue
                result = judge(counters,length,safesquares,cand1['Engine'],cand2['Engine'],
                            games=games)
                results += [(name1,name2,result)]
                fout.write(f"{name1},{name2},{result[0]},{result[1]}\n")
    
    return results

if __name__ == "__main__":
    tournament(12,36,(9,27),red_candidates,blue_candidates,10,"tournament.txt")
