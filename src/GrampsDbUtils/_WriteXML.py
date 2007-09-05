#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# load GRAMPS libraries
#
#-------------------------------------------------------------------------
import const
from QuestionDialog import ErrorDialog

import GrampsDb
import ExportOptions

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def exportData(database, filename, person, option_box, callback=None):
    return GrampsDb.exportData(database, filename, person, option_box, 
                               callback, const.version)

#-------------------------------------------------------------------------
#
# XmlWriter
#
#-------------------------------------------------------------------------
class XmlWriter(GramspDb.GrampsDbXmlWriter):
    """
    Writes a database to the XML file.
    """

    def __init__(self, db, callback, strip_photos, compress=1):
        GrampsDb.GrampsDbXmlWriter.__init__(self, db, strip_photos, compress, 
                                            const.version, callback)
        
    def write(self,filename):
        """
        Write the database to the specified file.
        """
        try:
            ret = GramspDb.GrampsDbXmlWriter.write(self, filename)
        except GrampsDb.GrampsDbWriteFailure, val:
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
_config = (_('GRAMPS XML export options'), ExportOptions.WriterOptionBox)
_filename = 'gramps'

from PluginUtils import register_export
register_export(exportData,_title,_description,_config,_filename)
