import logging
from twisted.python import log




class Logger(object):


    def __init__(self, verbose=False):

        fmt = "%(asctime)s %(levelname)s %(message)s"

        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(level=level, format=fmt)
        self.logger = logging.getLogger("pysqueezeboxserver")
        observer = log.PythonLoggingObserver()
        observer.start()



    def debug(self, msg):

        self.logger.debug(msg)


    def info(self, msg):

        self.logger.info(msg)


    def warn(self, msg):

        self.logger.warn(msg)


    def error(self, msg):

        self.logger.error(msg)


    def critical(self, msg):

        self.logger.critical(msg)

