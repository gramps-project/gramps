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
Regression test for :meth:`TreeBaseModel.reverse_order`.

Bug 0013214 reported that clicking a column header in the People view
after closing the family tree raised::

    KeyError: None

in ``treebasemodel.py:reverse_order``.  When the database closes the
framework clears the model's ``tree`` dict, so the root entry
``tree[None]`` disappears.  The unconditional ``self.tree[None]``
lookup in :meth:`reverse_order` then crashed.

This test exercises the same shape: drive ``reverse_order`` on a model
whose ``tree`` is empty.  Pre-fix the call raised ``KeyError``;
post-fix it returns silently.
"""

import unittest

from ..treebasemodel import TreeBaseModel


class TreeBaseModelReverseOrderTest(unittest.TestCase):
    """Bug 0013214 regression."""

    def test_reverse_order_with_empty_tree_does_not_raise(self):
        """Empty self.tree must short-circuit, not KeyError."""
        # Bypass __init__: TreeBaseModel.__init__ talks to a database,
        # which we do not have headless. We only need to drive the
        # one method, with the minimal state it touches.
        model = TreeBaseModel.__new__(TreeBaseModel)
        model.tree = {}
        # clear_path_cache() calls self.lru_path.clear().
        model.lru_path = {}
        # __reverse is a name-mangled private attr on TreeBaseModel.
        model._TreeBaseModel__reverse = False

        # Pre-fix this raised KeyError(None). Post-fix it returns
        # silently and toggles the internal reverse flag.
        model.reverse_order()

        # Sanity-check the only observable side-effect on the empty
        # path: the reverse flag was still toggled, since the user's
        # intent (next time data is loaded, sort the other way) is
        # captured even when the current model has nothing to flip.
        self.assertTrue(model._TreeBaseModel__reverse)


if __name__ == "__main__":
    unittest.main()
