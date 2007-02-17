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

"""
Contains the interface to allow a database to get written using
GRAMPS' XML file format.
"""

#-------------------------------------------------------------------------
#
# load standard python libraries
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WriteXML")

#-------------------------------------------------------------------------
#
# load GRAMPS libraries
#
#-------------------------------------------------------------------------
import const
from QuestionDialog import ErrorDialog

from GrampsDb import GrampsDbXmlWriter, GrampsDbWriteFailure
from GrampsDb import exportData as _exportData
from GrampsDb import quick_write as _quick_write

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename, person, callback=None, version=const.version):
    return _exportData(database, filename, person, version)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def quick_write(database, filename,callback=None,version=const.version):
    return _quick_write(database, filename, version)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class XmlWriter(GrampsDbXmlWriter):
    """
    Writes a database to the XML file.
    """

    def __init__(self,db,callback,strip_photos,compress=1):
        """
        """
        GrampsDbXmlWriter.__init__(self,version=const.version)
        
    def write(self,filename):
        """
        Write the database to the specified file.
        """
        try:
            ret = GrampsDbXmlWriter.write(self, filename)
        except GrampsDbWriteFailure, val:
            ErrorDialog(val[0],val[1])

        return ret
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
_title = _('GRAMPS _XML database')
_description = _('The GRAMPS XML database is a format used by older '
                'versions of GRAMPS. It is read-write compatible with '
                'the present GRAMPS database format.')
_config = None
_filename = 'gramps'

from PluginUtils import register_export
register_export(exportData,_title,_description,_config,_filename)
