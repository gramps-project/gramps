#
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

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import string
import os

#-------------------------------------------------------------------------
#
# Gnome/GTK
#
#-------------------------------------------------------------------------
from gnome.ui import GnomeErrorDialog

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from RelLib import *
from GrampsParser import GrampsParser, GrampsImportParser
from intl import gettext
_ = gettext

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
# Initialization function for the module.  Called to start the reading
# of data.
#
#-------------------------------------------------------------------------
def importData(database, filename, callback):

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
    else:
        use_gzip = 0

    try:
        if use_gzip:
            xml_file = gzip.open(filename,"rb")
        else:
            xml_file = open(filename,"r")
    except IOError,msg:
        GnomeErrorDialog(_("%s could not be opened\n") % filename + str(msg))
        return 0
    except:
        GnomeErrorDialog(_("%s could not be opened\n") % filename)
        return 0
        
    try:
        parser.parse(xml_file)
    except IOError,msg:
        GnomeErrorDialog(_("Error reading %s") % filename + "\n" + str(msg))
        import traceback
        traceback.print_exc()
        return 0
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
        return 0

    xml_file.close()
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
        filemsg = _("%s could not be opened\n") % filename
        GnomeErrorDialog(filemsg + str(msg))
        return 0
    except:
        GnomeErrorDialog(_("%s could not be opened\n") % filename)
        return 0

    try:
        parser.parse(xml_file)
    except IOError,msg:
        errmsg = "%s\n%s" % (_("Error reading %s") % filename,str(msg))
        GnomeErrorDialog(errmsg)
        import traceback
        traceback.print_exc()
        return 0
    except:
        GnomeErrorDialog(_("Error reading %s") % filename)
        import traceback
        traceback.print_exc()
        return 0

    xml_file.close()
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
        errmsg = "%s\n%s" % (_("Error reading %s") % filename, str(msg))
        GnomeErrorDialog(errmsg)
        import traceback
        traceback.print_exc()
        return 0
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
        return 0

    file.close()
    return 1
