#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import string
import os
import gtk
import shutil
from xml.parsers.expat import ExpatError

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import RelLib
from GrampsParser import GrampsParser, GrampsImportParser
from QuestionDialog import ErrorDialog, WarningDialog, MissingMediaDialog
from gettext import gettext as _
import Utils

#-------------------------------------------------------------------------
#
# Try to detect the presence of gzip
#
#-------------------------------------------------------------------------
try:
    import gzip
    gzip_ok = 1
except:
    gzip_ok = 0

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
# Must takes care of renaming media files according to their new IDs.
#
#-------------------------------------------------------------------------
def importData(database, filename, callback,cl=0):

    filename = os.path.normpath(filename)
    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}
    missmedia_action = 0

    parser = GrampsImportParser(database,callback,basefile)

    if gzip_ok:
        use_gzip = 1
        try:
            f = gzip.open(filename,"r")
            f.read(1)
            f.close()
        except IOError,msg:
            use_gzip = 0
        except ValueError, msg:
            use_gzip = 1
    else:
        use_gzip = 0

    try:
        if use_gzip:
            xml_file = gzip.open(filename,"rb")
        else:
            xml_file = open(filename,"r")
    except IOError,msg:
        if cl:
            print "Error: %s could not be opened Exiting." % filename
            print msg
            os._exit(1)
        else:
            ErrorDialog(_("%s could not be opened") % filename,str(msg))
            return 0
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
            os._exit(1)
        else:
            ErrorDialog(_("%s could not be opened") % filename)
            return 0
        
    try:
        parser.parse(xml_file)
    except IOError,msg:
        if cl:
            print "Error reading %s" % filename
            print msg
            import traceback
            traceback.print_exc()
            os._exit(1)
        else:
            ErrorDialog(_("Error reading %s") % filename,str(msg))
            import traceback
            traceback.print_exc()
            return 0
    except ExpatError, msg:
        if cl:
            print "Error reading %s" % filename
            print "The file is probably either corrupt or not a valid GRAMPS database."
            os._exit(1)
        else:
            ErrorDialog(_("Error reading %s") % filename,
                        _("The file is probably either corrupt or not a valid GRAMPS database."))
            return 0
    except ValueError, msg:
        pass
    except:
        if cl:
            import traceback
            traceback.print_exc()
            os._exit(1)
        else:
            import DisplayTrace
            DisplayTrace.DisplayTrace()
            return 0

    xml_file.close()
    
#-------------------------------------------------------------------------
    def remove_clicked():
        # File is lost => remove all references and the object itself
        mobj = ObjectMap[NewMediaID]
        for p in database.get_family_id_map().values():
            nl = p.get_media_list()
            for o in nl:
                if o.get_reference() == mobj:
                    nl.remove(o) 
            p.set_media_list(nl)
        for key in database.get_person_keys():
            p = database.get_person(key)
            nl = p.get_media_list()
            for o in nl:
                if o.get_reference() == mobj:
                    nl.remove(o) 
            p.set_media_list(nl)
        for key in database.get_source_keys():
            p = database.get_source(key)
            nl = p.get_media_list()
            for o in nl:
                if o.get_reference() == mobj:
                    nl.remove(o) 
            p.set_media_list(nl)
        for key in database.get_place_id_keys():
            p = database.get_place_id(key)
            nl = p.get_media_list()
            for o in nl:
                if o.get_reference() == mobj:
                    nl.remove(o) 
            p.set_media_list(nl)
        database.remove_object(NewMediaID) 


    def leave_clicked():
        # File is lost => do nothing, leave as is
        pass


    def select_clicked():
        # File is lost => select a file to replace the lost one
        def fs_close_window(obj):
            pass

        def fs_ok_clicked(obj):
            name = fs_top.get_filename()
            if os.path.isfile(name):
                shutil.copyfile(name,newfile)
                try:
                    shutil.copystat(name,newfile)
                except:
                    pass

        fs_top = gtk.FileSelection("%s - GRAMPS" % _("Select file"))
        fs_top.hide_fileop_buttons()
        fs_top.ok_button.connect('clicked',fs_ok_clicked)
        fs_top.cancel_button.connect('clicked',fs_close_window)
        fs_top.run()
        fs_top.destroy()

