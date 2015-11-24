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

def add(m, k):
    if k in m:
        m[k] += 1
    else:
        m[k] = 1

#total games two teams should play, pass in m which is a TGBase object or child
def total_games(m, team, opponent):
    if opponent.division is team.division:
        return m.DIVISIONAL_GAMES
    elif opponent in team.conf_opponents:
        return m.CONF_OPPONENTS_GAMES
    elif opponent.division.conference is team.division.conference:
        return m.REMAINING_CONF_GAMES
    else:
        return m.INTERCONF_GAMES
        
def valid_date(m, sk):
    domains = m.states[m.domains]
    selected = m.states[m.selected]
    t1, t2, g_n = sk
    dateindex = selected[sk]
    #constraints are:
    #any game before g_n can't have a date >= g_n
    #any game after g_n can't have a date <= g_n
    
    for state in domains:
        x1, x2, g_x = state
        #involves one of the two teams playing but not sk
        if state is not sk and (t1 in [x1, x2] or t2 in [x1, x2]):
            if g_x < g_n:
                #remove all dates >= dateindex
                domains[state][:] = [x for x in domains[state] if x < dateindex]
            elif g_x > g_n:
                #remove all dates <= dateindex
                domains[state][:] = [x for x in domains[state] if x > dateindex]
            if len(domains[state]) == 0 and selected[state] is None:
                return False
        elif state is sk:
            domains[state][:] = []
    
    return True
        
#check that the total number of home games is TOTAL_GAMES/2
def valid_venue(m, sk):
    selected = m.states[m.selected]
    domains = m.states[m.domains]
    home_games = {}
    num_games = {}
    for state in selected:
        if selected[state] is not None:
            t1, t2, g_n = state
            home = selected[state]
            add(home_games, t1 if home else t2)
            add(num_games, (t1, t2))
    for team in home_games:
        if home_games[team] > (m.TOTAL_GAMES+1)/2:
            return False
    for state in num_games:
        t1, t2 = state
        #remove the last domain element in case where t1 and t2 play odd number of games
        #domain was initialized to size 2*(num_games+1)/2
        if num_games[state] == total_games(m, t1, t2):
            domains[state] = []
    return True
            
#set opponent's matchup and update their domain
def valid_matchup(m, sk):
    team, game_num = sk
    domains = m.states[m.domains]
    selected = m.states[m.selected]
    opponent = selected[sk]
    if selected[(opponent, game_num)] is None:
        domains[opponent].remove(team)
        selected[(opponent, game_num)] = team
        return True
    return False
    