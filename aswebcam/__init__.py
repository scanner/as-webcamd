#!/usr/bin/env python
#
# File: $Id$
#
"""

"""

# system imports
#
import logging

# We define a NullHandler class and add this as the handler to our
# root logger. When logging is properly configured it will overwrite
# the NullHandler.
#
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# and set up our default global logger
#
h = NullHandler()
logger = logging.getLogger("aswebcam").addHandler(h)