#-------------------------------------------------------------------------

    # Rename media files if they were conflicting with existing ones
    ObjectMap = database.get_object_map()
    newpath = database.get_save_path()
    for OldMediaID in parser.MediaFileMap.keys():
        NewMediaID = parser.MediaFileMap[OldMediaID]
        oldfile = ObjectMap[NewMediaID].get_path()
        (junk,oldext) = os.path.splitext(os.path.basename(oldfile))
        oldfile = os.path.join(basefile,OldMediaID+oldext)
        newfile = os.path.join(newpath,NewMediaID+oldext)
    	ObjectMap[NewMediaID].set_path(newfile)
        ObjectMap[NewMediaID].setLocal(1)
        try:
	    shutil.copyfile(oldfile,newfile)
            try:
                shutil.copystat(oldfile,newfile)
            except:
                pass
        except:
            if cl:
                print "Warning: media file %s was not found," \
                    % os.path.basename(oldfile), "so it was ignored."
            else:
                # File is lost => ask what to do (if we were not told yet)
                if missmedia_action == 0:
                    mmd = MissingMediaDialog(_("Media object could not be found"),
	                _("%(file_name)s is referenced in the database, but no longer exists. " 
                            "The file may have been deleted or moved to a different location. " 
                            "You may choose to either remove the reference from the database, " 
                            "keep the reference to the missing file, or select a new file." 
                            ) % { 'file_name' : oldfile },
                        remove_clicked, leave_clicked, select_clicked)
                    missmedia_action = mmd.default_action
                elif missmedia_action == 1:
                    remove_clicked()
                elif missmedia_action == 2:
                    leave_clicked()
                elif missmedia_action == 3:
                    select_clicked()

    del parser
    return 1
    

#-------------------------------------------------------------------------
#
# Initialization function for the module.  Called to start the reading
# of data.
#
#-------------------------------------------------------------------------
def loadData(database, filename, callback=None):

    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}

    filename = os.path.normpath(filename)

    parser = GrampsParser(database,callback,basefile)

    if gzip_ok:
        use_gzip = 1
        try:
            f = gzip.open(filename,"r")
            f.read(1)
            f.close()
        except IOError,msg:
            use_gzip = 0
    else:
        use_gzip = 0

    try:
        if use_gzip:
            xml_file = gzip.open(filename,"rb")
        else:
            xml_file = open(filename,"r")
    except IOError,msg:
        filemsg = _("%s could not be opened.") % filename
        ErrorDialog(filemsg,str(msg))
        return 0
    except:
        ErrorDialog(_("%s could not be opened.") % filename)
        return 0

    try:
        parser.parse(xml_file)
    except IOError,msg:
        ErrorDialog(_("Error reading %s") % filename, str(msg))
        import traceback
        traceback.print_exc()
        return 0
#     except:
#         ErrorDialog(_("Error reading %s") % filename)
#         import traceback
#         traceback.print_exc()
#         return 0

    xml_file.close()
    del parser
    return 1

#-------------------------------------------------------------------------
#
# Initialization function for the module.  Called to start the reading
# of data.
#
#-------------------------------------------------------------------------
def loadRevision(database, file, filename, revision, callback=None):

    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}

    parser = GrampsParser(database,callback,basefile)

    filename = _("%s (revision %s)") % (filename,revision)
    
    try:
        parser.parse(file)
    except IOError,msg:
        ErrorDialog(_("Error reading %s") % filename,str(msg))
        import traceback
        traceback.print_exc()
        return 0
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
        return 0

    file.close()
    return 1
