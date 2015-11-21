# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 11:55:29 2015

Class representing the domain in the CSP
State representation: (Team, Game Number)
Domain: (Opposing Team, Home/Away (TRUE/FALSE), DateIndex)

@author: charlesliu
"""

class TGDomain(object):    
    def __init__(self, league, team, game_num, all_dates, total_games):
        self.domain = []
        #can omit these dates given game_num
        omit_dates = set(all_dates[0:game_num-1])
        omit_dates = omit_dates | set(all_dates[game_num - total_games : ]) if game_num < total_games else omit_dates

        #loop through every other team in the league
        for opponent in league.teams():
            if opponent is not team:
                #create a domain element with every home game
                #for team
                for home_date in team.home_dates:
                    if home_date not in omit_dates:
                        self.domain.append((opponent, True, home_date))
                #for opponent
                for home_date in opponent.home_dates:
                    if home_date not in omit_dates:
                        self.domain.append((opponent, False, home_date))
        self.domain.sort(key= lambda x: x[2])
                                
    def result(self):
        return self.domain[0] if len(self.domain) > 0 else None
        
    def __repr__(self):
        return "Domain: " + str(len(self.domain))