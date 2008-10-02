#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham, A. Roitman
# Copyright (C) 2007-2008  B. Malengier
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
# GNOME/GTK
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import sys
import getopt
from gettext import gettext as _
import logging

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import GrampsDbUtils
import Mime
from QuestionDialog import ErrorDialog
import Config
import RecentFiles
import Utils
import gen.db.exceptions as GX
import gen
from DbManager import CLIDbManager, NAME_FILE, find_locker_name

from PluginUtils import Tool
from gen.plug import PluginManager
from ReportBase import CATEGORY_BOOK, CATEGORY_CODE, CATEGORY_WEB, cl_report

IMPORT_TYPES = (const.APP_GRAMPS_XML, const.APP_GEDCOM, 
                const.APP_GRAMPS_PKG, const.APP_GENEWEB, 
                const.APP_GRAMPS)

_help = """
Usage: gramps.py [OPTION...]
  --load-modules=MODULE1,MODULE2,...     Dynamic modules to load

Help options
  -?, --help                             Show this help message
  --usage                                Display brief usage message

Application options
  -O, --open=FAMILY_TREE                 Open family tree
  -i, --import=FILENAME                  Import file
  -o, --output=FILENAME                  Write file
  -f, --format=FORMAT                    Specify format
  -a, --action=ACTION                    Specify action
  -p, --options=OPTIONS_STRING           Specify options
  -d, --debug=LOGGER_NAME                Enable debug logs
  -l                                     List Family Trees
  -L                                     List Family Tree Details
  -u                                     Force unlock of family tree
"""

