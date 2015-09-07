#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

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
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gui.utils import ProgressMeter
from gramps.gen.lib import (Event, Family, MediaObject, Note,
        Person, Place, Repository, Source, Citation)
from gramps.gen.db import DbTxn
from gramps.gui.plug import tool

_findint = re.compile('^[^\d]*(\d+)[^\d]*')

# gets the number specified in a format string, example: %04d returns '04'
_parseformat = re.compile('.*%(\d+)[^\d]+')

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------
class ReorderIds(tool.BatchTool):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        tool.BatchTool.__init__(self, dbstate, user, options_class, name)
        if self.fail:
            return

        db = dbstate.db
        self.uistate = uistate
        if uistate:
            self.progress = ProgressMeter(_('Reordering Gramps IDs'),'')
        else:
            print(_("Reordering Gramps IDs..."))

        with DbTxn(_("Reorder Gramps IDs"), db, batch=True) as self.trans:
            db.disable_signals()

            if uistate:
                self.progress.set_pass(_('Reordering People IDs'),
                                       db.get_number_of_people())
            self.reorder(Person,
                         db.get_person_from_gramps_id,
                         db.get_person_from_handle,
                         db.find_next_person_gramps_id,
                         db.person_map,
                         db.commit_person,
                         db.person_prefix)

            if uistate:
                self.progress.set_pass(_('Reordering Family IDs'),
                                       db.get_number_of_families())
            self.reorder(Family,
                         db.get_family_from_gramps_id,
                         db.get_family_from_handle,
                         db.find_next_family_gramps_id,
                         db.family_map,
                         db.commit_family,
                         db.family_prefix)
            if uistate:
                self.progress.set_pass(_('Reordering Event IDs'),
                                       db.get_number_of_events())
            self.reorder(Event,
                         db.get_event_from_gramps_id,
                         db.get_event_from_handle,
                         db.find_next_event_gramps_id,
                         db.event_map,
                         db.commit_event,
                         db.event_prefix)
            if uistate:
                self.progress.set_pass(_('Reordering Media Object IDs'),
                                       db.get_number_of_media_objects())
            self.reorder(MediaObject,
                         db.get_object_from_gramps_id,
                         db.get_object_from_handle,
                         db.find_next_object_gramps_id,
                         db.media_map,
                         db.commit_media_object,
                         db.mediaobject_prefix)
            if uistate:
                self.progress.set_pass(_('Reordering Source IDs'),
                                       db.get_number_of_sources())
            self.reorder(Source,
                         db.get_source_from_gramps_id,
                         db.get_source_from_handle,
                         db.find_next_source_gramps_id,
                         db.source_map,
                         db.commit_source,
                         db.source_prefix)
            if uistate:
                self.progress.set_pass(_('Reordering Citation IDs'),
                                       db.get_number_of_citations())
            self.reorder(Citation,
                         db.get_citation_from_gramps_id,
                         db.get_citation_from_handle,
                         db.find_next_citation_gramps_id,
                         db.citation_map,
                         db.commit_citation,
                         db.citation_prefix)
            if uistate:
                self.progress.set_pass(_('Reordering Place IDs'),
                                       db.get_number_of_places())
            self.reorder(Place,
                         db.get_place_from_gramps_id,
                         db.get_place_from_handle,
                         db.find_next_place_gramps_id,
                         db.place_map,
                         db.commit_place,
                         db.place_prefix)
            if uistate:
                self.progress.set_pass(_('Reordering Repository IDs'),
                                       db.get_number_of_repositories())
            self.reorder(Repository,
                         db.get_repository_from_gramps_id,
                         db.get_repository_from_handle,
                         db.find_next_repository_gramps_id,
                         db.repository_map,
                         db.commit_repository,
                         db.repository_prefix)
    #add reorder notes ID
            if uistate:
                self.progress.set_pass(_('Reordering Note IDs'),
                                       db.get_number_of_notes())
            self.reorder(Note,
                         db.get_note_from_gramps_id,
                         db.get_note_from_handle,
                         db.find_next_note_gramps_id,
                         db.note_map,
                         db.commit_note,
                         db.note_prefix)
            if uistate:
                self.progress.close()
            else:
                print(_("Done."))

        db.enable_signals()
        db.request_rebuild()

    def reorder(self, class_type, find_from_id, find_from_handle,
                find_next_id, table, commit, prefix):
        dups = []
        newids = {}

        formatmatch = _parseformat.match(prefix)

        for handle in list(table.keys()):
            if self.uistate:
                self.progress.step()

            sdata = table[handle]

            obj = class_type()
            obj.unserialize(sdata)
            gramps_id = obj.get_gramps_id()
            # attempt to extract integer, if we can't, treat it as a
            # duplicate

            try:
                match = _findint.match(gramps_id)
                if match:
                    # get the integer, build the new handle. Make sure it
                    # hasn't already been chosen. If it has, put this
                    # in the duplicate handle list

                    index = match.groups()[0]

                    if formatmatch:
                        if int(index) > int("9" * int(formatmatch.groups()[0])):
                            newgramps_id = find_next_id()
                        else:
                            newgramps_id = prefix % int(index)
                    else:
                        # the prefix does not contain a number after %, eg I%d
                        newgramps_id = prefix % int(index)

                    if newgramps_id == gramps_id:
                        if newgramps_id in newids:
                            dups.append(obj.get_handle())
                        else:
                            newids[newgramps_id] = gramps_id
                    elif find_from_id(newgramps_id) is not None:
                        dups.append(obj.get_handle())
                    else:
                        obj.set_gramps_id(newgramps_id)
                        commit(obj, self.trans)
                        newids[newgramps_id] = gramps_id
                else:
                    dups.append(handle)
            except:
                dups.append(handle)

        # go through the duplicates, looking for the first available
        # handle that matches the new scheme.

        if self.uistate:
            self.progress.set_pass(_('Finding and assigning unused IDs'),
                                   len(dups))
        for handle in dups:
            if self.uistate:
                self.progress.step()
            obj = find_from_handle(handle)
            obj.set_gramps_id(find_next_id())
            commit(obj, self.trans)

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class ReorderIdsOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
