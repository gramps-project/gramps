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

from RelLib import *
from GrampsParser import *

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

import string
import time
import os
from gnome.ui import *
import sys

import intl
_ = intl.gettext

try:
    import gzip
    gzip_ok = 1
except:
    gzip_ok = 0

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------

try:
    from xml.sax import make_parser, SAXParseException, SAXReaderNotAvailable
except:
    from _xmlplus.sax import make_parser, SAXParseException, SAXReaderNotAvailable

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

    try:
        parser = make_parser()
    except SAXReaderNotAvailable:
        msg1 = _("GRAMPS is not able to find an XML parser on your system.")
        msg2 = _("This is probably due to an incomplete python or PyXML installation")
        GnomeErrorDialog("%s\n%s" % (msg1,msg2))
        return
    
    parser.setContentHandler(GrampsImportParser(database,callback,basefile))

    if gzip_ok:
        use_gzip = 1
        try:
            f = gzip.open(filename,"r")
            f.read(1)
            f.close()
        except IOError,msg:
            use_gzip = 0
            f.close()
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
    except SAXParseException:
        GnomeErrorDialog(_("%s is a corrupt file") % filename)
        import traceback
        traceback.print_exc()
        return 0
    except IOError,msg:
        GnomeErrorDialog(_("Error reading %s") % filename + "\n" + str(msg))
        import traceback
        traceback.print_exc()
        return 0
    except:
        GnomeErrorDialog(_("Error reading %s") % filename)
        import traceback
        traceback.print_exc()
        return 0

    xml_file.close()

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

    parser = make_parser()
    parser.setContentHandler(GrampsParser(database,callback,basefile))

    if gzip_ok:
        use_gzip = 1
        try:
            f = gzip.open(filename,"r")
            f.read(1)
            f.close()
        except IOError,msg:
            use_gzip = 0
            f.close()
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
    except SAXParseException,msg:
        line = string.split(str(msg),':')
        filemsg = _("%s is a corrupt file.") % filename
        errtype = string.strip(line[3])
        errmsg = _('A "%s" error on line %s was detected.') % (errtype,line[1])
        GnomeErrorDialog("%s\n%s" % (filemsg,errmsg))
        return 0
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

    parser = make_parser()
    parser.setContentHandler(GrampsParser(database,callback,basefile))

    filename = _("%s (revision %s)") % (filename,revision)
    
    try:
        parser.parse(file)
    except SAXParseException,msg:
        line = string.split(str(msg),':')
        filemsg = _("%s is a corrupt file.") % filename
        errtype = string.strip(line[3])
        errmsg = _('A "%s" error on line %s was detected.') % (errtype,line[1])
        GnomeErrorDialog("%s\n%s" % (filemsg,errmsg))
        return 0
    except IOError,msg:
        errmsg = "%s\n%s" % (_("Error reading %s") % filename, str(msg))
        GnomeErrorDialog(errmsg)
        import traceback
        traceback.print_exc()
        return 0
    except:
        GnomeErrorDialog(_("Error reading %s") % filename)
        import traceback
        traceback.print_exc()
        return 0

    file.close()
    return 1


if __name__ == "__main__":
    import profile
    import cPickle
    
    database = RelDataBase()
    t1 = time.time()
    #profile.run('loadData(database, sys.argv[1])')
    loadData(database,sys.argv[1])
    t2 = time.time()
    print t2-t1
    f = gzip.open("autosave","w")
    p = cPickle.dump(database,f)
    f.close()
    t3 = time.time()
    print t3-t2
