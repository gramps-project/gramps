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

import string
import time
import gzip
import os
from gnome.ui import *

import xml.sax
import xml.sax.saxexts
import xml.sax.saxutils
import xml.parsers.expat

_ = intl.gettext

#-------------------------------------------------------------------------
#
# Initialization function for the module.  Called to start the reading
# of data.
#
#-------------------------------------------------------------------------
def importData(database, filename, callback):

    parser = xml.sax.saxexts.make_parser()
    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}
    parser.setDocumentHandler(GrampsParser(database,callback,basefile,1))
    xml_file = gzip.open(filename,"rb")

    parser.parseFile(xml_file)
    xml_file.close()

#-------------------------------------------------------------------------
#
# Initialization function for the module.  Called to start the reading
# of data.
#
#-------------------------------------------------------------------------
def loadData(database, filename, callback):

    parser = xml.sax.saxexts.make_parser()

    basefile = os.path.dirname(filename)
    database.smap = {}
    database.pmap = {}
    database.fmap = {}
    parser.setErrorHandler(xml.sax.saxutils.ErrorRaiser())
    parser.setDocumentHandler(GrampsParser(database,callback,basefile,0))

    filename = os.path.normpath(filename)

    try:
        xml_file = gzip.open(filename,"rb")
    except IOError,msg:
        GnomeErrorDialog(filename + _(" could not be opened\n") + str(msg))
        return 0
    except:
        GnomeErrorDialog(filename + _(" could not be opened\n"))
        return 0
        
    try:
        parser.parseFile(xml_file)
    except xml.sax.SAXParseException:
        GnomeErrorDialog(filename + _(" is a corrupt file"))
        return 0
    except xml.parsers.expat.ExpatError:
        GnomeErrorDialog(filename + _(" is a corrupt file"))
        return 0
    except IOError,msg:
        GnomeErrorDialog(filename + _(" is not a valid gramps file\n") + \
                         str(msg))
        return 0
    except:
        GnomeErrorDialog(_("Could not read ") + filename)
        return 0
        
    xml_file.close()
    return 1













