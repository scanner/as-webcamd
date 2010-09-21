#!/usr/bin/env python
#
# File: $Id$
#
"""
The webcam client logic.
"""

# system imports
#
import logging

## Set up our module specific logger
##
logger = logging.getLogger("aswebcam.webcam")

##################################################################
##################################################################
#
class ASWebCam(object):
    """
    The base class for our as webcam clients. There will be subclasses
    for specific models of different vendor's webcams.
    """

    ##################################################################
    #
    def __init__(self, name, host, model):
        """
        
        Arguments:
        - `name`: The unique name that identifies this webcam.
        - `host`: The hostname that represents this webcam.
        - `type`: What type it is (hnc210, ip1200, etc.)
        """
        pass

        
