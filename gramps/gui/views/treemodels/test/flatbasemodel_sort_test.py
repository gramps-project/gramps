#
# Gramps - a GTK+/GNOME based genealogy program
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
Regression test for bug #9267 -- a list view's row order must follow the
*current* display-name format.

Root cause
----------
``FlatBaseModel._rebuild_search`` / ``_rebuild_filter`` reuse the cached
``(sortkey, handle)`` map (``node_map.full_srtkey_hndl_map``) whenever it is
populated, recomputing ``sort_keys()`` only when the cache is empty.  That cache
is correct while the sort *function* is fixed -- a search/filter change only
restricts which handles are shown, never their order -- but it goes stale when
the sort key itself changes, e.g. when the user picks a new "Name format" in
Edit -> Preferences -> Display.  The view redisplays (the People view connects
``nameformat-changed`` to a rebuild) yet the rows keep the previous order until
the database is reopened.

Fix
---
``FlatBaseModel.rebuild_sort()`` marks the sort dirty so the next rebuild
recomputes ``sort_keys()`` with the current sort function; the People view calls
it before rebuilding on a format change.  ``BaseModel.rebuild_sort()`` is a
no-op default so the *same* view callback is safe on the hierarchical person
model (``PersonTreeModel`` -> ``TreeBaseModel``), which re-sorts from scratch on
every rebuild and so needs no cache invalidation.

This test drives the *real* production methods ``FlatBaseModel._rebuild_search``,
``FlatBaseModel._rebuild_filter`` and ``FlatBaseModel.rebuild_sort`` over the
*real* ``FlatNodeMap``, stubbing only the data source (``sort_keys``/``db``) so
the model machinery can run headlessly -- no database, GUI display or GObject
construction.  The methods are invoked unbound on a duck-typed ``self`` that
carries exactly the attributes they read.  A changing ``sort_keys`` stands in
for a name-format change.  Pre-fix, ``rebuild_sort`` does not exist and the
rebuild methods ignore the dirty flag, so the re-sort step raises
``AttributeError``; post-fix the rows re-sort.  A second test guards the
hierarchical path: ``TreeBaseModel`` must inherit a non-raising ``rebuild_sort``
so the shared person-view callback does not crash on a tree format change.
"""

import types
import unittest

from ..basemodel import BaseModel
from ..flatbasemodel import FlatBaseModel, FlatNodeMap
from ..treebasemodel import TreeBaseModel


class _OpenDb:
    """Minimal stand-in for the database the rebuild methods consult."""

    def is_open(self):
        return True


# Three people; the sort key is either the surname or the given name depending
# on the "format" currently selected.  The two orders are reverses of each
# other, so a re-sort is unambiguous.
PEOPLE = {
    "h_smith_alan": ("Smith", "Alan"),
    "h_brown_zoe": ("Brown", "Zoe"),
    "h_jones_mike": ("Jones", "Mike"),
}
ORDER_BY_SURNAME = ["h_brown_zoe", "h_jones_mike", "h_smith_alan"]
ORDER_BY_GIVEN = ["h_smith_alan", "h_jones_mike", "h_brown_zoe"]


def _make_fake():
    """A duck-typed ``self`` carrying exactly the attributes the production
    rebuild methods read, plus a mutable ``fmt`` selecting the sort key.

    Returns ``(fake, fmt)``; flip ``fmt["by"]`` between ``"surname"`` and
    ``"given"`` to model a name-format change.
    """
    fmt = {"by": "surname"}

    def sort_keys():
        keyed = []
        for handle, (surname, given) in PEOPLE.items():
            key = surname if fmt["by"] == "surname" else given
            keyed.append((key, handle))
        keyed.sort()
        return keyed

    fake = types.SimpleNamespace(
        node_map=FlatNodeMap(),
        clear_cache=lambda *a, **k: None,
        _in_build=False,
        db=_OpenDb(),
        search=None,
        skip=set(),
        _reverse=False,
        _sort_dirty=False,
        user=None,
        sort_keys=sort_keys,
    )
    return fake, fmt


def _displayed_order(fake):
    nm = fake.node_map
    return [nm.get_handle(path) for path in range(len(nm))]


class FlatBaseModelSortRebuildTest(unittest.TestCase):
    def _check_resort(self, rebuild):
        """``rebuild`` is the (unbound) production rebuild method to exercise."""
        fake, fmt = _make_fake()

        # Initial build: ordered by surname.
        rebuild(fake)
        self.assertEqual(_displayed_order(fake), ORDER_BY_SURNAME)

        # The user changes the name format -> the sort key now differs.
        fmt["by"] = "given"

        # A plain redisplay (search/filter rebuild) reuses the cached sort
        # order -- correct while the sort function is fixed; here it documents
        # that the cache is what must be invalidated.
        rebuild(fake)
        self.assertEqual(
            _displayed_order(fake),
            ORDER_BY_SURNAME,
            "a plain rebuild reuses the cached sort map",
        )

        # Invalidate the sort cache (what the People view does on
        # nameformat-changed), then rebuild: the rows must re-sort to the new
        # format without reopening the database.
        FlatBaseModel.rebuild_sort(fake)
        rebuild(fake)
        self.assertEqual(
            _displayed_order(fake),
            ORDER_BY_GIVEN,
            "rows did not re-sort after the name-format change (bug #9267)",
        )

    def test_resort_via_rebuild_filter(self):
        # The People flat view's default redisplay path (sidebar filter).
        self._check_resort(FlatBaseModel._rebuild_filter)

    def test_resort_via_rebuild_search(self):
        # The top-search-bar redisplay path.
        self._check_resort(FlatBaseModel._rebuild_search)


class TreeModelSortRebuildSafetyTest(unittest.TestCase):
    """The shared BasePersonView callback calls ``model.rebuild_sort()`` on
    whatever model the view holds.  ``PersonTreeView`` holds a ``PersonTreeModel``
    (``-> TreeBaseModel``), which has no cached sort map; ``rebuild_sort`` must
    therefore exist and be a harmless no-op there so the callback does not raise
    ``AttributeError`` on a name/place-format change in the Person Tree view.
    """

    def test_basemodel_provides_default_rebuild_sort(self):
        self.assertTrue(hasattr(BaseModel, "rebuild_sort"))

    def test_treebasemodel_rebuild_sort_is_noop(self):
        # Inherited from BaseModel; the body touches no instance state, so it is
        # safe to invoke unbound on a bare object and must return None.
        self.assertIsNone(TreeBaseModel.rebuild_sort(object()))


if __name__ == "__main__":
    unittest.main()
