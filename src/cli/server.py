#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Doug Blank <doug.blank@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Provides the start_server function, which the main program calls for server
execution of GRAMPS.

Provides also two small base classes: CLIDbLoader, CLIManager
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import socket
import threading
import pickle
from gettext import gettext as _
import os
import sys
import signal
import logging
import traceback

LOG = logging.getLogger(".grampscli")
#-------------------------------------------------------------------------
#
# GRAMPS  modules
#
#-------------------------------------------------------------------------
from BasicUtils import name_displayer
import Config
import const
import Errors
import DbState
from gen.db import (GrampsDBDir, FileVersionDeclineToUpgrade)
import gen.db.exceptions
from gen.plug import PluginManager
from Utils import get_researcher
import RecentFiles
import Simple

#-------------------------------------------------------------------------
#
# CLI DbLoader class
#
#-------------------------------------------------------------------------
class CLIDbLoader(object):
    """
    Base class for Db loading action inside a dbstate. Only the minimum is 
    present needed for CLI handling
    """
    def __init__(self, dbstate):
        self.dbstate = dbstate
    
    def _warn(self, title, warnmessage):
        """
        Issue a warning message. Inherit for GUI action
        """
        print _('WARNING: %s') % warnmessage
    
    def _errordialog(self, title, errormessage):
        """
        Show the error. A title for the error and an errormessage
        Inherit for GUI action
        """
        print _('ERROR: %s') % errormessage
        sys.exit(1)
    
    def _dberrordialog(self, msg):
        """
        Show a database error. 
        @param: msg : an error message
        @type: string
        @note: Inherit for GUI action
        """
        self._errordialog( '', _("Low level database corruption detected") 
            + '\n' +
            _("GRAMPS has detected a problem in the underlying "
              "Berkeley database. This can be repaired by from "
              "the Family Tree Manager. Select the database and "
              'click on the Repair button') + '\n\n' + str(msg))
    
    def _begin_progress(self):
        """
        Convenience method to allow to show a progress bar if wanted on load
        actions. Inherit if needed
        """
        pass
    
    def _pulse_progress(self, value):
        """
        Convenience method to allow to show a progress bar if wantedon load
        actions. Inherit if needed
        """
        pass

    def read_file(self, filename):
        """
        This method takes care of changing database, and loading the data.
        In 3.0 we only allow reading of real databases of filetype 
        'x-directory/normal'
        
        This method should only return on success.
        Returning on failure makes no sense, because we cannot recover,
        since database has already beeen changed.
        Therefore, any errors should raise exceptions.

        On success, return with the disabled signals. The post-load routine
        should enable signals, as well as finish up with other UI goodies.
        """

        if os.path.exists(filename):
            if not os.access(filename, os.W_OK):
                mode = "r"
                self._warn(_('Read only database'), 
                                             _('You do not have write access '
                                               'to the selected file.'))
            else:
                mode = "w"
        else:
            mode = 'w'

        dbclass = GrampsDBDir
        
        self.dbstate.change_database(dbclass())
        self.dbstate.db.disable_signals()

        self._begin_progress()
        
        try:
            self.dbstate.db.load(filename, self._pulse_progress, mode)
            self.dbstate.db.set_save_path(filename)
        except FileVersionDeclineToUpgrade:
            self.dbstate.no_database()
        except gen.db.exceptions.FileVersionError, msg:
            self.dbstate.no_database()
            self._errordialog( _("Cannot open database"), str(msg))
        except OSError, msg:
            self.dbstate.no_database()
            self._errordialog(
                _("Could not open file: %s") % filename, str(msg))
        except Errors.DbError, msg:
            self.dbstate.no_database()
            self._dberrordialog(msg)
        except Exception:
            self.dbstate.no_database()
            LOG.error("Failed to open database.", exc_info=True)
        return True

#-------------------------------------------------------------------------
#
# CLIManager class
#
#-------------------------------------------------------------------------

