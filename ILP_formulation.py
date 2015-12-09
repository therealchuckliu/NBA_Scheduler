import pulp
import datagen as dgen
import organization as org
import itertools
import numpy as np
import json

def create_var_string(value):
    # Input in a 3-element-tuple
    return str(value[0])+'-'+str(value[1])+'-'+str(value[2])

# Get a list of teams
team_list = []
data = dgen.DataGen(2015)
conferences = data.league.conferences
for key in conferences.keys():
    conf = conferences[key]
    for div in conf.divisions.keys():
        teams = conf.divisions[div].teams
        for team in teams.keys():
            team_list.append(teams[team])


#Generating list of possible game dates
possible_game_dates = data.game_indices

# Set number of games in the season
num_games = 82          
els = [tuple(x) for x in itertools.combinations(team_list, 2)]
# Create dictionary where keys are string representations of games
#    key: "{team1name}_{team2name}_{gamedate}"
#    value: information about home team and away team and game number
variable_dict = {}
for key in els:
    for date in key[0].home_dates:
        variable_dict[create_var_string((key[0].name,key[1].name,date))] = {'home':key[0].name,'away':key[1].name,'homeDiv':key[0].division.name,\
                                                                           'homeConf':key[0].division.conference.name,\
                                                                           'awayConf':key[1].division.conference.name,\
                                                                           'awayDiv':key[1].division.name,'value':0,'posDate':date}
    for date in key[1].home_dates:
        variable_dict[create_var_string((key[1].name,key[0].name,date))] = {'home':key[1].name,'away':key[0].name,'homeDiv':key[1].division.name,\
                                                                           'homeConf':key[1].division.conference.name,\
                                                                           'awayConf':key[0].division.conference.name,\
                                                                           'awayDiv':key[0].division.name,'value':0,'posDate':date}

x = pulp.LpVariable.dict("Game",variable_dict.keys(), lowBound=0, upBound=1, cat=pulp.LpInteger)


nba_schedule2 = pulp.LpProblem('NBA Schedule',pulp.LpMinimize)
for team in team_list:
    print("Adding conditions for ",team.name)
    nba_schedule2 += sum([x[key] for key in variable_dict.keys() if variable_dict[key]['home'] == team.name \
            or variable_dict[key]['away'] == team.name]) == num_games
    nba_schedule2 += sum([x[key] for key in variable_dict.keys() if variable_dict[key]['home'] == team.name])\
                         == num_games/2
    nba_schedule2 += sum([x[key] for key in variable_dict.keys() if variable_dict[key]['away'] == team.name])\
                         == num_games/2
    
    # Adding constraints for away and home games in a division
    for team_other in team_list:
        if team_other.name != team.name:
            nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeDiv'] == variable_dict[key]['awayDiv'] and\
                        variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) == 2
            nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeDiv'] == variable_dict[key]['awayDiv'] and\
                        variable_dict[key]['home'] == team.name and\
                            variable_dict[key]['away'] == team_other.name]) == 2
            #Out of conference teams
            nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeConf'] != variable_dict[key]['awayConf'] and\
                        variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) == 1
            nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeConf'] != variable_dict[key]['awayConf'] and\
                        variable_dict[key]['home'] == team.name and\
                            variable_dict[key]['away'] == team_other.name]) == 1
    # Ensuring one team plays only once on a single matchday       
    for date in possible_game_dates:
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                            if (variable_dict[key]['home'] == team.name or\
                                variable_dict[key]['away'] == team.name) and \
                            variable_dict[key]['posDate'] == date]) <= 1
    #Adding no away game right after home gain constraints
    num_dates = len(possible_game_dates)
    for idx in range(num_dates-1):
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                            if (variable_dict[key]['home'] == team.name and \
                            variable_dict[key]['posDate'] == idx)]) + \
                            sum([x[key] for key in variable_dict.keys()\
                            if (variable_dict[key]['away'] == team.name and \
                            variable_dict[key]['posDate'] == idx+1)]) <= 1
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                            if (variable_dict[key]['away'] == team.name and \
                            variable_dict[key]['posDate'] == idx)]) + \
                            sum([x[key] for key in variable_dict.keys()\
                            if (variable_dict[key]['away'] == team.name and \
                            variable_dict[key]['posDate'] == idx+1)]) <= 1
    #Adding 3 games in 5 days constraints.
    continuous_games = 5
    for idx in range(continuous_games,num_dates):
        date_range = possible_game_dates[idx-continuous_games:idx]
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                            if (variable_dict[key]['home'] == team.name or\
                                variable_dict[key]['away'] == team.name) and \
                            variable_dict[key]['posDate'] in date_range]) < 4
    
    # Adding constraints for playing 4 games against the 6 selected out-of-division in-conference opponents
    
    teams_in_conf = set(team.division.conference.teams())
    assert(len(teams_in_conf) == 15)
    teams_in_div = set(team.division.teams.values())
    assert(len(teams_in_div) == 5)
    for team_other in team.conf_opponents:
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) == 2
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['home'] == team.name and \
                             variable_dict[key]['away'] == team_other.name]) == 2
    
    # Adding constraints 3 games against the 4 remaining out-of-division in-conference teams    
    remaining_in_conf_teams = teams_in_conf - teams_in_div - team.conf_opponents
    assert len(remaining_in_conf_teams) == 4
    for team_other in remaining_in_conf_teams:
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) <= 2
        nba_schedule2 += sum([x[key] for key in variable_dict.keys()\
                        if ((variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name) or (variable_dict[key]['home'] == team.name and \
                             variable_dict[key]['away'] == team_other.name))]) == 3




#Solving the ILP
nba_schedule2.solve(pulp.solvers.GUROBI_CMD())

#Creating a schedule dictionary
schedule_dict={}
key_list = variable_dict.keys()
for key in key_list:
    if x[key].value() != 0:
        home = variable_dict[key]['home']
        away = variable_dict[key]['away']
        game_no = variable_dict[key]['posDate']
        rev_key = create_var_string((away,home,game_no))
        if rev_key in key_list:
            key_list.remove(rev_key)
for key in key_list:
    if x[key].value() != 0:
        schedule_dict[(team_dict[variable_dict[key]['home']],variable_dict[key]['posDate'])]\
        = (team_dict[variable_dict[key]['away']],'home')
        schedule_dict[(team_dict[variable_dict[key]['away']],variable_dict[key]['posDate'])]\
        = (team_dict[variable_dict[key]['home']],'away')

#Creating matchups and venues and saving them
key_list = variable_dict.keys()
Venues = []
for key in key_list:
    match = {}
    if x[key].value() != 0:
        home = variable_dict[key]['home']
        away = variable_dict[key]['away']
        date = variable_dict[key]['posDate']
        first_team = min(home,away)
        second_team = max(home,away)
        if first_team == home:
            value = True

Matchup = []
for key in schedule_dict.keys():
    match = {}
    team_1 = key[0].name
    game_date = key[1]
    team_2 = schedule_dict[key][0].name
    match["key"] = [team_1,game_date]
    match["value"] = team_2
    Matchup.append(match)
        else:
            value = False
        match["key"] = [first_team, second_team, date]
        match["value"] = value
        Venues.append(match)

##Saving the list to file
with open('Matchups_ILP.json', 'w') as outfile:
    json.dump(Matchup, outfile)
with open('Venues_ILP.json', 'w') as outfile:
    json.dump(Venues, outfile)
