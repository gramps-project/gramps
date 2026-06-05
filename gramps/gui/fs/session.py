# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025       Nick Hall
# Copyright (C) 2025-2026  Gabriel Rios
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
FamilySearch session/auth helper (GTK wrapper).
"""

# -------------------------------------------------------------------------
#
# Future imports
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import math
import os
import sys
import threading
from typing import Any

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # noqa: E402

from gramps.gen.constfunc import win
from gramps.gen.fs import session as fs_session_core

sys.modules.setdefault("gramps.gui.fs.session", sys.modules[__name__])

FSException = fs_session_core.FSException
FSPermission = fs_session_core.FSPermission
FamilySearchSession = fs_session_core.FamilySearchSession
Listener = fs_session_core.Listener
EnvProfile = fs_session_core.EnvProfile

AUTH_AUTO = fs_session_core.AUTH_AUTO
AUTH_WEBKIT = fs_session_core.AUTH_WEBKIT
AUTH_LOOPBACK = fs_session_core.AUTH_LOOPBACK
AUTH_MANUAL = fs_session_core.AUTH_MANUAL

ENV_BETA = fs_session_core.ENV_BETA
ENV_PROD = fs_session_core.ENV_PROD
DEFAULT_LOOPBACK_REDIRECT = fs_session_core.DEFAULT_LOOPBACK_REDIRECT

GLOBAL_SESSION = None
SESSION = None


def _try_import_webkit():
    if win():
        return False, None
    try:
        import gi as _gi

        _gi.require_version("WebKit2", "4.0")
        from gi.repository import WebKit2  # type: ignore

        return True, WebKit2
    except Exception:
        return False, None


class FSStatusIndicator:
    DOT_SIZE = 12

    def __init__(self):
        self._state = "DISCONNECTED"
        self._detail = ""
        self._http = None
        self._views: list[dict] = []
        self._window: Gtk.Window | None = None

    def create_widget(self) -> Gtk.Widget:
        dot = Gtk.DrawingArea()
        dot.set_size_request(self.DOT_SIZE, self.DOT_SIZE)
        dot.connect("draw", self._on_draw)

        label = Gtk.Label(label="FS: disconnected")
        label.set_xalign(0.0)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_border_width(6)
        box.pack_start(dot, False, False, 0)
        box.pack_start(label, True, True, 0)

        view = {"box": box, "dot": dot, "label": label}
        self._views.append(view)

        def _cleanup(*_args):
            try:
                self._views.remove(view)
            except Exception:
                pass

        box.connect("destroy", _cleanup)
        self._apply_to_view(view)
        return box

    def show_window(self, parent: Gtk.Window | None = None):
        if self._window is not None:
            self._window.present()
            return

        win_ = Gtk.Window(title="FamilySearch Connection")
        win_.set_default_size(360, 70)
        win_.set_resizable(False)
        win_.add(self.create_widget())
        try:
            win_.set_keep_above(True)
        except Exception:
            pass
        if parent is not None:
            try:
                win_.set_transient_for(parent)
            except Exception:
                pass
        win_.connect("destroy", lambda *_: setattr(self, "_window", None))
        win_.show_all()
        self._window = win_

    def set(self, state: str, detail: str = "", http: int | None = None):
        self._state = state
        self._detail = detail or ""
        self._http = http
        for view in list(self._views):
            self._apply_to_view(view)

    def _apply_to_view(self, view: dict):
        label: Gtk.Label = view["label"]
        dot: Gtk.DrawingArea = view["dot"]
        box: Gtk.Box = view["box"]

        extra = ""
        if self._http is not None:
            extra = f" (HTTP {self._http})"
        elif self._detail:
            extra = f" ({self._detail})"

        pretty = (self._state or "").lower().replace("_", " ")
        label.set_text(f"FS: {pretty}{extra}")

        tip = self._detail
        if self._http is not None and self._detail:
            tip = f"HTTP {self._http}: {self._detail}"
        if tip:
            box.set_tooltip_text(tip)

        dot.queue_draw()

    def _state_color(self):
        s = (self._state or "").upper()
        if s in ("CONNECTED", "API_OK"):
            return (0.20, 0.70, 0.25)
        if s in (
            "PROBING",
            "LOGGING_IN",
            "AUTHORIZING",
            "EXCHANGING_TOKEN",
            "AWAITING_BROWSER",
        ):
            return (0.95, 0.70, 0.15)
        if s in ("TOKEN_ACQUIRED", "AUTH_CODE_RECEIVED"):
            return (0.20, 0.55, 0.90)
        if s in ("ERROR", "API_FAIL"):
            return (0.85, 0.20, 0.20)
        return (0.55, 0.55, 0.55)

    def _on_draw(self, widget, cr):
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()
        r = min(w, h) / 2.0 - 1.0
        cx = w / 2.0
        cy = h / 2.0

        rr, gg, bb = self._state_color()
        cr.set_source_rgb(rr, gg, bb)
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.fill()

        cr.set_source_rgba(0, 0, 0, 0.25)
        cr.set_line_width(1.0)
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.stroke()
        return False


class Session(fs_session_core.Session):
    status_indicator: Any
    _status_state: str
    _status_detail: str
    _status_http: int | None

    def __init__(self, server: int = 0, app_key: str = "", redirect: str = ""):
        super().__init__(server=server, app_key=app_key, redirect=redirect)

        self.status_indicator = FSStatusIndicator()
        self._set_status(
            getattr(self, "_status_state", "DISCONNECTED"),
            getattr(self, "_status_detail", ""),
            getattr(self, "_status_http", None),
        )

        global GLOBAL_SESSION, SESSION
        GLOBAL_SESSION = self
        SESSION = self
        try:
            Session._shared = self
            Session._last_instance = self
        except Exception:
            pass

        if os.environ.get("GRAMPS_FS_SHOW_STATUS", "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        ):
            try:
                self.status_indicator.show_window(parent=self._get_parent_window())
            except Exception as e:
                fs_session_core._dbg(
                    f"status window: failed to show: {type(e).__name__}: {e}"
                )

    def _get_parent_window(self) -> Gtk.Window | None:
        try:
            wins = Gtk.Window.list_toplevels() or []
            for w in wins:
                try:
                    if w.get_visible():
                        return w
                except Exception:
                    continue
            return wins[0] if wins else None
        except Exception:
            return None

    def get_status_widget(self) -> Gtk.Widget:
        return self.status_indicator.create_widget()

    def _set_status(self, state: str, detail: str = "", http: int | None = None):
        self._status_state = state
        self._status_detail = detail or ""
        self._status_http = http
        fs_session_core._dbg(
            f"status: {state} detail={fs_session_core._safe(detail, 220)} http={http}"
        )
        try:
            if threading.current_thread() is threading.main_thread():
                self.status_indicator.set(state, detail=detail, http=http)
            else:
                GLib.idle_add(self.status_indicator.set, state, detail, http)
        except Exception:
            try:
                self.status_indicator.set(state, detail=detail, http=http)
            except Exception:
                pass

    def _iterate_ui_events(self) -> None:
        try:
            while Gtk.events_pending():
                Gtk.main_iteration()
        except Exception:
            pass

    def _supports_embedded_webkit(self) -> bool:
        has_webkit, _webkit = _try_import_webkit()
        return bool((not win()) and has_webkit)

    def _maybe_show_tools_window(self) -> None:
        try:
            val = os.environ.get("GRAMPS_FS_SHOW_TOOLS", "").strip().lower()
            if val in ("0", "false", "no", "off"):
                return
        except Exception:
            pass
        if getattr(self, "_tools_window_shown", False):
            return
        self._tools_window_shown = True

        def _open():
            try:
                from .tools_window import present_tools_window

                present_tools_window(self)
            except Exception as e:
                fs_session_core._dbg(
                    f"tools window: failed to open: {type(e).__name__}: {e}"
                )
            return False

        try:
            GLib.idle_add(_open)
        except Exception:
            _open()

    def _prompt_for_auth_code(self, auth_url: str) -> str:
        dlg = Gtk.Dialog(
            title="FamilySearch: Paste authorization code",
            transient_for=self._get_parent_window(),
            flags=0,
        )
        dlg.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dlg.add_button("Continue", Gtk.ResponseType.OK)

        box = dlg.get_content_area()
        box.set_border_width(10)
        box.set_spacing(10)

        msg = (
            "After approving access in your browser, paste the authorization code here.\n"
            "You may paste either:\n"
            "  - the CODE itself, or\n"
            "  - the full redirect URL containing ?code=...\n"
        )
        lab = Gtk.Label(label=msg)
        lab.set_xalign(0.0)
        lab.set_line_wrap(True)

        entry = Gtk.Entry()
        entry.set_activates_default(True)
        dlg.set_default_response(Gtk.ResponseType.OK)

        box.pack_start(lab, False, False, 0)
        box.pack_start(entry, False, False, 0)
        dlg.show_all()

        resp = dlg.run()
        text = entry.get_text()
        dlg.destroy()

        if resp != Gtk.ResponseType.OK:
            self._set_status("ERROR", "Manual login cancelled")
            return ""

        params = fs_session_core._extract_redirect_params_from_text(text)
        if (
            text.startswith("http://") or text.startswith("https://")
        ) and not self._validate_oauth_state(params):
            return ""
        if "error" in params or "error_description" in params:
            err = params.get("error", "")
            desc = params.get("error_description", "")
            self._set_status("ERROR", f"{err} {desc}".strip())
            return ""

        return (params.get("code", "") or "").strip()

    def _close_auth_window(self) -> None:
        win_ = getattr(self, "_auth_win", None)
        if win_ is not None:
            try:
                setattr(self, "_closing_auth_window", True)
                win_.destroy()
            except Exception:
                pass
            finally:
                setattr(self, "_closing_auth_window", False)
        setattr(self, "_auth_win", None)

    def _open_auth_ui(
        self, auth_url: str, capture_code: bool = False, expected_state: str = ""
    ) -> bool:
        has_webkit, WebKit2 = _try_import_webkit()
        if not has_webkit or WebKit2 is None:
            return False
        if win():
            return False
        setattr(self, "_auth_ui_cancelled", False)

        win_ = Gtk.Window(title="FamilySearch Login")
        win_.set_default_size(920, 920)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.pack_start(self.get_status_widget(), False, False, 0)

        web = WebKit2.WebView()
        try:
            settings = web.get_settings()
        except Exception:
            settings = None
        if settings is not None:
            try:
                settings.set_property("enable-smooth-scrolling", False)
            except Exception:
                pass
            try:
                settings.set_property("enable-webgl", False)
            except Exception:
                pass
            try:
                if hasattr(WebKit2, "HardwareAccelerationPolicy"):
                    settings.set_property(
                        "hardware-acceleration-policy",
                        WebKit2.HardwareAccelerationPolicy.NEVER,
                    )
            except Exception:
                pass
        sc = Gtk.ScrolledWindow()
        sc.add(web)
        outer.pack_start(sc, True, True, 0)
        win_.add(outer)

        handler_ids: dict[str, int | None] = {"decide": None, "load": None}

        def _shutdown_now():
            try:
                web.stop_loading()
            except Exception:
                pass
            try:
                if handler_ids["decide"] is not None:
                    web.disconnect(handler_ids["decide"])
                    handler_ids["decide"] = None
            except Exception:
                pass
            try:
                if handler_ids["load"] is not None:
                    web.disconnect(handler_ids["load"])
                    handler_ids["load"] = None
            except Exception:
                pass
            try:
                win_.destroy()
            except Exception:
                pass
            return False

        def _capture_from_uri(uri: str) -> None:
            try:
                q = fs_session_core.urlparse(uri).query
                qs = fs_session_core.parse_qs(q, keep_blank_values=True)
                got_state = qs.get("state", [""])[0] or ""
                if expected_state and got_state and got_state != expected_state:
                    self._oauth_error = (
                        "State mismatch (possible stale/duplicate redirect)"
                    )
                    self._oauth_code = ""
                    fs_session_core._dbg(
                        f"auth ui: state mismatch expected={expected_state!r} got={got_state!r}"
                    )
                    return
                if "error" in qs or "error_description" in qs:
                    self._oauth_error = (
                        qs.get("error_description", [""])[0] or qs.get("error", [""])[0]
                    )
                    self._oauth_code = ""
                else:
                    self._oauth_code = qs.get("code", [""])[0] or ""
                    self._oauth_error = ""
                fs_session_core._dbg(
                    f"auth ui: captured code_present={bool(self._oauth_code)} "
                    f"error={fs_session_core._safe(self._oauth_error, 200)}"
                )
            except Exception as e:
                self._oauth_error = f"{type(e).__name__}: {e}"
                self._oauth_code = ""

        def on_decide_policy(view, decision, decision_type):
            try:
                if decision_type not in (
                    WebKit2.PolicyDecisionType.NAVIGATION_ACTION,
                    WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION,
                ):
                    return False
                nav = decision.get_navigation_action()
                req = nav.get_request()
                uri = req.get_uri() or ""
                fs_session_core._dbg(
                    "auth ui: policy uri="
                    f"{fs_session_core._safe_url_for_log(uri, 500)}"
                )
                if capture_code and self.redirect and uri.startswith(self.redirect):
                    fs_session_core._dbg(
                        "auth ui: policy hit redirect uri (capturing code; ignoring navigation)"
                    )
                    _capture_from_uri(uri)
                    try:
                        decision.ignore()
                    except Exception:
                        pass
                    GLib.idle_add(_shutdown_now)
                    return True
                try:
                    decision.use()
                    return True
                except Exception:
                    return False
            except Exception:
                return False

        def on_load_changed(view, load_event):
            try:
                if load_event == WebKit2.LoadEvent.COMMITTED:
                    uri = view.get_uri() or ""
                    fs_session_core._dbg(
                        "auth ui: committed uri="
                        f"{fs_session_core._safe_url_for_log(uri, 500)}"
                    )
            except Exception:
                pass

        handler_ids["decide"] = web.connect("decide-policy", on_decide_policy)
        handler_ids["load"] = web.connect("load-changed", on_load_changed)

        def _on_destroy(*_a):
            try:
                if not getattr(self, "_closing_auth_window", False):
                    setattr(self, "_auth_ui_cancelled", True)
                if getattr(self, "_auth_win", None) is win_:
                    setattr(self, "_auth_win", None)
            except Exception:
                pass

        win_.connect("destroy", _on_destroy)
        setattr(self, "_auth_win", win_)
        win_.show_all()
        web.load_uri(auth_url)
        return True


def get_active_session():
    return fs_session_core.get_active_session()
