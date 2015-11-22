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
                    #specify what dates are possible to minimize domain size
                    #there are ~160 total dates for 82 games so have
                    #game_num -> should be 2*game_num, 2*game_num+1 indices in perfect world
                    #but let's specify a window of 2*game_num - window to 2*game_num + window possible dates
                    window = 5
                    possible_dates = all_dates[max(0, game_num*2 - window):game_num*2 + window+1]
                    
                    #loop through every other team in the league
                    for opponent in league.teams():
                        if opponent is not team:
                            #create a domain element with every home game
                            #for team
                            for home_date in team.home_dates:
                                if home_date in possible_dates:
                                    self.add(state, (opponent, True, home_date))
                            #for opponent
                            for home_date in opponent.home_dates:
                                if home_date in possible_dates:
                                    self.add(state, (opponent, False, home_date))
                        
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
    
    def successors(self):
        successorStates = []
        k = self.min_key()
        if k is not None:
            #create a new successor choosing 1 from all of k's domains
            for dom_elem in self.domains[k]:
                new_domain = self.copy()
                new_domain[k] = [dom_elem]
                new_TGS = TGStates(new_domain)
                if constraint.check(new_TGS, k):
                    successorStates.append(new_TGS)
            return successorStates
        return None
     
    '''
    processes hanging on join for some reason
    def successors_parallel(self):
        q = Queue()
        p = [None]*4
        successorStates = []
        k = self.min_key()
        if k is not None:
            #create a new successor choosing 1 from all of k's domains
            for i in range(len(p)):
                p[i] = Process(target=self.successor, args=(i, k, len(p), q))
                p[i].start()
            for t in p:
                t.join()
            while not q.empty():
                successorStates.append(q.get())
            return successorStates
        return None 
        
    def successor(self, i, k, step, q):
        for dom_elem in self.domains[k][i::step]:
            new_domain = self.copy()
            new_domain[k] = [dom_elem]
            new_TGS = TGStates(new_domain)
            if constraint.check(new_TGS, k):
                q.put(new_TGS)
        print "Done"
        
    def time_successors(self):
        start = time.time()
        serial = self.successors()
        serial_end = time.time()
        parallel = self.successors_parallel()
        par_end = time.time()
        print len(serial)
        print serial_end - start
        print len(parallel)
        print par_end - serial_end
    '''        

    #replace deepcopy because it's too slow
    #only need to copy new arrays, not objects within    
    def copy(self):
        domains = {}
        for k in self.domains:
            domains[k] = self.domains[k][:]
        return domains