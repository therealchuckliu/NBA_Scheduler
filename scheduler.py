# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 12:24:56 2015

CSP code running DFS on variables

@author: charlesliu
"""

import domain as dom
import datagen as dg
import json
import os

def write_output(domains, filename):
    try:
        os.remove(filename)
    except OSError:
        pass
    with open(filename + '.json', 'w') as fp:
        json.dump(map2list(domains), fp)

def read_output(league, filename):
    with open(filename + '.json', 'r') as fp:
        domains = list2map(league, json.load(fp))
    return domains
    
def map2list(m):
    l = []
    for k,v in m.iteritems():
        new_k = []
        new_v = v.name if type(v) is dg.org.Team else v
        for t in k:
            if type(t) is dg.org.Team:
                new_k.append(t.name)
            else:
                new_k.append(t)
        l.append({'key':new_k, 'value': new_v})
    return l
    
def list2map(league, l):
    m = {}
    for kv in l:
        new_k = []
        new_v = league.get_team(kv['value']) if type(kv['value']) is unicode else kv['value']
        for t in kv['key']:
            if type(t) is unicode:
                new_k.append(league.get_team(t))
            else:
                new_k.append(t)
        m[tuple(new_k)] = new_v
    return m

class Scheduler(object):
    
    def __init__(self, year, matchups_json = False, venues_json = False):
        self.data = dg.DataGen(year)
        self.matchups_json = matchups_json
        self.venues_json = venues_json

    def create_schedule(self):
        print "{}: Starting".format(dg.datetime.datetime.today())
        matchups = None
        initialState = dom.Matchups(None, self.data.league, self.data.game_indices)
        if self.matchups_json:
            matchups = read_output(self.data.league, "Matchups")
        else:
            matchups, matchups_statesExplored = self.DFS(initialState)
            print "{}: Matchups, {} states explored, {}".format(dg.datetime.datetime.today(), matchups_statesExplored, matchups is not None)
        
        if matchups is not None:
            write_output(matchups, "Matchups")        
            #now we have our matchups which is a dict of (team, game_num) -> [opponent]
            #we next want to assign home/away so we create a map of the form:
            #(team1, team2, game_num) -> [True/False]
            #where True indicates it's played at team1's venue
            #also team1 < team2 alphabetically
            venues = None
            if self.venues_json:
                venues = read_output(self.data.league, "Venues")
            else:
                venues_domains = {}
                venues_selected = {}
                for state in matchups:
                    t, g_n = state
                    o = matchups[state]
                    sk = (t, o, g_n) if t.name < o.name else (o, t, g_n)
                    dk = (t, o) if t.name < o.name else (o, t)
                    if sk not in venues_selected:
                        venues_selected[sk] = None
                        venues_domains[dk] = [True, False] * ((dom.constraint.total_games(initialState, t, o) + 1)/2)
                venueState = dom.Venues({initialState.domains: venues_domains, initialState.selected: venues_selected})
                venues, venues_statesExplored = self.DFS(venueState)
                print "{}: Venues, {} states explored, {}".format(dg.datetime.datetime.today(), venues_statesExplored, venues is not None)
            
            if venues is not None:
                #now we have our venues which is a dict of (team1, team2, game_num) -> True/False
                #we next want to assign dates to play so we create a map of the form:
                #(team1, team2, game_num) -> [d1, d2, d3, ...]
                #data.game_indices has around 160 dates for 82 games, so we should minimize the
                #domains to be roughly 2*game_num +/- window dates
                write_output(venues, "Venues")
                window = 10
                dates_domains = {}
                dates_selected = {}
                multiplier = len(self.data.game_indices)/initialState.TOTAL_GAMES
                for state in venues:
                    t1, t2, g_n = state
                    window_min = max(0, multiplier*g_n - window)
                    window_max = min(max(self.data.game_indices), multiplier*g_n + window)
                    ht = t1 if venues[state] else t2
                    dates_domains[state] = [d for d in self.data.game_indices if (d >= window_min and d <= window_max and d in ht.home_dates)]
                    dates_selected[state] = None
                dateState = dom.Dates({initialState.domains: dates_domains, initialState.selected: dates_selected})
                dates, dates_statesExplored = self.DFS(dateState)
                print "{}: Dates, {} states explored, {}".format(dg.datetime.datetime.today(), dates_statesExplored, dates is not None)
                
                if dates is not None:
                    write_output(dates, "Dates")
                    #create a master map of everything of the form:
                    #(team, game_num) -> (opponent, home, dateindex)
                    #where home is true if played at team's venue
                    sched_map = {}
                    for state in venues:
                        t1, t2, g_n = state
                        home = venues[state]
                        date = dates[state]
                        sched_map[(t1, g_n)] = (t2, home, date)
                        sched_map[(t2, g_n)] = (t1, not home, date)
                    return sched_map
                    
        return None
        
    def DFS(self, initialState):
        frontier = [initialState]
        statesExplored = 0
        
        while frontier:
            state = frontier.pop()
            statesExplored += 1
            if statesExplored % 100000 == 0:
                num_selected = 0
                for s in state.states[state.selected]:
                    if state.states[state.selected][s] is not None:
                        num_selected += 1
                print "{}: {}, {}, {}".format(dg.datetime.datetime.today(), statesExplored, len(frontier), num_selected)
                
            if state.complete():
                return (state.states[state.selected], statesExplored)
            else:
                successors = state.successors()
                if successors is not None:
                    frontier.extend(successors)
        return (None, statesExplored)
        
                   
    #methods for printing schedules
    def str_schedule(self, schedule, games = 82, teams = []):
        output = ""
        if type(teams) is str:
            teams = [teams]
        for t in (teams if len(teams) > 0 else self.data.league.teams()):
            t = self.data.league.get_team(t) if type(t) is str else t
            for i in range(1, games + 1):
                dom_elem = schedule[(t, i)]
                output += self.str_game(t, dom_elem) + "\n"
        return output
                
    def str_game(self, team, dom_elem):
        opponent, home, dateindex = dom_elem
        return "{},{},{}".format(self.data.i2d[dateindex], team.name if home else opponent.name, opponent.name if home else team.name)

if __name__ == '__main__':
    #The 2 True's correspond to reading in Matches.json and Venues.json so you don't have to recalculate
    sched = Scheduler(2015)
    today = dg.datetime.datetime.today()
    new_sched = sched.create_schedule()
    fin = dg.datetime.datetime.today()
    elapsed = fin - today
    elapsed = elapsed.total_seconds()
    #calculates minutes to run
    print elapsed/60.
    #sched is now a map of (team, game_num) -> (opponent, home, dateindex)