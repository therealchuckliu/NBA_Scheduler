# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 12:24:56 2015

CSP code running DFS on variables

@author: charlesliu
"""

import domain as dom
import datagen as dg
import json
import sys

def write_output(domains, filename):
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
        new_v = []
        for t in k:
            if type(t) is dg.org.Team:
                new_k.append(t.name)
            else:
                new_k.append(t)
        for t in v:
            if type(t) is dg.org.Team:
                new_v.append(t.name)
            else:
                new_v.append(t)
        l.append({'key':new_k, 'value': new_v})
    return l
    
def list2map(league, l):
    m = {}
    for kv in l:
        new_k = []
        new_v = []
        for t in kv['key']:
            if type(t) is unicode:
                new_k.append(league.get_team(t))
            else:
                new_k.append(t)
        for t in kv['value']:
            if type(t) is unicode:
                new_v.append(league.get_team(t))
            else:
                new_v.append(t)
        m[tuple(new_k)] = new_v
    return m

class Scheduler(object):
    
    def __init__(self, year):
        self.data = dg.DataGen(year)

    def create_schedule(self, matchups_json = False, venues_json = False, dates_json = False):
        print "{}: Starting".format(dg.datetime.datetime.today())
        matchups = None
        if matchups_json:
            matchups = read_output(self.data.league, "Matchups")
        else:
            initialState = dom.Matchups(None, self.data.league, self.data.game_indices)
            matchups, matchups_statesExplored = self.DFS(initialState)
            write_output(matchups, "Matchups")        
            print "{}: Matchups, {} states explored".format(dg.datetime.datetime.today(), matchups_statesExplored)
        
        if matchups is not None:
            #now we have our matchups which is a dict of (team, game_num) -> [opponent]
            #we next want to assign home/away so we create a map of the form:
            #(team1, team2, game_num) -> [True/False]
            #where True indicates it's played at team1's venue
            #also team1 < team2 alphabetically
            venues = None
            if venues_json:
                venues = read_output(self.data.league, "Venues")
            else:
                venues_domains = {}
                for state in matchups:
                    t, g_n = state
                    o = matchups[state][0]
                    v_k = (t, o, g_n) if t < o else (o, t, g_n)
                    if v_k not in venues_domains:
                        venues_domains[v_k] = [True, False]
                venueState = dom.Venues(venues_domains)
                venues, venues_statesExplored = self.DFS(venueState)
                write_output(venues, "Venues")
                print "{}: Venues, {} states explored".format(dg.datetime.datetime.today(), venues_statesExplored)
            
            if venues is not None:
                #now we have our venues which is a dict of (team1, team2, game_num) -> [True/False]
                #we next want to assign dates to play so we create a map of the form:
                #(team1, team2, game_num) -> [d1, d2, d3, ...]
                #data.game_indices has around 160 dates for 82 games, so we should minimize the
                #domains to be roughly 2*game_num +/- window dates
                dates = None
                if dates_json:
                    dates = read_output(self.data.league, "Dates")
                else:
                    window = 3
                    dates_domains = {}
                    for state in venues:
                        t1, t2, g_n = state
                        window_min = max(0, 2*g_n - window)
                        window_max = min(max(self.data.game_indices), 2*g_n + window)
                        dates = []
                        for d in self.data.game_indices:
                            if d >= window_min and d <= window_max:
                                dates.append(d)
                        dates_domains[state] = dates
                    dateState = dom.Dates(dates_domains)
                    dates, dates_statesExplored = self.DFS(dateState)
                    write_output(dates, "Dates")
                    print "{}: Dates, {} states explored".format(dg.datetime.datetime.today(), dates_statesExplored)
                    
                if dates is not None:
                    #create a master map of everything of the form:
                    #(team, game_num) -> (opponent, home, dateindex)
                    #where home is true if played at team's venue
                    sched_map = {}
                    for state in venues:
                        t1, t2, g_n = state
                        home = venues[state][0]
                        date = dates[state][0]
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
            successors = state.successors()
            if successors is None:
                return (state.domains, statesExplored)
            else:
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
    f = open('output.txt', 'w')
    sys.stdout = f
    sched = Scheduler(2015)
    today = dg.datetime.datetime.today()
    new_sched = sched.create_schedule()
    fin = dg.datetime.datetime.today()
    elapsed = fin - today
    elapsed = elapsed.total_seconds()
    print elapsed/60.
    f.close()