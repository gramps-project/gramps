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
import os
import sys
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RecentFiles
import Utils
import gen
from clidbman import CLIDbManager, NAME_FILE, find_locker_name

from PluginUtils import Tool
from gen.plug import BasePluginManager
from ReportBase import CATEGORY_BOOK, CATEGORY_CODE, cl_report

#-------------------------------------------------------------------------
# ArgHandler
#-------------------------------------------------------------------------
class ArgHandler(object):
    """
    This class is responsible for the non GUI handling of commands.
    The handler is passed a parser object, sanitizes it, and can execute the 
    actions requested working on a DbState.
    """

    def __init__(self, dbstate, parser, sessionmanager, 
                        errorfunc=None, gui=False):
        self.dbstate = dbstate
        self.sm = sessionmanager
        self.errorfunc = errorfunc
        self.gui = gui
        if self.gui:
            self.actions = []
            self.list = False
            self.list_more = False
            self.open_gui = None
        else:
            self.actions = parser.actions
            self.list = parser.list
            self.list_more = parser.list_more
        self.open_gui = parser.open_gui
        self.imp_db_path = None
        self.dbman = CLIDbManager(self.dbstate)
        self.force_unlock = parser.force_unlock
        self.cl = 0
        self.imports = []
        self.exports = []

        self.open = self.__handle_open_option(parser.open)
        self.sanitize_args(parser.imports, parser.exports)
    
    def __error(self, string):
        """
        Output an error. Uses errorfunc if given, otherwise a simple print.
        """
        if self.errorfunc:
            self.errorfunc(string)
        else:
            print string

    #-------------------------------------------------------------------------
    # Argument parser: sorts out given arguments
    #-------------------------------------------------------------------------
    def sanitize_args(self, importlist, exportlist):
        """
        Check the lists with open, exports, imports, and actions options.
        """
        for (value, family_tree_format) in importlist:
            self.__handle_import_option(value, family_tree_format)
        for (value, family_tree_format) in exportlist:
            self.__handle_export_option(value, family_tree_format)

    def __handle_open_option(self, value):
        """
        Handle the "-O" or "--open" option.
        Only Family trees or a dir with a family tree can be opened.                  
        """
        if value is None:
            return None
        db_path = self.__deduce_db_path(value)

        if db_path:
            # We have a potential database path.
            # Check if it is good.
            if not self.check_db(db_path, self.force_unlock):
                sys.exit(0)
            return db_path
        else:
            self.__error( _('Error: Input family tree "%s" does not exist.\n'
                    "If GEDCOM, Gramps-xml or grdb, use the -i option to "
                    "import into a family tree instead.") % value)
            sys.exit(0)

    def __handle_import_option(self, value, family_tree_format):
        """
        Handle the "-i" or "--import" option.
        Only Files supported by a plugin can be imported, so not Family Trees.
        """
        fname = value
        fullpath = os.path.abspath(os.path.expanduser(fname))
        if not os.path.exists(fullpath):
            self.__error(_('Error: Import file %s not found.') % fname)
            sys.exit(0)
        
        if family_tree_format is None:
            # Guess the file format based on the file extension.
            # This will get the lower case extension without a period, 
            # or an empty string.
            family_tree_format = os.path.splitext(fname)[-1][1:].lower()

        pmgr = BasePluginManager.get_instance()
        plugin_found = False
        for plugin in pmgr.get_import_plugins():
            if family_tree_format == plugin.get_extension():
                plugin_found = True
                
        if plugin_found:
            self.imports.append((fname, family_tree_format))
        else:
            self.__error(_('Error: Unrecognized type: "%(format)s" for '
                    'import file: %(filename)s') \
                  % {'format' : family_tree_format, 
                     'filename' : fname})
            sys.exit(0)
            
    def __handle_export_option(self, value, family_tree_format):
        """
        Handle the "-e" or "--export" option.  
        Note: this can only happen in the CLI version.                    
        """
        if self.gui:
            return
        fname = value
        fullpath = os.path.abspath(os.path.expanduser(fname))
        if os.path.exists(fullpath):
            self.__error(_("WARNING: Output file already exist!\n"
                    "WARNING: It will be overwritten:\n   %(name)s") % \
                    {'name' : fullpath})
            answer = None
            while not answer:
                answer = raw_input(_('OK to overwrite? (yes/no) '))
            if answer.upper() in ('Y', 'YES', _('YES')):
                self.__error( _("Will overwrite the existing file: %s") 
                                % fullpath)
            else:
                sys.exit(0)

        if family_tree_format is None:
            # Guess the file format based on the file extension.
            # This will get the lower case extension without a period, 
            # or an empty string.
            family_tree_format = os.path.splitext(fname)[-1][1:].lower()

        pmgr = BasePluginManager.get_instance()
        plugin_found = False
        for plugin in pmgr.get_export_plugins():
            if family_tree_format == plugin.get_extension():
                plugin_found = True
                
        if plugin_found:
            self.exports.append((fullpath, family_tree_format))
        else:
            self.__error(_("ERROR: Unrecognized format for export file %s") 
                            % fname)
            sys.exit(0)
        
    def __deduce_db_path(self, db_name_or_path):
        """
        Attempt to find a database path for the given parameter.
        
        @return: The path to a Gramps DB
                 or None if a database can not be deduced.
        """
        # First, check if this is the name of a family tree
        db_path = self.dbman.get_family_tree_path(db_name_or_path)

        if db_path is None:
            # This is not a known database name.
            # Check if the user provided a db path instead.
            fullpath = os.path.abspath(os.path.expanduser(db_name_or_path))
            if os.path.isdir(fullpath):
                # The user provided a directory. Check if it is a valid tree.
                name_file_path = os.path.join(fullpath, NAME_FILE)
                if os.path.isfile(name_file_path):
                    db_path = fullpath
                    
        return db_path

    #-------------------------------------------------------------------------
    # Overall argument handler: 
    # sorts out the sequence and details of operations
    #-------------------------------------------------------------------------
    def handle_args_gui(self):
        """
        method to handle the arguments that can be given for a GUI session.
        Returns the filename of the family tree that should be opened if 
        user just passed a famtree or a filename
            1/no options: a family tree can be given, if so, this name is tested
                        and returned. If a filename, it is imported in a new db
                        and name of new db returned
            2/an open and/or import option can have been given, if so, this 
                is handled, and None is returned
            
        """
        if self.open_gui:
            # First check if a Gramps database was provided
            # (either a database path or a database name)
            db_path = self.__deduce_db_path(self.open_gui)

            if not db_path:
                # Apparently it is not a database. See if it is a file that
                # can be imported.
                db_path, title = self.dbman.import_new_db(self.open_gui, None)

            if db_path:
                # Test if not locked or problematic
                if not self.check_db(db_path, self.force_unlock):
                    sys.exit(0)
                # Add the file to the recent items
                path = os.path.join(db_path, "name.txt")
                try:
                    ifile = open(path)
                    title = ifile.readline().strip()
                    ifile.close()
                except:
                    title = db_path
                RecentFiles.recent_files(db_path, title)
                self.open = db_path
                self.__open_action()
            else:
                sys.exit(0)
            return db_path
        
        # if not open_gui, parse any command line args. We can only have one 
        #  open argument, and perhaps some import arguments
        self.__open_action()
        self.__import_action()
        return None
    
    def handle_args_cli(self, cleanup=True):
        """
        Depending on the given arguments, import or open data, launch
        session, write files, and/or perform actions.
        
        @param: climan: the manager of a CLI session
        @type: CLIManager object
        """

        if self.list:
            print 'List of known family trees in your database path\n'
            for name, dirname in self.dbman.family_tree_list():
                print dirname, ', with name ', name 
            sys.exit(0)
            
        if self.list_more:
            print 'Gramps Family Trees:'
            summary_list = self.dbman.family_tree_summary()
            for summary in summary_list:
                print "Family Tree \"%s\":" % summary["Family tree"]
                for item in summary:
                    if item != "Family tree":
                        print "   %s: %s" % (item, summary[item])
            sys.exit(0)
           
        self.__open_action()
        self.__import_action()
            
        for (action, options_str) in self.actions:
            print "Performing action: %s." % action
            if options_str:
                print "Using options string: %s" % options_str
            self.cl_action(action, options_str)

        for expt in self.exports:
            print "Exporting: file %s, format %s." % expt
            self.cl_export(expt[0], expt[1])

        if cleanup:
            self.cleanup()
            print "Exiting."
            sys.exit(0)

    def cleanup(self):
        print "Cleaning up."
        # remove files in import db subdir after use
        self.dbstate.db.close()
        if self.imp_db_path:
            Utils.rm_tempdir(self.imp_db_path)

    def __import_action(self):
        """
        Take action for all given to import files. Note: Family trees are not
            supported.
        If a family tree is open, the import happens on top of it. If not open, 
        a new family tree is created, and the import done. If this is CLI, 
        the created tree is deleted at the end (as some action will have 
        happened that is now finished), if this is GUI, it is opened.
        """
        if self.imports:
            self.cl = bool(self.exports or self.actions or self.cl)

            if not self.open:
                # Create empty dir for imported database(s)
                if self.gui:
                    self.imp_db_path, title = self.dbman.create_new_db_cli()
                else:
                    self.imp_db_path = Utils.get_empty_tempdir("import_dbdir")
                
                    newdb = gen.db.DbBsddb()
                    newdb.write_version(self.imp_db_path)
                
                try:
                    self.sm.open_activate(self.imp_db_path)
                    print "Created empty family tree successfully"
                except:
                    print "Error opening the file." 
                    print "Exiting..." 
                    sys.exit(0)

            for imp in self.imports:
                print "Importing: file %s, format %s." % imp
                self.cl_import(imp[0], imp[1])

    def __open_action(self):
        """
        Take action on a family tree dir to open. It will be opened in the 
        session manager
        """
        if self.open:
            # Family Tree to open was given. Open it 
            # Then go on and process the rest of the command line arguments.
            self.cl = bool(self.exports or self.actions)

            # we load this file for use
            try:
                self.sm.open_activate(self.open)
                print "Opened successfully!"
            except:
                print "Error opening the file." 
                print "Exiting..." 
                sys.exit(0)

    def check_db(self, dbpath, force_unlock = False):
        """
        Test a given family tree path if it can be opened.
        """
        # Test if not locked or problematic
        if force_unlock:
            self.dbman.break_lock(dbpath)
        if self.dbman.is_locked(dbpath):
            self.__error((_("Database is locked, cannot open it!") + '\n' +
                          _("  Info: %s")) % find_locker_name(dbpath))
            return False
        if self.dbman.needs_recovery(dbpath):
            self.__error( _("Database needs recovery, cannot open it!"))
            return False
        return True

    #-------------------------------------------------------------------------
    #
    # Import handler
    #
    #-------------------------------------------------------------------------
    def cl_import(self, filename, family_tree_format):
        """
        Command-line import routine. Try to import filename using the family_tree_format.
        """
        pmgr = BasePluginManager.get_instance()
        for plugin in pmgr.get_import_plugins():
            if family_tree_format == plugin.get_extension():
                import_function = plugin.get_import_function()
                import_function(self.dbstate.db, filename, None)
        
        if not self.cl:
            if self.imp_db_path:
                return self.sm.open_activate(self.imp_db_path)
            else:
                return self.sm.open_activate(self.open)

    #-------------------------------------------------------------------------
    #
    # Export handler
    #
    #-------------------------------------------------------------------------
    def cl_export(self, filename, family_tree_format):
        """
        Command-line export routine. 
        Try to write into filename using the family_tree_format.
        """
        pmgr = BasePluginManager.get_instance()
        for plugin in pmgr.get_export_plugins():
            if family_tree_format == plugin.get_extension():
                export_function = plugin.get_export_function()
                export_function(self.dbstate.db, filename)

    #-------------------------------------------------------------------------
    #
    # Action handler
    #
    #-------------------------------------------------------------------------
    def cl_action(self, action, options_str):
        """
        Command-line action routine. Try to perform specified action.
        """
        pmgr = BasePluginManager.get_instance()
        if action == "report":
            try:
                options_str_dict = dict( [ tuple(chunk.split('='))
                    for chunk in options_str.split(',') ] )
            except:
                options_str_dict = {}
                print "Ignoring invalid options string."

            name = options_str_dict.pop('name', None)
            _cl_list = pmgr.get_reg_reports(gui=False)
            if name:
                for pdata in _cl_list:
                    if name == pdata.id:
                        mod = pmgr.load_plugin(pdata)
                        if not mod:
                            #import of plugin failed
                            return 
                        category = pdata.category
                        report_class = eval('mod.' + pdata.reportclass)
                        options_class = eval('mod.' + pdata.optionclass)
                        if category in (CATEGORY_BOOK, CATEGORY_CODE):
                            options_class(self.dbstate.db, name, category, 
                                          options_str_dict)
                        else:
                            cl_report(self.dbstate.db, name, category, 
                                      report_class, options_class,
                                      options_str_dict)
                        return
                # name exists, but is not in the list of valid report names
                msg = "Unknown report name."
            else:
                msg = "Report name not given. Please use -p name=reportname."
            
            print "%s\n Available names are:" % msg
            for pdata in _cl_list:
                # Print cli report name ([item[0]) and GUI report name (item[4])
                if len(pdata.id) <= 25:
                    print "   %s%s- %s" % ( pdata.id, 
                                            " " * (26 - len(pdata.id)),
                                            pdata.name)
                else:
                    print "   %s\t- %s" % (pdata.id, pdata.name)

        elif action == "tool":
            try:
                options_str_dict = dict( [ tuple(chunk.split('=')) for
                                           chunk in options_str.split(',') ] )
            except:
                options_str_dict = {}
                print "Ignoring invalid options string."

            name = options_str_dict.pop('name', None)
            _cli_tool_list = pmgr.get_reg_tools(gui=False)
            if name:
                for pdata in _cli_tool_list:
                    if name == pdata.id:
                        mod = pmgr.load_plugin(pdata)
                        if not mod:
                            #import of plugin failed
                            return 
                        category = pdata.category
                        tool_class = eval('mod.' + pdata.toolclass)
                        options_class = eval('mod.' + pdata.optionclass)
                        Tool.cli_tool(self.dbstate, name, category, tool_class, 
                                      options_class, options_str_dict)
                        return
                msg = "Unknown tool name."
            else:
                msg = "Tool name not given. Please use -p name=toolname."
            
            print "%s\n Available names are:" % msg
            for pdata in _cli_tool_list:
                # Print cli report name ([item[0]) and GUI report name (item[4])
                if len(pdata.id) <= 25:
                    print "   %s%s- %s" % ( pdata.id, 
                                            " " * (26 - len(pdata.id)),
                                            pdata.name)
                else:
                    print "   %s\t- %s" % (pdata.id, pdata.name)
        else:
            print "Unknown action: %s." % action
            sys.exit(0)
