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
import gen.datehandler
import gen.lib
from Utils import confidence
from gen.config import config

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

# Data for the Source object
COLUMN2_HANDLE     = 0
COLUMN2_ID         = 1
COLUMN2_TITLE      = 2
COLUMN2_AUTHOR     = 3
COLUMN2_PUBINFO    = 4
COLUMN2_ABBREV     = 7
COLUMN2_CHANGE     = 8

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
            citation = gen.lib.Citation()
            citation.unserialize(data)
            date_str =  gen.datehandler.get_date(citation)
            if date_str != "":
                retval = cgi.escape(date_str)
            if not gen.datehandler.get_date_valid(citation):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval
        return u''

    def citation_sort_date(self, data):
        if data[COLUMN_DATE]:
            citation = gen.lib.Citation()
            citation.unserialize(data)
            retval = "%09d" % citation.get_date_object().get_sort_value()
            if not gen.datehandler.get_date_valid(citation):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval
        return u''    
    
    def citation_id(self, data):
        return unicode(data[COLUMN_ID])

    def citation_page(self, data):
        return unicode(data[COLUMN_PAGE])

    def citation_confidence(self, data):
        return unicode(confidence[data[COLUMN_CONFIDENCE]])

    def citation_handle(self, data):
        return unicode(data[COLUMN_HANDLE])

    def citation_change(self, data):
        return gen.datehandler.format_time(data[COLUMN_CHANGE])
    
    def citation_sort_change(self, data):
        return "%012x" % data[COLUMN_CHANGE]

    def citation_source(self, data):
        return data[COLUMN_SOURCE]
    
    def citation_src_title(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_title())
        except:
            return u''

    def citation_src_id(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.gramps_id)
        except:
            return u''

    def citation_src_auth(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_author())
        except:
            return u''

    def citation_src_abbr(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_abbreviation())
        except:
            return u''

    def citation_src_pinfo(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_publication_info())
        except:
            return u''

    def citation_src_chan(self, data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return gen.datehandler.format_time(source.change)
        except:
            return u''

    def citation_tooltip(self, data):
        return u'Citation tooltip'

# Fields access when 'data' is a Source

    def source_handle(self, data):
        return unicode(data[COLUMN2_HANDLE])

    def source_src_title(self, data):
        return unicode(data[COLUMN2_TITLE])

    def source_src_id(self, data):
        return unicode(data[COLUMN2_ID])

    def source_src_auth(self, data):
        return unicode(data[COLUMN2_AUTHOR])

    def source_src_abbr(self, data):
        return unicode(data[COLUMN2_ABBREV])

    def source_src_pinfo(self, data):
        return unicode(data[COLUMN2_PUBINFO])

    def source_src_chan(self, data):
        return gen.datehandler.format_time(data[COLUMN2_CHANGE])

    def source_sort2_change(self, data):
        return "%012x" % data[COLUMN2_CHANGE]

    def source_tooltip(self, data):
        return u'Source tooltip'

    def dummy_sort_key(self, data):
        # dummy sort key for columns that don't have data
        return None
    
