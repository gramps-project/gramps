#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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
Regression test for issue 8622.

In the "Select Source or Citation" selector the source->citation tree lets you
expand a source and pick one of its existing citations.  As soon as a text
search is typed, the base model filters the secondary (citation) rows by the
*same* column and text as the primary (source) rows.  On the Title/Volume-Page
column that drops every citation of a matched source (a citation's page rarely
contains the source title), so the source is shown but has no citation children
-- the user is forced to create a *new* citation instead of reusing one.

These tests drive the **production** model-build path -- the selector's own
model class ``CitationTreeSelectorModel`` (what ``SelectCitation`` builds) and
the plain ``CitationTreeModel`` (what the standalone Citation Tree View builds)
-- with a ``search=`` tuple against a lightweight in-memory database, and assert
on the resulting node map.

Design notes
------------
* The reachability assertions do **not** hard-code the new class name so their
  *pre-fix* failure is the wrong *behaviour* (a matched source with no citation
  children -- an ``AssertionError``), not a bare import/``TypeError``: the
  selector model is looked up with a fallback to today's ``CitationTreeModel``
  when the fix is absent, so with the production change reverted the model is
  built and the reachability assertion fails on the node map (issue 8622's
  actual symptom), which is what the C4 red-without-fix leg exercises.
* ``test_selector_wiring_uses_selector_model`` closes the wiring gap: it asserts
  ``SelectCitation.get_model_class()`` really resolves to the selector model, so
  a typo there cannot leave every other test green while the dialog stays broken.
* ``test_selector_matching_orphan_citation_does_not_crash`` covers the orphan
  case: a citation whose page *matches the search text* but whose owning source
  was deleted must not break the source-grouped search -- deciding its
  visibility must never dereference its dangling ``source_handle`` (which would
  raise ``HandleError`` in ``add_row2``).
* ``test_selector_inverted_search_hides_matching_citation`` pins the inverted
  ("does not contain") case: grouping must not override the citation-level
  exclusion, so a citation whose page matches the excluded term stays hidden.
