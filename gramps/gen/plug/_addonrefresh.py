#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  The Gramps project
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
Liveness gate for the Addon Manager background refresh.

The Addon Manager fetches its listing off the GUI thread. When a project's
listing file is missing (e.g. an old ``gramps51`` path, or any URL where
``addons-<lang>.json`` 404s), that fetch is both slow and failing: every
language's listing is tried and times out in turn. If the Addon Manager
window is closed while such a refresh is still in flight, the result that
arrives later must be *dropped*. Delivering it would call back into the
destroyed window and leave a dangling pointer in the Gtk draw cycle, which
crashes Gramps (Mantis 13174).

:class:`AddonRefreshDispatch` is the gate that decides whether a fetched
result may still be applied. It holds no GUI references, so it can be unit
tested headless while the real Addon Manager routes its refresh delivery
through it.
"""


# -------------------------------------------------------------------------
#
# AddonRefreshDispatch
#
# -------------------------------------------------------------------------
class AddonRefreshDispatch:
    """
    Gate the delivery of one background addon-refresh result.

    A refresh creates a dispatch and hands :meth:`deliver` to the worker
    thread as its completion callback. When the requesting window is torn
    down (or a newer refresh supersedes this one), :meth:`cancel` is called;
    any result that arrives afterwards is then dropped instead of being
    applied to a destroyed window.

    :param apply_result: callable invoked with the fetched addon list when,
        and only when, the dispatch is still alive at delivery time.
    """

    def __init__(self, apply_result):
        self._apply_result = apply_result
        self._alive = True

    @property
    def alive(self):
        """True until :meth:`cancel` is called."""
        return self._alive

    def cancel(self):
        """
        Mark the requesting window as torn down.

        After this, :meth:`deliver` drops its result instead of applying it,
        so a late-arriving (possibly failed) refresh cannot touch a window
        that no longer exists.
        """
        self._alive = False

    def deliver(self, addon_list):
        """
        Apply a fetched result iff the dispatch is still alive.

        :param addon_list: the addon list returned by the background fetch
            (an empty list for a missing/404 listing).
        :returns: True if the result was applied, False if it was dropped
            because the window had been closed during the refresh.
        """
        if not self._alive:
            return False
        self._apply_result(addon_list)
        return True
