
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#
# Modified by Alex Roitman to handle media object files.
#

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import string
import os
import shutil
from xml.parsers.expat import ExpatError

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import RelLib
from GrampsParser import GrampsParser, GrampsImportParser
from QuestionDialog import ErrorDialog, WarningDialog
from intl import gettext as _

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
def importData(database, filename, callback):

    filename = os.path.normpath(filename)
    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}

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
        ErrorDialog(_("%s could not be opened") % filename,str(msg))
        return 0
    except:
        ErrorDialog(_("%s could not be opened") % filename)
        return 0
        
    try:
        parser.parse(xml_file)
    except IOError,msg:
        ErrorDialog(_("Error reading %s") % filename,str(msg))
        import traceback
        traceback.print_exc()
        return 0
    except ExpatError, msg:
        ErrorDialog(_("Error reading %s") % filename,
                    _("The file is probably either corrupt or not a valid GRAMPS database."))
        return 0
    except ValueError, msg:
        pass
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
        return 0

    xml_file.close()
    del parser
    
    # Rename media files if they were conflicting with existing ones
    ObjectMap = database.getObjectMap()
    newpath = database.getSavePath()
    for OldMediaID in parser.MediaFileMap.keys():
        NewMediaID = parser.MediaFileMap[OldMediaID]
        oldfile = ObjectMap[NewMediaID].getPath()
	oldpath = os.path.dirname(oldfile)
	(junk,oldext) = os.path.splitext(os.path.basename(oldfile))
        oldfile = os.path.join(basefile,OldMediaID+oldext)
        newfile = os.path.join(newpath,NewMediaID+oldext)
        try:
	    shutil.copy2(oldfile,newfile)
            ObjectMap[NewMediaID].setPath(os.path.join(newfile))
            ObjectMap[NewMediaID].setLocal(1)
        except:
            # File is lost => remove all references and the object itself
            mobj = ObjectMap[NewMediaID]
            for p in database.getFamilyMap().values():
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            for key in database.getPersonKeys():
                p = database.getPerson(key)
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            for key in database.getSourceKeys():
                p = database.getSource(key)
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            for key in database.getPlaceKeys():
                p = database.getPlace(key)
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            
            database.removeObject(NewMediaID) 
    
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
    except:
        ErrorDialog(_("Error reading %s") % filename)
        import traceback
        traceback.print_exc()
        return 0

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
