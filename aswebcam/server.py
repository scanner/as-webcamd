#!/usr/bin/env python
#
# File: $Id$
#
"""
The AS WebCam server logic.
"""

# system imports
#
import logging

## Set up our module specific logger
##
logger = logging.getLogger("aswebcam.server")

##################################################################
##################################################################
#
class ASWebCamServer(object):
    """
    The actual heart of this whole system. The ASWebCamServer. It will
    establish two zmq sockets for clients to connect to, list the
    webcams we know about, get images from them, and subscribe to
    streams of video from those webcams.

    For every webcam it knows about it will fork a subprocess to get a
    stream of images from that webcam and feed it to the server.

    For every webcam stream it has it will buffer one minute of frames
    from that webcam.

    It will listen for image and status messages from all the webcams
    it controls, listen and act on requests from clients, and publish
    streams of images from all of the webcams it gets data from.

    All done spiffily thanks to the magic of protobuf messages over
    zmq sockets.
    """

    ##################################################################
    #
    def __init__(self, req_port = 2146, pub_port = 2147, interface = "0.0.0.0"):
        """
        Set up our basic structures.

        Create our sockets.
        
        Arguments:
        - `req_port`: The port to listen on for client requests.
        - `pub_port`: The port to publish our video streams on
        - `interface`: The interface to listen on.
        """
        pass

    ##################################################################
    #
    def add_webcam(self, name, ):
        """
        Add a webcam and activate it.

        We use subprocess to spawn a webcam of the appropriate type
        and also connect up the socket on the server that will
        subscribe to the webcam's stream of images and a REQ/REP
        control channel.

        Arguments:
        - `webcam`: the webcam we are adding.
        """
        pass

    ##################################################################
    #
    def run(self):
        """
        Our main loop. Basically listen on all of our sockets, as we
        get frames from the webcam clients put them in to their image
        ring buffers, and write them to the PUB/SUB socket.

        Listen for commands and carry them out to the best of our ability.

        When we get the SHUTDOWN command shutdown all webcams, close
        our sockets and return.

        NOTE: You can not call run() again after it exits. State will
              be all horked up. You need to create a new server object
              and start all over again.
        """
        pass
