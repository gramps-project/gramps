# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2026  Gabriel Rios
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

from __future__ import annotations

from typing import Any

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.fs import tree
from gramps.gui.dialog import ErrorDialog, OkDialog, WarningDialog
from gramps.gui.fs.manager import get_session

_ = glocale.translation.gettext


class AuthMixin:
    @classmethod
    def ensure_session(cls, caller=None, verbosity=5) -> bool:
        """
        Ensure a shared session exists.
        Returns True if a session exists (logged-in or not).
        """
        try:
            sess = get_session(
                getattr(caller, "dbstate", None) if caller else None,
                getattr(caller, "uistate", None) if caller else None,
            )
            if sess:
                try:
                    tree._fs_session = sess
                except Exception:
                    pass
                return True
            return False
        except Exception:
            return False

    def _on_login(self, _btn: Any) -> None:
        """
        Interactive login button handler (shows OAuth UI).
        """
        sess = get_session(
            getattr(self, "dbstate", None), getattr(self, "uistate", None)
        )
        parent = getattr(self, "window", None) or getattr(
            getattr(self, "uistate", None), "window", None
        )

        if not sess:
            ErrorDialog(
                _("FamilySearch"),
                _("FamilySearch is not configured (missing app key / redirect)."),
                parent=parent,
            )
            return

        try:
            tree._fs_session = sess
        except Exception:
            pass

        try:
            if sess.logged:
                sess.probe_api(reason="ui-login")
                OkDialog(_("Already logged in to FamilySearch."))
            else:
                code = sess.authorize()
                if code and sess.get_token(code):
                    OkDialog(_("Logged in to FamilySearch."))
                else:
                    raise RuntimeError(
                        getattr(sess, "_status_detail", "") or _("Login failed.")
                    )
        except Exception as e:
            WarningDialog(_("Login failed:\n{err}").format(err=str(e)))

        try:
            refresh_status = getattr(self, "_refresh_status", None)
            if callable(refresh_status):
                refresh_status()
        except Exception:
            pass
