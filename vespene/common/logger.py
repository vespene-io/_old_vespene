#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  logger.py - basic wrapper around Python standard logging just so in
#  case we need to change this behavior it is all in one place
#  --------------------------------------------------------------------------

import logging

class Logger(object):

    __instance = None

    def __init__(self):
        pass

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warn(msg)

    def error(self, msg):
        self.logger.error(msg)

    def __new__(cls):

        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
        
            logger = logging.getLogger('vespene')
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

            Logger.__instance.logger = logger

        return Logger.__instance
