#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       Steve Youngs
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
Rule that checks for a note with a particular tag.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
from . import Rule
from ...lib.notebase import NoteBase
from ...db import Database

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# HasNoteTagBase
#
# -------------------------------------------------------------------------
class HasNoteTagBase(Rule):
    """
    Objects having a note with a particular tag.
    """

    labels = [_("Tag:")]
    name = _("Objects with notes with a specified tag.")
    description = _("Matches notes with a specified tag")
    category = _("General filters")

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.tag_handle = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        self.tag_handle = None
        tag = db.get_tag_from_name(self.list[0])
        if tag is not None:
            self.tag_handle = tag.handle

    def apply_to_one(self, db: Database, obj: NoteBase):
        """
        Apply the rule. Return True on a match.
        """
        note_list = obj.note_list
        for note_handle in note_list:
            note = db.get_note_from_handle(note_handle)
            if note is not None and self.tag_handle in note.tag_list:
                return True
        return False
