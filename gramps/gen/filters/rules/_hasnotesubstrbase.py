#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from . import Rule


# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib import Person
from ...types import Database


# -------------------------------------------------------------------------
# "People having notes that contain a substring"
# -------------------------------------------------------------------------
class HasNoteSubstrBase(Rule):
    """People having notes containing <substring>."""

    labels = [_("Substring:")]
    name = "Objects having notes containing <substring>"
    description = "Matches objects whose notes contain text matching a " "substring"
    category = _("General filters")

    def apply_to_one(self, db, person: Person) -> bool:
        notelist = person.note_list
        for notehandle in notelist:
            note = db.get_note_from_handle(notehandle)
            n = str(note.text)
            if n.upper().find(self.list[0].upper()) != -1:
                return True
        return False
