#
# Gramps - a GTK+/GNOME based genealogy program
#
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
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ToolTips
import DateHandler
import gen.lib
from Utils import confidence, format_time
import config
from gui.views.treemodels.flatbasemodel import FlatBaseModel
from gui.views.treemodels.treebasemodel import TreeBaseModel

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

COLUMN2_HANDLE     = 0
COLUMN2_ID         = 1
COLUMN2_TITLE      = 2

INVALID_DATE_FORMAT = config.get('preferences.invalid-date-format')

#-------------------------------------------------------------------------
#
# CitationModel
#
#-------------------------------------------------------------------------
class CitationBaseModel(object):

    def __init__(self,db):
        self.map = db.get_raw_citation_data
        self.gen_cursor = db.get_citation_cursor
        self.fmap = [
            self.column_page,
            self.column_id,
            self.column_date,
            self.column_confidence,
            self.column_change,
            self.column_src_title,
            self.column_src_id,
            self.column_src_auth,
            self.column_src_abbr,
            self.column_src_pinfo,
            self.column_src_chan,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_page,
            self.column_id,
            self.column_date,
            self.column_confidence,
            self.sort_change,
            self.column_src_title,
            self.column_src_id,
            self.column_src_auth,
            self.column_src_abbr,
            self.column_src_pinfo,
            self.column_src_chan,
            self.column_handle,
            self.column_tooltip
            ]

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

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_date(self,data):
        if data[COLUMN_DATE]:
            citation = gen.lib.Citation()
            citation.unserialize(data)
            date_str =  DateHandler.get_date(citation)
            if date_str != "":
                retval = cgi.escape(date_str)
            if not DateHandler.get_date_valid(citation):
                return INVALID_DATE_FORMAT % retval
            else:
                return retval
        return u''

    def column_id(self,data):
        return unicode(data[COLUMN_ID])

    def column_page(self,data):
        return unicode(data[COLUMN_PAGE])

    def column_confidence(self,data):
        return unicode(confidence[data[COLUMN_CONFIDENCE]])

    def column_handle(self,data):
        return unicode(data[COLUMN_HANDLE])

    def column_change(self,data):
        return format_time(data[COLUMN_CHANGE])
    
    def sort_change(self,data):
        return "%012x" % data[COLUMN_CHANGE]

    def column_src_title(self,data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_title())
        except:
            return u''

    def column_src_id(self,data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.gramps_id)
        except:
            return u''

    def column_src_auth(self,data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_author())
        except:
            return u''

    def column_src_abbr(self,data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_abbreviation())
        except:
            return u''

    def column_src_pinfo(self,data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return unicode(source.get_publication_info())
        except:
            return u''

    def column_src_chan(self,data):
        source_handle = data[COLUMN_SOURCE]
        try:
            source = self.db.get_source_from_handle(source_handle)
            return format_time(source.change)
        except:
            return u''

    def column_tooltip(self,data):
        if const.USE_TIPS:
            try:
                t = ToolTips.TipFromFunction(self.db, lambda:
                                             self.db.get_citation_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.",exc_info=True)
            return t
        else:
            return u''

#-------------------------------------------------------------------------
#
# CitationListModel
#
#-------------------------------------------------------------------------
class CitationListModel(CitationBaseModel, FlatBaseModel):
    """
    Flat citation model.  (Original code in CitationBaseModel).
    """
    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):

        CitationBaseModel.__init__(self, db)
        FlatBaseModel.__init__(self, db, scol, order, tooltip_column=12,
                               search=search, skip=skip, sort_map=sort_map)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        CitationBaseModel.destroy(self)
        FlatBaseModel.destroy(self)

#-------------------------------------------------------------------------
#
# CitationTreeModel
#
#-------------------------------------------------------------------------
class CitationTreeModel(CitationBaseModel, TreeBaseModel):
    """
    Hierarchical citation model.
    """
    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):

        CitationBaseModel.__init__(self, db)
        TreeBaseModel.__init__(self, db, scol=scol, order=order,
                               tooltip_column=12,
                               search=search, skip=skip, sort_map=sort_map,
                               nrgroups = 1,
                               group_can_have_handle = True)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.map2 = None
        self.fmap2 = None
        self.smap = None
# Can't call FlatBaseModel.destroy(self), because it fails when a treemodel 
# is passed, so can't just do:
#        CitationBaseModel.destroy(self)
        self.number_items = None
        TreeBaseModel.destroy(self)

    def _set_base_data(self):
        """See TreeBaseModel, for place, most have been set in init of
        CitationBaseModel
        """
        self.number_items = self.db.get_number_of_citations
        self.map2 = self.db.get_raw_source_data
        self.fmap2 = [
            self.column2_src_title,
            self.column2_src_id,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            self.column2_handle,
            None
            ]

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return [_('Source'), _('Citation')]

    def add_row(self, handle, data):
        """
        Add nodes to the node map for a single citation.

        handle      The handle of the gramps object.
        data        The object data.
        """
        source_handle = data[COLUMN_SOURCE]
        source = self.db.get_source_from_handle(source_handle)
        if source is not None:
            source_name = source.get_title()
            sort_key = self.sort_func(data)
            # add as node: parent, child, sortkey, handle; parent and child are 
            # nodes in the treebasemodel, and will be used as iters
            if self.get_node(source_handle) is None:
                self.add_node(None, source_handle, source_name, source_handle,
                              secondary=True)
            self.add_node(source_handle, handle, sort_key, handle)
        else:
            log.warn("Citation %s does not have a source" % 
                     unicode(data[COLUMN_PAGE]),
                      exc_info=True)

    def column2_handle(self, data):
        return unicode(data[COLUMN2_HANDLE])

    def column2_src_title(self, data):
        return unicode(data[COLUMN2_TITLE])

    def column2_src_id(self, data):
        return unicode(data[COLUMN2_ID])

    def column_header(self, node):
        """
        Return a column heading.  This is called for nodes with no associated      
        Gramps handle.
        """
        return node.name
