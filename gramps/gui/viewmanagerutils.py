#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010,2025  Nick Hall
# Copyright (C) 2026       The Gramps project
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
GTK-independent helpers for :mod:`gramps.gui.viewmanager`.

This module deliberately carries no ``gi`` / GTK import, so the pure
view-selection logic it holds can be unit tested headless (see
``gramps/gui/test/viewmanager_test.py``).  ``viewmanager`` re-imports
``views_to_show`` from here, so production and the test exercise the *same*
implementation rather than a parallel copy.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config


# -------------------------------------------------------------------------
#
# Functions
#
# -------------------------------------------------------------------------
def views_to_show(views, use_last=True):
    """
    Determine based on preference setting which views should be shown.

    Returns a ``(current_cat, current_cat_view, default_cat_views)`` tuple.
    When there are no views to show -- ``views`` is empty, e.g. every view
    plugin has been hidden in the Plugin Manager -- ``current_cat`` is ``None``
    to signal "no category to select", so the caller leaves the interface with
    no active page instead of navigating into the empty set.
    """
    current_cat = 0
    current_cat_view = 0
    default_cat_views = [0] * len(views)
    if not views:
        # bug 8796: with no available views there is no category to select.
        # Returning (0, 0, []) here claimed category 0 exists, so the caller's
        # goto_page(0, 0) indexed an empty current_views list and raised
        # 'IndexError: list assignment index out of range' at startup.  Signal
        # "no view to show" with a None category instead.
        return None, None, default_cat_views
    if use_last:
        current_page_id = config.get("preferences.last-view")
        default_page_ids = config.get("preferences.last-views")
        found = False
        for indexcat, cat_views in enumerate(views):
            cat_view = 0
            for pdata, page_def in cat_views:
                if not found:
                    if pdata.id == current_page_id:
                        current_cat = indexcat
                        current_cat_view = cat_view
                        default_cat_views[indexcat] = cat_view
                        found = True
                        break
                if pdata.id in default_page_ids:
                    default_cat_views[indexcat] = cat_view
                cat_view += 1
        if not found:
            current_cat = 0
            current_cat_view = 0
    return current_cat, current_cat_view, default_cat_views
