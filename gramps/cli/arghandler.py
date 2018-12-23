#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham, A. Roitman
# Copyright (C) 2007-2009  B. Malengier
# Copyright (C) 2008       Lukasz Rymarczyk
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2012       Doug Blank
# Copyright (C) 2012-2013  Paul Franklin
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Module responsible for handling the command line arguments for Gramps.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import sys
import re

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.recentfiles import recent_files
from gramps.gen.utils.file import rm_tempdir, get_empty_tempdir
from .clidbman import CLIDbManager, NAME_FILE, find_locker_name
from gramps.gen.db.utils import make_database
from gramps.gen.plug import BasePluginManager
from gramps.gen.plug.report import CATEGORY_BOOK, CATEGORY_CODE, BookList
from .plug import cl_report, cl_book
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.config import config

#-------------------------------------------------------------------------
#
# private functions
#
#-------------------------------------------------------------------------
def _split_options(options_str):
    """
    Split the options for the action.

    Rules:

    * Entries in the list of options are separated by commas without
      spaces between entries
    * List values must be inclosed in brackets ("[" and "]")
    * Entries within a list value are separated by commas
    * Text values (as a value or as entries in a list) do not have to be
      enclosed in quotes unless they include commas or quotation marks.
    * Text containing double quotes must be contained in single quotes
    * Text containing single quotes must be contained in double quotes
    * Text cannot include both single and double quotes

    Examples:

    Multiple options specified::

        report -p 'name=ancestor_chart,father_disp=["$n born $b"]'

    Using text with commas and quotes::

        title="This is some text with ,s and 's"
        title='This is some text with ,s and "s'

    Using a list of text::

        textlist=[row1,row2,"row3 with ' and ,"]
    """
    name = ""
    value = ""
    parsing_value = False
    in_quotes = False
    in_list = False
    quote_type = ""
    options_str_dict = {}

    for char in options_str:
        if not parsing_value:
            # Parsing the name of the option
            if char == "=":
                #print char, "This value ends the name"
                parsing_value = True
            else:
                #print char, "This value is part of the name"
                name += char
        else:
            # Parsing the value of the option
            if value == "" and char == '[':
                #print char, "This character begins a list"
                in_list = True
                value += char
            elif in_list == True and char == ']':
                #print char, "This character ends the list"
                in_list = False
                value += char
            elif not in_quotes and (char == '"' or char == "'"):
                #print char, "This character starts a quoted string"
                in_quotes = True
                quote_type = char
                value += char
            elif in_quotes and char == quote_type:
                #print char, "This character ends a quoted string"
                in_quotes = False
                value += char
            elif not in_quotes and not in_list and char == ",":
                #print char, "This character ends the value of the option"
                options_str_dict[name] = value
                name = ""
                value = ""
                parsing_value = False
                in_quotes = False
                in_list = False
            else:
                #print char, "This character is part of the value"
                value += char

    if parsing_value and not in_quotes and not in_list:
        # Add the last option
        options_str_dict[name] = value

    return options_str_dict

