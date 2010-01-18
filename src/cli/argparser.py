#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham, A. Roitman
# Copyright (C) 2007-2009  B. Malengier
# Copyright (C) 2008 Lukasz Rymarczyk
# Copyright (C) 2008 Raphael Ackermann
# Copyright (C) 2008 Brian G. Matherly
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
Module responsible for handling the command line arguments for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys
import getopt
from gen.ggettext import gettext as _
import logging

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const


# Note: Make sure to edit const.py POPT_TABLE too!
_HELP = _("""
Usage: gramps.py [OPTION...]
  --load-modules=MODULE1,MODULE2,...     Dynamic modules to load

Help options
  -?, --help                             Show this help message
  --usage                                Display brief usage message

Application options
  -O, --open=FAMILY_TREE                 Open family tree
  -i, --import=FILENAME                  Import file
  -e, --export=FILENAME                  Export file
  -f, --format=FORMAT                    Specify family tree format
  -a, --action=ACTION                    Specify action
  -p, --options=OPTIONS_STRING           Specify options
  -d, --debug=LOGGER_NAME                Enable debug logs
  -l                                     List Family Trees
  -L                                     List Family Trees in Detail
  -u, --force-unlock                     Force unlock of family tree
""")

#-------------------------------------------------------------------------
# ArgParser
#-------------------------------------------------------------------------
class ArgParser(object):
    """
    This class is responsible for parsing the command line arguments (if any)
    given to gramps, and determining if a GUI or a CLI session must be started.
    The valid arguments are:

    Possible: 
        1/ FAMTREE : Just the family tree (name or database dir)
        2/ -O, --open=FAMTREE, Open of a family tree
        3/ -i, --import=FILE, Import a family tree of any format understood by an 
                 importer, optionally provide- f to indicate format
        4/ -e, --export=FILE, export a family tree in required format, optionally 
                 provide -f to indicate format
        5/ -f, --format=FORMAT : format after a -i or -e option
        6/ -a, --action: An action (possible: 'check', 'summary', 'report', 
                            'tool')
        7/ -u, --force-unlock: A locked database can be unlocked by giving this
                argument when opening it
    
    If the filename (no flags) is specified, the interactive session is 
    launched using data from filename. 
    In this mode (filename, no flags), the rest of the arguments is ignored.
    This is a mode suitable by default for GUI launchers, mime type handlers,
    and the like
    
    If no filename or -i option is given, a new interactive session (empty
    database) is launched, since no data is given anyway.
    
    If -O or -i option is given, but no -e or -a options are given, an
    interactive session is launched with the FILE (specified with -i). 
    
    If both input (-O or -i) and processing (-e or -a) options are given,
    interactive session will not be launched. 
    """

    def __init__(self, args):
        """
        Pass the command line arguments on creation.
        """
        self.args = args

        self.open_gui = None
        self.open = None
        self.exports = []
        self.actions = []
        self.imports = []
        self.imp_db_path = None
        self.list = False
        self.list_more = False
        self.help = False
        self.force_unlock = False

        self.errors = []
        self.parse_args()

    #-------------------------------------------------------------------------
    # Argument parser: sorts out given arguments
    #-------------------------------------------------------------------------
    def parse_args(self):
        """
        Fill in lists with open, exports, imports, and actions options.

        Any errors are added to self.errors
        
        Possible: 
        1/ Just the family tree (name or database dir)
        2/ -O, --open:   Open of a family tree
        3/ -i, --import: Import a family tree of any format understood by an importer, 
                 optionally provide-f to indicate format
        4/ -e, --export: export a family tree in required format, optionally provide
                 -f to indicate format
        5/ -f, --format=FORMAT : format after a -i or -e option
        6/ -a, --action: An action (possible: 'check', 'summary', 'report', 
                            'tool')
        7/ -u, --force-unlock: A locked database can be unlocked by giving this
                argument when opening it
                            
        """
        try:
            options, leftargs = getopt.getopt(self.args[1:],
                                             const.SHORTOPTS, const.LONGOPTS)
        except getopt.GetoptError, msg:
            self.errors += [(_('Error parsing the arguments'), 
                        str(msg) + '\n' +
                        _("Error parsing the arguments: %s \n" 
                        "Type gramps --help for an overview of commands, or "
                        "read the manual pages.") % self.args[1:])]
            return

        if leftargs:
            # if there were an argument without option,
            # use it as a file to open and return
            self.open_gui = leftargs[0]
            print "Trying to open: %s ..." % leftargs[0]
            #see if force open is on
            for opt_ix in range(len(options)):
                option, value = options[opt_ix]
                if option in ('-u', '--force-unlock'):
                    self.force_unlock = True
                    break
            return

        # Go over all given option and place them into appropriate lists
        cleandbg = []
        for opt_ix in range(len(options)):
            option, value = options[opt_ix]
            if option in ( '-O', '--open'):
                self.open = value
            elif option in ( '-i', '--import'):
                family_tree_format = None
                if opt_ix < len(options) - 1 \
                   and options[opt_ix + 1][0] in ( '-f', '--format'): 
                    family_tree_format = options[opt_ix + 1][1]
                self.imports.append((value, family_tree_format))
            elif option in ( '-e', '--export' ):
                family_tree_format = None
                if opt_ix < len(options) - 1 \
                   and options[opt_ix + 1][0] in ( '-f', '--format'): 
                    family_tree_format = options[opt_ix + 1][1]
                self.exports.append((value, family_tree_format))
            elif option in ( '-a', '--action' ):
                action = value
                if action not in ( 'check', 'summary', 'report', 'tool' ):
                    print "Unknown action: %s. Ignoring." % action
                    continue
                options_str = ""
                if opt_ix < len(options)-1 \
                            and options[opt_ix+1][0] in ( '-p', '--options' ): 
                    options_str = options[opt_ix+1][1]
                self.actions.append((action, options_str))
            elif option in ('-d', '--debug'):
                print 'setup debugging', value
                logger = logging.getLogger(value)
                logger.setLevel(logging.DEBUG)
                cleandbg += [opt_ix]
            elif option in ('-l',):
                self.list = True
            elif option in ('-L',):
                self.list_more = True
            elif option in ('-h', '-?', '--help'):
                self.help = True
            elif option in ('-u', '--force-unlock'):
                self.force_unlock = True
        
        #clean options list
        cleandbg.reverse()
        for ind in cleandbg:
            del options[ind]
        
        if len(options) > 0 and self.open is None and self.imports == [] \
                and not (self.list or self.list_more or self.help):
            self.errors += [(_('Error parsing the arguments'), 
                        _("Error parsing the arguments: %s \n" 
                        "To use in the command-line mode," \
                "supply at least one input file to process.") % self.args[1:])]

    #-------------------------------------------------------------------------
    # Determine the need for GUI
    #-------------------------------------------------------------------------
    def need_gui(self):
        """
        Determine whether we need a GUI session for the given tasks.
        """
        if self.errors: 
            #errors in argument parsing ==> give cli error, no gui needed
            return False
        
        if self.list or self.list_more or self.help:
            return False

        if self.open_gui:
            # No-option argument, definitely GUI
            return True

        # If we have data to work with:
        if (self.open or self.imports):
            if (self.exports or self.actions):
                # have both data and what to do with it => no GUI
                return False
            else:
                # data given, but no action/export => GUI
                return True
        
        # No data, can only do GUI here
        return True
    
    def print_help(self):
        """
        If the user gives the --help or -h option, print the output to terminal.
        """
        if self.help:
            print _HELP
            sys.exit(0)
            
