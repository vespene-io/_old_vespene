#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0


class Shared(object):
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state

