# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 17:23:47 2015

Check factors for:
1) For each game, each team/opponent home/away lines up
2) Games against divisional opponents not exceeded, home/away even
3) Games against inter-conference opponents not exceeded, home/away even
4) Games against conf_opponents not exceeded, home/away even
5) Games against conference opponents not in conf_opponents not exceeded, home/away as even as possible

@author: charlesliu
"""

def check(tgs, k):
    team, game_num = k
    opponent, home, dateindex = tgs.domains[k][0]
    
    #count number of times each team has played at home and at opponent's
    #keys should be of form (team1, team2) with team1/team2 alphabetized
    #values should be of form [x,y] with x for team1 home games, y for team2
    game_counts = {}
    #count of number of home games
    home_games = {}
    
    for state in tgs.domains:
        #remove all (team, home, dateindex) from opponent states
        if state[0] == opponent:
            tgs.domains[state][:] = [x for x in tgs.domains[state] if not (x[0] is team and x[1] is home and x[2] is dateindex)]
        #remove all (*, *, dateindex) from team states for different game_num
        elif state[0] == team and game_num != state[1]:
            #if game is after game_num, remove all dates up to dateindex
            if state[1] > game_num:
                tgs.domains[state][:] = [x for x in tgs.domains[state] if x[2] > dateindex]
            #if game is before game_num, remove all dates after dateindex
            else:
                tgs.domains[state][:] = [x for x in tgs.domains[state] if x[2] < dateindex]
        #remove all (team, *, dateindex) from all other teams
        elif state[0] is not team: 
            tgs.domains[state][:] = [x for x in tgs.domains[state] if not (x[0] is team and x[2] is dateindex)]
                
        if len(tgs.domains[state]) == 0:
            return False
        #check that any games that are decided, i.e. domain size is 1, are within
        #max game constraints
        elif len(tgs.domains[state]) == 1:
            t1 = state[0]
            t2 = tgs.domains[state][0][0]
            h = tgs.domains[state][0][1]
            ht = t1 if h else t2
            if ht in home_games:
                home_games[ht] += 1
            else:
                home_games[ht] = 1
            gc_key = (t1, t2) if t1.name < t2.name else (t2, t1)
            #h checks if home game for first team in gc_key
            h = gc_key[0] is ht
            if gc_key in game_counts:
                game_counts[gc_key][0 if h else 1] += 1
            else:
                game_counts[gc_key] = [1,0] if h else [0,1]
    
    for t in home_games:
        if home_games[t] > tgs.TOTAL_GAMES/2:
            return False

    for t1, t2 in game_counts:
        total_games = tgs.DIVISIONAL_GAMES
        if t2 in t1.conf_opponents:
            total_games = tgs.CONF_OPPONENTS_GAMES
        elif t1.division.conference is not t2.division.conference:
            total_games = tgs.INTERCONF_GAMES
        elif t1.division is not t2.division:
            total_games = tgs.REMAINING_CONF_GAMES
            
        games = game_counts[(t1, t2)]
        if sum(games) > total_games:
            return False
        if max(games) > (total_games + 1)/2:
            return False
    return True