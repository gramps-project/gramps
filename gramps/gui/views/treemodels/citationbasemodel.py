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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

"""
CitationBaseModel classes for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import cgi
import logging
log = logging.getLogger(".")
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import format_time, get_date, get_date_valid
from gramps.gen.lib import Citation
from gramps.gen.utils.string import confidence
from gramps.gen.config import config
from gramps.gen.constfunc import cuni
from gramps.gen.const import GRAMPS_LOCALE as glocale

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
COLUMN_NAME        = 3
COLUMN_CONFIDENCE  = 4
COLUMN_SOURCE      = 5
COLUMN_CHANGE      = 9
COLUMN_TAGS        = 10
COLUMN_PRIV        = 11

# Data for the Source object
COLUMN2_HANDLE     = 0
COLUMN2_ID         = 1
COLUMN2_NAME       = 2
COLUMN2_TEMPLATE   = 3
COLUMN2_ABBREV     = 6
COLUMN2_CHANGE     = 7
COLUMN2_TAGS       = 10
COLUMN2_PRIV       = 11

INVALID_DATE_FORMAT = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# CitationModel
#
#-------------------------------------------------------------------------
class CitationBaseModel(object):

# Fields access when 'data' is a Citation

    def citation_date(self, data):
        if data[COLUMN_DATE]:
            citation = Citation()
            citation.unserialize(data)
            date_str =  get_date(citation)
            if date_str != "":
                retval = cgi.escape(date_str)
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
        return cuni(data[COLUMN_ID])

    def citation_name(self, data):
        return cuni(data[COLUMN_NAME])

    def citation_confidence(self, data):
        return cuni(confidence[data[COLUMN_CONFIDENCE]])

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
        return ', '.join(sorted(tag_list, key=glocale.sort_key))

    def citation_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_color = "#000000000000"
        tag_priority = None
        for handle in data[COLUMN_TAGS]:
            tag = self.db.get_tag_from_handle(handle)
            if tag:
                this_priority = tag.get_priority()
                if tag_priority is None or this_priority < tag_priority:
                    tag_color = tag.get_color()
                    tag_priority = this_priority
        return tag_color

    def citation_change(self, data):
        return format_time(data[COLUMN_CHANGE])
    
    def citation_sort_change(self, data):
        return "%012x" % data[COLUMN_CHANGE]

    def citation_source(self, data):
        return data[COLUMN_SOURCE]
    
    def citation_src_title(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return cuni(source.get_name())
        except:
            return ''

    def citation_src_template(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return cuni(source.get_template())
        except:
            return ''

    def citation_src_id(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return cuni(source.gramps_id)
        except:
            return ''

    def citation_src_auth(self, data):
        return ''
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return cuni(source.get_gedcom_author())
        except:
            return ''

    def citation_src_abbr(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return cuni(source.get_abbreviation())
        except:
            return ''

    def citation_src_pinfo(self, data):
        return ''
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return cuni(source.get_gedcom_publication_info())
        except:
            return ''

    def citation_src_private(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            if source.get_privacy():
                return 'gramps-lock'
            else:
                # There is a problem returning None here.
                return ''
        except:
            return ''

    def citation_src_tags(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            tag_list = list(map(self.get_tag_name, source.get_tag_list()))
            return ', '.join(sorted(tag_list, key=glocale.sort_key))
        except:
            return ''

    def citation_src_chan(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return format_time(source.change)
        except:
            return ''

# Fields access when 'data' is a Source

    def source_src_title(self, data):
        return cuni(data[COLUMN2_NAME])

    def source_src_template(self, data):
        return cuni(data[COLUMN2_TEMPLATE])

    def source_src_id(self, data):
        return cuni(data[COLUMN2_ID])

    def source_src_auth(self, data):
        source = self.db.get_source_from_handle(data[COLUMN2_HANDLE])
        return cuni(source.get_gedcom_author())

    def source_src_abbr(self, data):
        return cuni(data[COLUMN2_ABBREV])

    def source_src_pinfo(self, data):
        source = self.db.get_source_from_handle(data[COLUMN2_HANDLE])
        return cuni(source.get_gedcom_publication_info())

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
        return ', '.join(sorted(tag_list, key=glocale.sort_key))

    def source_src_tag_color(self, data):
        """
        Return the tag color.
        """
        tag_color = "#000000000000"
        tag_priority = None
        for handle in data[COLUMN2_TAGS]:
            tag = self.db.get_tag_from_handle(handle)
            if tag:
                this_priority = tag.get_priority()
                if tag_priority is None or this_priority < tag_priority:
                    tag_color = tag.get_color()
                    tag_priority = this_priority
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
        return self.db.get_tag_from_handle(tag_handle).get_name()
