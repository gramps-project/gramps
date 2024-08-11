#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2009-2010  Nick Hall
# Copyright (C) 2009       Benny Malengier
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
TreeModel for the Gramps Person tree.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
from html import escape

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# set up logging
#
# -------------------------------------------------------------------------
import logging

_LOG = logging.getLogger(".")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.lib import (
    Name,
    EventRef,
    EventType,
    EventRoleType,
    FamilyRelType,
    ChildRefType,
    NoteType,
)
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.datehandler import format_time, get_date, get_date_valid
from .flatbasemodel import FlatBaseModel
from .treebasemodel import TreeBaseModel
from .basemodel import BaseModel
from gramps.gen.config import config

# -------------------------------------------------------------------------
#
# COLUMN constants; positions in raw data structure
#
# -------------------------------------------------------------------------
COLUMN_ID = 1
COLUMN_GENDER = 2
COLUMN_NAME = 3
COLUMN_DEATH = 5
COLUMN_BIRTH = 6
COLUMN_EVENT = 7
COLUMN_FAMILY = 8
COLUMN_PARENT = 9
COLUMN_NOTES = 16
COLUMN_CHANGE = 17
COLUMN_TAGS = 18
COLUMN_PRIV = 19

invalid_date_format = config.get("preferences.invalid-date-format")
no_surname = config.get("preferences.no-surname-text")