* ``test_selector_skip_*`` pin the public ``skip`` set: grouping must not
  resurrect (via ``add_row2``'s force-add-parent) a source/citation the caller
  asked to hide.
* The model imports :mod:`gi.repository.Gtk`, but building it with a handful of
  rows never pops a progress dialog (the estimated time stays below the popup
  threshold), so the whole module runs headless.
"""

import unittest
from contextlib import contextmanager

from gramps.gen.errors import HandleError

from ..citationtreemodel import CitationTreeModel

try:
    # Present once the issue-8622 fix is applied; absent when the production
    # change is reverted (the C4 red-without-fix leg) -- the fallback below then
    # exercises today's dropping behaviour, so the red is behavioural.
    from ..citationtreemodel import CitationTreeSelectorModel

    _HAVE_SELECTOR = True
except ImportError:  # pragma: no cover - only on the reverted (pre-fix) tree
    CitationTreeSelectorModel = None  # type: ignore[assignment,misc]
    _HAVE_SELECTOR = False


# -------------------------------------------------------------------------
#
# Lightweight in-memory test doubles
#
# -------------------------------------------------------------------------
class _Source:
    """Raw source data as the model's ``fmap``/sort funcs read it."""

    def __init__(self, handle, gramps_id, title):
        self.handle = handle
        self.gramps_id = gramps_id
        self.title = title
        self.author = ""
        self.abbrev = ""
        self.pubinfo = ""
        self.private = False
        self.tag_list = []
        self.change = 0


class _Citation:
    """Raw citation data as the model's ``fmap2``/sort funcs read it."""

    def __init__(self, handle, gramps_id, page, source_handle):
        self.handle = handle
        self.gramps_id = gramps_id
        self.page = page
        self.source_handle = source_handle
        self.date = None
        self.confidence = 0
        self.private = False
        self.tag_list = []
        self.change = 0


class _FakeDb:
    """Minimal database exposing only what CitationTreeModel touches."""

    def __init__(self, sources, citations):
        self._sources = {s.handle: s for s in sources}
        self._citations = {c.handle: c for c in citations}

    def is_open(self):
        return True

    # --- sources (primary) ---
    def get_number_of_sources(self):
        return len(self._sources)

    def get_raw_source_data(self, handle):
        # Faithful to the real DB: a missing/deleted source handle raises,
        # so a test that reaches here for an orphan citation's source_handle
        # fails loudly instead of silently passing.
        try:
            return self._sources[handle]
        except KeyError:
            raise HandleError("Handle %s not found" % handle)

    def get_source_cursor(self):
        return self._cursor(self._sources)

    # --- citations (secondary) ---
    def get_number_of_citations(self):
        return len(self._citations)

    def get_raw_citation_data(self, handle):
        try:
            return self._citations[handle]
        except KeyError:
            raise HandleError("Handle %s not found" % handle)

    def get_citation_cursor(self):
        return self._cursor(self._citations)

    @staticmethod
    @contextmanager
    def _cursor(mapping):
        yield list(mapping.items())


# -------------------------------------------------------------------------
#
# The test
#
# -------------------------------------------------------------------------
class CitationSelectorSearchTest(unittest.TestCase):
    """Issue 8622 -- a shown source must keep its citations reachable."""

    # Handles.
    SRC_BIBLE = "SRC_BIBLE"
    SRC_NEWS = "SRC_NEWS"
    SRC_GONE = "SRC_GONE"  # never present in the DB (a deleted source)
    CIT_B1 = "CIT_B1"
    CIT_B2 = "CIT_B2"
    CIT_N1 = "CIT_N1"
    CIT_ORPH = "CIT_ORPH"  # points at SRC_GONE

    def _build_db(self, with_orphan=False):
        # Two sources; only "Holy Bible" matches a title search for "Bible".
        sources = [
            _Source(self.SRC_BIBLE, "S0001", "Holy Bible"),
            _Source(self.SRC_NEWS, "S0002", "Daily Newspaper"),
        ]
        # Two citations under the Bible, one under the Newspaper.  Pages are
        # distinctive so a page search can target exactly one of them.
        citations = [
            _Citation(self.CIT_B1, "C0001", "page 10", self.SRC_BIBLE),
            _Citation(self.CIT_B2, "C0002", "page 20", self.SRC_BIBLE),
            _Citation(self.CIT_N1, "C0003", "column 3", self.SRC_NEWS),
        ]
        if with_orphan:
            # A citation whose owning source has been deleted.  Its page *does*
            # match the "page" search below, so pre-guard the grouped search
            # would add its dangling source_handle to the shown set and crash on
            # it in add_row2 -- the guard must keep it out.
            citations.append(
                _Citation(self.CIT_ORPH, "C0004", "page 99", self.SRC_GONE)
            )
        return _FakeDb(sources, citations)

    def setUp(self):
        self.db = self._build_db()
        # uistate is only stashed by the (non-popping) progress monitor.
        self.uistate = object()

    # Column 0 = "Source: Title or Citation: Volume/Page".  A text search is
    # ``(filter?, (col, text, inv), exact?)`` with ``filter?`` False (not a
    # sidebar GenericFilter).
    @staticmethod
    def _text_search(text, inverted=False):
        return (False, (0, text, inverted), False)

    def _selector_model(self, search, db=None, skip=set()):
        """
        Build the model the selector builds.  Falls back to the plain
        ``CitationTreeModel`` when the fix is absent (pre-fix / reverted), so the
        reachability assertions fail on *behaviour* rather than a missing symbol.
        """
        model_class = CitationTreeSelectorModel if _HAVE_SELECTOR else CitationTreeModel
        return model_class(db or self.db, self.uistate, search=search, skip=skip)

    def _child_handles(self, model, source_handle):
        """Handles of the citation rows under ``source_handle`` in the model."""
        node = model.tree.get(source_handle)
        if node is None:
            return []
        return [model.nodemap.node(nid).handle for _sortkey, nid in node.children]

    # -- selector: source matched by its TITLE keeps all its citations --------
    def test_selector_keeps_citations_of_title_matched_source(self):
        """
        A search matching a source *title* keeps that source shown *and* every
        one of its existing citations reachable underneath it (issue 8622).
        Pre-fix the citations are dropped -> this assertion fails behaviourally.
        """
        model = self._selector_model(self._text_search("Bible"))
        try:
            self.assertIn(self.SRC_BIBLE, model.tree, "matched source must be shown")
            self.assertEqual(
                sorted(self._child_handles(model, self.SRC_BIBLE)),
                [self.CIT_B1, self.CIT_B2],
                "existing citations of the matched source must stay reachable",
            )
            # The non-matching source (and its citation) stays filtered out.
            self.assertNotIn(self.SRC_NEWS, model.tree)
        finally:
            model.destroy()

    # -- selector: source pulled in by ONE citation keeps its SIBLINGS too ----
    def test_selector_keeps_sibling_citations_of_citation_matched_source(self):
        """
        A search matching a single citation's *page* ("page 10") pulls its
        source into the tree; the invariant requires the source's *sibling*
        citations ("page 20") to remain reachable as well -- if a source is
        shown, all its citations are selectable (issue 8622, iteration-1
        finding 3).  The non-matching source stays hidden.
        """
        model = self._selector_model(self._text_search("page 10"))
        try:
            self.assertIn(
                self.SRC_BIBLE,
                model.tree,
                "source of a matched citation must be shown",
            )
            self.assertEqual(
                sorted(self._child_handles(model, self.SRC_BIBLE)),
                [self.CIT_B1, self.CIT_B2],
                "sibling citations of a shown source must stay reachable, "
                "not just the citation whose page matched",
            )
            # "page 10" matches no Newspaper citation and not its title.
            self.assertNotIn(self.SRC_NEWS, model.tree)
        finally:
            model.destroy()

    # -- selector: a MATCHING orphan citation must not crash the search -------
    def test_selector_matching_orphan_citation_does_not_crash(self):
        """
        A citation whose page *matches the search* but whose owning source has
        been deleted (a live-database reality) must not break the source-grouped
        search: deciding its visibility, and building the tree, must never
        dereference its dangling ``source_handle`` (issue 8622, iteration-2/3
        finding).  The "page" search matches CIT_ORPH (page 99), CIT_B1 and
        CIT_B2 -- the orphan must be hidden while the real match is unaffected,
        and *no* ``HandleError`` may be raised.
        """
        db = self._build_db(with_orphan=True)
        # Must not raise HandleError while building the model.
        model = self._selector_model(self._text_search("page"), db=db)
        try:
            # The real matched source keeps its citations.
            self.assertIn(self.SRC_BIBLE, model.tree)
            self.assertEqual(
                sorted(self._child_handles(model, self.SRC_BIBLE)),
                [self.CIT_B1, self.CIT_B2],
            )
            # The deleted source is not shown, and the orphan citation is not
            # smuggled in under any parent.
            self.assertNotIn(self.SRC_GONE, model.tree)
            self.assertNotIn(self.CIT_ORPH, model.tree)
        finally:
            model.destroy()

    # -- selector: an inverted search must keep citation-level exclusion ------
    def test_selector_inverted_search_hides_matching_citation(self):
        """
        An inverted ("does not contain") search excludes matching rows at the
        user's request.  Grouping by source must NOT override that: a citation
        whose page matches the excluded term ("page 10") stays hidden even
        though its source is shown (issue 8622, iteration-3 finding 1).  A naive
        widening that groups inverted searches too would wrongly show CIT_B1.
        """
        if not _HAVE_SELECTOR:
            self.skipTest("selector model absent (pre-fix / reverted tree)")
        model = self._selector_model(self._text_search("page 10", inverted=True))
        try:
            # The Bible source is shown (its title does not contain "page 10").
            self.assertIn(self.SRC_BIBLE, model.tree)
            children = self._child_handles(model, self.SRC_BIBLE)
            # CIT_B1 (page 10) is the excluded term -> hidden; CIT_B2 kept.
            self.assertNotIn(
                self.CIT_B1,
                children,
                "an inverted search must still hide the citation whose page "
                "matches the excluded term",
            )
            self.assertIn(self.CIT_B2, children)
        finally:
            model.destroy()

    # -- selector: a skipped SOURCE must not be resurrected by grouping -------
    def test_selector_skip_source_is_not_resurrected(self):
        """
        ``skip`` is a public ``BaseSelector`` parameter (handles to hide).  The
        source-grouped widening must honour it: with the Bible source skipped, a
        title search for "Bible" must NOT show it -- even though its citations
        would otherwise force it in through ``add_row2``'s force-add-parent
        fallback (issue 8622 skip guard).  Mirrors the plain model, which hides
        a skipped source.
        """
        if not _HAVE_SELECTOR:
            self.skipTest("selector model absent (pre-fix / reverted tree)")
        model = self._selector_model(self._text_search("Bible"), skip={self.SRC_BIBLE})
        try:
            self.assertNotIn(
                self.SRC_BIBLE,
                model.tree,
                "a skipped source must stay hidden, not be resurrected by "
                "source-grouping its citations",
            )
        finally:
            model.destroy()

    # -- selector: a skipped CITATION must not pull its source back in --------
    def test_selector_skip_citation_does_not_resurrect_source(self):
        """
        With only one matching citation (CIT_B1, "page 10") and that citation
        skipped, the search has nothing left to show under the Bible source, so
        grouping must not resurrect it (issue 8622 skip guard).  The plain model
        hides the source in this case; the selector must match.
        """
        if not _HAVE_SELECTOR:
            self.skipTest("selector model absent (pre-fix / reverted tree)")
        model = self._selector_model(self._text_search("page 10"), skip={self.CIT_B1})
        try:
            self.assertNotIn(
                self.SRC_BIBLE,
                model.tree,
                "a source whose only matching citation was skipped must not be "
                "resurrected by grouping",
            )
        finally:
            model.destroy()

    # -- selector: an empty search box shows the full tree (no widening) ------
    def test_selector_empty_search_shows_full_tree(self):
        """
        An empty search box yields a truthy ``(col, "", inv)`` tuple that the
        base treats as a live match-everything search.  The selector must show
        every source with all its citations (identical to the plain model) and
        must not run the (wasted) grouping scan (issue 8622 empty-box guard).
        """
        model = self._selector_model(self._text_search(""))
        try:
            self.assertIn(self.SRC_BIBLE, model.tree)
            self.assertIn(self.SRC_NEWS, model.tree)
            self.assertEqual(
                sorted(self._child_handles(model, self.SRC_BIBLE)),
                [self.CIT_B1, self.CIT_B2],
            )
            self.assertEqual(self._child_handles(model, self.SRC_NEWS), [self.CIT_N1])
        finally:
            model.destroy()

    # -- standalone view: independent secondary search is unchanged -----------
    def test_standalone_model_keeps_independent_secondary_search(self):
        """
        The plain ``CitationTreeModel`` (standalone Citation Tree View) must NOT
        change: its secondary search stays independent, so a title search drops
        the matched source's citations.  This pins the non-regression boundary
        of the fix (scope: selector only).
        """
        model = CitationTreeModel(
            self.db, self.uistate, search=self._text_search("Bible")
        )
        try:
            self.assertIn(self.SRC_BIBLE, model.tree)
            self.assertEqual(
                self._child_handles(model, self.SRC_BIBLE),
                [],
                "standalone view keeps filtering citations by page (unchanged)",
            )
        finally:
            model.destroy()

    # -- wiring: the selector actually uses the selector model ----------------
    def test_selector_wiring_uses_selector_model(self):
        """
        ``SelectCitation.get_model_class()`` must resolve to the selector model,
        so the fix reaches the real dialog and a wiring typo cannot leave the
        behavioural tests green while the user-visible bug persists (issue 8622,
        iteration-1 finding 1).
        """
        if not _HAVE_SELECTOR:
            self.skipTest("selector model absent (pre-fix / reverted tree)")
        # Import lazily: importing the selector (a ManagedWindow) is import-safe
        # headless -- it only defines classes -- but keep it out of module load.
        from gramps.gui.selectors.selectcitation import SelectCitation

        # get_model_class does not touch ``self``; call it unbound.
        self.assertIs(
            SelectCitation.get_model_class(None),
            CitationTreeSelectorModel,
            "SelectCitation must build the issue-8622 selector model",
        )


if __name__ == "__main__":
    unittest.main()
