#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Michiel D. Nauta
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
Provide merge capabilities for media objects.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib import Person, Family, Event, Source, Citation, Place, Note
from ..db import DbTxn
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from ..errors import MergeError


# -------------------------------------------------------------------------
#
# MergeMediaQuery
#
# -------------------------------------------------------------------------
class MergeMediaQuery:
    """
    Create datqabase query to merge two media objects.
    """

    def __init__(self, dbstate, phoenix, titanic):
        self.database = dbstate.db
        self.phoenix = phoenix
        self.titanic = titanic

    def execute(self):
        """
        Merges two media objects into a single object.
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        self.phoenix.merge(self.titanic)

        with DbTxn(_("Merge Media Objects"), self.database) as trans:
            self.database.commit_media(self.phoenix, trans)
            for class_name, handle in self.database.find_backlink_handles(old_handle):
                if class_name == Person.__name__:
                    person = self.database.get_person_from_handle(handle)
                    assert person.has_media_reference(old_handle)
                    person.replace_media_references(old_handle, new_handle)
                    self.database.commit_person(person, trans)
                elif class_name == Family.__name__:
                    family = self.database.get_family_from_handle(handle)
                    assert family.has_media_reference(old_handle)
                    family.replace_media_references(old_handle, new_handle)
                    self.database.commit_family(family, trans)
                elif class_name == Event.__name__:
                    event = self.database.get_event_from_handle(handle)
                    assert event.has_media_reference(old_handle)
                    event.replace_media_references(old_handle, new_handle)
                    self.database.commit_event(event, trans)
                elif class_name == Source.__name__:
                    source = self.database.get_source_from_handle(handle)
                    assert source.has_media_reference(old_handle)
                    source.replace_media_references(old_handle, new_handle)
                    self.database.commit_source(source, trans)
                elif class_name == Citation.__name__:
                    citation = self.database.get_citation_from_handle(handle)
                    assert citation.has_media_reference(old_handle)
                    citation.replace_media_references(old_handle, new_handle)
                    self.database.commit_citation(citation, trans)
                elif class_name == Place.__name__:
                    place = self.database.get_place_from_handle(handle)
                    assert place.has_media_reference(old_handle)
                    place.replace_media_references(old_handle, new_handle)
                    self.database.commit_place(place, trans)
                elif class_name == Note.__name__:
                    note = self.database.get_note_from_handle(handle)
                    assert note.has_handle_reference("Media", old_handle)
                    note.replace_handle_reference("Media", old_handle, new_handle)
                    self.database.commit_note(note, trans)
                else:
                    raise MergeError(
                        "Encounter an object of type % s that has "
                        "a media object reference." % class_name
                    )
            self.database.remove_media(old_handle, trans)
