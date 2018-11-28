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
CitationListModel class for Gramps.
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")
LOG = logging.getLogger(".citation")

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
from .flatbasemodel import FlatBaseModel
from .citationbasemodel import CitationBaseModel

#-------------------------------------------------------------------------
#
# CitationListModel
#
#-------------------------------------------------------------------------
class CitationListModel(CitationBaseModel, FlatBaseModel):
    """
    Flat citation model.  (Original code in CitationBaseModel).
    """
    def __init__(self, db, uistate, scol=0, order=Gtk.SortType.ASCENDING,
                 search=None, skip=set(), sort_map=None):
        self.map = db.get_raw_citation_data
        self.gen_cursor = db.get_citation_cursor
        self.fmap = [
            self.citation_page,
            self.citation_id,
            self.citation_date,
            self.citation_confidence,
            self.citation_private,
            self.citation_tags,
            self.citation_change,
            self.citation_src_title,
            self.citation_src_id,
            self.citation_src_auth,
            self.citation_src_abbr,
            self.citation_src_pinfo,
            self.citation_src_private,
            self.citation_src_chan,
            self.citation_tag_color
            ]
        self.smap = [
            self.citation_page,
            self.citation_id,
            self.citation_sort_date,
            self.citation_sort_confidence,
            self.citation_private,
            self.citation_tags,
            self.citation_sort_change,
            self.citation_src_title,
            self.citation_src_id,
            self.citation_src_auth,
            self.citation_src_abbr,
            self.citation_src_pinfo,
            self.citation_src_private,
            self.citation_src_sort_chan,
            self.citation_tag_color
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
        return 14

    def on_get_n_columns(self):
        return len(self.fmap)+1
