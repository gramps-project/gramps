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

"Database Processing/Reorder gramps IDs"

import utils
import intl

_ = intl.gettext

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):

    for prefix in ["xyzzytemporaryid%d", "I%d"] :
        index = 0
        pmap = database.getPersonMap()
        for id in pmap.keys():
            newid = prefix % index
            person = pmap[id]
            person.setId(newid)
            pmap[newid] = person
            del pmap[id]
            index = index + 1

    for prefix in ["xyzzytemporaryid%d", "F%d"] :
        index = 0
        pmap = database.getFamilyMap()
        for id in pmap.keys():
            newid = prefix % index
            person = pmap[id]
            person.setId(newid)
            pmap[newid] = person
            del pmap[id]
            index = index + 1

    for prefix in ["xyzzytemporaryid%d", "S%d"] :
        index = 0
        pmap = database.getSourceMap()
        for id in pmap.keys():
            newid = prefix % index
            person = pmap[id]
            person.setId(newid)
            pmap[newid] = person
            del pmap[id]
            index = index + 1

    utils.modified()
    callback(1)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_description():
    return _("Reorders the gramps IDs according to gramps' default rules.")

def get_name():
    return _("Database Processing/Reorder gramps IDs")
