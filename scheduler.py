# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 12:24:56 2015

CSP code running DFS on variables

@author: charlesliu
"""

import domain as dom
import datagen as dg

class Scheduler(object):
    
    def __init__(self, year):
        self.data = dg.DataGen(year)

    def create_schedule(self):
        initialstate = dom.TGStates(None, self.data.league, self.data.game_indices)
        frontier = [initialstate]
        statesExplored = 0
        
        while frontier:
            state = frontier.pop()
            statesExplored += 1
            successors = state.successors()
            if successors is None:
                return state.domains
            else:
                frontier.extend(successors)
        return None
        
                   
    #methods for printing schedules
    def str_schedule(self, games = 1, teams = []):
        output = ""
        if type(teams) is str:
            teams = [teams]
        for t in (teams if len(teams) > 0 else self.data.league.teams()):
            team = self.data.league.get_team(t)
            output += team.state + " " + team.name + "\n"
            for i in range(1, games + 1):
                dom_elem = self.variables[(team, i)][0]
                output += self.str_game(team, dom_elem) + "\n"
        return output
                
    def str_game(self, team, dom_elem):
        return str(self.data.i2d[dom_elem[2]]) + ": " + team.state + " " + team.name + (" vs. " if dom_elem[1] else " @ ") + dom_elem[0].state + " " + dom_elem[0].name

if __name__ == '__main__':
    sched = Scheduler(2015)
    new_sched = sched.create_schedule()
    