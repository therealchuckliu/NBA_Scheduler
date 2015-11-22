# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 11:55:29 2015

Class storing the domains in the CSP
State representation: (Team, Game Number)
Domain: (Opposing Team, Home/Away (TRUE/FALSE), DateIndex)

@author: charlesliu
"""
import constraint

class TGStates(object):    
    def __init__(self, domains = None, league = None, all_dates = None):
        self.TOTAL_GAMES = 82
        self.DIVISIONAL_GAMES = 4
        self.CONF_OPPONENTS_GAMES = 4
        self.REMAINING_CONF_GAMES = 3
        self.INTERCONF_GAMES = 2
        self.domains = {} if domains is None else domains
        if len(self.domains) == 0:
            for team in league.teams():
                for game_num in range(1, self.TOTAL_GAMES+1):
                    state = (team, game_num)
                    #can omit these dates given game_num
                    omit_dates = set(all_dates[0:game_num-1])
                    omit_dates = omit_dates | set(all_dates[game_num - self.TOTAL_GAMES : ]) if game_num < self.TOTAL_GAMES else omit_dates
            
                    #loop through every other team in the league
                    for opponent in league.teams():
                        if opponent is not team:
                            #create a domain element with every home game
                            #for team
                            for home_date in team.home_dates:
                                if home_date not in omit_dates:
                                    self.add(state, (opponent, True, home_date))
                            #for opponent
                            for home_date in opponent.home_dates:
                                if home_date not in omit_dates:
                                    self.add(state, (opponent, False, home_date))
                        
    def add(self, state, dom):
        if state in self.domains:
            self.domains[state].append(dom)
        else:
            self.domains[state] = [dom]
    
    def successors(self):
        successorStates = []
        for k in self.domains:
            if len(self.domains[k]) > 1:
                #create a new successor choosing 1 from all of k's domains
                for dom_elem in self.domains[k]:
                    new_domain = self.copy()
                    new_domain[k] = [dom_elem]
                    new_TGS = TGStates(new_domain)
                    if constraint.check(new_TGS, k):
                        successorStates.append(new_TGS)
                return successorStates
        return None

    #replace deepcopy because it's too slow
    #only need to copy new arrays, not objects within    
    def copy(self):
        domains = {}
        for k in self.domains:
            domains[k] = self.domains[k][:]
        return domains