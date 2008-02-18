#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007 Donald N. Allingham
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

# $Id:_GrampsDbWRFactories.py 9912 2008-01-22 09:17:46Z acraphae $

"""
This module contains factory methods for accessing the different
GrampsDb backends. These methods should be used obtain the correct class
for a database backend.

The app_* constants in const.py can be used to indicate which backend is
required e.g.:

>     # To get a XML writer
>     GrampsDb.gramps_db_writer_factory(db_type = const.APP_GRAMPS_XML)
>
>     # To get a Gedcom reader
>     GrampsDb.gramps_db_reader_factory(db_type = const.APP_GEDCOM)

As of 3.0 the writer_factory is deprecated. Exporter uses directly the plugin
system for export, no factory needed.
"""
import const

import logging
log = logging.getLogger(".GrampDb")

from gen.db import GrampsDbException
from PluginUtils import import_list

def gramps_db_reader_factory(db_type):
    """Factory class for obtaining a Gramps database importer.
    
    @param db_type: the type of backend required.
    @type db_type: one of the app_* constants in const.py

    Raises GrampsDbException if the db_type is not recognised.
    """
    if db_type == const.APP_FAMTREE :
        import importdbdir
        md = importdbdir.importData
    elif db_type == const.APP_GRAMPS_XML:
        import _ReadXML as ReadXML
        md = ReadXML.importData
    elif db_type == const.APP_GEDCOM:
        import _ReadGedcom as ReadGedcom
        md = ReadGedcom.importData
    else:
        #see if registered importer
        found = False
        for data in import_list:
            if db_type == data[2]:
                print "Found import plugin for %s" % data[4]
                found = True
                md = data[0]
                break
        if not found:
            raise GrampsDbException("Attempt to create a database "
                                    "reader for unknown format: "
                                    "db_type = %s" % (str(db_type)))

    return md


        
