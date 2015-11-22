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
                print "Explored:" + str(statesExplored)
                return state.domains
            else:
                frontier.extend(successors)
        return None
        
                   
    #methods for printing schedules
    def str_schedule(self, schedule, games = 82, teams = []):
        output = ""
        if type(teams) is str:
            teams = [teams]
        for t in (teams if len(teams) > 0 else self.data.league.teams()):
            team = self.data.league.get_team(t)
            for i in range(1, games + 1):
                dom_elem = schedule[(team, i)][0]
                output += self.str_game(team, dom_elem) + "\n"
        return output
                
    def str_game(self, team, dom_elem):
        opponent, home, dateindex = dom_elem
        return "{},{},{}".format(self.data.i2d[dateindex], team.name if home else opponent.name, opponent.name if home else team.name)

if __name__ == '__main__':
    sched = Scheduler(2015)
    today = dg.datetime.datetime.today()
    new_sched = sched.create_schedule()
    fin = dg.datetime.datetime.today()
    elapsed = fin - today
    elapsed = elapsed.total_seconds()
    print elapsed/60.
    #output new sched to file
    fn = str(today).split()[0]
    f = open(fn, 'w')
    f.write(sched.str_schedule(new_sched))
    f.close()
    