#-------------------------------------------------------------------------
# ArgHandler
#-------------------------------------------------------------------------
class ArgHandler:
    """
    This class is responsible for handling command line arguments (if any)
    given to gramps. The valid arguments are:

    FAMTREE             :   family tree name or database dir to open. 
                            All following arguments will be ignored.
    -O, --open=FAMTREE  :   Family tree or family tree database dir to open.
    -i, --import=FILE   :   filename to import.
    -o, --output=FILE   :   filename to export.
    -f, --format=FORMAT :   format of the file preceding this option.
    
    If the filename (no flags) is specified, the interactive session is 
    launched using data from filename. 
    In this mode (filename, no flags), the rest of the arguments is ignored.
    This is a mode suitable by default for GUI launchers, mime type handlers,
    and the like
    
    If no filename or -i option is given, a new interactive session (empty
    database) is launched, since no data is given anyway.
    
    If -O or -i option is given, but no -o or -a options are given, an
    interactive session is launched with the FILE (specified with -i). 
    
    If both input (-O or -i) and processing (-o or -a) options are given,
    interactive session will not be launched. 
    """

    def __init__(self, state, vm, args):
        self.state = state
        self.vm = vm
        self.args = args

        self.open_gui = None
        self.open = None
        self.cl = 0
        self.exports = []
        self.actions = []
        self.imports = []
        self.imp_db_path = None
        self.list = False
        self.list_more = False
        self.help = False
        self.force_unlock = False
        self.dbman = CLIDbManager(self.state)

        self.parse_args()

    #-------------------------------------------------------------------------
    # Argument parser: sorts out given arguments
    #-------------------------------------------------------------------------
    def parse_args(self):
        """
        Fill in lists with open, exports, imports, and actions options.

        Any parsing errors lead to abort.
        
        Possible: 
        1/ Just the family tree (name or database dir)
        2/ -O, Open of a family tree
        3/ -i, Import of any format understood by an importer, optionally provide
            -f to indicate format (possible: 'gedcom','gramps-xml','gramps-pkg',
                'grdb','geneweb'
        4/ -o, output a family tree in required format, optionally provide
            -f to indicate format (possible: 'gedcom',
                'gramps-xml','gramps-pkg','iso','wft','geneweb')
        5/ -a, --action:    An action (possible: 'check', 'summary', 'report', 
                            'tool')
        6/ -u, --force-unlock: A locked database can be unlocked by given this
                argument when opening it
                            
        """
        try:
            options, leftargs = getopt.getopt(self.args[1:],
                                             const.SHORTOPTS, const.LONGOPTS)
        except getopt.GetoptError, msg:
            print msg
            # return without filling anything if we could not parse the args
            print "Error parsing the arguments: %s " % self.args[1:]
            print "Type gramps --help for an overview of commands, or ",
            print "read manual pages."
            sys.exit(0)

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
        for opt_ix in range(len(options)):
            option, value = options[opt_ix]
            if option in ( '-O', '--open'):
                self.handle_open_option(value)
            elif option in ( '-i', '--import'):
                fname = value
                fullpath = os.path.abspath(os.path.expanduser(fname))

                format = 'famtree'
                ftype = Mime.get_type(fullpath)
                if not os.path.exists(fullpath):
                    #see if not just a name of a database is given
                    data = self.dbman.family_tree(fname)
                    if data is not None:
                        fname, ftype, title = data
                    else:
                        print "Input file does not exist:  %s" % fullpath
                        continue
                elif os.path.isdir(fullpath):
                    ftype = const.APP_FAMTREE
                    fname = fullpath
                elif opt_ix<len(options)-1 \
                            and options[opt_ix+1][0] in ( '-f', '--format'): 
                    format = options[opt_ix+1][1]
                    if format not in ('gedcom',
                                      'gramps-xml',
                                      'gramps-pkg',
                                      'grdb',
                                      'geneweb'):
                        print "Invalid format:  %s" % format
                        print "Ignoring input file:  %s" % fname
                        continue
                elif ftype == const.APP_GEDCOM:
                    format = 'gedcom'
                elif ftype == const.APP_GRAMPS_PKG:
                    format = 'gramps-pkg'
                elif ftype == const.APP_GRAMPS_XML:
                    format = 'gramps-xml'
                elif ftype == const.APP_GRAMPS:
                    format = 'grdb'
                elif ftype == const.APP_GENEWEB:
                    format = 'geneweb'
                else:
                    print 'Unrecognized type: "%s" for input file: %s' \
                          % (ftype,fname)
                    print "Ignoring input file:  %s" % fname
                    continue
                self.imports.append((fname, format))
            elif option in ( '-o', '--output' ):
                outfname = value
                fullpath = os.path.abspath(os.path.expanduser(outfname))
                if os.path.exists(fullpath):
                    print "WARNING: Output file already exist!"
                    print "WARNING: It will be overwritten:\n   %s" % fullpath
                    answer = None
                    while not answer:
                        answer = raw_input('OK to overwrite? (yes/no) ')
                    if answer.upper() in ('Y','YES'):
                        print "Will overwrite the existing file: %s" % fullpath
                    else:
                        print "Will skip the output file: %s" % fullpath
                        continue
                if opt_ix < len(options)-1 \
                            and options[opt_ix+1][0] in ( '-f', '--format'): 
                    outformat = options[opt_ix+1][1]
                    if outformat not in ('gedcom',
                                         'gramps-xml',
                                         'gramps-pkg',
                                         'grdb',
                                         'iso',
                                         'wft',
                                         'geneweb'):
                        print "Invalid format for output:  %s" % outformat
                        print "Ignoring output file:  %s" % outfname
                        continue
                elif outfname[-3:].upper() == "GED":
                    outformat = 'gedcom'
                elif outfname[-4:].upper() == "GPKG":
                    outformat = 'gramps-pkg'
                elif outfname[-3:].upper() == "WFT":
                    outformat = 'wft'
                elif outfname[-2:].upper() == "GW":
                    outformat = 'geneweb'
                elif outfname[-6:].upper() == "GRAMPS":
                    outformat = 'gramps-xml'
                elif outfname[-4:].upper() == "GRDB":
                    outformat = 'grdb'
                else:
                    print "Unrecognized format for output file %s" % outfname
                    print "Ignoring output file:  %s" % outfname
                    continue
                self.exports.append((fullpath, outformat))
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
                logger = logging.getLogger(value)
                logger.setLevel(logging.DEBUG)
            elif option in ('-l',):
                self.list = True
            elif option in ('-L',):
                self.list_more = True
            elif option in ('-h', '-?', '--help'):
                self.help = True
            elif option in ('-u', '--force-unlock'):
                self.force_unlock = True

    def handle_open_option(self, value):
        """
        Handle the "-O" or "--open" option.                            
        """
        db_path = None
        
        # First, check if this is the name of a family tree
        data = self.dbman.family_tree(value)
        if data is not None:
            # This is a known database name. Use it.
            db_path, ftype, title = data
        else:
            # This is not a known database name.
            # Check if the user provided a db path instead.
            fullpath = os.path.abspath(os.path.expanduser(value))
            if os.path.isdir(fullpath):
                # The user provided a directory. Check if it is a valid tree.
                name_file_path = os.path.join(fullpath, NAME_FILE)
                if os.path.isfile(name_file_path):
                    db_path = fullpath

        if db_path:
            # We have a potential database path.
            # Check if it is good.
            if not self.__check_db(db_path, self.force_unlock):
                sys.exit(0)
            self.open = db_path
        else:
            print _('Input family tree "%s" does not exist.') % value
            print _("If gedcom, gramps-xml or grdb, use the -i option to "
                    "import into a family tree instead")
            sys.exit(0)
                
    #-------------------------------------------------------------------------
    # Determine the need for GUI
    #-------------------------------------------------------------------------
    def need_gui(self):
        """
        Determine whether we need a GUI session for the given tasks.
        """
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
           
    #-------------------------------------------------------------------------
    # Overall argument handler: 
    # sorts out the sequence and details of operations
    #-------------------------------------------------------------------------
    def handle_args(self):
        """
        Depending on the given arguments, import or open data, launch
        session, write files, and/or perform actions.
        """

        if self.list:
            print 'List of known family trees in your database path\n'
            for name, dirname in self.dbman.family_tree_list():
                print dirname, ', with name ', name 
            sys.exit(0)
        if self.list_more:
            print 'GRAMPS Family Trees:'
            list = self.dbman.family_tree_summary()
            for dict in list:
                print "Family Tree \"%s\":" % dict["Family tree"]
                for item in dict:
                    if item != "Family tree":
                        print "   %s: %s" % (item, dict[item])
            sys.exit(0)
        if self.help:
            print _help
            sys.exit(0)
        if self.open_gui:
            # Filename was given as gramps FILENAME. 
            # Open a session with that file. Forget the rest of given arguments
            success = False
            if os.path.isdir(self.open_gui):
                #only accept if a name.txt is found
                path_name = os.path.join(self.open_gui, NAME_FILE)
                if os.path.isfile(path_name):
                    filetype = const.APP_FAMTREE
                    filename = self.open_gui
                else:
                    filetype = 'No Fam Tree Dir'
                    filename = self.open_gui
            else:
                filename = os.path.abspath(os.path.expanduser(self.open_gui))
                filetype = Mime.get_type(filename)
            if filetype in ('x-directory/normal',):
                success = True
                pass
            elif filetype in IMPORT_TYPES:
                # Say the type outloud
                if filetype == const.APP_GRAMPS:
                    print "Type: GRAMPS 2.2.x GRDB database"
                elif filetype == const.APP_GEDCOM:
                    print "Type: GEDCOM file"
                elif filetype == const.APP_GRAMPS_XML:
                    print "Type: GRAMPS XML database"
                elif filetype == const.APP_GRAMPS_PKG:
                    print "Type: GRAMPS XML package"

                filename, filetype, name = self.dbman.import_new_db(filetype, 
                                                               filename, None)
                success = True
            else:
                #see if not just a name of a database is given
                data = self.dbman.family_tree(self.open_gui)
                if data is not None:
                    filename, filetype = data[0], data[1]
                    success = True
                else:
                    ErrorDialog( 
                        _("Could not open file: %s") % filename,
                        _('Not a valid Family tree given to open\n\n'
                         ))
                    print "Exiting..." 
                    sys.exit(0)
            if success:
                # Test if not locked or problematic
                if not self.__check_db(filename, self.force_unlock):
                    sys.exit(0)
                # Add the file to the recent items
                path = os.path.join(filename, "name.txt")
                try:
                    ifile = open(path)
                    title = ifile.readline().strip()
                    ifile.close()
                except:
                    title = filename
                RecentFiles.recent_files(filename, title)
            else:
                sys.exit(1)
            return (filename, filetype)
           
        if self.open:
            # Family Tree to open was given. Open it 
            # Then go on and process the rest of the command line arguments.
            self.cl = bool(self.exports or self.actions)

            filename = self.open

            try:
                self.vm.open_activate(filename)
                print "Opened successfully!"
            except:
                print "Error opening the file." 
                print "Exiting..." 
                sys.exit(1)

        if self.imports:
            self.cl = bool(self.exports or self.actions or self.cl)

            if not self.open:
                # Create empty dir for imported database(s)
                self.imp_db_path = Utils.get_empty_tempdir("import_dbdir")
                
                newdb = gen.db.GrampsDBDir()
                newdb.write_version(self.imp_db_path)
                
                if not self.vm.db_loader.read_file(self.imp_db_path):
                    sys.exit(0)

            for imp in self.imports:
                print "Importing: file %s, format %s." % imp
                self.cl_import(imp[0], imp[1])

        elif len(self.args) > 1 and not self.open:
            print "No data was given -- will launch interactive session."
            print "To use in the command-line mode,", \
                "supply at least one input file to process."
            print "Launching interactive session..."

        if self.cl:
            for (action, options_str) in self.actions:
                print "Performing action: %s." % action
                if options_str:
                    print "Using options string: %s" % options_str
                self.cl_action(action, options_str)

            for expt in self.exports:
                print "Exporting: file %s, format %s." % expt
                self.cl_export(expt[0], expt[1])

            print "Cleaning up."
            # remove files in import db subdir after use
            self.state.db.close()
            if self.imp_db_path:
                Utils.rm_tempdir(self.imp_db_path)
            print "Exiting."
            sys.exit(0)

        elif Config.get(Config.RECENT_FILE) and Config.get(Config.AUTOLOAD):
            filename = Config.get(Config.RECENT_FILE)
            if os.path.isdir(filename) and \
                    os.path.isfile(os.path.join(filename, "name.txt")) and \
                    self.__check_db(filename):
                self.vm.db_loader.read_file(filename)
                return (filename, const.APP_FAMTREE)

    def __check_db(self, dbpath, force_unlock = False):
        # Test if not locked or problematic
        if force_unlock:
            self.dbman.break_lock(dbpath)
        if self.dbman.is_locked(dbpath):
            print _("Database is locked, cannot open it!")
            print _("  Info: %s") % find_locker_name(dbpath)
            return False
        if self.dbman.needs_recovery(dbpath):
            print _("Database needs recovery, cannot open it!")
            return False
        return True

    #-------------------------------------------------------------------------
    #
    # Import handler
    #
    #-------------------------------------------------------------------------
    def cl_import(self, filename, format):
        """
        Command-line import routine. Try to import filename using the format.
        Any errors will cause the sys.exit(1) call.
        """
        if format == 'famtree':
            #3.x database
            if not self.__check_db(filename):
                sys.exit(0)
            try:
                GrampsDbUtils.gramps_db_reader_factory(const.APP_FAMTREE)(
                    self.state.db, filename, empty)
            except AttributeError:
                print "Error importing Family Tree %s" % filename
                sys.exit(1)
        elif format == 'grdb':
            #2.x database
            filename = os.path.normpath(os.path.abspath(filename))
            try:
                GrampsDbUtils.gramps_db_reader_factory(const.APP_GRAMPS)(
                    self.state.db,filename,empty)
            except GX.GrampsDbException, e:
                print "%s" % e.value
                sys.exit(1)
            except:
                print "Error importing %s" % filename
                sys.exit(1)
        elif format == 'gedcom':
            filename = os.path.normpath(os.path.abspath(filename))
            filename = Utils.get_unicode_path(filename)
            try:
                # Cheating here to use default encoding
                from GrampsDbUtils._ReadGedcom import import2
                import2(self.state.db, filename, None, "", False)
            except:
                print "Error importing %s" % filename
                sys.exit(1)
        elif format == 'gramps-xml':
            try:
                GrampsDbUtils.gramps_db_reader_factory(const.APP_GRAMPS_XML)(
                    self.state.db,filename,None,self.cl)
            except:
                print "Error importing %s" % filename
                sys.exit(1)
        elif format == 'geneweb':
            import ImportGeneWeb
            filename = os.path.normpath(os.path.abspath(filename))
            try:
                ImportGeneWeb.importData(self.state.db, filename, None)
            except:
                print "Error importing %s" % filename
                sys.exit(1)
        elif format == 'gramps-pkg':
            tmpdir_path = Utils.get_empty_tempdir("imp_gpkgdir")
            try:
                import tarfile
                archive = tarfile.open(filename)
                for tarinfo in archive:
                    archive.extract(tarinfo, tmpdir_path)
                archive.close()
            except tarfile.ReadError, msg:
                print "Error reading archive:", msg
                sys.exit(1)
            except tarfile.CompressionError, msg:
                print "Error uncompressing archive:", msg
                sys.exit(1)
            except:
                print "Error extracting into %s" % tmpdir_path
                sys.exit(1)

            dbname = os.path.join(tmpdir_path, const.XMLFILE)

            try:
                GrampsDbUtils.gramps_db_reader_factory(const.APP_GRAMPS_XML)(
                    self.state.db,dbname,None)
            except:
                print "Error importing %s" % filename
                sys.exit(1)
            # Clean up tempdir after ourselves
            #     THIS HAS BEEN CHANGED, because now we want to keep images
            #     stay after the import is over. Just delete the XML file.
            ##jgs:FIXME for how long? just for debug? or this session?
            ##  must not be forever, since re-exec of this routine 
            ##   clears dirfiles without asking 
            ##   & expands nre tarball possibly overwriting subdirs
            ##
            ## if only debugging, could do Utils.rm_tempdir here
            ## in any case, no real harm (exc. space) to leave stuff here
            ## until next exec of this, which will discard all old stuff
            os.remove(dbname)
