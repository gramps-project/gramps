#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# Written by Alex Roitman

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

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import GrampsDb
import Mime
import QuestionDialog
import Config
import RecentFiles
import Utils

from PluginUtils import Tool, cl_list, cli_tool_list
from ReportBase import CATEGORY_BOOK, CATEGORY_CODE, CATEGORY_WEB, cl_report

#-------------------------------------------------------------------------
# ArgHandler
#-------------------------------------------------------------------------
class ArgHandler:
    """
    This class is responsible for handling command line arguments (if any)
    given to gramps. The valid arguments are:

    FILE                :   filename to open. 
                            All following arguments will be ignored.
    -i, --import=FILE   :   filename to import.
    -O, --open=FILE     :   filename to open.
    -o, --output=FILE   :   filename to export.
    -f, --format=FORMAT :   format of the file preceding this option.
    
    If the filename (no flags) is specified, the interactive session is 
    launched using data from filename. If the filename is not in a natvive
    (grdb) format, dialog will be presented to set up a grdb database.
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

    def __init__(self,state,vm,args):
        self.state = state
        self.vm = vm
        self.args = args

        self.open_gui = None
        self.open = None
        self.cl = 0
        self.exports = []
        self.actions = []
        self.imports = []

        self.parse_args()

    #-------------------------------------------------------------------------
    # Argument parser: sorts out given arguments
    #-------------------------------------------------------------------------
    def parse_args(self):
        """
        Fill in lists with open, exports, imports, and actions options.

        Any parsing errors lead to abort via os._exit(1).
        """

        try:
            options,leftargs = getopt.getopt(self.args[1:],
                                             const.shortopts,const.longopts)
        except getopt.GetoptError:
            # return without filling anything if we could not parse the args
            print "Error parsing arguments: %s " % self.args[1:]
            os._exit(1)

        if leftargs:
            # if there were an argument without option,
            # use it as a file to open and return
            self.open_gui = leftargs[0]
            print "Trying to open: %s ..." % leftargs[0]
            return

        # Go over all given option and place them into appropriate lists
        for opt_ix in range(len(options)):
            o,v = options[opt_ix]
            if o in ( '-O', '--open'):
                fname = v
                fullpath = os.path.abspath(os.path.expanduser(fname))
                if not os.path.exists(fullpath):
                    print "Input file does not exist:  %s" % fullpath
                    continue
                ftype = Mime.get_type(fullpath)
                if opt_ix<len(options)-1 \
                            and options[opt_ix+1][0] in ( '-f', '--format'): 
                    format = options[opt_ix+1][1]
                    if format not in ('gedcom','gramps-xml','grdb'):
                        print "Invalid format:  %s" % format
                        print "Ignoring input file:  %s" % fname
                        continue
                elif ftype == const.app_gedcom:
                    format = 'gedcom'
                elif ftype == const.app_gramps_xml:
                    format = 'gramps-xml'
                elif ftype == const.app_gramps:
                    format = 'grdb'
                else:
                    print 'Unrecognized type: "%s" for input file: %s' \
                          % (ftype,fname)
                    print "Ignoring input file:  %s" % fname
                    continue
                self.open = (fname,format)
            elif o in ( '-i', '--import'):
                fname = v
                fullpath = os.path.abspath(os.path.expanduser(fname))
                if not os.path.exists(fullpath):
                    print "Input file does not exist:  %s" % fullpath
                    continue
                ftype = Mime.get_type(fullpath)

                if opt_ix<len(options)-1 \
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
                elif ftype == const.app_gedcom:
                    format = 'gedcom'
                elif ftype == const.app_gramps_package:
                    format = 'gramps-pkg'
                elif ftype == const.app_gramps_xml:
                    format = 'gramps-xml'
                elif ftype == const.app_gramps:
                    format = 'grdb'
                elif ftype == const.app_geneweb:
                    format = 'geneweb'
                else:
                    print 'Unrecognized type: "%s" for input file: %s' \
                          % (ftype,fname)
                    print "Ignoring input file:  %s" % fname
                    continue
                self.imports.append((fname,format))
            elif o in ( '-o', '--output' ):
                outfname = v
                fullpath = os.path.abspath(os.path.expanduser(outfname))
                if os.path.exists(fullpath):
                    print "WARNING: Output file already exist!"
                    print "WARNING: It will be overwritten:\n   %s" % fullpath
                    answer = None
                    while not answer:
                        answer = raw_input('OK to overwrite?  ')
                    if answer.upper() in ('Y','YES'):
                        print "Will overwrite the existing file: %s" % fullpath
                    else:
                        print "Will skip the output file: %s" % fullpath
                        continue
                if opt_ix<len(options)-1 \
                            and options[opt_ix+1][0] in ( '-f', '--format'): 
                    outformat = options[opt_ix+1][1]
                    if outformat not in ('gedcom',
                                         'gramps-xml',
                                         'gramps-pkg',
                                         'grdb',
                                         'iso',
                                         'wft',
                                         'geneweb'):
                        print "Invalid format:  %s" % outformat
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
                self.exports.append((outfname,outformat))
            elif o in ( '-a', '--action' ):
                action = v
                if action not in ( 'check', 'summary', 'report', 'tool' ):
                    print "Unknown action: %s. Ignoring." % action
                    continue
                options_str = ""
                if opt_ix<len(options)-1 \
                            and options[opt_ix+1][0] in ( '-p', '--options' ): 
                    options_str = options[opt_ix+1][1]
                self.actions.append((action,options_str))

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

        if self.open_gui:
            # Filename was given. Open a session with that file. Forget
            # the rest of given arguments.
            success = False
            filename = os.path.abspath(os.path.expanduser(self.open_gui))
            filetype = Mime.get_type(filename) 
            if filetype in (const.app_gramps,const.app_gedcom,
                            const.app_gramps_xml):
                # Say the type outloud
                if filetype == const.app_gramps:
                    print "Type: GRAMPS database"
                elif filetype == const.app_gedcom:
                    print "Type: GEDCOM file"
                elif filetype == const.app_gramps_xml:
                    print "Type: GRAMPS XML database"

                try:
                    self.vm.read_recent_file(filename,filetype)
                    print "Opened successfully!"
                    success = True
                except:
                    print "Cannot open %s. Exiting..."
            elif filetype in (const.app_gramps_package,):
                QuestionDialog.OkDialog( _("Opening non-native format"), 
                                    _("New GRAMPS database has to be set up "
                                      "when opening non-native formats. The "
                                      "following dialog will let you select "
                                      "the new database."),
                                    self.vm.window)
                prompter = NewNativeDbPrompter(self.vm,self.state)
                if not prompter.chooser():
                    QuestionDialog.ErrorDialog( 
                        _("New GRAMPS database was not set up"),
                        _('GRAMPS cannot open non-native data '
                          'without setting up new GRAMPS database.'))
                    print "Cannot continue without native database. Exiting..."
                    os._exit(1)
                elif filetype == const.app_gramps_package:
                    print "Type: GRAMPS package"
                    self.read_pkg(filename)
                success = True
            else:
                print "Unknown file type: %s" % filetype
                QuestionDialog.ErrorDialog( 
                        _("Could not open file: %s") % filename,
                        _('File type "%s" is unknown to GRAMPS.\n\n'
                          'Valid types are: GRAMPS database, GRAMPS XML, '
                          'GRAMPS package, and GEDCOM.') % filetype)
                print "Exiting..." 
                os._exit(1)
            if success:
                # Add the file to the recent items
                #RecentFiles.recent_files(filename,filetype)
                pass
            else:
                os._exit(1)
            return
           
        if self.open:
            # Filename to open was given. Open it natively (grdb or any of
            # the InMem formats, without setting up a new database. Then
            # go on and process the rest of the command line arguments.

            self.cl = bool(self.exports or self.actions)

            name,format = self.open
            success = False
            filename = os.path.abspath(os.path.expanduser(name))

            if format == 'grdb':
                filetype = const.app_gramps
                print "Type: GRAMPS database"
            elif format == 'gedcom':
                filetype = const.app_gedcom
                print "Type: GEDCOM"
            elif format == 'gramps-xml':
                filetype = const.app_gramps_xml
                print "Type: GRAMPS XML"
            else:
                print "Unknown file type: %s" % format
                print "Exiting..." 
                os._exit(1)

            try:
                self.vm.read_recent_file(filename,filetype)
                print "Opened successfully!"
                success = True
            except:
                print "Error opening the file." 
                print "Exiting..." 
                os._exit(1)

        if self.imports:
            self.cl = bool(self.exports or self.actions or self.cl)

            # Create dir for imported database(s)
            self.impdir_path = os.path.join(const.home_dir,"import")
            self.imp_db_path = os.path.join(self.impdir_path,"import_db.grdb")
            if not os.path.isdir(self.impdir_path):
                try:
                    os.mkdir(self.impdir_path,0700)
                except:
                    print "Could not create import directory %s. Exiting." \
                        % self.impdir_path 
                    os._exit(1)
            elif not os.access(self.impdir_path,os.W_OK):
                print "Import directory %s is not writable. Exiting." \
                    % self.impdir_path 
                os._exit(1)
            # and clean it up before use
            files = os.listdir(self.impdir_path) ;
            for fn in files:
                if os.path.isfile(os.path.join(self.impdir_path,fn)):
                    os.remove(os.path.join(self.impdir_path,fn))

            self.vm.db_loader.read_file(self.imp_db_path,const.app_gramps)

            for imp in self.imports:
                print "Importing: file %s, format %s." % imp
                self.cl_import(imp[0],imp[1])

        elif len(self.args) > 1 and not self.open:
            print "No data was given -- will launch interactive session."
            print "To use in the command-line mode,", \
                "supply at least one input file to process."
            print "Launching interactive session..."

        if self.cl:
            for (action,options_str) in self.actions:
                print "Performing action: %s." % action
                if options_str:
                    print "Using options string: %s" % options_str
                self.cl_action(action,options_str)

            for expt in self.exports:
                print "Exporting: file %s, format %s." % expt
                self.cl_export(expt[0],expt[1])

            print "Cleaning up."
            # remove import db after use
            self.state.db.close()
            if self.imports:
                os.remove(self.imp_db_path)
            print "Exiting."
            os._exit(0)

        elif Config.get(Config.RECENT_FILE) and Config.get(Config.AUTOLOAD):
            rf = Config.get(Config.RECENT_FILE)
            if os.path.isfile(rf):
                filetype = Mime.get_type(rf)
                self.vm.read_recent_file(rf,filetype)

    #-------------------------------------------------------------------------
    #
    # Import handler
    #
    #-------------------------------------------------------------------------
    def cl_import(self,filename,format):
        """
        Command-line import routine. Try to import filename using the format.
        Any errors will cause the os._exit(1) call.
        """
        if format == 'grdb':
            filename = os.path.normpath(os.path.abspath(filename))
            try:
                GrampsDb.gramps_db_reader_factory(const.app_gramps)(
                    self.state.db,filename,empty)
            except:
                print "Error importing %s" % filename
                os._exit(1)
        elif format == 'gedcom':
            filename = os.path.normpath(os.path.abspath(filename))
            try:
                # Cheating here to use default encoding
                from GrampsDb._ReadGedcom import import2
                import2(self.state.db,filename,None,None,False)
            except:
                print "Error importing %s" % filename
                os._exit(1)
        elif format == 'gramps-xml':
            try:
                GrampsDb.gramps_db_reader_factory(const.app_gramps_xml)(
                    self.state.db,filename,None,self.cl)
            except:
                print "Error importing %s" % filename
                os._exit(1)
        elif format == 'geneweb':
            import ImportGeneWeb
            filename = os.path.normpath(os.path.abspath(filename))
            try:
                ImportGeneWeb.importData(self.state.db,filename,None)
            except:
                print "Error importing %s" % filename
                os._exit(1)
        elif format == 'gramps-pkg':
            # Create tempdir, if it does not exist, then check for writability
            tmpdir_path = os.path.join(const.home_dir,"tmp")
            if not os.path.isdir(tmpdir_path):
                try:
                    os.mkdir(tmpdir_path,0700)
                except:
                    print "Could not create temporary directory %s" \
                          % tmpdir_path 
                    os._exit(1)
            elif not os.access(tmpdir_path,os.W_OK):
                print "Temporary directory %s is not writable" % tmpdir_path 
                os._exit(1)
            else:    # tempdir exists and writable -- clean it up if not empty
                files = os.listdir(tmpdir_path) ;
                for fn in files:
                    os.remove( os.path.join(tmpdir_path,fn) )

            try:
                import tarfile
                archive = tarfile.open(filename)
                for tarinfo in archive:
                    archive.extract(tarinfo,tmpdir_path)
                archive.close()
            except ReadError, msg:
                print "Error reading archive:", msg
                os._exit(1)
            except CompressError, msg:
                print "Error uncompressing archive:", msg
                os._exit(1)
            except:
                print "Error extracting into %s" % tmpdir_path
                os._exit(1)

            dbname = os.path.join(tmpdir_path,const.xmlFile)

            try:
                GrampsDb.gramps_db_reader_factory(const.app_gramps_xml)(
                    self.state.db,dbname,None)
            except:
                print "Error importing %s" % filename
                os._exit(1)
            # Clean up tempdir after ourselves
            #     THIS HAS BEEN CHANGED, because now we want to keep images
            #     stay after the import is over. Just delete the XML file.
            os.remove(dbname)
##             files = os.listdir(tmpdir_path) 
##             for fn in files:
##                 os.remove(os.path.join(tmpdir_path,fn))
##             os.rmdir(tmpdir_path)
        else:
            print "Invalid format:  %s" % format
            os._exit(1)
        if not self.cl:
            return self.vm.post_load()

    #-------------------------------------------------------------------------
    #
    # Export handler
    #
    #-------------------------------------------------------------------------
    def cl_export(self,filename,format):
        """
        Command-line export routine. 
        Try to write into filename using the format.
        Any errors will cause the os._exit(1) call.
        """
        filename = os.path.abspath(os.path.expanduser(filename))
        if format == 'grdb':
            try:
                GrampsDb.gramps_db_writer_factory(const.app_gramps)(
                    self.state.db,filename)
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        elif format == 'gedcom':
            try:
                gw = GrampsDb.GedcomWriter(self.state.db,None,1,filename)
                ret = gw.export_data(filename)
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        elif format == 'gramps-xml':
            filename = os.path.normpath(os.path.abspath(filename))
            if filename:
                try:
                    g = GrampsDb.XmlWriter(self.state.db,None,0,1)
                    ret = g.write(filename)
                except:
                    print "Error exporting %s" % filename
                    os._exit(1)
        elif format == 'gramps-pkg':
            try:
                import WritePkg
                writer = WritePkg.PackageWriter(self.state.db,filename)
                ret = writer.export()
            except:
                print "Error creating %s" % filename
                os._exit(1)
        elif format == 'iso':
            import WriteCD
            try:
                writer = WriteCD.PackageWriter(self.state.db,filename,1)
                ret = writer.export()
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        elif format == 'wft':
            import WriteFtree
            try:
                writer = WriteFtree.FtreeWriter(self.state.db,None,1,filename)
                ret = writer.export_data()
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        elif format == 'geneweb':
            import WriteGeneWeb
            try:
                writer = WriteGeneWeb.GeneWebWriter(self.state.db,
                                                    None,1,filename)
                ret = writer.export_data()
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        else:
            print "Invalid format: %s" % format
            os._exit(1)

    #-------------------------------------------------------------------------
    #
    # Action handler
    #
    #-------------------------------------------------------------------------
    def cl_action(self,action,options_str):
        """
        Command-line action routine. Try to perform specified action.
        Any errors will cause the os._exit(1) call.
        """
        if action == 'check':
            import Check
            checker = Check.CheckIntegrity(self.state.db,None,None)
            checker.check_for_broken_family_links()
            checker.cleanup_missing_photos(1)
            checker.check_parent_relationships()
            checker.cleanup_empty_families(0)
            errs = checker.build_report(1)
            if errs:
                checker.report(1)
        elif action == 'summary':
            import Summary
            text = Summary.build_report(self.state.db,None)
            print text
        elif action == "report":
            try:
                options_str_dict = dict( [ tuple(chunk.split('='))
                    for chunk in options_str.split(',') ] )
            except:
                options_str_dict = {}
                print "Ignoring invalid options string."

            name = options_str_dict.pop('name',None)
            if not name:
                print "Report name not given. Please use name=reportname"
                os._exit(1)

            for item in cl_list:
                if name == item[0]:
                    category = item[1]
                    report_class = item[2]
                    options_class = item[3]
                    if category in (CATEGORY_BOOK,CATEGORY_CODE,CATEGORY_WEB):
                        options_class(self.state.db,name,
                                      category,options_str_dict)
                    else:
                        cl_report(self.state.db,name,category,
                                  report_class,options_class,
                                  options_str_dict)
                    return

            print "Unknown report name. Available names are:"
            for item in cl_list:
                print "   %s" % item[0]
        elif action == "tool":
            try:
                options_str_dict = dict( [ tuple(chunk.split('=')) for
                                           chunk in options_str.split(',') ] )
            except:
                options_str_dict = {}
                print "Ignoring invalid options string."

            name = options_str_dict.pop('name',None)
            if not name:
                print "Tool name not given. Please use name=toolname"
                os._exit(1)

            for item in cli_tool_list:
                if name == item[0]:
                    category = item[1]
                    tool_class = item[2]
                    options_class = item[3]
                    Tool.cli_tool(self.state,name,category,
                                  tool_class,options_class,options_str_dict)
                    return

            print "Unknown tool name. Available names are:"
            for item in cli_tool_list:
                print "   %s" % item[0]
        else:
            print "Unknown action: %s." % action
            os._exit(1)

#-------------------------------------------------------------------------
#
# NewNativeDbPrompter
#
#-------------------------------------------------------------------------
class NewNativeDbPrompter:
    """
    This class allows to set up a new empty native (grdb) database.
    The filename is forced to have an '.grdb' extension. If not given,
    it is appended. 
    """
    
    def __init__(self,vm,state):
        self.vm = vm
        self.state = state

    def chooser(self):
        """
        Select the new file. Suggest the Untitled_X.grdb name.
        Return 1 when selection is made and 0 otherwise.
        """
        choose = gtk.FileChooserDialog(_('GRAMPS: Create GRAMPS database'),
                                       self.vm.window,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
        self.state.db.close()

        # Always add automatic (macth all files) filter
        add_all_files_filter(choose)
        add_grdb_filter(choose)

        # Suggested folder: try last open file, import, then last export, 
        # then home.
        default_dir = os.path.split(Config.get(Config.RECENT_FILE))[0] + os.path.sep
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_IMPORT_DIR)
        if len(default_dir)<=1:
            default_dir = Config.get(Config.RECENT_EXPORT_DIR)
        if len(default_dir)<=1:
            default_dir = '~/'

        new_filename = Utils.get_new_filename('grdb',default_dir)
        
        choose.set_current_folder(default_dir)
        choose.set_current_name(os.path.split(new_filename)[1])

        while (True):
            response = choose.run()
            if response == gtk.RESPONSE_OK:
                filename = unicode(choose.get_filename(),
                                   sys.getfilesystemencoding())
                if filename == None:
                    continue
                if os.path.splitext(filename)[1] != ".grdb":
                    filename = filename + ".grdb"
                choose.destroy()
                print Config.TRANSACTIONS
                self.state.db = GrampsDb.gramps_db_factory(const.app_gramps)(
                    Config.TRANSACTIONS)
                self.vm.read_file(filename)
                self.state.signal_change()
                self.change_page(None, None)
                # Add the file to the recent items
                RecentFiles.recent_files(filename,const.app_gramps)
                return True
            else:
                choose.destroy()
                return False
        choose.destroy()
        return False

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
    mime_filter.add_mime_type(const.app_gramps)
    chooser.add_filter(mime_filter)

def read_pkg(filename):
    print "FIXME: This is not re-implemented yet."

def empty(val):
    pass
