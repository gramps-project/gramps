#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import re
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
from QuestionDialog import WarningDialog

_findint = re.compile('^[^\d]*(\d+)[^\d]*')

def runTool(db,active_person,callback,parent):
    """Changed person, family, object, source, and place ids"""
    #FIXME -- Remove when the tool is back from the dead
    WarningDialog(_('Tool currently unavailable'),
                _('This tool has not yet been brought up to date '
                'after transition to the database, sorry.'),parent.topWindow)
    return
    
    #FIXME
    try:
        ReorderIds(db,callback)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------
class ReorderIds:

    def __init__(self,db,callback):

        self.db = db

        self.reorder_person()
        self.reorder(db.get_family_handle_map(),db.fprefix,None)
        self.reorder(db.get_object_map(),db.oprefix,None)
        self.reorder(db.get_source_map(),db.sprefix,db.build_source_display)
        self.reorder(db.get_place_handle_map(),db.pprefix,db.build_place_display)
        callback(1)
        
    def reorder_person(self):
        dups = []
        newids = {}
        key_list = []

        # search all ids in the map

        cursor = self.db.get_person_cursor()
        data = cursor.first()
        while data:
            (handle,sdata) = data

            gramps_id = sdata[1]

            # attempt to extract integer, if we can't, treat it as a
            # duplicate

            match = _findint.match(gramps_id)
            if match:
                # get the integer, build the new handle. Make sure it
                # hasn't already been chosen. If it has, put this
                # in the duplicate handle list

                try:
                    index = match.groups()[0]
                    newgramps_id = prefix % int(index)
                    if newgramps_id == gramps_id:
                        newids[newgramps_id] = gramps_id
                        continue
                    elif data_map.has_key(newgramps_id):
                        dups.append(handle)
                    else:
                        data = data_map[gramps_id]
                        data_map[newgramps_id] = data
                        newids[newgramps_id] = gramps_id
                        data.set_gramps_id(newgramps_id)
                        del data_map[gramps_id]
                        if update:
                            update(newgramps_id,gramps_id)
                except:
                    dups.append(handle)
            else:
                dups.append(handle)

            data = cursor.next()

            
        # go through the duplicates, looking for the first availble
        # handle that matches the new scheme.
    
        index = 0
        for gramps_id in dups:
            while 1:
                newgramps_id = prefix % index
                if not newids.has_key(newgramps_id):
                    break
                index = index + 1
            newids[newgramps_id] = newgramps_id
            data = data_map[gramps_id]
            data.set_gramps_id(newgramps_id)
            data_map[newgramps_id] = data
            if update:
                update(newgramps_id,gramps_id)
            del data_map[gramps_id]
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    runTool,
    _("Reorder gramps IDs"),
    category=_("Database Processing"),
    description=_("Reorders the gramps IDs according to gramps' default rules.")
    )

