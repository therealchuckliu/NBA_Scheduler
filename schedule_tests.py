def list_compare(ref_value,list_check):
    for elem in list_check:
        if elem != ref_value:
            return False
    return True

def schedule_test(schedule_dict,num_games):
    teams = set(map(lambda x:x[0],schedule_dict.keys()))
    teamNames = set(map(lambda x:x[0].name,schedule_dict.keys()))
    for team in teams:
        #print "Testing schedule for:",team.name
        home_count = 0
        away_count = 0
        home_cdiv = {}
        away_cdiv = {}
        total_cdiv = {}
        home_div = {}
        away_div = {}
        total_div = {}
        home_oconf = {}
        away_oconf = {}
        total_oconf = {}
        home_odiv = {}
        away_odiv = {}
        total_odiv = {}
        for conf_team in team.conf_opponents:
            home_cdiv[conf_team.name] = 0
            away_cdiv[conf_team.name] = 0
            total_cdiv[conf_team.name] = 0
        for div in team.division.teams:
            if div != team.name:
                home_div[div] = 0
                away_div[div] = 0
                total_div[div] = 0
        out_conf_set = set(teams) - set(team.division.conference.teams())
        for out_conf in out_conf_set:
            home_oconf[out_conf.name] = 0
            away_oconf[out_conf.name] = 0
            total_oconf[out_conf.name] = 0
        out_div_set = set(team.division.conference.teams()) - set(team.conf_opponents) - set(team.division.teams.values())
        for out_div in out_div_set:
            home_odiv[out_div.name] = 0
            away_odiv[out_div.name] = 0
            total_odiv[out_div.name] = 0
        #Running through all the games:
        for num in range(1,num_games+1):
            (opponent,g_type) = schedule_dict[(team,num)]
            
            if g_type == 'away':
                other = 'home'
            else:
                other = 'away'
            assert(schedule_dict[(opponent,num)] == (team,other))
            if g_type == 'home':
                home_count +=1
            else:
                away_count +=1
            if opponent in team.conf_opponents:
                if g_type == 'home':
                    home_cdiv[opponent.name] +=1
                    total_cdiv[opponent.name] +=1
                else:
                    away_cdiv[opponent.name] +=1
                    total_cdiv[opponent.name] +=1
            if opponent in out_conf_set:
                if g_type == 'home':
                    home_oconf[opponent.name] +=1
                    total_oconf[opponent.name] +=1
                else:
                    away_oconf[opponent.name] +=1
                    total_oconf[opponent.name] +=1
                    
            if opponent.name in team.division.teams:
                if g_type == 'home':
                    home_div[opponent.name] +=1
                    total_div[opponent.name] +=1
                else:
                    away_div[opponent.name] +=1
                    total_div[opponent.name] +=1
            
            if opponent in out_div_set:
                if g_type == 'home':
                    home_odiv[opponent.name] +=1
                    total_odiv[opponent.name] +=1
                else:
                    away_odiv[opponent.name] +=1
                    total_odiv[opponent.name] +=1
        
        #Checking out of conference:
        assert(list_compare(1, home_oconf.values()) == True)
        assert(list_compare(1, away_oconf.values()) == True)
        assert(list_compare(2, total_oconf.values()) == True)
        
        #Checking in 3 game teams:
        assert(list_compare(3, total_odiv.values()) == True)
        assert(all(i <= 2 for i in home_odiv.values()) == True)
        assert(all(i >= 1 for i in home_odiv.values()) == True)
        assert(all(i <= 2 for i in away_odiv.values()) == True)
        assert(all(i >= 1 for i in away_odiv.values()) == True)
        
        #Checking in division:
        assert(list_compare(2, home_div.values()) == True)
        assert(list_compare(2, away_div.values()) == True)
        assert(list_compare(4, total_div.values()) == True)
        
        #Checking in conference:
        assert(list_compare(2, home_cdiv.values()) == True)
        assert(list_compare(2, away_cdiv.values()) == True)
        assert(list_compare(4, total_cdiv.values()) == True)
        
        #Checking number of home and away games:
        assert(home_count == num_games/2)
        assert(away_count == num_games/2)
        print 'Test passed for:',team.name
    print 'All tests passed'
