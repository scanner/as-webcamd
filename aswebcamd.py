#!/usr/bin/env python
#
# File: $Id$
#
"""
The driver for the AS WebCam server daemon. Not much happens in here
except parsing command line arguments, load a configuration file and
call the server's startup method.
"""

# system imports
#
import os
import sys
import optparse
import logging
import logging.handlers
from ConfigParser import SafeConfigParser

# 3rd party module imports
#

# aswebcamd imports
#
from aswebcam import logger

############################################################################
#
def setup_option_parser():
    """This function uses the python OptionParser module to define an option
    parser for parsing the command line options for this script. This does not
    actually parse the command line options. It returns the parser object that
    can be used for parsing them.
    """
    parser = optparse.OptionParser(usage = "%prog [options]",
                                   version = "%prog 0.1")
    parser.set_defaults(config = "/usr/local/etc/aswebcamd.conf",
                        req_port = 2146,
                        pub_port = 2147,
                        interface = "0.0.0.0",
                        background = True,
                        debug = False,
                        user = None,
                        logger = "syslog.local2")

    parser.add_option("--config", action="store", dest="config",
                      help = "The path to the config file to use. NOTE: "
                      "command line options override things set in the "
                      "config file. Default: %default")
    parser.add_option("--debug", action="store_true",dest="debug",
                      help="Turn on debugging options and debugging log "
                      "output. Default: %default")
    parser.add_option("--req_port", action="store", type="int",dest="req_port",
                      help="What port do we listen on for the REQ/REP service "
                      "used by clients communication with the server."
                      " Default: %default")
    parser.add_option("--pub_port", action="store", type="int",dest="pub_port",
                      help="What port does the PUB/SUB service run on used "
                      "by clients to get video streams from webcams."
                      " Default: %default")
    parser.add_option("--interface", action="store",dest="interface",
                      help="What interface do we listen on. Default: %default")
    parser.add_option("--foreground", action="store_false",dest="background",
                      help = "Does the server daemonize or not. "
                      "Default: %default")
    parser.add_option("--user", action="store", dest="user",
                      help="Which user to run as. Only useful as an option "
                      "when run as root and you want to change to a different "
                      "user.")
    parser.add_option("--logger", action="store",dest="logger",
                      help="Where we do log messages. This should either be "
                      "syslog.<foo> where <foo> is the syslog service to log "
                      "to, or 'stderr' to log to standard error, 'stdout' "
                      "to log to standard out. Any other string will be "
                      "considered the path to a file to log to."
                      " Default: %default")
    return parser

############################################################################
#
# This was copied from django's daemonize module,
#
# http://www.djangoproject.org/
#
# Copyright (c) Django Software Foundation and individual
# contributors.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#     1. Redistributions of source code must retain the above copyright notice, 
#        this list of conditions and the following disclaimer.
#    
#     2. Redistributions in binary form must reproduce the above copyright 
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Django nor the names of its contributors
#        may be used to endorse or promote products derived from this
#       software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
if os.name == 'posix':
    def become_daemon(our_home_dir='.', out_log='/dev/null', err_log='/dev/null'):
        "Robustly turn into a UNIX daemon, running in our_home_dir."
        # First fork
        try:
            if os.fork() > 0:
                sys.exit(0)     # kill off parent
        except OSError, e:
            sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
            sys.exit(1)
        os.setsid()
        os.chdir(our_home_dir)
        os.umask(0)

        # Second fork
        try:
            if os.fork() > 0:
                os._exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
            os._exit(1)

        si = open('/dev/null', 'r')
        so = open(out_log, 'a+', 0)
        se = open(err_log, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        # Set custom file descriptors so that they get proper buffering.
        sys.stdout, sys.stderr = so, se
else:
    def become_daemon(our_home_dir='.', out_log=None, err_log=None):
        """
        If we're not running under a POSIX system, just simulate the daemon
        mode by doing redirections and directory changing.
        """
        os.chdir(our_home_dir)
        os.umask(0)
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()
        if err_log:
            sys.stderr = open(err_log, 'a', 0)
        else:
            sys.stderr = NullDevice()
        if out_log:
            sys.stdout = open(out_log, 'a', 0)
        else:
            sys.stdout = NullDevice()

    class NullDevice:
        "A writeable object that writes to nowhere -- like /dev/null."
        def write(self, s):
            pass

############################################################################
#
def become_user(user = None):
    """
    Change to run as the specified user. If 'None' then we just return.
    If we are already running as the given user, also do nothing and return.
    """
    if user == None:
        return

    current_user = pwd.getpwuid(os.getuid())
    if current_user[0] == user:
        return

    pwinfo = pwd.getpwnam(user)
    os.setregid(pwinfo[3],pwinfo[3])
    os.setreuid(pwinfo[2],pwinfo[2])
    return

#############################################################################
#
def main():
    """
    Main entry point.

    Parse arguments. Load the configuration file. Call the server
    startup function.
    """
    parser = setup_option_parser()
    (options, args) = parser.parse_args()

    # Now we load the config file as determined by our run time
    # options (or the defaults we get)
    #
    config = SafeConfigParser()
    config.read(options.config)

    # Now that we have loaded the config, override options that may
    # have been in the config with whatever was set on the command line.
    #
    # NOTE: all the command line stuff over-rides the 'general' section of the
    #       config (maybe we should call that the 'server' section?)
    #
    if not config.has_section("general"):
        config.add_section("general")
        
    config.set("general", "req_port", str(options.req_port))
    config.set("general", "pub_port", str(options.pub_port))
    config.set("general", "interface", options.interface)
    config.set("general", "background", str(options.background).lower())
    config.set("general", "logger", options.logger)
    config.set("general", "debug", str(options.debug).lower())
    if options.user is not None:
        config.set("general", "user", options.user)

    # Set up our logger. We set a variable in the logger module that every
    # other module will then use.
    #
    if config.get("general", "debug"):
        logger.setLevel(logging.DEBUG)

    loggertype = config.get("general", "logger").lower()

    # Warn the user if they have set the logging to go out to stderr or stdout
    # if they are daemonizing because this means they will not see any log
    # output.
    #
    if loggertype in ["stderr", "stdout"] and \
            not config.get("general", "background"):
        sys.stderr.write("NOTE: You have selected %s for your logging yet "
                         "you are going to background this process. This "
                         "means all logging messages will be lost.")
        
    if loggertype == "stderr":
        handler = logging.StreamHandler(sys.stderr)

    elif loggertype == "stdout":
        handler = logging.StreamHandler(sys.stdout)

    elif loggertype[0:7] == "syslog.":
        # Log to syslog.. we log at INFO or higher, unless debug is
        # set in which case we log at DEBUG and higher.
        #
        facility = logging.handlers.SysLogHandler.facility_names[loggertype[7:]]
        handler = logging.handlers.SysLogHandler(facility = facility)

    else:
        # Otherwise we try to log to a file of the name specified.
        #
        handler = logging.handlers.WatchedFileHandler(loggertype)

    logger.addHandler(handler)

    if config.has_option("general", "user"):
        logger.info("Changing to the user %s" % config.get("general", "user"))
        become_user(config.get("general", "user"))

    if config.getboolean("general", "background"):
        logger.info("Backgrounding to enter daemon mode.")
        become_daemon()

    return

############################################################################
############################################################################
#
# Here is where it all starts
#
if __name__ == "__main__":
    main()
#
#
############################################################################
############################################################################
