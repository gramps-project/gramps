# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Gramps developers
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
Selection-resolution helper for the Families view (Mantis 12539).

Kept as a separate, ``gi``-free module so the filter -> detail-tab refresh
decision can be reasoned about and unit-tested without importing Gtk.
``FamilyView.build_tree`` routes through :func:`resolve_active_after_filter`
after every (re)build of the family list so that the embedded "Children" tab
follows the current *visible* selection once a filter/Find changes the list.
"""


def resolve_active_after_filter(active_handle, visible_handles):
    """
    Return the family handle that should be active after a list (re)build.

    :param active_handle: the currently active family handle, or a falsy value
        when no family is active.
    :param visible_handles: the family handles currently shown in the
        (possibly filtered) list, in display order.
    :returns: the handle that should become/stay active, or ``None``.

    Rules:

    * No active family -> ``None``: never auto-select on a plain build or at
      startup, preserving the existing "nothing selected" state.
    * Active family still visible -> keep it, so no spurious active-changed
      signal fires when the selection did not actually move.
    * Active family filtered out while the list is non-empty -> the first
      visible family, so the detail tabs track a valid, visible selection
      instead of the now-hidden previous one (the Mantis 12539 symptom: the
      Children tab kept showing the filtered-out family).
    * Active family filtered out and nothing visible -> ``None``.
    """
    if not active_handle:
        return None
    if active_handle in visible_handles:
        return active_handle
    if visible_handles:
        return visible_handles[0]
    return None