# -------------------------------------------------------------------------
#
# PeopleBaseModel
#
# -------------------------------------------------------------------------
class PeopleBaseModel(BaseModel):
    """
    Basic Model interface to handle the PersonViews
    """

    _GENDER = [_("female"), _("male"), _("unknown"), _("other")]

    def __init__(self, db):
        """
        Initialize the model building the initial data
        """
        BaseModel.__init__(self)
        self.db = db
        self.gen_cursor = db.get_person_cursor
        self.map = db.get_raw_person_data

        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_gender,
            self.column_birth_day,
            self.column_birth_place,
            self.column_death_day,
            self.column_death_place,
            self.column_spouse,
            self.column_parents,
            self.column_marriages,
            self.column_children,
            self.column_todo,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
        ]
        self.smap = [
            self.sort_name,
            self.column_id,
            self.column_gender,
            self.sort_birth_day,
            self.column_birth_place,
            self.sort_death_day,
            self.column_death_place,
            self.column_spouse,
            self.sort_parents,
            self.sort_marriages,
            self.sort_children,
            self.sort_todo,
            self.column_private,
            self.column_tags,
            self.sort_change,
            self.column_tag_color,
        ]

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        BaseModel.destroy(self)
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None

    def color_column(self):
        """
        Return the color column.
        """
        return 15

    def on_get_n_columns(self):
        """Return the number of columns in the model"""
        return len(self.fmap) + 1

    def sort_name(self, data):
        handle = data[0]
        cached, name = self.get_cached_value(handle, "SORT_NAME")
        if not cached:
            name = name_displayer.raw_sorted_name(data[COLUMN_NAME])
            self.set_cached_value(handle, "SORT_NAME", name)
        return name

    def column_name(self, data):
        handle = data[0]
        cached, name = self.get_cached_value(handle, "NAME")
        if not cached:
            name = name_displayer.raw_display_name(data[COLUMN_NAME])
            self.set_cached_value(handle, "NAME", name)
        return name

    def column_spouse(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SPOUSE")
        if not cached:
            value = self._get_spouse_data(data)
            self.set_cached_value(handle, "SPOUSE", value)
        return value

    def column_private(self, data):
        if data[COLUMN_PRIV]:
            return "gramps-lock"
        else:
            # There is a problem returning None here.
            return ""

    def _get_spouse_data(self, data):
        spouses_names = ""
        for family_handle in data[COLUMN_FAMILY]:
            family = self.db.get_family_from_handle(family_handle)
            for spouse_id in [family.get_father_handle(), family.get_mother_handle()]:
                if not spouse_id:
                    continue
                if spouse_id == data[0]:
                    continue
                spouse = self.db.get_person_from_handle(spouse_id)
                if spouses_names:
                    spouses_names += ", "
                spouses_names += name_displayer.display(spouse)
        return spouses_names

    def column_id(self, data):
        return data[COLUMN_ID]

    def sort_change(self, data):
        return "%012x" % data[COLUMN_CHANGE]

    def column_change(self, data):
        return format_time(data[COLUMN_CHANGE])

    def column_gender(self, data):
        return PeopleBaseModel._GENDER[data[COLUMN_GENDER]]

    def column_birth_day(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "BIRTH_DAY")
        if not cached:
            value = self._get_birth_data(data, False)
            self.set_cached_value(handle, "BIRTH_DAY", value)
        return value

    def sort_birth_day(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_BIRTH_DAY")
        if not cached:
            value = self._get_birth_data(data, True)
            self.set_cached_value(handle, "SORT_BIRTH_DAY", value)
        return value

    def _get_birth_data(self, data, sort_mode):
        index = data[COLUMN_BIRTH]
        if index != -1:
            try:
                local = data[COLUMN_EVENT][index]
                b = EventRef()
                b.unserialize(local)
                birth = self.db.get_event_from_handle(b.ref)
                if sort_mode:
                    retval = "%09d" % birth.get_date_object().get_sort_value()
                else:
                    date_str = get_date(birth)
                    if date_str != "":
                        retval = escape(date_str)
                if not get_date_valid(birth):
                    return invalid_date_format % retval
                else:
                    return retval
            except:
                return ""

        for event_ref in data[COLUMN_EVENT]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            date_str = get_date(event)
            if (
                etype.is_birth_fallback()
                and er.get_role() == EventRoleType.PRIMARY
                and date_str != ""
            ):
                if sort_mode:
                    retval = "%09d" % event.get_date_object().get_sort_value()
                else:
                    retval = "<i>%s</i>" % escape(date_str)
                if not get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval

        return ""

    def column_death_day(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "DEATH_DAY")
        if not cached:
            value = self._get_death_data(data, False)
            self.set_cached_value(handle, "DEATH_DAY", value)
        return value

    def sort_death_day(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_DEATH_DAY")
        if not cached:
            value = self._get_death_data(data, True)
            self.set_cached_value(handle, "SORT_DEATH_DAY", value)
        return value

    def _get_death_data(self, data, sort_mode):
        index = data[COLUMN_DEATH]
        if index != -1:
            try:
                local = data[COLUMN_EVENT][index]
                ref = EventRef()
                ref.unserialize(local)
                event = self.db.get_event_from_handle(ref.ref)
                if sort_mode:
                    retval = "%09d" % event.get_date_object().get_sort_value()
                else:
                    date_str = get_date(event)
                    if date_str != "":
                        retval = escape(date_str)
                if not get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
            except:
                return ""

        for event_ref in data[COLUMN_EVENT]:
            er = EventRef()
            er.unserialize(event_ref)
            event = self.db.get_event_from_handle(er.ref)
            etype = event.get_type()
            date_str = get_date(event)
            if (
                etype.is_death_fallback()
                and er.get_role() == EventRoleType.PRIMARY
                and date_str
            ):
                if sort_mode:
                    retval = "%09d" % event.get_date_object().get_sort_value()
                else:
                    retval = "<i>%s</i>" % escape(date_str)
                if not get_date_valid(event):
                    return invalid_date_format % retval
                else:
                    return retval
        return ""

    def column_birth_place(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "BIRTH_PLACE")
        if cached:
            return value
        else:
            index = data[COLUMN_BIRTH]
            if index != -1:
                try:
                    local = data[COLUMN_EVENT][index]
                    br = EventRef()
                    br.unserialize(local)
                    event = self.db.get_event_from_handle(br.ref)
                    if event:
                        place_title = place_displayer.display_event(self.db, event)
                        if place_title:
                            value = escape(place_title)
                            self.set_cached_value(handle, "BIRTH_PLACE", value)
                            return value
                except:
                    value = ""
                    self.set_cached_value(handle, "BIRTH_PLACE", value)
                    return value

            for event_ref in data[COLUMN_EVENT]:
                er = EventRef()
                er.unserialize(event_ref)
                event = self.db.get_event_from_handle(er.ref)
                etype = event.get_type()
                if etype.is_birth_fallback() and er.get_role() == EventRoleType.PRIMARY:
                    place_title = place_displayer.display_event(self.db, event)
                    if place_title:
                        value = "<i>%s</i>" % escape(place_title)
                        self.set_cached_value(handle, "BIRTH_PLACE", value)
                        return value
            value = ""
            self.set_cached_value(handle, "BIRTH_PLACE", value)
            return value

    def column_death_place(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "DEATH_PLACE")
        if cached:
            return value
        else:
            index = data[COLUMN_DEATH]
            if index != -1:
                try:
                    local = data[COLUMN_EVENT][index]
                    dr = EventRef()
                    dr.unserialize(local)
                    event = self.db.get_event_from_handle(dr.ref)
                    if event:
                        place_title = place_displayer.display_event(self.db, event)
                        if place_title:
                            value = escape(place_title)
                            self.set_cached_value(handle, "DEATH_PLACE", value)
                            return value
                except:
                    value = ""
                    self.set_cached_value(handle, "DEATH_PLACE", value)
                    return value

            for event_ref in data[COLUMN_EVENT]:
                er = EventRef()
                er.unserialize(event_ref)
                event = self.db.get_event_from_handle(er.ref)
                etype = event.get_type()
                if etype.is_death_fallback() and er.get_role() == EventRoleType.PRIMARY:
                    place_title = place_displayer.display_event(self.db, event)
                    if place_title:
                        value = "<i>%s</i>" % escape(place_title)
                        self.set_cached_value(handle, "DEATH_PLACE", value)
                        return value
            value = ""
            self.set_cached_value(handle, "DEATH_PLACE", value)
            return value

    def _get_parents_data(self, data):
        parents = 0
        if data[COLUMN_PARENT]:
            person = self.db.get_person_from_gramps_id(data[COLUMN_ID])
            family_list = person.get_parent_family_handle_list()
            for fam_hdle in family_list:
                family = self.db.get_family_from_handle(fam_hdle)
                if family.get_father_handle():
                    parents += 1
                if family.get_mother_handle():
                    parents += 1
        return parents

    def _get_marriages_data(self, data):
        marriages = 0
        for family_handle in data[COLUMN_FAMILY]:
            family = self.db.get_family_from_handle(family_handle)
            if int(family.get_relationship()) == FamilyRelType.MARRIED:
                marriages += 1
        return marriages

    def _get_children_data(self, data):
        children = 0
        for family_handle in data[COLUMN_FAMILY]:
            family = self.db.get_family_from_handle(family_handle)
            for child_ref in family.get_child_ref_list():
                if (
                    child_ref.get_father_relation() == ChildRefType.BIRTH
                    and child_ref.get_mother_relation() == ChildRefType.BIRTH
                ):
                    children += 1
        return children

    def _get_todo_data(self, data):
        todo = 0
        for note_handle in data[COLUMN_NOTES]:
            note = self.db.get_note_from_handle(note_handle)
            if int(note.get_type()) == NoteType.TODO:
                todo += 1
        return todo

    def column_parents(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "PARENTS")
        if not cached:
            value = self._get_parents_data(data)
            self.set_cached_value(handle, "PARENTS", value)
        return str(value)

    def sort_parents(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_PARENTS")
        if not cached:
            value = self._get_parents_data(data)
            self.set_cached_value(handle, "SORT_PARENTS", value)
        return "%06d" % value

    def column_marriages(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "MARRIAGES")
        if not cached:
            value = self._get_marriages_data(data)
            self.set_cached_value(handle, "MARRIAGES", value)
        return str(value)

    def sort_marriages(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_MARRIAGES")
        if not cached:
            value = self._get_marriages_data(data)
            self.set_cached_value(handle, "SORT_MARRIAGES", value)
        return "%06d" % value

    def column_children(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "CHILDREN")
        if not cached:
            value = self._get_children_data(data)
            self.set_cached_value(handle, "CHILDREN", value)
        return str(value)

    def sort_children(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_CHILDREN")
        if not cached:
            value = self._get_children_data(data)
            self.set_cached_value(handle, "SORT_CHILDREN", value)
        return "%06d" % value

    def column_todo(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "TODO")
        if not cached:
            value = self._get_todo_data(data)
            self.set_cached_value(handle, "TODO", value)
        return str(value)

    def sort_todo(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_TODO")
        if not cached:
            value = self._get_todo_data(data)
            self.set_cached_value(handle, "SORT_TODO", value)
        return "%06d" % value

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
        cached, value = self.get_cached_value(tag_handle, "TAG_NAME")
        if not cached:
            tag = self.db.get_tag_from_handle(tag_handle)
            if tag:
                value = tag.get_name()
                self.set_cached_value(tag_handle, "TAG_NAME", value)
        return value

    def column_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_handle = data[0]
        cached, value = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data[COLUMN_TAGS]:
                tag = self.db.get_tag_from_handle(handle)
                if tag:
                    this_priority = tag.get_priority()
                    if tag_priority is None or this_priority < tag_priority:
                        tag_color = tag.get_color()
                        tag_priority = this_priority
            value = tag_color
            self.set_cached_value(tag_handle, "TAG_COLOR", value)
        return value

    def column_tags(self, data):
        """
        Return the sorted list of tags.
        """
        handle = data[0]
        cached, value = self.get_cached_value(handle, "TAGS")
        if not cached:
            tag_list = list(map(self.get_tag_name, data[COLUMN_TAGS]))
            # TODO for Arabic, should the next line's comma be translated?
            value = ", ".join(sorted(tag_list, key=glocale.sort_key))
            self.set_cached_value(handle, "TAGS", value)
        return value


class PersonListModel(PeopleBaseModel, FlatBaseModel):
    """
    Listed people model.
    """

    def __init__(
        self,
        db,
        uistate,
        scol=0,
        order=Gtk.SortType.ASCENDING,
        search=None,
        skip=set(),
        sort_map=None,
    ):
        PeopleBaseModel.__init__(self, db)
        FlatBaseModel.__init__(
            self,
            db,
            uistate,
            search=search,
            skip=skip,
            scol=scol,
            order=order,
            sort_map=sort_map,
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        PeopleBaseModel.destroy(self)
        FlatBaseModel.destroy(self)


class PersonTreeModel(PeopleBaseModel, TreeBaseModel):
    """
    Hierarchical people model.
    """

    def __init__(
        self,
        db,
        uistate,
        scol=0,
        order=Gtk.SortType.ASCENDING,
        search=None,
        skip=set(),
        sort_map=None,
    ):
        PeopleBaseModel.__init__(self, db)
        TreeBaseModel.__init__(
            self,
            db,
            uistate,
            search=search,
            skip=skip,
            scol=scol,
            order=order,
            sort_map=sort_map,
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        PeopleBaseModel.destroy(self)
        self.number_items = None
        TreeBaseModel.destroy(self)

    def _set_base_data(self):
        """See TreeBaseModel, we also set some extra lru caches"""
        self.number_items = self.db.get_number_of_people

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return [_("Group As"), _("Name")]

    def column_header(self, node):
        return node.name if node.name else no_surname

    def add_row(self, handle, data):
        """
        Add nodes to the node map for a single person.

        handle      The handle of the gramps object.
        data        The object data.
        """
        ngn = name_displayer.name_grouping_data

        name_data = data[COLUMN_NAME]
        group_name = ngn(self.db, name_data)
        sort_key = self.sort_func(data)

        # if group_name not in self.group_list:
        # self.group_list.append(group_name)
        # self.add_node(None, group_name, group_name, None)

        # add as node: parent, child, sortkey, handle; parent and child are
        # nodes in the treebasemodel, and will be used as iters
        self.add_node(group_name, handle, sort_key, handle)
