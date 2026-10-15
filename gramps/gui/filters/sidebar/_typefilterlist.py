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
Keep a :class:`SidebarFilter`'s database-derived "Type" selectors consistent
with the database's current custom types (bug 13716).

This module is deliberately free of GUI (``gi`` / ``gramps.gui``) imports: it
holds only the repopulate orchestration, so the logic can be unit-tested
headlessly while the GUI :class:`SidebarFilter` wires its Gtk type-selector
widgets to it.
"""


# -------------------------------------------------------------------------
#
# TypeFilterList class
#
# -------------------------------------------------------------------------
class TypeFilterList:
    """
    Registry of a sidebar filter's database-derived "Type" selectors.

    A view's sidebar filter reads the database's custom types only once, when
    the filter widget is first built, and never refreshes them.  A custom type
    added to an already-open database (for example the "GEDCOM import" Note type
    created by importing a GEDCOM with errors) therefore never appears in the
    selector until the gramplet/view is torn down and rebuilt (bug 13716).  The
    editor dialogs do not have this problem because they rebuild their type
    selector from the database every time they are shown.

    Each selector is registered with two callables:

    * ``fetch`` -- returns the database's *current* custom types.  It must
      re-read the live database on every call, never close over a
      construction-time snapshot, so that types added after construction are
      seen.
    * ``apply`` -- rebuilds the widget's offered options from a given list of
      custom types.

    :meth:`refresh` re-fetches every registered selector from the database and
    re-applies it, so the options presented to the user reflect the database's
    current custom-type set rather than a snapshot frozen at construction time.
    """

    def __init__(self):
        self._selectors = []

    def register(self, fetch, apply):
        """
        Register a type selector by its ``fetch`` and ``apply`` callables.

        :param fetch: callable returning the database's current custom types.
        :param apply: callable taking a list of custom types and rebuilding the
                      widget's offered options.
        """
        self._selectors.append((fetch, apply))

    def refresh(self):
        """
        Re-read every registered selector's custom types from the database and
        rebuild its offered options, restoring consistency with the database's
        current custom-type set.
        """
        for fetch, apply in self._selectors:
            apply(list(fetch()))
