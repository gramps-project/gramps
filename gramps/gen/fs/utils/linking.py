# -*- coding: utf-8 -*-
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

from typing import Any, Optional, Union

from gramps.gen.db import DbTxn
from gramps.gen.lib import Attribute, SrcAttribute, Person, Event, Citation
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


from .index import FS_INDEX_PEOPLE


def link_gramps_fs_id(db: Any, gr_object: Any, fsid: str) -> None:
    """
    Attach or update the _FSFTID attribute on a Gramps object and commit.
    Updates global FS_INDEX_PEOPLE if the object is a Person.
    """
    if not fsid or gr_object is None:
        return

    internal_txn = False
    if getattr(db, "transaction", None):
        txn = db.transaction
    else:
        internal_txn = True
        txn = DbTxn(_("FamilySearch tags"), db)

    existing_attr: Optional[Union[Attribute, SrcAttribute]] = None
    for a in gr_object.get_attribute_list():
        if a.get_type() == "_FSFTID":
            existing_attr = a
            if a.get_value() != fsid:
                a.set_value(fsid)
            break

    if existing_attr is None:
        attr: Union[Attribute, SrcAttribute]
        if isinstance(gr_object, Citation):
            attr = SrcAttribute()
        else:
            attr = Attribute()
        attr.set_type("_FSFTID")
        attr.set_value(fsid)
        gr_object.add_attribute(attr)

    if isinstance(gr_object, Person):
        db.commit_person(gr_object, txn)
        FS_INDEX_PEOPLE[fsid] = gr_object.get_handle()
    elif isinstance(gr_object, Event):
        db.commit_event(gr_object, txn)
    elif isinstance(gr_object, Citation):
        db.commit_citation(gr_object, txn)
    else:
        print(
            "fs_utilities.link_gramps_fs_id: unsupported class:",
            gr_object.__class__.__name__,
        )

    if internal_txn:
        db.transaction_commit(txn)


def link_gramps_fs_id_by_handle(
    db: Any, handle: Optional[str], fallback_object: Any, fsid: str
) -> Any:
    """
    Attach/update the _FSFTID attribute on the database's own copy of a
    person and commit it, so a FamilySearch link is saved immediately,
    independent of any other unsaved edits sitting in a live person
    editor for the same person.

    Falls back to committing `fallback_object` directly when `handle`
    does not resolve in the database, e.g. a brand-new, not-yet-saved
    person for which there is no separate database copy to commit.

    :returns: the object that was actually committed.
    """
    target = None
    if isinstance(handle, str) and handle:
        try:
            target = db.get_person_from_handle(handle)
        except Exception:
            target = None

    if target is None:
        target = fallback_object

    link_gramps_fs_id(db, target, fsid)
    return target
