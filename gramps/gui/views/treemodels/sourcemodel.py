#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2013       Tim G L Lyons
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
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.datehandler import format_time
from gramps.gen.constfunc import cuni
from .flatbasemodel import FlatBaseModel
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.citeref import (get_gedcom_title, get_gedcom_author,
                                      get_gedcom_pubinfo)


COLUMN_HANDLE     = 0
COLUMN_ID         = 1
COLUMN_NAME       = 2
COLUMN_TEMPLATE   = 3
COLUMN_ABBREV     = 6
COLUMN_CHANGE     = 7
COLUMN_TAGS       = 10
COLUMN_PRIV       = 11

#-------------------------------------------------------------------------
#
# SourceModel
#
#-------------------------------------------------------------------------
class SourceModel(FlatBaseModel):

    def __init__(self, db, scol=0, order=Gtk.SortType.ASCENDING, search=None,
                 skip=set(), sort_map=None):
        self.map = db.get_raw_source_data
        self.gen_cursor = db.get_source_cursor
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.column_template,
            self.column_private,
            self.column_tags,
            self.column_change,
            self.column_tag_color
            ]
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.column_template,
            self.column_private,
            self.column_tags,
            self.sort_change,
            self.column_tag_color
            ]
        FlatBaseModel.__init__(self, db, scol, order, search=search, skip=skip,
                               sort_map=sort_map)

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
        return 9

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_name(self, data):
        return cuni(data[COLUMN_NAME])

    def column_author(self, data):
        source = self.db.get_source_from_handle(data[COLUMN_HANDLE])
        return cuni(get_gedcom_author(self.db, source))

    def column_template(self, data):
        return cuni(data[COLUMN_TEMPLATE])

    def column_abbrev(self, data):
        return cuni(data[COLUMN_ABBREV])

    def column_id(self, data):
        return cuni(data[COLUMN_ID])

    def column_pubinfo(self, data):
        source = self.db.get_source_from_handle(data[COLUMN_HANDLE])
        return cuni(get_gedcom_pubinfo(self.db, source))

    def column_private(self, data):
        if data[COLUMN_PRIV]:
            return 'gramps-lock'
        else:
            # There is a problem returning None here.
            return ''

    def column_change(self,data):
        return format_time(data[COLUMN_CHANGE])
    
    def sort_change(self,data):
        return "%012x" % data[COLUMN_CHANGE]

    def get_tag_name(self, tag_handle):
        """
        Return the tag name from the given tag handle.
        """
        return self.db.get_tag_from_handle(tag_handle).get_name()
        
    def column_tag_color(self, data):
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

    def column_tags(self, data):
        """
        Return the sorted list of tags.
        """
        tag_list = list(map(self.get_tag_name, data[COLUMN_TAGS]))
        return ', '.join(sorted(tag_list, key=glocale.sort_key))
