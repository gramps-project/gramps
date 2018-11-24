#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons, Nick Hall
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
CitationBaseModel classes for Gramps.
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from html import escape
import logging
log = logging.getLogger(".")
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.datehandler import format_time, get_date, get_date_valid
from gramps.gen.lib import Citation
from gramps.gen.utils.string import conf_strings
from gramps.gen.config import config

#-------------------------------------------------------------------------
#
# COLUMN constants
#
#-------------------------------------------------------------------------
# These are the column numbers in the serialize/unserialize interfaces in
# the Citation object
COLUMN_HANDLE      = 0
COLUMN_ID          = 1
COLUMN_DATE        = 2
COLUMN_PAGE        = 3
COLUMN_CONFIDENCE  = 4
COLUMN_SOURCE      = 5
COLUMN_CHANGE      = 9
COLUMN_TAGS        = 10
COLUMN_PRIV        = 11

# Data for the Source object
COLUMN2_HANDLE     = 0
COLUMN2_ID         = 1
COLUMN2_TITLE      = 2
COLUMN2_AUTHOR     = 3
COLUMN2_PUBINFO    = 4
COLUMN2_ABBREV     = 7
COLUMN2_CHANGE     = 8
COLUMN2_TAGS       = 11
COLUMN2_PRIV       = 12

INVALID_DATE_FORMAT = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# CitationModel
#
#-------------------------------------------------------------------------
class CitationBaseModel:

# Fields access when 'data' is a Citation

    def citation_date(self, data):
        if data[COLUMN_DATE]:
            citation = Citation()
            citation.unserialize(data)
            date_str =  get_date(citation)
            if date_str != "":
                retval = escape(date_str)
            if not get_date_valid(citation):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval
        return ''

    def citation_sort_date(self, data):
        if data[COLUMN_DATE]:
            citation = Citation()
            citation.unserialize(data)
            retval = "%09d" % citation.get_date_object().get_sort_value()
            if not get_date_valid(citation):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval
        return ''

    def citation_id(self, data):
        return data[COLUMN_ID]

    def citation_page(self, data):
        return data[COLUMN_PAGE]

    def citation_sort_confidence(self, data):
        if data[COLUMN_CONFIDENCE]:
            return str(data[COLUMN_CONFIDENCE])
        return ''

    def citation_confidence(self, data):
        return _(conf_strings[data[COLUMN_CONFIDENCE]])

    def citation_private(self, data):
        if data[COLUMN_PRIV]:
            return 'gramps-lock'
        else:
            # There is a problem returning None here.
            return ''

    def citation_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = list(map(self.get_tag_name, data[COLUMN_TAGS]))
        # TODO for Arabic, should the next line's comma be translated?
        return ', '.join(sorted(tag_list, key=glocale.sort_key))

    def citation_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_handle = data[0]
        cached, tag_color = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data[COLUMN_TAGS]:
                tag = self.db.get_tag_from_handle(handle)
                this_priority = tag.get_priority()
                if tag_priority is None or this_priority < tag_priority:
                    tag_color = tag.get_color()
                    tag_priority = this_priority
            self.set_cached_value(tag_handle, "TAG_COLOR", tag_color)
        return tag_color

    def citation_change(self, data):
        return format_time(data[COLUMN_CHANGE])

    def citation_sort_change(self, data):
        return "%012x" % data[COLUMN_CHANGE]

    def citation_source(self, data):
        return data[COLUMN_SOURCE]

    def citation_src_title(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_TITLE")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                value = source.get_title()
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_TITLE", value)
        return value

    def citation_src_id(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_ID")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                value = source.gramps_id
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_ID", value)
        return value

    def citation_src_auth(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_AUTH")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                value = source.get_author()
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_AUTH", value)
        return value

    def citation_src_abbr(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_ABBR")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                value = source.get_abbreviation()
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_ABBR", value)
        return value

    def citation_src_pinfo(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_PINFO")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                value = source.get_publication_info()
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_PINFO", value)
        return value

    def citation_src_private(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_PRIVATE")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                if source.get_privacy():
                    value = 'gramps-lock'
                else:
                    # There is a problem returning None here.
                    value = ''
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_PRIVATE", value)
        return value

    def citation_src_tags(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_TAGS")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                tag_list = list(map(self.get_tag_name, source.get_tag_list()))
                # TODO for Arabic, should the next line's comma be translated?
                value = ', '.join(sorted(tag_list, key=glocale.sort_key))
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_TAGS", value)
        return value

    def citation_src_chan(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_CHAN")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                value = format_time(source.change)
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_CHAN", value)
        return value

    def citation_src_sort_change(self, data):
        source_handle = data[COLUMN_SOURCE]
        cached, value = self.get_cached_value(source_handle, "SRC_CHAN")
        if not cached:
            try:
                source = self.db.get_source_from_handle(source_handle)
                value = "%012x" % source.change
            except:
                value = ''
            self.set_cached_value(source_handle, "SRC_CHAN", value)
        return value

# Fields access when 'data' is a Source

    def source_src_title(self, data):
        return data[COLUMN2_TITLE]

    def source_src_id(self, data):
        return data[COLUMN2_ID]

    def source_src_auth(self, data):
        return data[COLUMN2_AUTHOR]

    def source_src_abbr(self, data):
        return data[COLUMN2_ABBREV]

    def source_src_pinfo(self, data):
        return data[COLUMN2_PUBINFO]

    def source_src_private(self, data):
        if data[COLUMN2_PRIV]:
            return 'gramps-lock'
        else:
            # There is a problem returning None here.
            return ''

    def source_src_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = list(map(self.get_tag_name, data[COLUMN2_TAGS]))
        # TODO for Arabic, should the next line's comma be translated?
        return ', '.join(sorted(tag_list, key=glocale.sort_key))

    def source_src_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_handle = data[0]
        cached, tag_color = self.get_cached_value(tag_handle, "TAG_COLOR")
        if not cached:
            tag_color = ""
            tag_priority = None
            for handle in data[COLUMN2_TAGS]:
                tag = self.db.get_tag_from_handle(handle)
                this_priority = tag.get_priority()
                if tag_priority is None or this_priority < tag_priority:
                    tag_color = tag.get_color()
                    tag_priority = this_priority
            self.set_cached_value(tag_handle, "TAG_COLOR", tag_color)
        return tag_color

    def source_src_chan(self, data):
        return format_time(data[COLUMN2_CHANGE])

    def source_sort2_change(self, data):
        return "%012x" % data[COLUMN2_CHANGE]

    def dummy_sort_key(self, data):
        # dummy sort key for columns that don't have data
        return None

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
        cached, value = self.get_cached_value(tag_handle, "TAG_NAME")
        if not cached:
            value = self.db.get_tag_from_handle(tag_handle).get_name()
            self.set_cached_value(tag_handle, "TAG_NAME", value)
        return value
