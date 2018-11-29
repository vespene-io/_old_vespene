#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0
#  -------------------------------------------------------------------------
#  settings.py - the central Django settings file. Rather than edit this
#  use files in /etc/vespene/settings.d/, though we'll also accept
#  some other locations.
#  --------------------------------------------------------------------------

from split_settings.tools import include, optional

include(
    'config/*.py',
    optional('local_settings.py'),
    optional('/etc/vespene/settings.py'),
    optional('/etc/vespene/settings.d/*.py')
)
