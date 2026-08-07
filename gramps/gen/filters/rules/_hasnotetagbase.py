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
Rule that checks for objects whose notes have a particular tag.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from typing import Set

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
from . import Rule

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ...lib.primaryobj import PrimaryObject
from ...db import Database
from ...types import PrimaryObjectHandle

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
    namespace = ""

    def prepare(self, db: Database, user) -> None:
        """
        Build the set of matching object handles via a two-hop backlink walk:
        tag → notes → objects of this namespace.
        """
        self.selected_handles: Set[PrimaryObjectHandle] = set()
        tag = db.get_tag_from_name(self.list[0])
        if tag is not None:
            for _cls, note_handle in db.find_backlink_handles(
                tag.handle, include_classes=["Note"]
            ):
                for _cls2, obj_handle in db.find_backlink_handles(
                    note_handle, include_classes=[self.namespace]
                ):
                    self.selected_handles.add(obj_handle)

    def apply_to_one(self, db: Database, obj: PrimaryObject) -> bool:
        """
        Return True if this object's handle is in the pre-built match set.
        """
        return obj.handle in self.selected_handles
