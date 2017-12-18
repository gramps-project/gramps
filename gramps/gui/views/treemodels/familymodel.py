#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import displayer, format_time, get_date_valid
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.lib import EventRoleType, FamilyRelType
from .flatbasemodel import FlatBaseModel
from gramps.gen.utils.db import get_marriage_or_fallback
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale

invalid_date_format = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# FamilyModel
#
#-------------------------------------------------------------------------
class FamilyModel(FlatBaseModel):

    def __init__(self, db, uistate, scol=0, order=Gtk.SortType.ASCENDING,
                 search=None, skip=set(), sort_map=None):
        self.gen_cursor = db.get_family_cursor
        self.map = db.get_raw_family_data
        self.fmap = [
            self.column_id,
            self.column_father,
            self.column_mother,
            self.column_type,
            self.column_marriage,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color,
            ]
        self.smap = [
            self.column_id,
            self.sort_father,
            self.sort_mother,
            self.column_type,
            self.sort_marriage,
            self.column_private,
            self.column_tags,
            self.sort_change,
            self.column_tag_color,
            ]
        FlatBaseModel.__init__(self, db, uistate, scol, order, search=search,
                               skip=skip, sort_map=sort_map)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def color_column(self):
        """
        Return the color column.
        """
        return 8

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_father(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "FATHER")
        if not cached:
            if data[2]:
                person = self.db.get_person_from_handle(data[2])
                value = name_displayer.display_name(person.primary_name)
            else:
                value = ""
            self.set_cached_value(handle, "FATHER", value)
        return value

    def sort_father(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_FATHER")
        if not cached:
            if data[2]:
                person = self.db.get_person_from_handle(data[2])
                value = name_displayer.sorted_name(person.primary_name)
            else:
                value = ""
            self.set_cached_value(handle, "SORT_FATHER", value)
        return value

    def column_mother(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "MOTHER")
        if not cached:
            if data[3]:
                person = self.db.get_person_from_handle(data[3])
                value = name_displayer.display_name(person.primary_name)
            else:
                value = ""
            self.set_cached_value(handle, "MOTHER", value)
        return value

    def sort_mother(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_MOTHER")
        if not cached:
            if data[3]:
                person = self.db.get_person_from_handle(data[3])
                value = name_displayer.sorted_name(person.primary_name)
            else:
                value = ""
            self.set_cached_value(handle, "SORT_MOTHER", value)
        return value

    def column_type(self, data):
        return str(FamilyRelType(data[5]))

    def column_marriage(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "MARRIAGE")
        if not cached:
            family = self.db.get_family_from_handle(data[0])
            event = get_marriage_or_fallback(self.db, family, "<i>%s</i>")
            if event:
                if event.date.format:
                    value = event.date.format % displayer.display(event.date)
                elif not get_date_valid(event):
                    value = invalid_date_format % displayer.display(event.date)
                else:
                    value = "%s" % displayer.display(event.date)
            else:
                value = ''
            self.set_cached_value(handle, "MARRIAGE", value)
        return value

    def sort_marriage(self, data):
        handle = data[0]
        cached, value = self.get_cached_value(handle, "SORT_MARRIAGE")
        if not cached:
            family = self.db.get_family_from_handle(data[0])
            event = get_marriage_or_fallback(self.db, family)
            if event:
                value = "%09d" % event.date.get_sort_value()
            else:
                value = ''
            self.set_cached_value(handle, "SORT_MARRIAGE", value)
        return value

    def column_id(self, data):
        return data[1]

    def column_private(self, data):
        if data[14]:
            return 'gramps-lock'
        else:
            # There is a problem returning None here.
            return ''

    def sort_change(self, data):
        return "%012x" % data[12]

    def column_change(self, data):
        return format_time(data[12])

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
        cached, value = self.get_cached_value(tag_handle, "TAG_NAME")
        if not cached:
            value = self.db.get_tag_from_handle(tag_handle).get_name()
            self.set_cached_value(tag_handle, "TAG_NAME", value)
        return value

    def column_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_handle = data[0]
        cached, tag_color = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data[13]:
                tag = self.db.get_tag_from_handle(handle)
                this_priority = tag.get_priority()
                if tag_priority is None or this_priority < tag_priority:
                    tag_color = tag.get_color()
                    tag_priority = this_priority
            self.set_cached_value(tag_handle, "TAG_COLOR", tag_color)
        return tag_color

    def column_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = list(map(self.get_tag_name, data[13]))
        # TODO for Arabic, should the next line's comma be translated?
        return ', '.join(sorted(tag_list, key=glocale.sort_key))
