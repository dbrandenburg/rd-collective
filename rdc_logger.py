import logging
LOGFILE = "rdcollective.log"
DEFAULT_LOG_LEVEL = "debug"
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
         }
LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def start_logging(filename=LOGFILE, level=DEFAULT_LOG_LEVEL):
    "Start login with given filename and level"
    logging.basicConfig(filename=filename, level=LEVELS[level], format=LOGFORMAT)
start_logging()