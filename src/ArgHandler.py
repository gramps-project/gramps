#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

#
# Written by Alex Roitman
#

"""
Module responsible for handling the command line arguments for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import getopt

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import ReadXML

#-------------------------------------------------------------------------
#
# ArgHandler
#
#-------------------------------------------------------------------------
class ArgHandler:

    def __init__(self,parent,args):
        self.parent = parent
        self.handle_args(args)

    def handle_args(self,args):
        try:
            options,leftargs = getopt.getopt(args,
                        const.shortopts,const.longopts)
        except getopt.GetoptError,msg:
            print "Error: %s. Exiting." % msg
            os._exit(1)
        except:
            print "Error parsing arguments: %s " % args
        if leftargs:
            print "Unrecognized option: %s" % leftargs[0]
            os._exit(1)
        exports = []
        actions = []
        imports = []
        for opt_ix in range(len(options)):
            o = options[opt_ix][0][1]
            if o == '-':
                continue
            elif o == 'i':
                fname = options[opt_ix][1]
                if opt_ix<len(options)-1 and options[opt_ix+1][0][1]=='f': 
                    format = options[opt_ix+1][1]
                    if format not in [ 'gedcom', 'gramps', 'gramps-pkg' ]:
                        print "Invalid format:  %s" % format
                        os._exit(1)
                elif fname[-3:].upper()== "GED":
                    format = 'gedcom'
                elif fname[-3:].upper() == "TGZ":
                    format = 'gramps-pkg'
                elif os.path.isdir(fname):
                    format = 'gramps'
                else:
                    print "Unrecognized format for input file %s" % fname
                    os._exit(1)
                imports.append((fname,format))
            elif o == 'o':
                outfname = options[opt_ix][1]
                if opt_ix<len(options)-1 and options[opt_ix+1][0][1]=='f': 
                    outformat = options[opt_ix+1][1]
                    if outformat not in [ 'gedcom', 'gramps', 'gramps-pkg', 'iso', 'wft' ]:
                        print "Invalid format:  %s" % outformat
                        os._exit(1)
                elif outfname[-3:].upper() == "GED":
                    outformat = 'gedcom'
                elif outfname[-3:].upper() == "TGZ":
                    outformat = 'gramps-pkg'
                elif outfname[-3:].upper() == "WFT":
                    outformat = 'wft'
                elif not os.path.isfile(outfname):
                    if not os.path.isdir(outfname):
                        try:
                            os.makedirs(outfname,0700)
                        except:
                            print "Cannot create directory %s" % outfname
                            os._exit(1)
                    outformat = 'gramps'
                else:
                    print "Unrecognized format for output file %s" % outfname
                    os._exit(1)
                exports.append((outfname,outformat))
            elif o == 'a':
                action = options[opt_ix][1]
                if action not in [ 'check', 'summary' ]:
                    print "Unknown action: %s." % action
                    os._exit(1)
                actions.append(action)
            
        if imports:
            self.parent.cl = bool(exports or actions)
            # Create dir for imported database(s)
            self.impdir_path = os.path.expanduser("~/.gramps/import" )
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
            self.parent.clear_database()
            self.parent.db.set_save_path(self.impdir_path)
            for imp in imports:
                print "Importing: file %s, format %s." % (imp[0],imp[1])
                self.cl_import(imp[0],imp[1])
        else:
            print "No data was given. Launching interactive session."
            print "To use in the command-line mode,", \
                "supply at least one input file to process."

        if self.parent.cl:
            for expt in exports:
                print "Exporting: file %s, format %s." % (expt[0],expt[1])
                self.cl_export(expt[0],expt[1])

            for action in actions:
                print "Performing action: %s." % action
                self.cl_action(action)
            
            print "Cleaning up."
            # clean import dir up after use
            files = os.listdir(self.impdir_path) ;
            for fn in files:
                if os.path.isfile(os.path.join(self.impdir_path,fn)):
                    os.remove(os.path.join(self.impdir_path,fn))
            print "Exiting."
            os._exit(0)


    def cl_import(self,filename,format):
        if format == 'gedcom':
            import ReadGedcom
            filename = os.path.normpath(os.path.abspath(filename))
            try:
                g = ReadGedcom.GedcomParser(self.parent.db,filename,None)
                g.parse_gedcom_file()
                g.resolve_refns()
                del g
            except:
                print "Error importing %s" % filename
                os._exit(1)
        elif format == 'gramps':
            try:
                dbname = os.path.join(filename,const.xmlFile)
                ReadXML.importData(self.parent.db,dbname,None,self.parent.cl)
            except:
                print "Error importing %s" % filename
                os._exit(1)
        elif format == 'gramps-pkg':
            # Create tempdir, if it does not exist, then check for writability
            tmpdir_path = os.path.expanduser("~/.gramps/tmp" )
            if not os.path.isdir(tmpdir_path):
                try:
                    os.mkdir(tmpdir_path,0700)
                except:
                    print "Could not create temporary directory %s" % tmpdir_path 
                    os._exit(1)
            elif not os.access(tmpdir_path,os.W_OK):
                print "Temporary directory %s is not writable" % tmpdir_path 
                os._exit(1)
            else:    # tempdir exists and writable -- clean it up if not empty
	        files = os.listdir(tmpdir_path) ;
                for fn in files:
                    os.remove( os.path.join(tmpdir_path,fn) )

            try:
                import TarFile
                t = TarFile.ReadTarFile(filename,tmpdir_path)
	        t.extract()
	        t.close()
            except:
                print "Error extracting into %s" % tmpdir_path 
                os._exit(1)

            dbname = os.path.join(tmpdir_path,const.xmlFile)  

            try:
                ReadXML.importData(self.parent.db,dbname,None)
            except:
                print "Error importing %s" % filename
                os._exit(1)
            # Clean up tempdir after ourselves
            files = os.listdir(tmpdir_path) 
            for fn in files:
                os.remove(os.path.join(tmpdir_path,fn))
            os.rmdir(tmpdir_path)
        else:
            print "Invalid format:  %s" % format
            os._exit(1)
        if not self.parent.cl:
            return self.parent.post_load(self.impdir_path)

    def cl_export(self,filename,format):
        if format == 'gedcom':
            import WriteGedcom
            try:
                g = WriteGedcom.GedcomWriter(self.parent.db,None,1,filename)
                del g
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        elif format == 'gramps':
            filename = os.path.normpath(os.path.abspath(filename))
            dbname = os.path.join(filename,const.xmlFile)
            if filename:
                try:
                    self.parent.save_media(filename)
                    self.parent.db.save(dbname,None)
                except:
                    print "Error exporting %s" % filename
                    os._exit(1)
        elif format == 'gramps-pkg':
            import TarFile
            import time
            import WriteXML
            from cStringIO import StringIO

            try:
                t = TarFile.TarFile(filename)
                mtime = time.time()
            except:
                print "Error creating %s" % filename
                os._exit(1)
        
            try:
                # Write media files first, since the database may be modified 
                # during the process (i.e. when removing object)
                ObjectMap = self.parent.db.get_object_map()
                for ObjectId in ObjectMap.keys():
                    oldfile = ObjectMap[ObjectId].get_path()
                    base = os.path.basename(oldfile)
                    if os.path.isfile(oldfile):
                        g = open(oldfile,"rb")
                        t.add_file(base,mtime,g)
                        g.close()
                    else:
                        print "Warning: media file %s was not found," % base,\
                            "so it was ignored."
            except:
                print "Error exporting media files to %s" % filename
                os._exit(1)
            try:
                # Write XML now
                g = StringIO()
                gfile = WriteXML.XmlWriter(self.parent.db,None,1)
                gfile.write_handle(g)
                mtime = time.time()
                t.add_file("data.gramps",mtime,g)
                g.close()
                t.close()
            except:
                print "Error exporting data to %s" % filename
                os._exit(1)
        elif format == 'iso':
            import WriteCD
            try:
                WriteCD.PackageWriter(self.parent.db,1,filename)
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        elif format == 'wft':
            import WriteFtree
            try:
                WriteFtree.FtreeWriter(self.parent.db,None,1,filename)
            except:
                print "Error exporting %s" % filename
                os._exit(1)
        else:
            print "Invalid format: %s" % format
            os._exit(1)

    def cl_action(self,action):
        if action == 'check':
            import Check
            checker = Check.CheckIntegrity(self.parent.db)
            checker.check_for_broken_family_links()
            checker.cleanup_missing_photos(1)
            checker.check_parent_relationships()
            checker.cleanup_empty_families(0)
            errs = checker.build_report(1)
            if errs:
                checker.report(1)
        elif action == 'summary':
            import Summary
            text = Summary.build_report(self.parent.db,None)
            print text
        else:
            print "Unknown action: %s." % action
            os._exit(1)
