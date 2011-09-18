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
CitationTreeModel classes for GRAMPS.
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
# internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

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
from Utils import get_source_referents
from gui.views.treemodels.treebasemodel import TreeBaseModel
from gui.views.treemodels.citationbasemodel import CitationBaseModel

#-------------------------------------------------------------------------
#
# CitationModel
#
#-------------------------------------------------------------------------
class CitationTreeModel(CitationBaseModel, TreeBaseModel):
    """
    Hierarchical citation model.
    """
    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):
        self.db = db
        self.map = self.db.get_raw_source_data
        self.gen_cursor = self.db.get_source_cursor
        # The items here must correspond, in order, with data in 
        # CitationTreeView, and with the items in the secondary fmap, fmap2
        self.fmap = [
            self.source_src_title,   # COL_TITLE_PAGE (both Source & Citation)
            self.source_src_id,      # COL_ID         (both Source & Citation)
            None,                    # COL_DATE       (not for Source)
            None,                    # COL_CONFIDENCE (not for Source)
            self.source_src_chan,    # COL_CHAN       (both Source & Citation)
            self.source_src_auth,    # COL_SRC_AUTH   (Source only)
            self.source_src_abbr,    # COL_SRC_ABBR   (Source only)
            self.source_src_pinfo,   # COL_SRC_PINFO  (Source only)
            self.source_handle,
            self.source_tooltip
            ]
        self.smap = [
            self.source_src_title,
            self.source_src_id,
            self.dummy_sort_key,
            self.dummy_sort_key,
            self.source_sort2_change,
            self.source_src_auth,
            self.source_src_abbr,
            self.source_src_pinfo,
            self.source_handle,
            self.source_tooltip
            ]
        
        TreeBaseModel.__init__(self, self.db, scol=scol, order=order,
                               tooltip_column=9,
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
        self.number_items = None
        TreeBaseModel.destroy(self)

    def _set_base_data(self):
        """See TreeBaseModel, for citations, most have been set in init of
        CitationBaseModel
        """
        self.number_items = self.db.get_number_of_citations
        self.map2 = self.db.get_raw_citation_data
        self.fmap2 = [
            self.citation_page,
            self.citation_id,
            self.citation_date,
            self.citation_confidence,
            self.citation_change,
            None,
            None,
            None,
            self.citation_handle,
            self.citation_tooltip
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
        # first add the source
#        source_name = self.source_src_title(data)
        sort_key = self.sort_func(data)
        # add as node: parent, child, sortkey, handle; parent and child are 
        # nodes in the treebasemodel, and will be used as iters
        if self.get_node(handle) is None:
            self.add_node(None, handle, sort_key, handle)
        # now add all the related citations
        source_handle_list = []
        for i in get_source_referents(handle, self.db):
            for j in i:
                source_handle_list.append(j)
        for citation_handle in source_handle_list:
#            # add as node: parent, child, sortkey, handle; parent and child are 
#            # nodes in the treebasemodel, and will be used as iters
            citation = self.db.get_citation_from_handle(citation_handle)
            citation_page = citation.get_page()
            self.add_node(handle, citation_handle, citation_page, 
                          citation_handle, secondary=True)
#        try:
#            source_handle = data[COLUMN_SOURCE]
#        except:
#            LOG.debug("add_row: data %s is empty, handle %s citation %s data %s" %
#                      (data, handle, self.db.get_citation_from_handle(handle),
#                       self.db.get_citation_from_handle(handle).serialize()))
#        source = self.db.get_source_from_handle(source_handle)
#        if source is not None:
#            source_name = source.get_title()
#            sort_key = self.sort_func(data)
#            if self.get_node(source_handle) is None:
#                self.add_node(None, source_handle, source_name, source_handle,
#                              secondary=True)
#            self.add_node(source_handle, handle, sort_key, handle)
#        else:
#            log.warn("Citation %s does not have a source" % 
#                     unicode(data[COLUMN_PAGE]),
#                      exc_info=True)

    def add_secondary_row(self, handle, data):
        """
        Add a secondary node to the node map for a citation.
        """
        # parameters are parent, child, sortkey, handle
        self.add_node(self.citation_source(data), handle, 
                      self.citation_page(data), handle, secondary=True)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_header(self, node):
        """
        Return a column heading.  This is called for nodes with no associated      
        Gramps handle.
        """
        return node.name
