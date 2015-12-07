#!/usr/bin/python
import sys, getopt
import scheduler

def main(argv):
    team = ''
    num_games = 82
    sched = scheduler.Scheduler(2015, True, True)
    new_sched = sched.create_schedule()
    try:
        opts, args = getopt.getopt(argv,"ht:n:",["team=","num_game="])
    except getopt.GetoptError:
        print 'read_schedule.py -t <team1,team2,...> -n <num games>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'read_schedule.py -t <team1,team2,...> -n <num games>'
            print 'The list of possible teams are:'
            print sorted(sched.data.league.teams(), key=lambda x: x.name)
            print 'num games between 1 and 82'
            print 'Output will be of the form Date,Home Team,Away Team'
            sys.exit()
        elif opt in ("-t", "--team"):
            team = arg.replace(" ", "").split(",")
        elif opt in ("-n", "--num_games"):
            num_games = int(arg)
    print sched.str_schedule(new_sched, num_games, team)

if __name__ == "__main__":
   main(sys.argv[1:])