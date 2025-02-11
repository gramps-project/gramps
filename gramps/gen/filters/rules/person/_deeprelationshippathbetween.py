#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Robert Ham <rah@bash.sh>
# Copyright (C) 2011 Adam Stein <adam@csh.rit.edu>
# Copyright (C) 2017 Paul Culley <paulr2787@gmail.com>
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
from __future__ import annotations
from collections import deque

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .. import Rule
from . import MatchesFilter
from ....const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import Union, List, Set, Dict
from ....lib import Person
from ....db import Database
from ....types import FamilyHandle, PersonHandle

_ = glocale.translation.gettext
# -------------------------------------------------------------------------
#
# DeepRelationshipPathBetween
#
# -------------------------------------------------------------------------


def get_family_handle_people(
    db: Database, exclude_handle: str, family_handle: FamilyHandle
):
    people: Set[str] = set()

    family = db.get_family_from_handle(family_handle)

    def possibly_add_handle(h: str):
        if h is not None and h != exclude_handle:
            people.add(h)

    possibly_add_handle(family.father_handle)
    possibly_add_handle(family.mother_handle)

    for child_ref in family.child_ref_list:
        if child_ref:
            possibly_add_handle(child_ref.ref)

    return people


def get_person_family_people(
    db: Database, person: Person, person_handle: PersonHandle
) -> Set[str]:
    people: Set[str] = set()

    def add_family_handle_list(fam_list: List[FamilyHandle]):
        for family_handle in fam_list:
            people.update(get_family_handle_people(db, person_handle, family_handle))

    add_family_handle_list(person.family_list)
    add_family_handle_list(person.parent_family_list)

    return people


def find_deep_relations(
    db: Database, user, person: Person | None, target_people: List[str]
) -> Set[str]:
    """This explores all possible paths between a person and one or more
    targets.  The algorithm processes paths in a breadth first wave, one
    remove at a time.  The first path that reaches a target causes the target
    to be marked complete and the path to be stored in the return_paths set.
    By processing in wave, the return path should be a shortest path.
    The function stores to do data and intermediate results in an ordered dict,
    rather than using a recursive algorithm because some trees have been found
    that exceed the standard python recursive depth."""
    return_paths: Set[str] = set()  # all people in paths between targets and person
    if person is None:
        return return_paths
    todo = deque([person.handle])  # list of work to do, handles, add to right,
    #                                pop from left
    done: Dict[str, Union[str, None]] = {}  # The key records handles already examined,
    # the value is a handle of the previous person in the path, or None at
    # head of path.  This forms a linked list of handles along the path.
    done[person.handle] = None

    while todo:
        handle = todo.popleft()

        if user:
            user.step_progress()

        if handle in target_people:  # if we found a target
            prev_hndl = handle
            # Go through linked list and save the handles in return_paths
            while prev_hndl:
                return_paths.add(prev_hndl)
                prev_hndl = done[prev_hndl]
            target_people.remove(handle)
            if not target_people:  # Quit searching if all targets found
                break

        person = db.get_person_from_handle(handle)
        if person is None:
            continue

        people = get_person_family_people(db, person, handle)
        for p_hndl in people:
            if p_hndl in done:  # check if we have already been here
                continue  # and ignore if we have
            todo.append(p_hndl)  # Add to the todo list
            done[p_hndl] = handle  # Add to the (almost) done list

    return return_paths


class DeepRelationshipPathBetween(Rule):
    """Checks if there is any familial connection between a person and a
    filter match by searching over all connections."""

    labels = [_("ID:"), _("Filter name:")]
    name = _("Relationship path between <person> and people matching <filter>")
    category = _("Relationship filters")
    description = _(
        "Searches over the database starting from a specified"
        " person and returns everyone between that person and"
        " a set of target people specified with a filter.  "
        "This produces a set of relationship paths (including"
        " by marriage) between the specified person and the"
        " target people.  Each path is not necessarily"
        " the shortest path."
    )

    def prepare(self, db: Database, user):
        root_person_id = self.list[0]
        root_person = db.get_person_from_gramps_id(root_person_id)

        filter_name = self.list[1]
        self.filt = MatchesFilter([filter_name])
        self.filt.requestprepare(db, user)

        if user:
            user.begin_progress(
                _("Finding relationship paths"),
                _("Retrieving all sub-filter matches"),
                db.get_number_of_people(),
            )
        target_people = []
        for person in db.iter_people():
            if self.filt.apply_to_one(db, person):
                target_people.append(person.handle)
            if user:
                user.step_progress()
        if user:
            user.end_progress()
            user.begin_progress(
                _("Finding relationship paths"),
                _("Evaluating people"),
                db.get_number_of_people(),
            )
        self.selected_handles: Set[str] = find_deep_relations(
            db, user, root_person, target_people
        )
        if user:
            user.end_progress()

    def reset(self):
        self.filt.requestreset()
        self.selected_handles.clear()

    def apply_to_one(self, db: Database, person: Person) -> bool:
        return person.handle in self.selected_handles
