#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2026  Gabriel Rios
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

from __future__ import annotations

from typing import Optional

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Person
from gramps.gui.dialog import QuestionDialog2

from gramps.gen.fs.utils.attributes import get_fsftid
from gramps.gen.fs.utils.index import FS_INDEX_PEOPLE, FS_INDEX_PLACES

_ = glocale.translation.gettext


def build_fs_index(caller, progress, total_steps: int) -> None:
    """Build fast lookup indexes for the FSFTID -> handle.

    Creates two dictionaries that map FamilySearch identifiers to Gramps handles:
      * FS_INDEX_PEOPLE[fsid] = person_handle
      * FS_INDEX_PLACES[url]  = place_handle (only for URLs tagged "FamilySearch")
    """
    db = caller.dbstate.db

    dup_warning = True
    FS_INDEX_PEOPLE.clear()

    progress.set_pass(
        _("Build FSID list (1/%(total)d)") % {"total": total_steps},
        db.get_number_of_people(),
    )
    for person_handle in db.get_person_handles():
        progress.step()
        person: Optional[Person] = db.get_person_from_handle(person_handle)
        fsid = get_fsftid(person) if person else ""
        if not fsid:
            continue
        if fsid in FS_INDEX_PEOPLE:
            print(_("FamilySearch duplicate ID: %s ") % (fsid,))
            if dup_warning:
                qd = QuestionDialog2(
                    _("Duplicate FSFTID"),
                    _("FamilySearch duplicate ID: %s ") % (fsid,),
                    _("_Continue warning"),
                    _("_Stop warning"),
                    parent=getattr(caller.uistate, "window", None),
                )
                if not qd.run():
                    dup_warning = False
        else:
            FS_INDEX_PEOPLE[fsid] = person_handle

    FS_INDEX_PLACES.clear()
    progress.set_pass(
        _("Build FSID list for places (2/%(total)d)") % {"total": total_steps},
        db.get_number_of_places(),
    )
    for place_handle in db.get_place_handles():
        progress.step()
        place = db.get_place_from_handle(place_handle)
        for url in getattr(place, "urls", []) or []:
            if str(getattr(url, "type", "")) == "FamilySearch":
                FS_INDEX_PLACES[getattr(url, "path", "")] = place_handle
