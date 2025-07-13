#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2012,2024  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2025       Steve Youngs <steve@youngs.cc>
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
Package providing filtering framework for Gramps.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import logging
import time

# ------------------------------------------------------------------------
#
# Gramps imports
#
# ------------------------------------------------------------------------
from ..lib.person import Person
from ..lib.family import Family
from ..lib.src import Source
from ..lib.citation import Citation
from ..lib.event import Event
from ..lib.place import Place
from ..lib.repo import Repository
from ..lib.media import Media
from ..lib.note import Note
from ..lib.tag import Tag
from ..const import GRAMPS_LOCALE as glocale
from .rules import Rule
from .optimizer import Optimizer

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from typing import cast, Dict, List, Literal, Set, Tuple
from ..db import Database
from ..types import PrimaryObjectHandle

_ = glocale.translation.gettext
LOG = logging.getLogger(".filter.results")


# -------------------------------------------------------------------------
#
# GenericFilter
#
# -------------------------------------------------------------------------
class GenericFilter:
    """Filter class that consists of zero, one or more rules."""

    logical_functions = ["and", "or", "one"]
    logical_op: Literal["and", "or", "one"]

    def __init__(self, source=None):
        if source:
            self.need_param = source.need_param
            self.flist = source.flist[:]
            self.name = source.name
            self.comment = source.comment
            self.logical_op = source.logical_op
            self.invert = source.invert
        else:
            self.need_param = 0
            self.flist = []
            self.name = ""
            self.comment = ""
            self.logical_op = "and"
            self.invert = False

    def match(self, handle, db):
        """
        Return True or False depending on whether the handle matches the filter.
        """
        obj = self.get_object(db, handle)
        return self.apply_to_one(db, obj)

    def is_empty(self):
        return (len(self.flist) == 0) or (
            len(self.flist) == 1 and ((self.flist[0].is_empty() and not self.invert))
        )

    def set_logical_op(self, val):
        if val in GenericFilter.logical_functions:
            self.logical_op = val
        else:
            raise Exception("invalid operator: %r" % val)

    def set_invert(self, val):
        self.invert = bool(val)

    def get_invert(self):
        return self.invert

    def get_name(self, ulocale=glocale):
        return self.name

    def set_name(self, name):
        self.name = name

    def set_comment(self, comment):
        self.comment = comment

    def get_comment(self):
        return self.comment

    def add_rule(self, rule):
        self.flist.append(rule)

    def delete_rule(self, rule):
        self.flist.remove(rule)

    def set_rules(self, rules):
        self.flist = rules

    def get_rules(self):
        return self.flist

    def get_all_handles(self, db):
        return db.get_person_handles()

    def get_cursor(self, db):
        return db.get_person_cursor()

    def get_tree_cursor(self, db):
        return db.get_person_cursor()

    def make_obj(self):
        return Person()

    def find_from_handle(self, db, handle):
        return db.get_person_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_people()

    def apply_logical_op_to_all(
        self,
        db,
        possible_handles: Set[PrimaryObjectHandle],
        apply_logical_op,
        user=None,
    ):
        LOG.debug(
            "Starting possible_handles: %s",
            len(possible_handles),
        )

        # use the Optimizer to refine the set of possible_handles
        optimizer = Optimizer()
        handles_in, handles_out = optimizer.compute_potential_handles_for_filter(self)

        # LOG.debug(
        #    "Optimizer possible_handles: %s",
        #    len(possible_handles),
        # )

        # if user:
        #    user.begin_progress(_("Filter"), _("Applying ..."), len(possible_handles))

        # test each value in possible_handles to compute the final_list
        final_list = []
        for handle in possible_handles:
            if handles_in is not None and handle not in handles_in:
                continue
            if handles_out is not None and handle in handles_out:
                continue

            if user:
                user.step_progress()

            obj = self.get_object(db, handle)

            if apply_logical_op(db, obj, self.flist) != self.invert:
                final_list.append(obj.handle)

        if user:
            user.end_progress()

        return final_list

    def and_test(self, db, data: dict, flist):
        return all(rule.apply_to_one(db, data) for rule in flist)

    def one_test(self, db, data: dict, flist):
        found_one = False
        for rule in flist:
            if rule.apply_to_one(db, data):
                if found_one:
                    return False  # There can be only one!
                found_one = True
        return found_one

    def or_test(self, db, data: dict, flist):
        return any(rule.apply_to_one(db, data) for rule in flist)

    def get_logical_op(self):
        return self.logical_op

    def apply_to_one(self, db, data: dict) -> bool:
        """
        Filter-level apply rules to single data item.
        """
        if self.logical_op == "and":
            res = self.and_test(db, data, self.flist)
        elif self.logical_op == "or":
            res = self.or_test(db, data, self.flist)
        elif self.logical_op == "one":
            res = self.one_test(db, data, self.flist)
        else:
            raise Exception("invalid operator: %r" % self.logical_op)
        return res != self.invert

    def apply(
        self,
        db,
        id_list: List[PrimaryObjectHandle | Tuple] | None = None,
        tupleind: int | None = None,
        user=None,
        tree: bool = False,
    ) -> List[PrimaryObjectHandle | Tuple]:
        """
        Apply the filter using db.

        If id_list and tupleind given, id_list is a list of tuples. tupleind is the
        index of the object handle. So handle_0 = id_list[0][tupleind]. The input
        order in maintained in the output. If multiple tuples have the same handle,
        it is undefined which tuple is returned.

        If id_list given and tupleind is None, id_list if the list of handles to use

        If id_list is None and tree is False, all handles in the database are searched.
        The order of handles in the result is not guaranteed

        If id_list is None and tree is True, all handles in the database are searched.
        The order of handles in the result matches the order of traversal
        by get_tree_cursor

        id_list takes precendence over tree

        user is optional. If present it must be an instance of a User class.

        :Returns: if id_list given, it is returned with the items that
                do not match the filter, filtered out.
                if id_list not given, all items in the database that
                match the filter are returned as a list of handles
        """
        start_time = time.time()
        for rule in self.flist:
            rule.requestprepare(db, user)
        LOG.debug("Prepare time: %s seconds", time.time() - start_time)

        if self.logical_op == "and":
            apply_logical_op = self.and_test
        elif self.logical_op == "or":
            apply_logical_op = self.or_test
        elif self.logical_op == "one":
            apply_logical_op = self.one_test
        else:
            raise Exception("invalid operator: %r" % self.logical_op)

        start_time = time.time()

        # build the starting set of possible_handles to be filtered
        possible_handles: Set[PrimaryObjectHandle]
        if id_list is not None:
            if tupleind is not None:
                # construct a dict from handle to corresponding tuple
                # this is used to efficiently transform final_list from a list of
                # handles to a list of tuples
                handle_tuple: Dict[PrimaryObjectHandle, Tuple] = {
                    data[tupleind]: data for data in cast(List[Tuple], id_list)
                }
                possible_handles = set(handle_tuple.keys())
            else:
                possible_handles = set(cast(List[PrimaryObjectHandle], id_list))
        elif tree:
            tree_handles = [handle for handle, obj in self.get_tree_cursor(db)]
            possible_handles = set(tree_handles)
        else:
            possible_handles = set(self.get_all_handles(db))

        res = self.apply_logical_op_to_all(db, possible_handles, apply_logical_op, user)

        # convert the filtered set of handles to the correct result type
        if id_list is not None and tupleind is not None:
            # convert the final_list of handles back to the corresponding final_list of tuples
            res = sorted(
                [handle_tuple[handle] for handle in res],
                key=lambda x: id_list.index(x),
            )
        elif tree:
            # sort final_list into the same order as traversed by get_tree_cursor
            res = sorted(res, key=lambda x: tree_handles.index(x))

        LOG.debug("Apply time: %s seconds", time.time() - start_time)

        for rule in self.flist:
            rule.requestreset()

        return res

    def get_object(self, db, handle):
        return db.get_person_from_handle(handle)


class GenericFamilyFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_family_handles()

    def get_cursor(self, db):
        return db.get_family_cursor()

    def make_obj(self):
        return Family()

    def find_from_handle(self, db, handle):
        return db.get_family_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_families()

    def get_object(self, db, handle):
        return db.get_family_from_handle(handle)


class GenericEventFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_event_handles()

    def get_cursor(self, db):
        return db.get_event_cursor()

    def make_obj(self):
        return Event()

    def find_from_handle(self, db, handle):
        return db.get_event_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_events()

    def get_object(self, db, handle):
        return db.get_event_from_handle(handle)


class GenericSourceFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_source_handles()

    def get_cursor(self, db):
        return db.get_source_cursor()

    def make_obj(self):
        return Source()

    def find_from_handle(self, db, handle):
        return db.get_source_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_sources()

    def get_object(self, db, handle):
        return db.get_source_from_handle(handle)


class GenericCitationFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_citation_handles()

    def get_cursor(self, db):
        return db.get_citation_cursor()

    def get_tree_cursor(self, db):
        return db.get_citation_cursor()

    def make_obj(self):
        return Citation()

    def find_from_handle(self, db, handle):
        return db.get_citation_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_citations()

    def get_object(self, db, handle):
        return db.get_citation_from_handle(handle)


class GenericPlaceFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_place_handles()

    def get_cursor(self, db):
        return db.get_place_cursor()

    def get_tree_cursor(self, db):
        return db.get_place_tree_cursor()

    def make_obj(self):
        return Place()

    def find_from_handle(self, db, handle):
        return db.get_place_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_places()

    def get_object(self, db, handle):
        return db.get_place_from_handle(handle)


class GenericMediaFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_media_handles()

    def get_cursor(self, db):
        return db.get_media_cursor()

    def make_obj(self):
        return Media()

    def find_from_handle(self, db, handle):
        return db.get_media_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_media()

    def get_object(self, db, handle):
        return db.get_media_from_handle(handle)


class GenericRepoFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_repository_handles()

    def get_cursor(self, db):
        return db.get_repository_cursor()

    def make_obj(self):
        return Repository()

    def find_from_handle(self, db, handle):
        return db.get_repository_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_repositories()

    def get_object(self, db, handle):
        return db.get_repository_from_handle(handle)


class GenericNoteFilter(GenericFilter):
    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_all_handles(self, db):
        return db.get_note_handles()

    def get_cursor(self, db):
        return db.get_note_cursor()

    def make_obj(self):
        return Note()

    def find_from_handle(self, db, handle):
        return db.get_note_from_handle(handle)

    def get_number(self, db):
        return db.get_number_of_notes()

    def get_object(self, db, handle):
        return db.get_note_from_handle(handle)


def GenericFilterFactory(namespace):
    if namespace == "Person":
        return GenericFilter
    elif namespace == "Family":
        return GenericFamilyFilter
    elif namespace == "Event":
        return GenericEventFilter
    elif namespace == "Source":
        return GenericSourceFilter
    elif namespace == "Citation":
        return GenericCitationFilter
    elif namespace == "Place":
        return GenericPlaceFilter
    elif namespace == "Media":
        return GenericMediaFilter
    elif namespace == "Repository":
        return GenericRepoFilter
    elif namespace == "Note":
        return GenericNoteFilter


class DeferredFilter(GenericFilter):
    """
    Filter class allowing for deferred translation of the filter name
    """

    def __init__(self, filter_name, person_name):
        GenericFilter.__init__(self, None)
        self.name_pair = [filter_name, person_name]

    def get_name(self, ulocale=glocale):
        """
        return the filter name, possibly translated

        If ulocale is passed in (a :class:`.GrampsLocale`) then
        the translated value will be returned instead.

        :param ulocale: allow deferred translation of strings
        :type ulocale: a :class:`.GrampsLocale` instance
        """
        self._ = ulocale.translation.gettext
        if self.name_pair[1]:
            return self._(self.name_pair[0]) % self.name_pair[1]
        return self._(self.name_pair[0])


class DeferredFamilyFilter(GenericFamilyFilter):
    """
    Filter class allowing for deferred translation of the filter name
    """

    def __init__(self, filter_name, family_name):
        GenericFamilyFilter.__init__(self, None)
        self.name_pair = [filter_name, family_name]

    def get_name(self, ulocale=glocale):
        """
        return the filter name, possibly translated

        If ulocale is passed in (a :class:`.GrampsLocale`) then
        the translated value will be returned instead.

        :param ulocale: allow deferred translation of strings
        :type ulocale: a :class:`.GrampsLocale` instance
        """
        self._ = ulocale.translation.gettext
        if self.name_pair[1]:
            return self._(self.name_pair[0]) % self.name_pair[1]
        return self._(self.name_pair[0])