#-------------------------------------------------------------------------
# ArgHandler
#-------------------------------------------------------------------------
class ArgHandler:
    """
    This class is responsible for the non GUI handling of commands.
    The handler is passed a parser object, sanitizes it, and can execute the
    actions requested working on a :class:`.DbState`.
    """

    def __init__(self, dbstate, parser, sessionmanager,
                 errorfunc=None, gui=False):
        self.dbstate = dbstate
        self.smgr = sessionmanager
        self.errorfunc = errorfunc
        self.gui = gui
        self.user = sessionmanager.user
        if self.gui:
            self.actions = []
            self.list = False
            self.list_more = False
            self.open_gui = None
        else:
            self.actions = parser.actions
            self.list = parser.list
            self.list_more = parser.list_more
            self.list_table = parser.list_table
            self.database_names = parser.database_names
        self.open_gui = parser.open_gui
        self.imp_db_path = None
        self.dbman = CLIDbManager(self.dbstate)
        self.force_unlock = parser.force_unlock
        self.cl_bool = False
        self.imports = []
        self.exports = []
        self.removes = parser.removes
        self.username = parser.username
        self.password = parser.password

        self.open = self.__handle_open_option(parser.open, parser.create)
        self.sanitize_args(parser.imports, parser.exports)

    def __error(self, msg1, msg2=None):
        """
        Output an error. Uses errorfunc if given, otherwise a simple print.
        """
        if self.errorfunc:
            self.errorfunc(msg1)
        else:
            print(msg1, file=sys.stderr)
            if msg2 is not None:
                print(msg2, file=sys.stderr)

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

    def __handle_open_option(self, value, create):
        """
        Handle the "-O" or "--open" and "-C" or "--create" options.
        Only Family trees or a dir with a family tree can be opened.
        If create is True, then create the tree if it doesn't exist.
        """
        if value is None:
            return None
        db_path = self.__deduce_db_path(value)

        if db_path:
            # We have a potential database path.
            # Check if it is good.
            if not self.check_db(db_path, self.force_unlock):
                sys.exit(1)
            if create:
                self.__error(_("Error: Family Tree '%s' already exists.\n"
                               "The '-C' option cannot be used."
                              ) % value)
                sys.exit(1)
            return db_path
        elif create:
            # create the tree here, and continue
            dbid = config.get('database.backend')
            db_path, title = self.dbman.create_new_db_cli(title=value,
                                                          dbid=dbid)
            return db_path
        else:
            self.__error(_('Error: Input Family Tree "%s" does not exist.\n'
                           "If GEDCOM, Gramps-xml or grdb, use the -i option "
                           "to import into a Family Tree instead."
                          ) % value)
            sys.exit(1)

    def __handle_import_option(self, value, family_tree_format):
        """
        Handle the "-i" or "--import" option.
        Only Files supported by a plugin can be imported, so not Family Trees.
        """
        fname = value
        fullpath = os.path.abspath(os.path.expanduser(fname))
        if fname != '-' and not os.path.exists(fullpath):
            self.__error(_('Error: Import file %s not found.') % fname)
            sys.exit(1)

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
                           'import file: %(filename)s'
                          ) % {'format'   : family_tree_format,
                               'filename' : fname})
            sys.exit(1)

    def __handle_export_option(self, value, family_tree_format):
        """
        Handle the "-e" or "--export" option.

        .. note:: this can only happen in the CLI version.
        """
        if self.gui:
            return
        fname = value
        if fname == '-':
            fullpath = '-'
        else:
            fullpath = os.path.abspath(os.path.expanduser(fname))
            if os.path.exists(fullpath):
                message = _("WARNING: Output file already exists!\n"
                            "WARNING: It will be overwritten:\n   %s"
                           ) % fullpath
                accepted = self.user.prompt(_('OK to overwrite?'), message,
                                            _('yes'), _('no'),
                                            default_label=_('yes'))
                if accepted:
                    self.__error(_("Will overwrite the existing file: %s"
                                  ) % fullpath)
                else:
                    sys.exit(1)

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
            self.__error(_("ERROR: Unrecognized format for export file %s"
                          ) % fname)
            sys.exit(1)

    def __deduce_db_path(self, db_name_or_path):
        """
        Attempt to find a database path for the given parameter.

        :returns: The path to a Gramps DB or None if a database can not be
                  deduced.
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
        Method to handle the arguments that can be given for a GUI session.

        :returns: the filename of the family tree that should be opened if
                  user just passed a famtree or a filename.

        1. no options: a family tree can be given, if so, this name is tested
           and returned. If a filename, it is imported in a new db and name of
           new db returned
        2. an open and/or import option can have been given, if so, this is
           handled, and None is returned
        """
        if self.open_gui:
            # First check if a Gramps database was provided
            # (either a database path or a database name)
            db_path = self.__deduce_db_path(self.open_gui)

            if not db_path:
                # Apparently it is not a database. See if it is a file that
                # can be imported.
                db_path, title = self.dbman.import_new_db(self.open_gui,
                                                          self.user)

            if db_path:
                # Test if not locked or problematic
                if not self.check_db(db_path, self.force_unlock):
                    sys.exit(1)
                # Add the file to the recent items
                title = self.dbstate.db.get_dbname()
                if not title:
                    title = db_path
                recent_files(db_path, title)
                self.open = db_path
                self.__open_action()
            else:
                sys.exit(_("Error: cannot open '%s'") % self.open_gui)
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

        :param: climan: the manager of a CLI session
        :type: :class:`.CLIManager` object
        """
        # Handle the "-l" List Family Trees option.
        if self.list:
            print(_('List of known Family Trees in your database path\n'))

            for name, dirname in sorted(self.dbman.family_tree_list(),
                                        key=lambda pair: pair[0].lower()):
                if (self.database_names is None
                        or any([(re.match("^" + dbname + "$", name)
                                 or dbname == name)
                                for dbname in self.database_names])):
                    print(_('%(full_DB_path)s with name "%(f_t_name)s"'
                           ) % {'full_DB_path' : dirname,
                                'f_t_name'     : name})
            return

        # Handle the "--remove" Family Tree
        if self.removes:
            for name in self.removes:
                self.dbman.remove_database(name, self.user)
            return

        # Handle the "-L" List Family Trees in detail option.
        if self.list_more:
            self.dbman.print_family_tree_summaries(self.database_names)
            return

        # Handle the "-t" List Family Trees, tab delimited option.
        if self.list_table:
            print(_('Gramps Family Trees:'))
            summary_list = self.dbman.family_tree_summary(self.database_names)
            if not summary_list:
                return
            # We have to construct the line elements together, to avoid
            # insertion of blank spaces when print on the same line is used
            line_list = [_("Family Tree")]
            for key in sorted(summary_list[0]):
                if key != _("Family Tree"):
                    line_list += [key]
            print("\t".join(line_list))
            for summary in sorted(summary_list,
                                  key=lambda
                                      sum: sum[_("Family Tree")].lower()):
                line_list = [(_('"%s"') % summary[_("Family Tree")])]
                for item in sorted(summary):
                    if item != _("Family Tree"):
                        # translators: used in French+Russian, ignore otherwise
                        line_list += [(_('"%s"') % summary[item])]
                print("\t".join(line_list))
            return

        self.__open_action()
        self.__import_action()

        for (action, op_string) in self.actions:
            print(_("Performing action: %s."
                   ) % action,
                  file=sys.stderr)
            if op_string:
                print(_("Using options string: %s"
                       ) % op_string,
                      file=sys.stderr)
            self.cl_action(action, op_string)

        for expt in self.exports:
            print(_("Exporting: file %(filename)s, format %(format)s."
                   ) % {'filename' : expt[0],
                        'format'   : expt[1]},
                  file=sys.stderr)
            self.cl_export(expt[0], expt[1])

        if cleanup:
            self.cleanup()

    def cleanup(self):
        """ clean up any remaining files """
        print(_("Cleaning up."), file=sys.stderr)
        # remove files in import db subdir after use
        self.dbstate.db.close()
        if self.imp_db_path:
            rm_tempdir(self.imp_db_path)

    def __import_action(self):
        """
        Take action for all given import files.

        .. note:: Family trees are not supported.

        If a family tree is open, the import happens on top of it. If not
        open, a new family tree is created, and the import done. If this
        is CLI, the created tree is deleted at the end (as some action will
        have happened that is now finished), if this is GUI, it is opened.
        """
        if self.imports:
            self.cl_bool = bool(self.exports or self.actions or self.cl_bool)

            if not self.open:
                # Create empty dir for imported database(s)
                if self.gui:
                    dbid = config.get('database.backend')
                    self.imp_db_path, title = self.dbman.create_new_db_cli(
                        dbid=dbid)
                else:
                    self.imp_db_path = get_empty_tempdir("import_dbdir")
                    dbid = config.get('database.backend')
                    newdb = make_database(dbid)

                try:
                    self.smgr.open_activate(self.imp_db_path, self.username, self.password)
                    msg = _("Created empty Family Tree successfully")
                    print(msg, file=sys.stderr)
                except:
                    print(_("Error opening the file."), file=sys.stderr)
                    print(_("Exiting..."), file=sys.stderr)
                    sys.exit(1)

            for imp in self.imports:
                msg = _("Importing: file %(filename)s, format %(format)s."
                       ) % {'filename' : imp[0],
                            'format'   : imp[1]}
                print(msg, file=sys.stderr)
                self.cl_import(imp[0], imp[1])

    def __open_action(self):
        """
        Take action on a family tree dir to open. It will be opened in the
        session manager
        """
        if self.open:
            # Family Tree to open was given. Open it
            # Then go on and process the rest of the command line arguments.
            self.cl_bool = bool(self.exports or self.actions)

            # we load this file for use
            try:
                self.smgr.open_activate(self.open, self.username, self.password)
                print(_("Opened successfully!"), file=sys.stderr)
            except:
                print(_("Error opening the file."), file=sys.stderr)
                print(_("Exiting..."), file=sys.stderr)
                sys.exit(1)

    def check_db(self, dbpath, force_unlock=False):
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
            self.__error(_("Database needs recovery, cannot open it!"))
            return False
        if self.dbman.backend_unavailable(dbpath):
            self.__error(_("Database backend unavailable, cannot open it!"))
            return False
        return True

    #-------------------------------------------------------------------------
    #
    # Import handler
    #
    #-------------------------------------------------------------------------
    def cl_import(self, filename, family_tree_format):
        """
        Command-line import routine.
        Try to import filename using the family_tree_format.
        """
        pmgr = BasePluginManager.get_instance()
        for plugin in pmgr.get_import_plugins():
            if family_tree_format == plugin.get_extension():
                import_function = plugin.get_import_function()
                import_function(self.dbstate.db, filename, self.user)

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
                export_function(self.dbstate.db, filename, self.user)

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
                options_str_dict = _split_options(options_str)
            except:
                options_str_dict = {}
                print(_("Ignoring invalid options string."),
                      file=sys.stderr)

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
                msg = _("Unknown report name.")
            else:
                msg = _("Report name not given. "
                        "Please use one of %(donottranslate)s=reportname"
                       ) % {'donottranslate' : '[-p|--options] name'}

            print(_("%s\n Available names are:") % msg, file=sys.stderr)
            for pdata in sorted(_cl_list, key=lambda pdata: pdata.id.lower()):
                # Print cli report name ([item[0]), GUI report name (item[4])
                if len(pdata.id) <= 25:
                    print("   %s%s- %s" % (pdata.id,
                                           " " * (26 - len(pdata.id)),
                                           pdata.name),
                          file=sys.stderr)
                else:
                    print("   %s\t- %s" % (pdata.id, pdata.name),
                          file=sys.stderr)

        elif action == "tool":
            from gramps.gui.plug import tool
            try:
                options_str_dict = dict([tuple(chunk.split('='))
                                         for chunk in options_str.split(',')])
            except:
                options_str_dict = {}
                print(_("Ignoring invalid options string."),
                      file=sys.stderr)

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
                        tool.cli_tool(dbstate=self.dbstate,
                                      name=name,
                                      category=category,
                                      tool_class=tool_class,
                                      options_class=options_class,
                                      options_str_dict=options_str_dict,
                                      user=self.user)
                        return
                msg = _("Unknown tool name.")
            else:
                msg = _("Tool name not given. "
                        "Please use one of %(donottranslate)s=toolname."
                       ) % {'donottranslate' : '[-p|--options] name'}

            print(_("%s\n Available names are:") % msg, file=sys.stderr)
            for pdata in sorted(_cli_tool_list,
                                key=lambda pdata: pdata.id.lower()):
                # Print cli report name ([item[0]), GUI report name (item[4])
                if len(pdata.id) <= 25:
                    print("   %s%s- %s" % (pdata.id,
                                           " " * (26 - len(pdata.id)),
                                           pdata.name),
                          file=sys.stderr)
                else:
                    print("   %s\t- %s" % (pdata.id, pdata.name),
                          file=sys.stderr)

        elif action == "book":
            try:
                options_str_dict = _split_options(options_str)
            except:
                options_str_dict = {}
                print(_("Ignoring invalid options string."),
                      file=sys.stderr)

            name = options_str_dict.pop('name', None)
            book_list = BookList('books.xml', self.dbstate.db)
            if name:
                if name in book_list.get_book_names():
                    cl_book(self.dbstate.db, name, book_list.get_book(name),
                            options_str_dict)
                    return
                msg = _("Unknown book name.")
            else:
                msg = _("Book name not given. "
                        "Please use one of %(donottranslate)s=bookname."
                       ) % {'donottranslate' : '[-p|--options] name'}

            print(_("%s\n Available names are:") % msg, file=sys.stderr)
            for name in sorted(book_list.get_book_names()):
                print("   %s" % name, file=sys.stderr)

        else:
            print(_("Unknown action: %s.") % action, file=sys.stderr)
            sys.exit(1)
