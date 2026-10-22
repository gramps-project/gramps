#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons, Nick Hall
# Copyright (C) 2024       Doug Blank
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
CitationTreeModel classes for Gramps.
"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------
import logging

log = logging.getLogger(".")
LOG = logging.getLogger(".citation")

# -------------------------------------------------------------------------
#
# internationalization
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# GNOME/GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.utils.db import get_source_referents
from .treebasemodel import TreeBaseModel
from .citationbasemodel import CitationBaseModel


# -------------------------------------------------------------------------
#
# CitationModel
#
# -------------------------------------------------------------------------
class CitationTreeModel(CitationBaseModel, TreeBaseModel):
    """
    Hierarchical citation model.
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
        self.db = db
        self.number_items = self.db.get_number_of_sources
        self.map = self.db.get_raw_source_data
        self.gen_cursor = self.db.get_source_cursor
        # The items here must correspond, in order, with data in
        # CitationTreeView, and with the items in the secondary fmap, fmap2
        self.fmap = [
            self.source_src_title,  # COL_TITLE_PAGE (both Source & Citation)
            self.source_src_id,  # COL_ID         (both Source & Citation)
            None,  # COL_DATE       (not for Source)
            None,  # COL_CONFIDENCE (not for Source)
            self.source_src_private,  # COL_PRIV       (both Source & Citation)
            self.source_src_tags,  # COL_TAGS       (both Source & Citation)
            self.source_src_chan,  # COL_CHAN       (both Source & Citation)
            self.source_src_auth,  # COL_SRC_AUTH   (Source only)
            self.source_src_abbr,  # COL_SRC_ABBR   (Source only)
            self.source_src_pinfo,  # COL_SRC_PINFO  (Source only)
            self.source_src_tag_color,
        ]
        self.smap = [
            self.source_src_title,
            self.source_src_id,
            self.dummy_sort_key,
            self.dummy_sort_key,
            self.source_src_private,
            self.source_src_tags,
            self.source_sort2_change,
            self.source_src_auth,
            self.source_src_abbr,
            self.source_src_pinfo,
            self.source_src_tag_color,
        ]

        TreeBaseModel.__init__(
            self,
            self.db,
            uistate,
            scol=scol,
            order=order,
            search=search,
            skip=skip,
            sort_map=sort_map,
            nrgroups=1,
            group_can_have_handle=True,
            has_secondary=True,
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None
        self.number_items = None
        self.gen_cursor2 = None
        self.map2 = None
        self.fmap2 = None
        self.smap2 = None
        self.number_items2 = None
        TreeBaseModel.destroy(self)

    def _set_base_data(self):
        """See TreeBaseModel, for citations, most have been set in init of
        CitationBaseModel
        """
        self.number_items2 = self.db.get_number_of_citations
        self.map2 = self.db.get_raw_citation_data
        self.gen_cursor2 = self.db.get_citation_cursor
        self.fmap2 = [
            self.citation_page,
            self.citation_id,
            self.citation_date,
            self.citation_confidence,
            self.citation_private,
            self.citation_tags,
            self.citation_change,
            None,
            None,
            None,
            self.citation_tag_color,
        ]
        self.smap2 = [
            self.citation_page,
            self.citation_id,
            self.citation_sort_date,
            self.citation_sort_confidence,
            self.citation_private,
            self.citation_tags,
            self.citation_sort_change,
            self.dummy_sort_key,
            self.dummy_sort_key,
            self.dummy_sort_key,
            self.citation_tag_color,
        ]

    def color_column(self):
        """
        Return the color column.
        """
        return 10

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return [_("Source"), _("Citation")]

    def add_row(self, handle, data):
        """
        Add source nodes to the node map.

        handle      The handle of the gramps object.
        data        The object data.
        """
        sort_key = self.sort_func(data)
        self.add_node(None, handle, sort_key, handle)

    def add_row2(self, handle, data):
        """
        Add citation nodes to the node map.

        handle      The handle of the gramps object.
        data        The object data.
        """
        sort_key = self.sort_func2(data)
        # If the source for this citation already exists (in the tree model) we
        # add the citation as a child of the source. Otherwise we add the source
        # first (because citations don't have any meaning without the associated
        # source)
        if self._get_node(data.source_handle):
            #             parent   child   sortkey   handle
            self.add_node(data.source_handle, handle, sort_key, handle, secondary=True)
        else:
            # add the source node first
            source_sort_key = self.sort_func(self.map(data.source_handle))
            #            parent child    sortkey          handle
            self.add_node(None, data.source_handle, source_sort_key, data.source_handle)

            #            parent    child   sortkey   handle
            self.add_node(data.source_handle, handle, sort_key, handle, secondary=True)

    def on_get_n_columns(self):
        return len(self.fmap) + 1

    def column_header(self, node):
        """
        Return a column heading.  This is called for nodes with no associated
        Gramps handle.
        """
        return node.name


# -------------------------------------------------------------------------
#
# _SourceGroupSearchFilter
#
# -------------------------------------------------------------------------
class _SourceGroupSearchFilter:
    """
    Filter that groups a hierarchical source->citation text search *by source*
    (issue 8622).

    It matches against sets precomputed by :func:`grouped_shown_sources`.  A
    primary (source) row is shown when its handle is in the *shown* set.  A
    secondary (citation) row is shown when its parent source matched by title
    (so every citation of a title-matched source stays reachable underneath it)
    or when the citation itself matched (so a page search lists only the
    matching citations, not their siblings).  The sets are built once and
    shared by the primary and secondary instances, so matching here is a pure
    set-membership test that never dereferences a source handle.
    """

    def __init__(self, groups, secondary, get_source_handle):
        self._shown, self._title_matched, self._matched_citations = groups
        self._secondary = secondary
        self._get_source_handle = get_source_handle

    def match(self, handle, db):
        """
        Return whether the row for ``handle`` is shown.  For a citation row the
        parent source handle is looked up (never the source data itself), so an
        orphan citation whose source was excluded simply fails the membership
        test instead of raising.
        """
        if self._secondary:
            return (
                handle in self._matched_citations
                or self._get_source_handle(handle) in self._title_matched
            )
        return handle in self._shown


def grouped_shown_sources(
    source_filter, citation_filter, source_cursor, citation_cursor, db, skip
):
    """
    Compute the sets a source-grouped search needs (issue 8622), returned as
    ``(shown, title_matched, matched_citations)``:

    * ``title_matched`` -- sources whose own (title) column matches the primary
      search.  All of their citations are shown.
    * ``matched_citations`` -- citations whose (page) column matches the
      secondary search.  Only these are shown under a source that did not
      match by title.
    * ``shown`` -- the sources to show: ``title_matched`` plus every source
      owning a matched citation.

    Both filters run only against handles yielded by their own cursor (always
    live), and a citation is recorded as matched *only* when it belongs to a
    source that still exists.  A citation pointing at a deleted source (an
    orphan) therefore never gets itself or its dangling ``source_handle`` into
    the sets, so the later add-row pass never dereferences a missing source --
    the orphan is simply hidden (its source no longer exists to show it under).

    ``skip`` is the selector's set of handles to hide (public ``BaseSelector``
    parameter).  A skipped source is never shown, and a skipped citation never
    pulls its source into the shown set -- so grouping cannot resurrect a row
    the caller asked to hide via ``add_row2``'s force-add-parent fallback.
    """
    shown = set()
    title_matched = set()
    matched_citations = set()
    existing_sources = set()
    with source_cursor() as cursor:
        for handle, _data in cursor:
            existing_sources.add(handle)
            if handle not in skip and source_filter.match(handle, db):
                title_matched.add(handle)
    shown.update(title_matched)
    with citation_cursor() as cursor:
        for handle, data in cursor:
            # A skipped citation must not pull its source into the shown set,
            # else the source-grouped widening resurrects a row the plain model
            # (which honours skip) would hide (issue 8622 skip guard).
            if handle in skip:
                continue
            if citation_filter.match(handle, db):
                source_handle = data.source_handle
                # Orphan/skip guard: never record a citation unless its source
                # still exists AND is not itself skipped (else add_row2 would
                # force-add a missing or hidden source).
                if source_handle in existing_sources and source_handle not in skip:
                    matched_citations.add(handle)
                    shown.add(source_handle)
    return shown, title_matched, matched_citations


# -------------------------------------------------------------------------
#
# CitationTreeSelectorModel
#
# -------------------------------------------------------------------------
class CitationTreeSelectorModel(CitationTreeModel):
    """
    Citation tree model for the "Select Source or Citation" selector.

    Identical to :class:`CitationTreeModel` except that a *positive* plain text
    search is grouped by source (issue 8622): a source whose title matches keeps
    *all* of its existing citations reachable, so the user can reuse one instead
    of being forced to create a new citation.  A source shown only because some
    of its citations matched lists just those citations, not their siblings.

    An **inverted** ("does not contain") search is deliberately left to the base
    model's independent secondary search: there the citation-level exclusion is
    the user's intent, so a citation whose page matches the excluded term must
    stay hidden -- grouping by source must not override that.  The reachability
    artefact this fix removes only arises for a positive search (a citation's
    page rarely contains a source title), which is the reported defect.

    The standalone Citation Tree View keeps plain :class:`CitationTreeModel`, so
    its behaviour is unchanged.
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
        # Capture skip BEFORE super().__init__ runs, because it calls
        # set_search() (which needs skip to group correctly) before it passes
        # skip on to rebuild_data.  The base model does not otherwise retain it.
        self._skip = skip
        super().__init__(
            db,
            uistate,
            scol=scol,
            order=order,
            search=search,
            skip=skip,
            sort_map=sort_map,
        )

    def set_search(self, search):
        """
        See :meth:`TreeBaseModel.set_search`.  After the base builds the
        independent primary (source) and secondary (citation) search filters,
        widen a *positive* plain text search so it is grouped by source
        (issue 8622).
        """
        super().set_search(search)
        # Only widen a plain (non-sidebar) text search:
        #  * ``search`` falsy / ``search[0]`` truthy -> sidebar GenericFilter
        #    (out of scope);
        #  * ``search[1]`` falsy                      -> no search tuple.
        if not (search and not search[0] and search[1]):
            return
        _col, text, inverted = search[1]
        # An empty search box still yields a truthy ``(col, "", inv)`` tuple
        # (gramps/gui/filters/_searchbar.py) that the base treats as a live
        # search matching everything; there is nothing to group, so skip the
        # widening (and its extra cursor scan) entirely.
        if not text:
            return
        # An inverted search keeps the base independent secondary filter, so a
        # citation matching the excluded term stays hidden (see class docstring).
        if inverted:
            return
        # The base filters are None only for an empty search text (handled
        # above); guard anyway so we never group without both legs, and never
        # touch a closed/absent database.
        if (
            self.search is None
            or self.search2 is None
            or self.db is None
            or not self.db.is_open()
        ):
            return
        groups = grouped_shown_sources(
            self.search,
            self.search2,
            self.gen_cursor,
            self.gen_cursor2,
            self.db,
            getattr(self, "_skip", set()),
        )
        self.search = _SourceGroupSearchFilter(
            groups, False, self._citation_source_handle
        )
        self.search2 = _SourceGroupSearchFilter(
            groups, True, self._citation_source_handle
        )
        self.current_filter = self.search
        self.current_filter2 = self.search2

    def _citation_source_handle(self, citation_handle):
        """Return the source handle a (live) citation belongs to."""
        return self.map2(citation_handle).source_handle
