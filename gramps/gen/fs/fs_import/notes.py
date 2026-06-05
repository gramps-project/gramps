#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# -------------------------------------------------------------------------
#
# Future imports
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Note, NoteType, StyledText, StyledTextTag, StyledTextTagType
from . import _


def add_note(db, txn, fs_note, existing_note_handles):
    for nh in existing_note_handles:
        n = db.get_note_from_handle(nh)
        title = _(n.type.xml_str())
        if title == fs_note.subject:
            for tag in n.text.get_tags():
                if tag.name == StyledTextTagType.LINK:
                    fs_id = tag.value
                    if title == fs_note.subject and fs_id == "_fsftid=" + fs_note.id:
                        return n

    gr_note = Note()
    gr_note.set_format(Note.FORMATTED)
    gr_note.set_type(NoteType(fs_note.subject))
    if fs_note.id:
        # store FSFTID in a LINK tag on the first char
        tags = [
            StyledTextTag(
                StyledTextTagType.LINK,
                "_fsftid=" + fs_note.id,
                [(0, 1)],
            )
        ]
        gr_note.set_styledtext(StyledText("\ufeff" + (fs_note.text or ""), tags))

    db.add_note(gr_note, txn)
    db.commit_note(gr_note, txn)
    return gr_note
