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

import re
import utils
import intl

_ = intl.gettext

_findint = re.compile('^[^\d]*(\d+)[^\d]*')

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):

    make_new_ids(database.getPersonMap(),database.iprefix)
    make_new_ids(database.getFamilyMap(),database.fprefix)
    make_new_ids(database.getObjectMap(),database.oprefix)
    make_new_ids(database.getSourceMap(),database.sprefix)
    make_new_ids(database.getPlaceMap(),database.pprefix)
    utils.modified()
    callback(1)


def make_new_ids(data_map,prefix):
    dups = []
    newids = []
    for id in data_map.keys():
        match = _findint.match(id)
        if match:
            index = match.groups()[0]
            newid = prefix % int(index)
            if newid == id:
                continue
            elif data_map.has_key(newid):
                dups.append(id)
            else:
                newids.append(id)
                data = data_map[id]
                data.setId(newid)
                data_map[newid] = data
                del data_map[id]
    index = 0
    for id in dups:
        while 1:
            newid = prefix % index
            if newid not in newids:
                break
            index = index + 1
        newids.append(newid)
        data = data_map[id]
        data.setId(newid)
        data_map[newid] = data
        del data_map[id]
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Reorder gramps IDs"),
    category=_("Database Processing"),
    description=_("Reorders the gramps IDs according to gramps' default rules.")
    )

