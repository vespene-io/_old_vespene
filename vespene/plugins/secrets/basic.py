#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  basic.py - this is a cloaking plugin for symetric encryption of secrets.
#  it's not intended to be a fortress but for the implementation to use
#  when you're not using something more complex.  It is versioned by implementation
#  classes so the plugin can support improvements in existing cloaked secrets
#  when required.
#  --------------------------------------------------------------------------

from django.conf import settings
from cryptography import fernet
import binascii
from vespene.common.logger import Logger

LOG = Logger()

class BasicV1(object):

    HEADER = "[VESPENE-CLOAK][BASIC][V1]"

    def __init__(self):
        pass

    def cloak(self, msg):
        symetric = settings.SYMETRIC_SECRET_KEY
        print("SYM=%s" % symetric)
        ff = fernet.Fernet(symetric)
        msg = msg.encode('utf-8')
        enc = ff.encrypt(msg)
        henc = binascii.hexlify(enc).decode('utf-8')
        return "%s%s" % (self.HEADER, henc)

    def decloak(self, msg):
        symetric = settings.SYMETRIC_SECRET_KEY
        ff = fernet.Fernet(symetric)
        henc = msg.replace(self.HEADER, "", 1)
        enc = binascii.unhexlify(henc)
        msg = ff.decrypt(enc)
        rc = msg.decode('utf-8')
        return rc

class Plugin(object):

    HEADER = "[VESPENE-CLOAK][BASIC]"

    def __init__(self):
        pass

    def implementation_for_version(self, msg):
        if msg.startswith(BasicV1.HEADER):
            return BasicV1()
        raise Exception("unknown cloaking version")

    def cloak(self, msg):
        return BasicV1().cloak(msg)

    def decloak(self, msg):
        impl = self.implementation_for_version(msg)
        return impl.decloak(msg)

    def recognizes(self, msg):
        if settings.SYMETRIC_SECRET_KEY is None:
            # user didn't run 'make secrets' yet, so disable the plugin
            return False
        return msg.startswith(self.HEADER)