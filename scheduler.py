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
        self.TOTAL_GAMES = 82
        self.DIVISIONAL_GAMES = 4
        self.CONF_OPPONENTS_GAMES = 4
        self.REMAINING_CONF_GAMES = 3
        self.INTERCONF_GAMES = 2
        self.data = dg.DataGen(year)
        self.variables = {}
        #dictionary from (team, game_num) -> variable
        for team in self.data.league.teams():
            for i in range(1, self.TOTAL_GAMES + 1):
                self.variables[(team, i)] = dom.TGDomain(self.data.league, team, i, self.data.game_indices, self.TOTAL_GAMES)
                    
    #methods for printing schedules
    def str_schedule(self, teams = []):
        output = ""
        if type(teams) is str:
            teams = [teams]
        for t in (teams if len(teams) > 0 else self.data.league.teams()):
            team = self.data.league.get_team(t)
            output += team.state + " " + team.name + "\n"
            for i in range(1, self.TOTAL_GAMES + 1):
                dom_elem = self.variables[(team, i)].result()
                output += self.str_game(team, dom_elem) + "\n"
        return output
                
    def str_game(self, team, dom_elem):
        return str(self.data.i2d[dom_elem[2]]) + ": " + team.state + " " + team.name + (" vs. " if dom_elem[1] else " @ ") + dom_elem[0].state + " " + dom_elem[0].name


if __name__ == '__main__':
    sched = Scheduler(2015)
    print sched.str_schedule("Knicks")