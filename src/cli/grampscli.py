#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2009 Benny Malengier
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

# $Id:gramps_main.py 9912 2008-01-22 09:17:46Z acraphae $

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import os
import sys

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
from gen.db import GrampsDBDir
from gen.plug import PluginManager
import GrampsCfg
import RecentFiles

#-------------------------------------------------------------------------
#
# CLI DbLoader class
#
#-------------------------------------------------------------------------
class CLIDbLoader(object):
    def __init__(self, dbstate):
        self.dbstate = dbstate
    
    def _warn(title, warnmessage):
        print _('WARNING: %s') %warnmessage
    
    def _errordialog(title, errormessage):
        """
        Show the error. A title for the error and an errormessage
        """
        print _('ERROR: %s') % errormessage
        sys.exit(1)
    
    def _dberrordialog(self, msg):
        self._errordialog( '', _("Low level database corruption detected") 
            + '\n' +
            _("GRAMPS has detected a problem in the underlying "
              "Berkeley database. This can be repaired by from "
              "the Family Tree Manager. Select the database and "
              'click on the Repair button') + '\n\n' + str(msg))
    
    def _begin_progress(self):
        pass
    
    def _pulse_progress(self, value):
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
        except gen.db.FileVersionDeclineToUpgrade:
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
            _LOG.error("Failed to open database.", exc_info=True)
        return True

#-------------------------------------------------------------------------
#
# CLIManager class
#
#-------------------------------------------------------------------------

class CLIManager(object):
    """
    A reduced viewmanager suitable for cli actions. 
    Aim is to manage a database on which to work
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
    
    def _errordialog(title, errormessage):
        """
        Show the error. A title for the error and an errormessage
        """
        print _('ERROR: %s') % errormessage
        sys.exit(1)
        
    def _read_recent_file(self, filename):
        """
        Called when a file needs to be loaded
        """
        # A recent database should already have a directory 
        # If not, do nothing, just return. This can be handled better if family tree
        # delete/rename also updated the recent file menu info in DisplayState.py
        if not  os.path.isdir(filename):
            self.errordialog(
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
        self._post_load_newdb_nongui(filename, filetype, title)
    
    def _post_load_newdb_nongui(self, filename, filetype, title=None):
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
        owner = GrampsCfg.get_researcher()
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
            self.dbstate.change_active_person(self.dbstate.db.find_initial_person())
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

def startcli(errors, argparser):
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
    
    handler.handle_args_cli(climanager)
    
    sys.exit(0)
