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

def runTool(db,active_person,callback,parent):
    """Changed person, family, object, source, and place ids"""
    # FIXME: Remove when plugin is properly implemented
    from QuestionDialog import OkDialog
    OkDialog(_("Plugin unavailable"),
            _("This plugin is not implemented yet. Please check the next version."),
            parent.topWindow)
    return

    try:
        ReorderIds(db,callback)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

class ReorderIds:

    def __init__(self,db,callback):

        self.db = db

        self.reorder(db.get_person_handle_map(),db.iprefix,db.build_person_display)
        self.reorder(db.get_family_handle_map(),db.fprefix,None)
        self.reorder(db.get_object_map(),db.oprefix,None)
        self.reorder(db.get_source_map(),db.sprefix,db.build_source_display)
        self.reorder(db.get_place_handle_map(),db.pprefix,db.build_place_display)
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

        for handle in key_list:
            
            # attempt to extract integer, if we can't, treat it as a
            # duplicate

            match = _findint.match(handle)
            if match:
                # get the integer, build the new handle. Make sure it
                # hasn't already been chosen. If it has, put this
                # in the duplicate handle list

                try:
                    index = match.groups()[0]
                    newhandle = prefix % int(index)
                    if newhandle == handle:
                        newids[newhandle] = handle
                        continue
                    elif data_map.has_key(newhandle):
                        dups.append(handle)
                    else:
                        data = data_map[handle]
                        data_map[newhandle] = data
                        newids[newhandle] = handle
                        data.set_handle(newhandle)
                        del data_map[handle]
                        if update:
                            update(newhandle,handle)
                except:
                    dups.append(handle)
            else:
                dups.append(handle)
            
        # go through the duplicates, looking for the first availble
        # handle that matches the new scheme.
    
        index = 0
        for handle in dups:
            while 1:
                newhandle = prefix % index
                if not newids.has_key(newhandle):
                    break
                index = index + 1
            newids[newhandle] = newhandle
            data = data_map[handle]
            data.set_handle(newhandle)
            data_map[newhandle] = data
            if update:
                update(newhandle,handle)
            del data_map[handle]
    
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

