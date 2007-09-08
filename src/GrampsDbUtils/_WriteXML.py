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
# export_data
#
#-------------------------------------------------------------------------
def export_data(database, filename, person, option_box, callback=None):
    """
    Calls the XML writer with the syntax expected by the export plugin
    """
    return GrampsDb.exportData(database, filename, person, option_box, 
                               callback, const.VERSION)

#-------------------------------------------------------------------------
#
# XmlWriter
#
#-------------------------------------------------------------------------
class XmlWriter(GrampsDb.GrampsDbXmlWriter):
    """
    Writes a database to the XML file.
    """

    def __init__(self, dbase, callback, strip_photos, compress=1):
        GrampsDb.GrampsDbXmlWriter.__init__(
            self, dbase, strip_photos, compress, const.VERSION, callback)
        
    def write(self, filename):
        """
        Write the database to the specified file.
        """
        try:
            ret = GrampsDb.GrampsDbXmlWriter.write(self, filename)
        except GrampsDb.GrampsDbWriteFailure, val:
            ErrorDialog(val[0], val[1])
        return ret
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
TITLE = _('GRAMPS _XML database')
DESCRIPTION = _('The GRAMPS XML database is a format used by older '
                'versions of GRAMPS. It is read-write compatible with '
                'the present GRAMPS database format.')
CONFIG = (_('GRAMPS XML export options'), ExportOptions.WriterOptionBox)
FILENAME = 'gramps'

from PluginUtils import register_export
register_export(export_data, TITLE, DESCRIPTION, CONFIG, FILENAME)
