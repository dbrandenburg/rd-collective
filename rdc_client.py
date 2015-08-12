#!/usr/bin/env python3

import optparse
import redis
import rdc_handler


def main():

    usage = "usage: rdc_client.py [options] hostname"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-r", "--redishost",
                      dest="redis_host",
                      default="localhost",
                      help="redis host")

    parser.add_option("-p", "--redisport",
                      dest="redis_port",
                      default=6379,
                      help="redis port")

    parser.add_option("-d", "--redisdb",
                      dest="redis_db",
                      default=0,
                      help="redis database")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        print("Too few arguments given.")
        parser.print_help()
        exit(1)
    elif len(args) > 1:
        print("Too many arguments given.")
        parser.print_help()
        exit(1)

    redis_connection = redis.StrictRedis(
        host=options.redis_host,
        port=options.redis_port,
        db=options.redis_db)
    agent = rdc_handler.CommandHandler(redis_connection)
    hostname = args[0]
    try:
        agent.pull_commands(hostname)
    except KeyboardInterrupt:
        print("Exiting")

if __name__ == "__main__":
    main()
