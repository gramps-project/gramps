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
import shutil
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# load GRAMPS libraries
#
#-------------------------------------------------------------------------
import const
from QuestionDialog import ErrorDialog

import GrampsDbUtils
import ExportOptions
from gen.db.exceptions import GrampsDbWriteFailure
import gen.proxy

#-------------------------------------------------------------------------
#
# Attempt to load the GZIP library. Some version of python do not seem
# to be compiled with this available.
#
#-------------------------------------------------------------------------
try:
    import gzip
    _gzip_ok = 1
except:
    _gzip_ok = 0

#-------------------------------------------------------------------------
#
# export_data
#
#-------------------------------------------------------------------------
def export_data(database, filename, person, option_box, callback=None):
    """
    Call the XML writer with the syntax expected by the export plugin.
    """
    if os.path.isfile(filename):
        try:
            shutil.copyfile(filename, filename + ".bak")
            shutil.copystat(filename, filename + ".bak")
        except:
            pass

    compress = _gzip_ok == 1

    option_box.parse_options()

    restrict = option_box.restrict
    private = option_box.private

    if private:
        database = gen.proxy.PrivateProxyDb(database)

    if restrict:
        database = gen.proxy.LivingProxyDb(
            database, gen.proxy.LivingProxyDb.MODE_RESTRICT)

    if not option_box.cfilter.is_empty():
        database = gen.proxy.FilterProxyDb(database, option_box.cfilter)

    g = XmlWriter(database, callback, 0, compress)
    return g.write(filename)

#-------------------------------------------------------------------------
#
# XmlWriter
#
#-------------------------------------------------------------------------
class XmlWriter(GrampsDbUtils.GrampsDbXmlWriter):
    """
    Writes a database to the XML file.
    """

    def __init__(self, dbase, callback, strip_photos, compress=1):
        GrampsDbUtils.GrampsDbXmlWriter.__init__(
            self, dbase, strip_photos, compress, const.VERSION, callback)
        
    def write(self, filename):
        """
        Write the database to the specified file.
        """
        ret = 0 #False
        try:
            ret = GrampsDbUtils.GrampsDbXmlWriter.write(self, filename)
        except GrampsDbWriteFailure, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1, m2)
        return ret
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
TITLE = _('GRAMPS _XML database')
DESCRIPTION = _('The GRAMPS XML database is a text version of a family tree. '
                'It is read-write compatible with '
                'the present GRAMPS database format.')
CONFIG = (_('GRAMPS XML export options'), ExportOptions.WriterOptionBox)
FILENAME = 'gramps'

from PluginUtils import register_export
register_export(export_data, TITLE, DESCRIPTION, CONFIG, FILENAME)
