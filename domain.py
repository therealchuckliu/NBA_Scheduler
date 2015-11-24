# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 11:55:29 2015

Class storing the domains in the CSP
State representation: (Team, Game Number)
Domain: (Opposing Team, Home/Away (TRUE/FALSE), DateIndex)

@author: charlesliu
"""
import constraint
import random

class TGBase(object):    
    def __init__(self, states = None, league = None, all_dates = None):
        self.TOTAL_GAMES = 82
        self.DIVISIONAL_GAMES = 4
        self.CONF_OPPONENTS_GAMES = 4
        self.REMAINING_CONF_GAMES = 3
        self.INTERCONF_GAMES = 2
        self.states = {} if states is None else states
        self.domains = "domains"
        self.selected = "selected"
        if len(self.states) == 0:
            domains = {}
            selected = {}
            for team in league.teams():
                #formulate a list of the games it has to play
                games = []
                for opponent in league.teams():
                    if opponent is not team:
                        games += [opponent]*constraint.total_games(self, team, opponent)
                random.shuffle(games)
                domains[team] = games
                for i in range(1, self.TOTAL_GAMES+1):
                    selected[(team, i)] = None
            self.states[self.domains] = domains
            self.states[self.selected] = selected
            

    def min_key(self):
        min_len = float("inf")
        min_k = None
        for k in self.states[self.domains]:
            l = len(self.states[self.domains][k])
            if l < min_len and l > 0:
                min_len = l
                min_k = k
        if min_k is None:
            return (None, None)
        return (min_k, self.min_key_helper(min_k))
        
    def min_key_helper(self, min_k):
        raise NotImplementedError('Base class, use a super class')
    
    def successorDomains(self, domain_class, constraint_func):
        domains = []
        dk, sk = self.min_key()
        if dk is not None and sk is not None:
            #iterate through domain and add to list
            for dom_elem in self.states[self.domains][dk]:
                new_states = self.copy()
                new_states[self.domains][dk].remove(dom_elem)
                new_states[self.selected][sk] = dom_elem
                new_obj = domain_class(new_states)
                if constraint_func(new_obj, sk):
                    domains.append(new_obj)
            return domains
        return None
        
    def successors(self):
        raise NotImplementedError('Base class, use a super class')
        
    def complete(self):
        for k in self.states[self.selected]:
            if self.states[self.selected][k] is None:
                return False
        return True
     
    #replace deepcopy because it's too slow
    #only need to copy new arrays, not objects within    
    def copy(self):
        domains = {}
        selected = {}
        for k in self.states[self.domains]:
            domains[k] = self.states[self.domains][k][:]
        for k in self.states[self.selected]:
            selected[k] = self.states[self.selected][k]
        return {self.domains:domains, self.selected:selected}
        
class Matchups(TGBase):
    def successors(self):
        return self.successorDomains(Matchups, constraint.valid_matchup)
    def min_key_helper(self, min_k):
        for i in range(1, self.TOTAL_GAMES + 1):
            if self.states[self.selected][(min_k, i)] is None:
                return (min_k, i)
        return None
        
class Venues(TGBase):
    def successors(self):
        return self.successorDomains(Venues, constraint.valid_venue)
    def min_key_helper(self, min_k):
        tx, ty = min_k
        for state in self.states[self.selected]:
            t1, t2, gn = state
            if self.states[self.selected][state] is None and tx is t1 and ty is t2:
                return state
        return None
        
class Dates(TGBase):
    def successors(self):
        return self.successorDomains(Dates, constraint.valid_date)
    def min_key_helper(self, min_k):
        return min_k
        
        