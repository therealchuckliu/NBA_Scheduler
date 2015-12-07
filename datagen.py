# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 10:39:40 2015
Module for Data Generation
Functions related to extracting dates
Logic for Divisions/NBA teams

@author: charlesliu
"""
import datetime
import organization as org
import conf_opponents as cf

class DataGen:
    
    def __init__(self, year):
        #The first date of the NBA season is between Oct 20-30
        start_d = datetime.date(year, 10, org.np.random.randint(20, 30))
        #The last date of the NBA season is between April 10-20
        end_d = datetime.date(year+1, 4, org.np.random.randint(20, 30))
        #No game on Christmas Eve
        c_eve = datetime.date(year, 12, 24)
        #No games over All-Star week, choose random week in February
        as_week = org.np.random.randint(1, 5)

        #create a master list of all dates in between start_d and end_d
        dates = []
        curr_d = start_d
        while(curr_d != end_d):
            dates.append(curr_d)
            curr_d += datetime.timedelta(days=1)
            #Skip Christmas Eve
            if curr_d == c_eve:
                curr_d += datetime.timedelta(days=1)
            
            #Skip All-Star Week
            if curr_d.month == 2 and curr_d.weekday() == 0 and curr_d.day > (as_week-1)*7 and curr_d.day <= as_week*7:
                curr_d += datetime.timedelta(days=7)
            
            #Skip first Monday of April for NCAA Championship
            if curr_d.month == 4 and curr_d.weekday() == 0 and curr_d.day <= 7:
                curr_d += datetime.timedelta(days=1)
        
        #dates -> integer translation
        indices = range(len(dates))
        
        #dictionary from dates to integer index
        self.d2i = dict(zip(dates, indices))
        #dictionary from integer index to dates
        self.i2d = dict(zip(indices, dates))
        #list of game dates (will update after home game dates generated below)
        self.game_indices = set(indices)
        
        #Structure of the league
        self.league = org.League()
        for conference in ["Eastern", "Western"]:
            self.league.conferences[conference] = org.Conference(conference)
        self.add_division(self.league.conferences["Eastern"], ["Atlantic", "Central", "Southeast"])
        self.add_division(self.league.conferences["Western"], ["Northwest", "Pacific", "Southwest"])
        self.add_teams(self.league.get_division("Atlantic"), 
                       [("Toronto", "Raptors"), 
                        ("Boston", "Celtics"), 
                        ("New York", "Knicks"),
                        ("Brooklyn", "Nets"), 
                        ("Philadelphia", "76ers")], indices)
        self.add_teams(self.league.get_division("Central"), 
                       [("Cleveland", "Cavaliers"), 
                        ("Chicago", "Bulls"), 
                        ("Indiana", "Pacers"),
                        ("Detroit", "Pistons"), 
                        ("Milwaukee", "Bucks")], indices)
        self.add_teams(self.league.get_division("Southeast"), 
                       [("Atlanta", "Hawks"), 
                        ("Miami", "Heat"), 
                        ("Charlotte", "Hornets"),
                        ("Washington", "Wizards"), 
                        ("Orlando", "Magic")], indices)
        self.add_teams(self.league.get_division("Northwest"), 
                       [("Oklahoma City", "Thunder"), 
                        ("Utah", "Jazz"), 
                        ("Denver", "Nuggets"),
                        ("Minnesota", "Timberwolves"), 
                        ("Portland", "Trailblazers")], indices)
        self.add_teams(self.league.get_division("Pacific"), 
                       [("Golden State", "Warriors"), 
                        ("Los Angeles", "Clippers"), 
                        ("Phoenix", "Suns"),
                        ("Sacramento", "Kings"), 
                        ("Los Angeles", "Lakers")], indices)
        self.add_teams(self.league.get_division("Southwest"), 
                       [("San Antonio", "Spurs"), 
                        ("Dallas", "Mavericks"), 
                        ("Memphis", "Grizzlies"),
                        ("Houston", "Rockets"), 
                        ("New Orleans", "Pelicans")], indices)
                        
        #All home game dates have been removed from game_dates in add_teams 
        #now set game_indices to all indices - game_indices
        #i.e., game_indices = all available dates for games
        self.game_indices = list(set(indices) - self.game_indices)
        
        #set the 6 conference opponents that team will play 4 times
        for team in self.league.teams():
            for opp in cf.conf_opponents[team.name]:
                opp_team = self.league.get_team(opp)
                team.conf_opponents.add(opp_team)
                    
        
    def add_division(self, conference, divisions):
        for division in divisions:
            conference.divisions[division] = org.Division(division, conference)
                               
    def add_teams(self, division, teams, indices):
        for state, team in teams:
            division.teams[team] = org.Team(state, team, division, indices)
            #remove the home indices from game_indices
            #see comment at end of init
            for idx in division.teams[team].home_dates:
                self.game_indices.discard(idx)
