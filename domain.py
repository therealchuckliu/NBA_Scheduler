# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 11:55:29 2015

Class storing the domains in the CSP
State representation: (Team, Game Number)
Domain: (Opposing Team, Home/Away (TRUE/FALSE), DateIndex)

@author: charlesliu
"""
import constraint

class TGBase(object):    
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
                    for opponent in league.teams():
                        if opponent is not team:
                            self.add(state, opponent)
                        
    def add(self, state, dom):
        if state in self.domains:
            self.domains[state].append(dom)
        else:
            self.domains[state] = [dom]

    def min_key(self):
        min_len = float("inf")
        min_k = None
        for k in self.domains:
            l = len(self.domains[k])
            if l < min_len and l > 1:
                min_len = l
                min_k = k
        return min_k
    
    def successorDomains(self, domain_class, constraint_func):
        domains = []
        k = self.min_key()
        if k is not None:
            #create a new successor choosing 1 from all of k's domains
            for dom_elem in self.domains[k]:
                new_domain = self.copy()
                new_domain[k] = [dom_elem]
                domain_obj = domain_class(new_domain)
                if constraint_func(domain_obj, k):
                    domains.append(domain_obj)
            return domains
        return None
        
    def successors(self):
        raise NotImplementedError('Base class, use a super class')
     
    #replace deepcopy because it's too slow
    #only need to copy new arrays, not objects within    
    def copy(self):
        domains = {}
        for k in self.domains:
            domains[k] = self.domains[k][:]
        return domains
        
class Matchups(TGBase):
    def successors(self):
        return self.successorDomains(Matchups, constraint.valid_matchup)
        
class Venues(TGBase):
    def successors(self):
        return self.successorDomains(Venues, constraint.valid_venue)
        
class Dates(TGBase):
    def successors(self):
        return self.successorDomains(Dates, constraint.valid_date)
        