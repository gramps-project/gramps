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

"""
Change id IDs of all the elements in the database to conform to the
scheme specified in the database's prefix ids
"""

import re
import Utils
import intl

_ = intl.gettext

_findint = re.compile('^[^\d]*(\d+)[^\d]*')

def runTool(db,active_person,callback):
    """Changed person, family, object, source, and place ids"""
    try:
        ReorderIds(db,callback)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

class ReorderIds:

    def __init__(self,db,callback):
        self.db = db

        self.reorder(db.getPersonMap(),db.iprefix,db.buildPersonDisplay)
        self.reorder(db.getFamilyMap(),db.fprefix,None)
        self.reorder(db.getObjectMap(),db.oprefix,None)
        self.reorder(db.getSourceMap(),db.sprefix,db.buildSourceDisplay)
        self.reorder(db.getPlaceMap(),db.pprefix,db.buildPlaceDisplay)
        Utils.modified()
        callback(1)

    def reorder(self,data_map,prefix,update):
        """Try to extract the old integer out of the id, and reuse it
        if possible. Otherwise, blindly renumber those that can't."""
        
        dups = []
        newids = []
        key_list = []

        # search all ids in the map

        for x in data_map.keys():
            key_list.append(x)

        for id in key_list:
            
            # attempt to extract integer, if we can't, treat it as a
            # duplicate

            match = _findint.match(id)
            if match:
                # get the integer, build the new id. Make sure it
                # hasn't already been chosen. If it has, put this
                # in the duplicate id list

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
                    if update:
                        update(newid,id)
            else:
                dups.append(id)
            
        # go through the duplicates, looking for the first availble
        # id that matches the new scheme.
    
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
            if update:
                update(newid,id)
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

