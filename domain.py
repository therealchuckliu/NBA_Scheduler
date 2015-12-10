# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 11:55:29 2015

Class storing the domains in the CSP
State representation: (Team, Game Number)
Domain: (Opposing Team, Home/Away (TRUE/FALSE), DateIndex)

@author: charlesliu
"""
import constraint
import random

class TGBase(object):
    def __init__(self, states = None, league = None, all_dates = None):
        self.DIVISIONAL_GAMES = 4
        self.CONF_OPPONENTS_GAMES = 4
        self.REMAINING_CONF_GAMES = 3
        self.INTERCONF_GAMES = 2
        self.TOTAL_GAMES = self.DIVISIONAL_GAMES*4 + self.CONF_OPPONENTS_GAMES*6 + self.REMAINING_CONF_GAMES*4 + self.INTERCONF_GAMES*15
        self.states = {} if states is None else states
        self.domains = "domains"
        self.selected = "selected"
        self.master_dates = "master_dates"
        self.current_cost = 'current_cost'
        if len(self.states) == 0:
            domains = {}
            selected = {}
            for team in league.teams():
                #formulate a list of the games it has to play
                games = []
                for opponent in league.teams():
                    if opponent is not team:
                        games += [opponent]*constraint.total_games(self, team, opponent)
                random.shuffle(games)
                domains[team] = games
                for i in range(1, self.TOTAL_GAMES+1):
                    selected[(team, i)] = None
            self.states[self.domains] = domains
            self.states[self.selected] = selected

        if self.current_cost not in self.states:
            self.states[self.current_cost] = 1230
        if self.master_dates not in self.states:
            self.states[self.master_dates] = {}


    def min_key(self):
        min_len = float("inf")
        min_k = None
        for k in self.states[self.domains]:
            l = len(self.states[self.domains][k])
            if l < min_len and l > 0:
                min_len = l
                min_k = k
        if min_k is None:
            return (None, None)
        return (min_k, self.min_key_helper(min_k))

    def min_key_helper(self, min_k):
        raise NotImplementedError('Base class, use a super class')

    def successorDomains(self, domain_class, constraint_func):
        domains = []
        dk, sk = self.min_key()
        if dk is not None and sk is not None:
            #iterate through domain and add to list but keep track of ones we've already done
            #because some domains are repeated elements
            added_elems = set()
            for dom_elem in self.ordered_domain(dk, sk):
                if dom_elem not in added_elems:
                    new_obj = self.copy_states(domain_class, dk, sk, dom_elem)
                    if constraint_func(new_obj, sk):
                        domains.append(new_obj)
                    added_elems.add(dom_elem)
            return domains
        return None
    def cost(self, dk, sk, dom_elem):
        # Returns the cost of assigning dom_elem to sk
        return 0

    def ordered_domain(self, dk, sk):
        return self.states[self.domains][dk]

    def copy_states(self, domain_class, dk, sk, dom_elem):
        new_states = self.copy()
        new_states[self.domains][dk].remove(dom_elem)
        new_states[self.selected][sk] = dom_elem
        new_obj = domain_class(new_states)
        return new_obj

    def successors(self):
        raise NotImplementedError('Base class, use a super class')

    def complete(self):
        for k in self.states[self.selected]:
            if self.states[self.selected][k] is None:
                return False
        return True

    #replace deepcopy because it's too slow
    #only need to copy new arrays, not objects within
    def copy(self):
        domains = {}
        selected = {}
        master_dates = {}
        for k in self.states[self.domains]:
            domains[k] = self.states[self.domains][k][:]

        for k in self.states[self.selected]:
            selected[k] = self.states[self.selected][k] if self.states[self.selected][k] is not None else None

        for k in self.states[self.master_dates]:
            master_dates[k] = self.states[self.master_dates][k][:]
        return {self.domains:domains, self.selected:selected, self.master_dates:master_dates, self.current_cost: self.states[self.current_cost]}

class Matchups(TGBase):
    def successors(self):
        return self.successorDomains(Matchups, constraint.valid_matchup)
    def min_key(self):
        best_count = float("inf")
        best_game = None
        best_k = None
        for k in self.states[self.domains]:
            l = len(self.states[self.domains][k])
            if l > 0:
                counts = constraint.game_counts(self, k)
                if counts is not None:
                    l_k = sorted(counts.keys(), key= lambda x: counts[x])[0]
                    if counts[l_k] < best_count:
                        best_count = counts[l_k]
                        best_game = l_k
                        best_k = k
        if best_k is None:
            return (None, None)
        return (best_k, (best_k, best_game))
    def ordered_domain(self, dk, sk):
        domain_dict = {}
        for dom_elem in self.states[self.domains][dk]:
            if dom_elem not in domain_dict:
                new_obj = self.copy_states(Matchups, dk, sk, dom_elem)
                counts = constraint.game_counts(new_obj, dk)
                if counts is not None:
                    if len(counts) == 0:
                        domain_dict[dom_elem] = float("inf")
                    else:
                        l_k = sorted(counts.values())[0]
                        domain_dict[dom_elem] = l_k
        #order domain elements from lowest to highest, when this gets added
        #to the states list, it will be read backwards so highest to lowest
        return sorted(domain_dict.keys(), key= lambda x: domain_dict[x])

class Venues(TGBase):
    def successors(self):
        return self.successorDomains(Venues, constraint.valid_venue)
    def min_key_helper(self, min_k):
        tx, ty = min_k
        # Find matchup between tx, ty with the lowest game number
        min_gn = float('inf')
        min_state = None
        for state in self.states[self.selected]:
            t1, t2, gn = state
            if self.states[self.selected][state] is None and t1 is tx and t2 is ty and gn < min_gn:
                    min_gn = gn
                    min_state = state
        return min_state

    def min_key(self):
        '''
            Goal is to first assign the games for teams with opponents they have an
            even number of games with. Then once they are all assigned we try to fit
            the remaining games, there's a little more flexibility there as it's not strict
            split
        '''
        teams_selected_even = {}
        teams_selected_odd = {}
        #calculate number of games against even-gamed opponents
        total_even_games = 4*self.DIVISIONAL_GAMES + 6*self.CONF_OPPONENTS_GAMES + 15*self.INTERCONF_GAMES
        total_odd_games = self.TOTAL_GAMES - total_even_games
        begin_search = True
        for state in self.states[self.selected]:
            if self.states[self.selected][state] is not None:
                begin_search = False
                t1, t2, g_n = state
                total_games = total_even_games if constraint.total_games(self, t1, t2)%2==0 else total_odd_games
                teams_selected = teams_selected_even if constraint.total_games(self, t1, t2)%2==0 else teams_selected_odd
                constraint.add(teams_selected, t1)
                constraint.add(teams_selected, t2)
                if teams_selected[t1] == total_games:
                    teams_selected.pop(t1, None)
                if teams_selected[t2] == total_games:
                    teams_selected.pop(t2, None)

        #teams_selected_* stores how many teams have selected their home/away for games
        #removing those that have had all their games scheduled with home/away
        #if it's empty then no team has had a selected home/away yet
        if begin_search:
            for k in self.states[self.domains]:
                if len(self.states[self.domains][k]) > 0 and constraint.total_games(self, k[0], k[1])%2==0:
                    return (k, self.min_key_helper(k))
        elif len(teams_selected_even) == 0 and len(teams_selected_odd) == 0:
            for k in self.states[self.domains]:
                if len(self.states[self.domains][k]) > 0 and constraint.total_games(self, k[0], k[1])%2!=0:
                    return (k, self.min_key_helper(k))

        #choose the team with the most selected home/away venues, i.e. least domain size remaining
        min_k = None
        if len(teams_selected_even) > 0:
            min_k = sorted(teams_selected_even.keys(), key=lambda x: -teams_selected_even[x])[0]
        elif len(teams_selected_odd) > 0:
            min_k = sorted(teams_selected_odd.keys(), key=lambda x: -teams_selected_odd[x])[0]
        else:
            return (None, None)
        best_k_even = None
        best_len_even = float("-inf")
        best_k_odd = None
        best_len_odd = float("-inf")
        #we have the team we want to next choose a venue for, but domains are pairs of teams,
        #so choose the pair with the largest remaining games to choose from
        for k in self.states[self.domains]:
            t1, t2 = k
            #store best_k for opponents u play even/odd # of games w/
            l = len(self.states[self.domains][k])
            if t1 is min_k or t2 is min_k:
                if constraint.total_games(self, t1, t2)%2 == 0:
                    if l > 0 and l > best_len_even:
                        best_len_even = l
                        best_k_even = k
                else:
                    if l > 0 and l > best_len_odd:
                        best_len_odd = l
                        best_k_odd = k
        #want to first assign games with teams you play even # of games with
        if best_k_even is not None:
            return (best_k_even, self.min_key_helper(best_k_even))
        elif best_k_odd is not None:
            return (best_k_odd, self.min_key_helper(best_k_odd))
        else:
            return (None, None)

    def ordered_domain(self, dk, sk):
        t1, t2 = dk
        home_games, away_games, num_games = constraint.home_away_num_game_dicts(sk, self.states[self.selected])
        if dk not in num_games or num_games[dk] < constraint.total_games(self, t1, t2):
            total = (self.TOTAL_GAMES + 1)/2
            t1_home = home_games[t1] if t1 in home_games else 0
            t1_away = away_games[t1] if t1 in away_games else 0
            t2_home = home_games[t2] if t2 in home_games else 0
            t2_away = away_games[t2] if t2 in away_games else 0
            '''
                If there's enough of home or away games only try the other
                Check that it's in the domain, the opponents where you play an
                odd number of games against can tilt the number of home/away games
                on inconsistent states
            '''
            if (t1_home == total or t2_away == total) and False in self.states[self.domains][dk]:
                return self.domain_dates(False, sk, True)
            elif (t1_away == total or t2_home == total) and True in self.states[self.domains][dk]:
                return self.domain_dates(True, sk, True)
            '''
                We want to try the T/F that there's more of in the domain first
                Check for reverse because DFS takes states in reverse order
            '''
            T_num = len([x for x in self.states[self.domains][dk] if x])
            F_num = len(self.states[self.domains][dk]) - T_num
            if (T_num == F_num):
                t_first = random.choice([True,False])
            else:
                t_first = T_num < F_num
            return self.order_TF(dk, t_first, sk)
        else:
            return []

    def order_TF(self, dk, t_first, sk):
        true_dates = []
        false_dates = []
        dates = []
        if t_first in self.states[self.domains][dk]: true_dates = self.domain_dates(t_first, sk)
        if (not t_first) in self.states[self.domains][dk]: false_dates = self.domain_dates(not t_first, sk)

        true_dates.sort(key=lambda x: -abs(x[0] - (sk[2]-1)*2))
        false_dates.sort(key=lambda x: -abs(x[0] - (sk[2]-1)*2))
        for i in range(max(len(true_dates), len(false_dates))):
            true_index = len(true_dates) - 1 - i
            false_index = len(false_dates) - 1 - i
            if true_index < 0:
                dates = [false_dates[false_index]] + dates
            elif false_index < 0:
                dates = [true_dates[true_index]] + dates
            else:
                dates = [false_dates[false_index]] + dates
                dates = [true_dates[true_index]] + dates

        return dates

    def domain_dates(self, t_f, sk, sort = False):
        dates = []
        for i in self.states[self.master_dates][(sk, t_f)]:
            dates.append((i, t_f))
        if sort:
            dates.sort(key=lambda x: -abs(x[0] - (sk[2]-1)*2))
        return dates

    def copy_states(self, domain_class, dk, sk, dom_elem):
        date, t_f = dom_elem
        t, o, g_n = sk
        new_states = self.copy()
        new_states[self.domains][dk].remove(t_f)
        new_states[self.selected][sk] = dom_elem
        #pruning master dates
        new_states[self.master_dates][(sk, t_f)][:] = [date]
        new_states[self.master_dates][(sk, not t_f)][:] = []
        for selected_state in self.states[self.selected]:
            tx, ox, g_nx = selected_state
            if (tx is t or ox is t) or (tx is o or ox is o):
                if g_nx < g_n:
                    new_states[self.master_dates][(selected_state, True)][:] = [d for d in new_states[self.master_dates][(selected_state, True)] if d < date]
                    new_states[self.master_dates][(selected_state, False)][:] = [d for d in new_states[self.master_dates][(selected_state, False)] if d < date]
                if g_nx > g_n:
                    new_states[self.master_dates][(selected_state, True)][:] = [d for d in new_states[self.master_dates][(selected_state, True)] if d > date]
                    new_states[self.master_dates][(selected_state, False)][:] = [d for d in new_states[self.master_dates][(selected_state, False)] if d > date]

        #new_states[self.current_cost] = self.states[self.current_cost] + added_cost
        new_states[self.current_cost] = self.cost(dk, sk, dom_elem)

        new_obj = domain_class(new_states)
        # update cost

        return new_obj

    def cost(self, dk, sk, dom_elem):
        # Returns the cost of assigning dom_elem to sk
        # Idea:
        # Next assignment: (t,o,g_n) --> (date, t_f)
        t, o, g_n = sk
        date, t_f = dom_elem
        # we assign determine cost based on sum of (maximum number of games (m) in n consecutive nights for each team)
        m = 4
        n = 5
        # number of assignments that have already been made
        num_selected = 0
        # Cost Function:
        # Keys are 5-day window start date, values are counts
        o_num_games_in_n_nights = {}
        t_num_games_in_n_nights = {}
        min_window_start = max(0, date - (n - 1))
        max_window_start = date + n - 1
        for window_start in range(min_window_start, max_window_start + 1):
            t_num_games_in_n_nights[window_start] = 0
            o_num_games_in_n_nights[window_start] = 0
        # Iterate over all assigned dates, and count the number of games
        # o and t play in each n day window containing date
        for matchup in self.states[self.selected]:
            if self.states[self.selected][matchup] is not None:
                num_selected += 1
                tx,ox,g_nx = matchup
                datex, t_fx = self.states[self.selected][matchup]
                # Check if in date range
                if datex >= min_window_start and datex <= max_window_start:
                    # Check if t or o are in the game
                    if tx is t or ox is t:
                        t_num_games_in_n_nights[datex] += 1
                    elif tx is o or ox is o:
                        o_num_games_in_n_nights[datex] += 1
        max_games_in_n_nights = max([max(t_num_games_in_n_nights.values()),max(o_num_games_in_n_nights.values())])
        total_games = len(self.states[self.selected])
        current_cost = total_games - num_selected + abs(date - (g_n-1)*2)
        if max_games_in_n_nights >= m:
            return current_cost + 10000
        else:
            return current_cost

