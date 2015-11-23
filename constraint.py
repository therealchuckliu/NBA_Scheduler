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
        
def valid_date(m, k):
    dates = m.domains
    t1, t2, g_n = k
    dateindex = dates[k][0]
    #constraints are:
    #any game before g_n can't have a date >= g_n
    #any game after g_n can't have a date <= g_n
    
    for state in dates:
        x1, x2, g_x = state
        #involves one of the two teams playing
        if t1 in [x1, x2] or t2 in [x1, x2]:
            if g_x < g_n:
                #remove all dates >= dateindex
                dates[state][:] = [x for x in dates[state] if x < dateindex]
            elif g_x > g_n:
                #remove all dates <= dateindex
                dates[state][:] = [x for x in dates[state] if x > dateindex]
            if len(dates[state]) == 0:
                return False
    
    return True
        
def valid_venue(m, k):
    venues = m.domains
    #number of games played, key = (team1, team2, home)
    #where home is True if played at team1
    games_played = {}
    #number of home games per team, key = team
    home_games = {}
    for state in venues:
        if len(venues[state]) == 1:
            t1, t2, g_n = state
            home = venues[state][0]
            key = (t1, t2, home)
            add(games_played, key)
            add(home_games, t1 if home else t2)
        
    for state in games_played:
        t1, t2, home = state
        games = games_played[state]
        #number of home games per matchup should be roughly half of total games
        if games > (total_games(m, t1, t2) + 1)/2:
            return False
    
    for team in home_games:
        if home_games[team] > m.TOTAL_GAMES/2:
            return False
    
    return True

def valid_matchup(m, k):
    team, game_num = k
    matchups = m.domains
    opponent = matchups[k][0]
    #number of games played, key = (team1, team2) 
    games_played = {}
    
    #reverse matchup must match
    opp_k = (opponent, game_num)
    if team not in matchups[opp_k]:
        return False
    matchups[opp_k] = [team]
            
    for state in matchups:
        t, g_n = state
        if g_n == game_num and t is not opponent and team in matchups[state]:
            matchups[state].remove(team)
            if len(matchups[state]) == 0:
                return False
        if len(matchups[state]) == 1:
            o = matchups[state][0]
            key = (t, o) if t < o else (o, t)
            add(games_played, key)
                
    for state in games_played:
        if games_played[state] > total_games(m, state[0], state[1]):
            return False
    
    return True
    