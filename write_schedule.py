#!/usr/bin/python
import sys, getopt
import scheduler

def main(argv):
    use_matchups = False
    use_debug = False
    use_year = scheduler.dg.datetime.datetime.today().year
    try:
        opts, args = getopt.getopt(argv,"hm:y:d:",["use_matchups=","use_year=", "use_debug"])
    except getopt.GetoptError:
        print 'write_schedule.py -m <true/false> -d <true/false> -y <year>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'write_schedule.py -m <true/false> -d <true/false> -y <year>'
            print '-m Use the Matchups.json file already saved. New schedule will only have new dates. Default False.'
            print '-d Include debug info of progress of CSP. Default False.'
            print '-y What year the schedule should be for. Default current year.'
            sys.exit()
        elif opt in ("-m", "--use_matchups"):
            use_matchups = arg[0].lower() == "t"
        elif opt in ("-d", "--use_debug"):
            use_debug = arg[0].lower() == "t"
        elif opt in ("-y", "--use_year"):
            use_year = int(arg)
    sched = scheduler.Scheduler(use_year, use_matchups)
    sched.set_debug(use_debug)
    sched.create_schedule()
    print "Schedule written to json. Use read_schedule to read from it."

if __name__ == "__main__":
   main(sys.argv[1:])