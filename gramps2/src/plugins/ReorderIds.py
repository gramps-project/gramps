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
import RelLib
from QuestionDialog import WarningDialog

_findint = re.compile('^[^\d]*(\d+)[^\d]*')

def runTool(db,active_person,callback,parent):
    """Changed person, family, object, source, and place ids"""
    #FIXME -- Remove when the tool is back from the dead
    #WarningDialog(_('Tool currently unavailable'),
    #            _('This tool has not yet been brought up to date '
    #            'after transition to the database, sorry.'),parent.topWindow)
    #return
    
    #FIXME
    try:
        ReorderIds(db)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------
class ReorderIds:

    def __init__(self,db):

        self.db = db

        self.progress = Utils.ProgressMeter(_('Reording GRAMPS IDs'),'')
                                            
        self.trans = db.transaction_begin()

        self.progress.set_pass(_('Reordering People IDs'),db.get_number_of_people())
        self.reorder(RelLib.Person, db.get_person_from_gramps_id, db.get_person_from_handle,
                     db.find_next_person_gramps_id, db.get_person_cursor, db.commit_person,
                     db.iprefix)
        self.progress.set_pass(_('Reordering Family IDs'),db.get_number_of_families())
        self.reorder(RelLib.Family,db.get_family_from_gramps_id, db.get_family_from_handle,
                     db.find_next_family_gramps_id, db.get_family_cursor, db.commit_family,
                     db.fprefix)
        self.progress.set_pass(_('Reordering Media Object IDs'),db.get_number_of_media_objects())
        self.reorder(RelLib.MediaObject, db.get_object_from_gramps_id, db.get_object_from_handle,
                     db.find_next_object_gramps_id, db.get_media_cursor, db.commit_media_object,
                     db.oprefix)
        self.progress.set_pass(_('Reordering Source IDs'),db.get_number_of_sources())
        self.reorder(RelLib.Source, db.get_source_from_gramps_id, db.get_source_from_handle,
                     db.find_next_source_gramps_id, db.get_source_cursor, db.commit_source,
                     db.sprefix)
        self.progress.set_pass(_('Reordering Place IDs'),db.get_number_of_places())
        self.reorder(RelLib.Place, db.get_place_from_gramps_id, db.get_place_from_handle,
                     db.find_next_place_gramps_id, db.get_place_cursor, db.commit_place,
                     db.pprefix)
        self.progress.close()
        db.transaction_commit(self.trans,_("Reorder gramps IDs"))
        
    def reorder(self, class_type, find_from_id, find_from_handle, find_next_id, get_cursor, commit, prefix):
        dups = []
        newids = {}
        key_list = []

        # search all ids in the map

        cursor = get_cursor()
        data = cursor.first()
        while data:
            self.progress.step()
            (handle,sdata) = data

            obj = class_type()
            obj.unserialize(sdata)
            gramps_id = obj.get_gramps_id()
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
                    elif find_from_id(newgramps_id) != None:
                        dups.append(obj.get_handle())
                    else:
                        data.set_gramps_id(newgramps_id)
                        commit(obj,self.trans)
                        newids[newgramps_id] = gramps_id
                except:
                    dups.append(handle)
            else:
                dups.append(handle)

            data = cursor.next()
        cursor.close()
            
        # go through the duplicates, looking for the first availble
        # handle that matches the new scheme.
    
        self.progress.set_pass(_('Finding and assigning unused IDs'),len(dups))
        for handle in dups:
            self.progress.step()
            obj = find_from_handle(handle)
            obj.set_gramps_id(find_next_id())
            commit(obj,self.trans)
    
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

