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
import intl
_ = intl.gettext


import string
import time
import gzip
import os
from gnome.ui import *

import xml.sax
import xml.sax.saxutils

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------
try:
    import xml.sax.saxexts
    sax = 1
except:
    from codecs import *
    sax = 2

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

    if sax == 1:
        parser = xml.sax.saxexts.make_parser()
        parser.setDocumentHandler(GrampsParser(database,callback,basefile,1))
        parser.setErrorHandler(xml.sax.saxutils.ErrorRaiser())
        xml_file = gzip.open(filename,"rb")
        parser.parseFile(xml_file)
    else:
        parser = xml.sax.make_parser()
        parser.setContentHandler(GrampsParser(database,callback,basefile,1))
        xml_file = EncodedFile(gzip.open(filename,"rb"),'utf-8','latin-1')
        parser.parse(xml_file)
        
    xml_file.close()

#-------------------------------------------------------------------------
#
# Initialization function for the module.  Called to start the reading
# of data.
#
#-------------------------------------------------------------------------
def loadData(database, filename, callback):

    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}

    filename = os.path.normpath(filename)

    if sax == 1:
        parser = xml.sax.saxexts.make_parser()
        parser.setDocumentHandler(GrampsParser(database,callback,basefile,0))
        parser.setErrorHandler(xml.sax.saxutils.ErrorRaiser())
    else:
        parser = xml.sax.make_parser()
        parser.setContentHandler(GrampsParser(database,callback,basefile,0))

    try:
        if sax == 1:
            xml_file = gzip.open(filename,"rb")
        else:
            xml_file = EncodedFile(gzip.open(filename,"rb"),'utf-8','latin-1')
    except IOError,msg:
        GnomeErrorDialog(_("%s could not be opened\n") % filename + str(msg))
        return 0
    except:
        GnomeErrorDialog(_("%s could not be opened\n") % filename)
        return 0
        
    try:
        if sax == 1:
            parser.parseFile(xml_file)
        else:
            parser.parse(xml_file)
    except xml.sax.SAXParseException:
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
    return 1


if __name__ == "__main__":

    import sys
    import time
    import profile
    
    def lcb(val):
        pass
    
    db = RelDataBase()
    file = sys.argv[1]

    t1 = time.time()

    loadData(db,file,lcb)
    t2 = time.time()
    print t2 - t1