##             files = os.listdir(tmpdir_path) 
##             for fn in files:
##                 os.remove(os.path.join(tmpdir_path,fn))
##             os.rmdir(tmpdir_path)
        else:
            print "Invalid format:  %s" % format
            sys.exit(1)
        if not self.cl:
            if self.imp_db_path:
                return self.vm.open_activate(self.imp_db_path)
            else:
                return self.vm.open_activate(self.open)

    #-------------------------------------------------------------------------
    #
    # Export handler
    #
    #-------------------------------------------------------------------------
    def cl_export(self, filename, format):
        """
        Command-line export routine. 
        Try to write into filename using the format.
        Any errors will cause the sys.exit(1) call.
        """
        filename = os.path.abspath(os.path.expanduser(filename))
        if format == 'grdb':
            print "GRDB format write is no longer supported!"
            sys.exit(1)
        elif format == 'gedcom':
            try:
                gw = GrampsDbUtils.GedcomWriter(self.state.db, None, 1)
                ret = gw.write_gedcom_file(filename)
                print "... finished writing %s" % filename
            except:
                print "Error exporting %s" % filename
                sys.exit(1)
        elif format == 'gramps-xml':
            filename = os.path.normpath(os.path.abspath(filename))
            if filename:
                try:
                    g = GrampsDbUtils.XmlWriter(self.state.db, None, 0, 1)
                    ret = g.write(filename)
                    print "... finished writing %s" % filename
                except:
                    print "Error exporting %s" % filename
                    sys.exit(1)
            else:
                print "Error exporting %s" % filename
        elif format == 'gramps-pkg':
            try:
                import WritePkg
                writer = WritePkg.PackageWriter(self.state.db, filename)
                ret = writer.export()
                print "... finished writing %s" % filename
            except:
                print "Error creating %s" % filename
                sys.exit(1)
        elif format == 'iso':
            import WriteCD
            try:
                writer = WriteCD.PackageWriter(self.state.db, filename, 1)
                ret = writer.export()
                print "... finished writing %s" % filename
            except:
                print "Error exporting %s" % filename
                sys.exit(1)
        elif format == 'wft':
            import WriteFtree
            try:
                writer = WriteFtree.FtreeWriter(self.state.db, None, 1,
                                                filename)
                ret = writer.export_data()
                print "... finished writing %s" % filename
            except:
                print "Error exporting %s" % filename
                sys.exit(1)
        elif format == 'geneweb':
            import WriteGeneWeb
            try:
                writer = WriteGeneWeb.GeneWebWriter(self.state.db,
                                                    None, 1, filename)
                ret = writer.export_data()
                print "... finished writing %s" % filename
            except:
                print "Error exporting %s" % filename
                sys.exit(1)
        else:
            print "Invalid format: %s" % format
            sys.exit(1)

    #-------------------------------------------------------------------------
    #
    # Action handler
    #
    #-------------------------------------------------------------------------
    def cl_action(self, action, options_str):
        """
        Command-line action routine. Try to perform specified action.
        """
        pmgr = PluginManager.get_instance()
        if action == 'check':
            import Check
            checker = Check.CheckIntegrity(self.state.db, None, None)
            checker.check_for_broken_family_links()
            checker.cleanup_missing_photos(1)
            checker.check_parent_relationships()
            checker.cleanup_empty_families(0)
            errs = checker.build_report(1)
            if errs:
                checker.report(1)
        elif action == 'summary':
            import Summary
            text = Summary.build_report(self.state.db, None)
            print text
        elif action == "report":
            try:
                options_str_dict = dict( [ tuple(chunk.split('='))
                    for chunk in options_str.split(',') ] )
            except:
                options_str_dict = {}
                print "Ignoring invalid options string."

            name = options_str_dict.pop('name', None)
            _cl_list = pmgr.get_cl_list()
            if name:
                for item in _cl_list:
                    if name == item[0]:
                        category = item[1]
                        report_class = item[2]
                        options_class = item[3]
                        if category in (CATEGORY_BOOK, CATEGORY_CODE):
                            options_class(self.state.db, name, category, 
                                          options_str_dict)
                        else:
                            cl_report(self.state.db, name, category, report_class, 
                                      options_class, options_str_dict)
                        return
                # name exists, but is not in the list of valid report names
                msg = "Unknown report name."
            else:
                msg = "Report name not given. Please use -p name=reportname."
            
            print "%s\n Available names are:" % msg
            for item in _cl_list:
                # Print cli report name ([item[0]) and GUI report name (item[4])
                if len(item[0]) <= 25:
                    print "   %s%s- %s" % (item[0], 
                                           " " * (26 - len(item[0])), item[4])
                else:
                    print "   %s\t- %s" % (item[0], item[4])

        elif action == "tool":
            try:
                options_str_dict = dict( [ tuple(chunk.split('=')) for
                                           chunk in options_str.split(',') ] )
            except:
                options_str_dict = {}
                print "Ignoring invalid options string."

            name = options_str_dict.pop('name', None)
            _cli_tool_list = pmgr.get_cl_tool_list()
            if name:
                for item in _cli_tool_list:
                    if name == item[0]:
                        category = item[1]
                        tool_class = item[2]
                        options_class = item[3]
                        Tool.cli_tool(self.state, name, category, tool_class, 
                                      options_class, options_str_dict)
                        return
                msg = "Unknown tool name."
            else:
                msg = "Tool name not given. Please use -p name=toolname."
            
            print "%s\n Available names are:" % msg
            for item in _cli_tool_list:
                print "   %s" % item[0]
        else:
            print "Unknown action: %s." % action
            sys.exit(1)

def add_all_files_filter(chooser):
    """
    Add an all-permitting filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('All files'))
    mime_filter.add_pattern('*')
    chooser.add_filter(mime_filter)

def add_grdb_filter(chooser):
    """
    Add a GRDB filter to the file chooser dialog.
    """
    mime_filter = gtk.FileFilter()
    mime_filter.set_name(_('GRAMPS databases'))
    mime_filter.add_mime_type(const.APP_GRAMPS)
    chooser.add_filter(mime_filter)

def read_pkg(filename):
    print "FIXME: This is not re-implemented yet."

def empty(val):
    pass
