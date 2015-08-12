#!/usr/bin/env python3

import optparse
import redis
import rdc_handler
import logging
import rdc_logger


def main():
    
    usage = "usage: rdc_master.py [options] hostname \"command\""
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

    if len(args) < 2:
        logging.error("Too few arguments given. Exiting.")
        print("Too few arguments given.")
        parser.print_help()
        exit(1)
    elif len(args) > 2:
        logging.error("Too few arguments given. Exiting")
        print("Too many arguments given.")
        parser.print_help()
        exit(1)

    redis_connection = redis.StrictRedis(
        host=options.redis_host,
        port=options.redis_port,
        db=options.redis_db)
    master = rdc_handler.CommandHandler(redis_connection)
    (hostnames, command) = args
    hostnames = tuple(hostnames.split(','))
    try:
        results = master.push_command(hostnames, command)
        print(results)
    except KeyboardInterrupt:
        logging.info("Cought Keyboard Interrupt.Exiting.")
        print("Exiting")

if __name__ == "__main__":
    main()
