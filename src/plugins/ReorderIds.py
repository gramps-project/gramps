#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
Change id IDs of all the elements in the database to conform to the
scheme specified in the database's prefix ids
"""

import re
import Utils
from gettext import gettext as _

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

        self.reorder(db.get_person_id_map(),db.iprefix,db.build_person_display)
        self.reorder(db.get_family_id_map(),db.fprefix,None)
        self.reorder(db.get_object_map(),db.oprefix,None)
        self.reorder(db.get_source_map(),db.sprefix,db.build_source_display)
        self.reorder(db.get_place_id_map(),db.pprefix,db.build_place_display)
        Utils.history_broken()
        callback(1)
        
    def reorder(self,data_map,prefix,update):
        """Try to extract the old integer out of the id, and reuse it
        if possible. Otherwise, blindly renumber those that can't."""
        
        dups = []
        newids = {}
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

                try:
                    index = match.groups()[0]
                    newid = prefix % int(index)
                    if newid == id:
                        newids[newid] = id
                        continue
                    elif data_map.has_key(newid):
                        dups.append(id)
                    else:
                        data = data_map[id]
                        data_map[newid] = data
                        newids[newid] = id
                        data.set_id(newid)
                        del data_map[id]
                        if update:
                            update(newid,id)
                except:
                    dups.append(id)
            else:
                dups.append(id)
            
        # go through the duplicates, looking for the first availble
        # id that matches the new scheme.
    
        index = 0
        for id in dups:
            while 1:
                newid = prefix % index
                if not newids.has_key(newid):
                    break
                index = index + 1
            newids[newid] = newid
            data = data_map[id]
            data.set_id(newid)
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

