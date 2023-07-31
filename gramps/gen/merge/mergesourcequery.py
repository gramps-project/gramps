#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
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
Provide merge capabilities for sources.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib import Citation, Note
from ..db import DbTxn
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from ..errors import MergeError


# -------------------------------------------------------------------------
#
# MergeSourceQuery
#
# -------------------------------------------------------------------------
class MergeSourceQuery:
    """
    Create database query to merge two sources.
    """

    def __init__(self, dbstate, phoenix, titanic):
        self.database = dbstate.db
        self.phoenix = phoenix
        self.titanic = titanic

    def execute(self):
        """
        Merges to sources into a single source.
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        self.phoenix.merge(self.titanic)

        with DbTxn(_("Merge Source"), self.database) as trans:
            self.database.commit_source(self.phoenix, trans)
            for class_name, handle in self.database.find_backlink_handles(old_handle):
                if class_name == Citation.__name__:
                    citation = self.database.get_citation_from_handle(handle)
                    assert citation.get_reference_handle() == old_handle
                    citation.set_reference_handle(new_handle)
                    self.database.commit_citation(citation, trans)
                elif class_name == Note.__name__:
                    note = self.database.get_note_from_handle(handle)
                    assert note.has_handle_reference("Source", old_handle)
                    note.replace_handle_reference("Source", old_handle, new_handle)
                    self.database.commit_note(note, trans)
                else:
                    raise MergeError(
                        "Encounter an object of type %s that has "
                        "a source reference." % class_name
                    )
            self.database.remove_source(old_handle, trans)
