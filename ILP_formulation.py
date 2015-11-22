import pulp
import datagen as dgen
import organization as org
import itertools

def create_var_string(value):
    #Input in a 3-element-tuple
    return str(value[0])+'-'+str(value[1])+'-'+str(value[2])

team_list = []
data = dgen.DataGen(2015)
conferences = data.league.conferences
for key in conferences.keys():
    conf = conferences[key]
    for div in conf.divisions.keys():
        teams = conf.divisions[div].teams
        for team in teams.keys():
            team_list.append(teams[team])
# Set number of games in the season
num_games = 82          
els = [tuple(x) for x in itertools.combinations(team_list, 2)]
# Create dictionary where keys are string representations of games
#    key: "{team1name}_{team2name}_{gamenum}"
#    value: information about home team and away team and game number
variable_dict = {}
for key in els:
    for idx in range(1,num_games+1):
        variable_dict[create_var_string((key[0].name,key[1].name,idx))] = {'home':key[0].name,'away':key[1].name,'homeDiv':key[0].division.name,\
                                                                           'homeConf':key[0].division.conference.name,\
                                                                           'awayConf':key[1].division.conference.name,\
                                                                           'awayDiv':key[1].division.name,'value':0,'gameNum':idx}
        variable_dict[create_var_string((key[1].name,key[0].name,idx))] = {'home':key[1].name,'away':key[0].name,'homeDiv':key[1].division.name,\
                                                                           'homeConf':key[1].division.conference.name,\
                                                                           'awayConf':key[0].division.conference.name,\
                                                                           'awayDiv':key[0].division.name,'value':0,'gameNum':idx}

x = pulp.LpVariable.dict("Game",variable_dict.keys(), lowBound=0, upBound=1, cat=pulp.LpInteger)
#Creating LP Problem
nba_schedule = pulp.LpProblem('NBA Schedule',pulp.LpMinimize)
for team in team_list:
    print("Adding conditions for ",team.name)
    nba_schedule += sum([x[key] for key in variable_dict.keys() if variable_dict[key]['home'] == team.name \
            or variable_dict[key]['away'] == team.name]) == num_games
    '''
    nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if (variable_dict[key]['home'] == team.name or\
                        variable_dict[key]['away'] == team.name) and \
                        variable_dict[key]['homeDiv'] == variable_dict[key]['awayDiv']]) == 16
    '''
    # Adding constraints for away and home games in a division
    for team_other in team_list:
        if team_other.name != team.name:
            nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeDiv'] == variable_dict[key]['awayDiv'] and\
                        variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) == 2
            nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeDiv'] == variable_dict[key]['awayDiv'] and\
                        variable_dict[key]['home'] == team.name and\
                            variable_dict[key]['away'] == team_other.name]) == 2
            #Out of conference teams
            nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeConf'] != variable_dict[key]['awayConf'] and\
                        variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) == 1
            nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['homeConf'] != variable_dict[key]['awayConf'] and\
                        variable_dict[key]['home'] == team.name and\
                            variable_dict[key]['away'] == team_other.name]) == 1
    # Ensuring one team plays only once on a single matchday       
    for num in range(1,num_games+1):
        nba_schedule += sum([x[key] for key in variable_dict.keys()\
                            if (variable_dict[key]['home'] == team.name or\
                                variable_dict[key]['away'] == team.name) and \
                            variable_dict[key]['gameNum'] == num]) == 1
    
    # Adding constraints for playing 4 games against the 6 selected out-of-division in-conference opponents
    
    teams_in_conf = set(team.division.conference.teams())
    assert(len(teams_in_conf) == 15)
    teams_in_div = set(team.division.teams.values())
    assert(len(teams_in_div) == 5)
    for team_other in team.conf_opponents:
        
        nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) == 2
        nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['home'] == team.name and \
                             variable_dict[key]['away'] == team_other.name]) == 2
    
    # Adding constraints 3 games against the 4 remaining out-of-division in-conference teams    
    remaining_in_conf_teams = teams_in_conf - teams_in_div - team.conf_opponents
    assert len(remaining_in_conf_teams) == 4
    for team_other in remaining_in_conf_teams:
        nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name]) <= 2
        nba_schedule += sum([x[key] for key in variable_dict.keys()\
                        if ((variable_dict[key]['away'] == team.name and \
                             variable_dict[key]['home'] == team_other.name) or (variable_dict[key]['home'] == team.name and \
                             variable_dict[key]['away'] == team_other.name))]) == 3
#Saving the LP problem
prob.writeLP("nba_schedule.lp")
#Solving the LP
print("Solving")
nba_schedule.solve()
list_celtics = []
for key in variable_dict.keys():
    if (variable_dict[key]['home'] == 'Celtics' or variable_dict[key]['away'] == 'Celtics') and x[key].value() != 0:
         list_celtics.append((key,x[key].value(),variable_dict[key]['gameNum']))
print list_celtics

