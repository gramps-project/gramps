#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005  Donald N. Allingham
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

# Written by Alex Roitman

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from _GrampsBSDDB import GrampsBSDDB
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
#
#-------------------------------------------------------------------------
def exportData(database, filename, person=None, callback=None, cl=False):

    filename = os.path.normpath(filename)

    new_database = GrampsBSDDB()
    try:
        new_database.load(filename,callback)
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
        else:
            ErrorDialog(_("%s could not be opened") % filename)
        return
    
    # copy all data from new_database to database,

    for handle in database.person_map.keys():
        new_database.person_map.put(handle,
                database.person_map.get(handle))
    for handle in database.family_map.keys():
        new_database.family_map.put(handle,
                database.family_map.get(handle))
    for handle in database.place_map.keys():
        new_database.place_map.put(handle,
                database.place_map.get(handle))
    for handle in database.source_map.keys():
        new_database.source_map.put(handle,
                database.source_map.get(handle))
    for handle in database.media_map.keys():
        new_database.media_map.put(handle,
                database.media_map.get(handle))
    for handle in database.event_map.keys():
        new_database.event_map.put(handle,
                database.event_map.get(handle))
    for handle in database.metadata.keys():
        new_database.metadata.put(handle,
                database.metadata.get(handle))

    new_database.close()
