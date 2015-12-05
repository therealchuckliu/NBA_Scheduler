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
    away_games = {}
    num_games = {}
    # NOTE: we are only concerned with t1 and t2 since those are the only teams that are
    # affected by the selected game.
    # Note, since we ordered when generating team pairs, t1 < t2. So if t1, t2 are both in a game,
    # the order is (t1,t2), not (t2,t1)
    t1, t2, gn = sk
    for state in selected:
        tx, ty, gnxy = state
        if (t1 in [tx,ty] or t2 in [tx,ty]) and (selected[state] is not None):
            home = selected[state]
            
            
            if t1 == tx:
                if t2 == ty:
                    add(num_games, (t1, t2))
                    add(away_games if home else home_games, t2)
                add(home_games if home else away_games, t1)
            elif t1 == ty:
                add(away_games if home else home_games, t1)
            
            # t1 not in state
            elif t2 == tx:
                add(home_games if home else away_games, t2)
            #t2 == ty
            else:
                add(away_games if home else home_games, t2)   
      
    # scheduled the required number of games between the two teams
    # clear domain
    if num_games[(t1,t2)] == total_games(m, t1, t2):
        domains[(t1,t2)] = []
        return True
    
    # add t1 and t2 to list if respectively if they have played enough home games or away games
    enough_home_games_list = []
    enough_away_games_list = []
    for team in [t1,t2]:
        if team in home_games and home_games[team] == (m.TOTAL_GAMES+1)/2:
            enough_home_games_list.append(team)
        if team in away_games and away_games[team] == (m.TOTAL_GAMES+1)/2:
            enough_away_games_list.append(team)
    # iterate over team pairs and remove home games for teams (t1 or t2) that have played enough
    # home games or away games
    for team_pair in domains:
        tx, ty = team_pair
        if tx in enough_home_games_list:
            domains[team_pair] = [x for x in domains[team_pair] if not x]
        elif ty in enough_home_games_list:
            domains[team_pair] = [x for x in domains[team_pair] if x]
        if tx in enough_away_games_list:
            domains[team_pair] = [x for x in domains[team_pair] if x] 
        elif ty in enough_away_games_list:
            domains[team_pair] = [x for x in domains[team_pair] if not x]
    return True
    #old method below
    '''
    for state in selected:
        if selected[state] is not None:
            t1, t2, g_n = state
            home = selected[state]
            add(home_games, t1 if home else t2)
            add(away_games, t2 if home else t1)
            add(num_games, (t1, t2))
    for state in num_games:
        t1, t2 = state
        #if all games scheduled
        #remove the last domain element in case where t1 and t2 play odd number of games
        #domain was initialized to size 2*(num_games+1)/2
        if num_games[state] == total_games(m, t1, t2):
            domains[state] = []        
    #check if home/away game limits have been reached, if so remove from domains
    for team in home_games:
        if home_games[team] == (m.TOTAL_GAMES+1)/2:
            for state in domains:
                t1, t2 = state
                if t2 is team:
                    domains[state] = [x for x in domains[state] if x]
                elif t1 is team:
                    domains[state] = [x for x in domains[state] if not x]
    for team in away_games:
        if away_games[team] == (m.TOTAL_GAMES+1)/2:
            for state in domains:
                t1, t2 = state
                if t2 is team:
                    domains[state] = [x for x in domains[state] if not x]
                elif t1 is team:
                    domains[state] = [x for x in domains[state] if x]
    
    return True
    '''        
#set opponent's matchup and update their domain
def valid_matchup(m, sk):
    team, game_num = sk
    domains = m.states[m.domains]
    selected = m.states[m.selected]
    opponent = selected[sk]
    if selected[(opponent, game_num)] is None:
        domains[opponent].remove(team)
        selected[(opponent, game_num)] = team
        return game_counts(m, team) is not None
    return False
    
#get a hash for a team of games left vs. opponents, possible games given schedule
#of opponents, and the counts at each game of possible opponents
def game_counts(m, team):
    opponents_left = {}
    for opponent in m.states[m.domains][team]:
        add(opponents_left, opponent)
    opponents_possible = {}
    game_counts = {}
    for i in range(1, m.TOTAL_GAMES + 1):
        if m.states[m.selected][(team, i)] is None:
            for opponent in opponents_left:
                if m.states[m.selected][(opponent, i)] is None:
                    add(game_counts, i)
                    add(opponents_possible, opponent)
            #no opponents left for game i meaning this schedule won't work
            if i not in game_counts:
                return None
    for opponent in opponents_left:
        #for the remaining game numbers left, check that the opponent
        #has matching game numbers left for at least as many times as they
        #have left to play
        if opponent in opponents_possible:
            if opponents_possible[opponent] < opponents_left[opponent]:
                return None
        else:
            return None
    return game_counts
    