class CLIManager(object):
    """
    Sessionmanager for GRAMPS. This is in effect a reduced viewmanager 
    instance (see gui/viewmanager), suitable for CLI actions. 
    Aim is to manage a dbstate on which to work (load, unload), and interact
    with the plugin session
    """
    def __init__(self, dbstate, setloader):
        self.dbstate = dbstate
        if setloader:
            self.db_loader = CLIDbLoader(self.dbstate)
        else:
            self.db_loader = None
        self.file_loaded = False
        self._pmgr = PluginManager.get_instance()
    
    def open_activate(self, path):
        """
        Open and make a family tree active
        """
        self._read_recent_file(path)
    
    def _errordialog(self, title, errormessage):
        """
        Show the error. A title for the error and an errormessage
        """
        print _('ERROR: %s') % errormessage
        sys.exit(1)
        
    def _read_recent_file(self, filename):
        """
        Called when a file needs to be loaded
        """
        # A recent database should already have a directory If not, do nothing,
        #  just return. This can be handled better if family tree delete/rename
        #  also updated the recent file menu info in DisplayState.py
        if not  os.path.isdir(filename):
            self._errordialog(
                    _("Could not load a recent Family Tree."), 
                    _("Family Tree does not exist, as it has been deleted."))
            return

        if self.db_loader.read_file(filename):
            # Attempt to figure out the database title
            path = os.path.join(filename, "name.txt")
            try:
                ifile = open(path)
                title = ifile.readline().strip()
                ifile.close()
            except:
                title = filename

            self._post_load_newdb(filename, 'x-directory/normal', title)
    
    def _post_load_newdb(self, filename, filetype, title=None):
        """
        The method called after load of a new database. 
        Here only CLI stuff is done, inherit this method to add extra stuff
        """
        self._post_load_newdb_nongui(filename, title)
    
    def _post_load_newdb_nongui(self, filename, title=None):
        """
        Called after a new database is loaded.
        """
        if not filename:
            return
        
        if filename[-1] == os.path.sep:
            filename = filename[:-1]
        name = os.path.basename(filename)
        if title:
            name = title

        # This method is for UI stuff when the database has changed.
        # Window title, recent files, etc related to new file.

        self.dbstate.db.set_save_path(filename)
        
        # apply preferred researcher if loaded file has none
        res = self.dbstate.db.get_researcher()
        owner = get_researcher()
        if res.get_name() == "" and owner.get_name() != "":
            self.dbstate.db.set_researcher(owner)
        
        name_displayer.set_name_format(self.dbstate.db.name_formats)
        fmt_default = Config.get(Config.NAME_FORMAT)
        if fmt_default < 0:
            name_displayer.set_default_format(fmt_default)

        self.dbstate.db.enable_signals()
        self.dbstate.signal_change()

        Config.set(Config.RECENT_FILE, filename)

        try:
            self.dbstate.change_active_person(
                                    self.dbstate.db.find_initial_person())
        except:
            pass
        
        RecentFiles.recent_files(filename, name)
        self.file_loaded = True
    
    def do_load_plugins(self):
        """
        Loads the plugins at initialization time. The plugin status window is 
        opened on an error if the user has requested.
        """
        # load plugins
        
        error = self._pmgr.load_plugins(const.PLUGINS_DIR)
        error |= self._pmgr.load_plugins(const.USER_PLUGINS)
        
        return error

def start_server(errors, argparser):
    """
    Starts a cli session of GRAMPS. 
    errors    : errors already encountered 
    argparser : ArgParser instance
    """
    if errors:
        #already errors encountered. Show first one on terminal and exit
        print _('Error encountered: %s') % errors[0][0]
        print _('  Details: %s') % errors[0][1]
        sys.exit(1)
    
    if argparser.errors: 
        print _('Error encountered in argument parsing: %s') \
                                                    % argparser.errors[0][0]
        print _('  Details: %s') % argparser.errors[0][1]
        sys.exit(1)

    #we need to keep track of the db state
    dbstate = DbState.DbState()
    #we need a manager for the CLI session
    climanager = CLIManager(dbstate, True)
    #load the plugins
    climanager.do_load_plugins()
    # handle the arguments
    from arghandler import ArgHandler
    handler = ArgHandler(dbstate, argparser, climanager)
    # create a manager to manage the database
    handler.handle_args_cli(cleanup=False) # cleanup later
    simple_access = Simple.SimpleAccess(dbstate.db)
    # server request handler:
    port = int(argparser.server)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen(5)
    # Set the signal handler
    signal.signal(signal.SIGINT, 
                  lambda signum, frame: ctrlc_handler(signum, frame, handler))
    print "GRAMPS server listening on port %d." % port
    print "Use CONTROL+C to exit..."
    print "-" * 50
    remote_interface = RemoteInterfaceHandler(dbstate, climanager, handler,
                                              simple_access)
    while True: # keep handling requests
        client_socket, client_address = server_socket.accept()
        BackgroundThread(client_socket, client_address, remote_interface).run()

def ctrlc_handler(signum, frame, handler):
    """
    Control+c program to handle clean up of databases, unlocking tables, etc.
    Exits the server.
    """
    handler.cleanup()
    sys.exit(0)

class RemoteInterfaceHandler:
    """
    Class that handles requests that come in on a socket connection via
    the GRAMPS remote interface.
    """
    def __init__(self, dbstate, climanager, arghandler, simple_access):
        """
        Constructor for RI. Pass in objects necessary for interacting with
        data and reports.
        """
        self.dbstate = dbstate
        self.climanager = climanager
        self.arghandler = arghandler
        self.sdb = simple_access
        self.env = {}
        self.env["self"] = self

    def reset(self):
        self.env = {}
        self.env["self"] = self

    def eval(self, command):
        """
        Evaluate the remote command and return results.
        """
        retval = None
        try:
            retval = eval(command, self.env)
        except:
            exec command in self.env
            retval = "ok"
        return retval

class BackgroundThread(threading.Thread):
    """
    A thread class for running things in the background.
    """
    def __init__(self, socket, address, remote_api, pause = 0.01):
        """
        Constructor, setting initial variables
        """
        self.client_socket = socket
        self.client_address = address
        self.remote_api = remote_api
        self._stopevent = threading.Event()
        self._sleepperiod = pause
        threading.Thread.__init__(self, name="GRAMPS Server Thread")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        print "Connection opened from %s:%s" % (self.client_address[0], 
                                                self.client_address[1])
        while not self._stopevent.isSet():
            self.process()
        print "Connection closed from %s:%s" % (self.client_address[0],
                                                self.client_address[1])
        self.client_socket.close()

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)
        self.client_socket.close()

    def process(self):
        """
        Process a remote request.
        """
        try:
            data = self.client_socket.recv(1024)
        except:
            data = None
        if data:
            print "    Request:", data
            try:
                result = self.remote_api.eval(data)
                presult = pickle.dumps(result)
            except Exception as exception:
                result =  exception 
                presult = pickle.dumps(result)
                    
            try:
                self.client_socket.send(presult)
            except:
                print "Error in sending data. Continuing anyway."
        else:
            self._stopevent.set()
	
