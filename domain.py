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
        self.DIVISIONAL_GAMES = 4
        self.CONF_OPPONENTS_GAMES = 4
        self.REMAINING_CONF_GAMES = 3
        self.INTERCONF_GAMES = 2
        self.TOTAL_GAMES = self.DIVISIONAL_GAMES*4 + self.CONF_OPPONENTS_GAMES*6 + self.REMAINING_CONF_GAMES*4 + self.INTERCONF_GAMES*15
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
            #iterate through domain and add to list but keep track of ones we've already done
            #because some domains are repeated elements
            added_elems = set()
            for dom_elem in self.states[self.domains][dk]:
                if dom_elem not in added_elems:
                    new_states = self.copy()
                    new_states[self.domains][dk].remove(dom_elem)
                    new_states[self.selected][sk] = dom_elem
                    new_obj = domain_class(new_states)
                    if constraint_func(new_obj, sk):
                        domains.append(new_obj)
                    added_elems.add(dom_elem)
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
    def min_key(self):
        min_count = float("inf")
        min_game = None
        best_k = None
        for k in self.states[self.domains]:
            l = len(self.states[self.domains][k])
            if l > 0:
                counts = constraint.game_counts(self, k)
                if counts is not None:
                    l_k = sorted(counts.keys(), key= lambda x: counts[x])[0]
                    if counts[l_k] < min_count:
                        min_count = counts[l_k]
                        min_game = l_k
                        best_k = k
        if best_k is None:
            return (None, None)
        return (best_k, (best_k, min_game))
        
class Venues(TGBase):
    def successors(self):
        return self.successorDomains(Venues, constraint.valid_venue)
    def min_key_helper(self, min_k):
        tx, ty = min_k
        for state in self.states[self.selected]:
            t1, t2, gn = state
            if self.states[self.selected][state] is None and t1 is tx and t2 is ty:
                return state
        return None
    def min_key(self):
        teams_selected = {}
        for state in self.states[self.selected]:
            if self.states[self.selected][state] is not None:
                t1, t2, g_n = state
                constraint.add(teams_selected, t1)
                constraint.add(teams_selected, t2)
                if teams_selected[t1] == self.TOTAL_GAMES:
                    teams_selected.pop(t1, None)
                if teams_selected[t2] == self.TOTAL_GAMES:
                    teams_selected.pop(t2, None)
        
        #teams_selected stores how many teams have selected their home/away for games
        #removing those that have had all their games scheduled with hom/away
        #if it's empty then no team has had a selected home/away yet
        if len(teams_selected) == 0:
            for k in self.states[self.domains]:
                if len(self.states[self.domains][k]) > 0:
                    return (k, self.min_key_helper(k))
                    
        #choose the team with the most selected home/away venues, i.e. least domain size remaining
        min_k = sorted(teams_selected.keys(), key=lambda x: -teams_selected[x])[0]
        best_k = None
        best_len = float("inf")
        #we have the team we want to next choose a venue for, but domains are pairs of teams, 
        #so choose the pair with the remaining least domain size
        for k in self.states[self.domains]:
            t1, t2 = k
            l = len(self.states[self.domains][k])
            if (t1 is min_k or t2 is min_k) and  l > 0 and l < best_len:
                best_len = l
                best_k = k
        return (best_k, self.min_key_helper(best_k)) if best_k is not None else (None, None)     
        
class Dates(TGBase):
    def successors(self):
        return self.successorDomains(Dates, constraint.valid_date)
    def min_key_helper(self, min_k):
        return min_k
        
        