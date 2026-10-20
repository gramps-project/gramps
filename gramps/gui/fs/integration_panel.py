# gramps/gui/fs/integration_panel.py
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gabriel Rios
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

# ------------------------
# Python modules
# ------------------------
import logging
import os
import threading
from typing import Any
from urllib.parse import urlsplit

import requests
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf, GLib, Gtk

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.config import config
from gramps.gen.const import IMAGE_DIR, GRAMPS_LOCALE as glocale
from gramps.gui.display import display_url

# ------------------------
# Gramps specific
# ------------------------
from . import manager

_ = glocale.translation.gettext
LOG = logging.getLogger(__name__)
MIDDLEWARE_URL = "https://fs-auth-portal.gramps-project.org"
ARTWORK = "FS-CompatibleSolution902x304.png"


def middleware_address() -> str:
    """Return the configured middleware address, respecting environment overrides."""
    return (
        os.environ.get("GRAMPS_FS_FOUNDATION_BASE_URL", "").strip()
        or str(config.get("familysearch.middleware.base-url") or "").strip()
        or MIDDLEWARE_URL
    ).rstrip("/")


def selected_server() -> int:
    """Return the effective server selection used by the session."""
    environment = os.environ.get("GRAMPS_FS_ENV", "").strip().lower()
    if environment in ("beta", "prod"):
        return 0 if environment == "beta" else 1
    try:
        value = int(
            os.environ.get("GRAMPS_FS_SERVER") or config.get("familysearch.server") or 0
        )
    except ValueError:
        value = int(config.get("familysearch.server") or 0)
    return 0 if value == 0 else 1


def check_middleware(address: str) -> str:
    """
    Check reachability without sending an access key or starting a login.

    :param address: The middleware base URL.
    :returns: A translated description of the HTTP result.
    """
    try:
        parsed = urlsplit(address)
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            return _("Enter a valid middleware address.")
        with requests.get(
            address, timeout=(3, 5), allow_redirects=False, stream=True
        ) as response:
            return _("Middleware responded (HTTP %d).") % response.status_code
    except (requests.RequestException, OSError, ValueError):
        return _("Could not reach the middleware. Check the address and connection.")


# ------------------------------------------------------------
#
# FamilySearchIntegrationPanel
#
# ------------------------------------------------------------
class FamilySearchIntegrationPanel:
    """Display integration setup separately from FamilySearch account sign-in."""

    def __init__(self, uistate: Any) -> None:
        """
        Build the Preferences section without making network requests.

        :param uistate: The application interface state.
        """
        self.uistate = uistate
        self._busy = False
        self._destroyed = False
        self._generation = 0
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._build_header()
        self._build_settings()
        self._timer = GLib.timeout_add_seconds(1, self.cb_refresh)
        self.widget.connect("destroy", self.cb_destroy)
        self.cb_refresh()

    def _build_header(self) -> None:
        """Keep the official logo independent of connection status."""
        header = Gtk.Box(spacing=16)
        self._expanded = Gtk.Expander()
        self._expanded.set_valign(Gtk.Align.CENTER)
        self._expanded.connect("notify::expanded", self.cb_expand)
        header.pack_start(self._expanded, False, False, 0)
        artwork = Gtk.Image()
        artwork.set_margin_top(16)
        artwork.set_margin_bottom(16)
        artwork.set_margin_start(16)
        artwork.set_margin_end(16)
        try:
            artwork.set_from_pixbuf(
                GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    os.path.join(IMAGE_DIR, ARTWORK), 280, -1, True
                )
            )
        except GLib.Error:
            LOG.warning("Cannot load the FamilySearch integration artwork")
        brand = Gtk.EventBox()
        brand.add(artwork)
        style = Gtk.CssProvider()
        style.load_from_data(b".fs-preferences-brand { background-color: white; }")
        brand.get_style_context().add_class("fs-preferences-brand")
        brand.get_style_context().add_provider(
            style, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        header.pack_start(brand, False, False, 0)
        self._enabled = Gtk.CheckButton(label=_("Enable integration"))
        self._enabled.set_valign(Gtk.Align.CENTER)
        self._enabled.set_active(bool(config.get("familysearch.enable")))
        self._enabled.connect("toggled", self.cb_enable)
        header.pack_start(self._enabled, False, False, 0)
        self.widget.pack_start(header, False, False, 0)

    def _row(self, title: str, control: Gtk.Widget) -> None:
        """
        Append a labelled control to the configuration grid.

        :param title: The translated field label.
        :param control: The field widget.
        """
        self._grid.attach(Gtk.Label(label=title, xalign=1.0), 0, self._row_number, 1, 1)
        control.set_hexpand(True)
        self._grid.attach(control, 1, self._row_number, 1, 1)
        self._row_number += 1

    def _wide(self, control: Gtk.Widget) -> None:
        """
        Append content aligned with the configuration fields.

        :param control: The content widget.
        """
        self._grid.attach(control, 1, self._row_number, 1, 1)
        self._row_number += 1

    def _entry(self, key: str, secret: bool = False) -> Gtk.Entry:
        """
        Create a configuration entry with optional key masking.

        :param key: The configuration key.
        :param secret: Whether the value must be hidden.
        :returns: The configured entry.
        """
        entry = Gtk.Entry()
        entry.set_text(str(config.get(key) or ""))
        entry.set_visibility(not secret)
        entry.connect("changed", self.cb_entry, key)
        if secret:
            entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, "view-reveal-symbolic"
            )
            entry.set_icon_tooltip_text(
                Gtk.EntryIconPosition.SECONDARY, _("Show access key")
            )
            entry.connect("icon-press", self.cb_reveal)
        return entry

    def _build_settings(self) -> None:
        """Build the collapsible access setup and account controls."""
        self._grid = Gtk.Grid(column_spacing=12, row_spacing=8)
        self._grid.set_margin_start(24)
        self._row_number = 0
        self._server = Gtk.ComboBoxText()
        for title in (_("Beta (testing)"), _("Production")):
            self._server.append_text(title)
        self._server.set_active(selected_server())
        self._server.connect("changed", self.cb_server)
        self._row(_("Server:"), self._server)
        self._account_note = Gtk.Label(xalign=0.0, wrap=True)
        self._account_note.set_max_width_chars(60)
        self._wide(self._account_note)
        heading = Gtk.Label(label=_("Gramps middleware access"), xalign=0.0)
        heading.set_markup(
            "<b>%s</b>" % GLib.markup_escape_text(_("Gramps middleware access"))
        )
        heading.set_margin_top(12)
        self._wide(heading)
        self._address = self._entry("familysearch.middleware.base-url")
        self._address.set_placeholder_text(MIDDLEWARE_URL)
        self._row(_("Middleware address:"), self._address)
        self._key = self._entry("familysearch.middleware.access-code", secret=True)
        self._row(_("Integration access key:"), self._key)
        self._request = Gtk.Expander(label=_("Don't have an Integration access key?"))
        request = Gtk.Button(label=_("Request integration access"))
        request.set_halign(Gtk.Align.START)
        request.set_margin_start(16)
        request.set_margin_top(8)
        request.connect("clicked", self.cb_request)
        self._request.add(request)
        self._wide(self._request)
        self._advanced = Gtk.Expander(label=_("Developer settings"))
        advanced = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._provider = Gtk.ComboBoxText()
        self._provider.append_text(_("Foundation middleware"))
        self._provider.append_text(_("Direct FamilySearch"))
        self._provider.set_active(
            1 if config.get("familysearch.auth-provider") == "direct" else 0
        )
        self._provider.connect("changed", self.cb_provider)
        advanced.pack_start(self._provider, False, False, 0)
        for key, title in (
            ("familysearch.app-key", _("App key")),
            ("familysearch.redirect", _("Redirect URL")),
        ):
            advanced.pack_start(Gtk.Label(label=title, xalign=0.0), False, False, 0)
            advanced.pack_start(
                self._entry(key, secret=key.endswith("app-key")), False, False, 0
            )
        self._advanced.add(advanced)
        self._wide(self._advanced)
        account = Gtk.Label(label=_("FamilySearch account"), xalign=0.0)
        account.set_markup(
            "<b>%s</b>" % GLib.markup_escape_text(_("FamilySearch account"))
        )
        account.set_margin_top(12)
        self._wide(account)
        buttons = Gtk.Box(spacing=8)
        self._sign_in = Gtk.Button(label=_("Sign in to FamilySearch"))
        self._sign_in.connect("clicked", self.cb_sign_in)
        self._sign_out = Gtk.Button(label=_("Sign out"))
        self._sign_out.connect("clicked", self.cb_sign_out)
        self._test = Gtk.Button(label=_("Test connection"))
        self._test.set_tooltip_text(
            _("Check the middleware address without signing in.")
        )
        self._test.connect("clicked", self.cb_test)
        for button in (self._sign_in, self._sign_out, self._test):
            button.set_no_show_all(True)
            buttons.pack_start(button, False, False, 0)
        self._wide(buttons)
        self._status = Gtk.Label(xalign=0.0, wrap=True)
        self._status.set_max_width_chars(60)
        self._wide(self._status)
        self._revealer = Gtk.Revealer()
        self._revealer.add(self._grid)
        self.widget.pack_start(self._revealer, False, False, 0)

    def cb_expand(self, expander: Gtk.Expander, _property: Any) -> None:
        """Show settings when expanded and conceal keys when collapsed."""
        self._revealer.set_reveal_child(expander.get_expanded())
        if not expander.get_expanded():
            self._key.set_visibility(False)

    def cb_reveal(self, entry: Gtk.Entry, position: Any, _event: Any) -> None:
        """Toggle access-key visibility without copying it elsewhere."""
        if position == Gtk.EntryIconPosition.SECONDARY:
            visible = not entry.get_visibility()
            entry.set_visibility(visible)
            entry.set_icon_from_icon_name(
                position, "view-conceal-symbolic" if visible else "view-reveal-symbolic"
            )
            entry.set_icon_tooltip_text(
                position, _("Hide access key") if visible else _("Show access key")
            )

    def _changed(self) -> None:
        """Invalidate old settings and any pending connection-test result."""
        manager.invalidate_session()
        self._generation += 1
        self._busy = False
        self._status.set_text("")
        self.cb_refresh()

    def cb_enable(self, button: Gtk.CheckButton) -> None:
        """Save integration enablement and expand initial setup."""
        config.set("familysearch.enable", button.get_active())
        if button.get_active():
            self._expanded.set_expanded(True)
        self.cb_refresh()

    def cb_entry(self, entry: Gtk.Entry, key: str) -> None:
        """Save a changed setting without contacting either service."""
        config.set(key, entry.get_text())
        self._changed()

    def cb_server(self, combo: Gtk.ComboBoxText) -> None:
        """Select an environment without retaining the previous status."""
        config.set("familysearch.server", combo.get_active())
        self._changed()

    def cb_provider(self, combo: Gtk.ComboBoxText) -> None:
        """Save the developer authentication-provider selection."""
        config.set(
            "familysearch.auth-provider",
            "direct" if combo.get_active() else "foundation",
        )
        self._changed()

    def cb_request(self, _button: Gtk.Button) -> None:
        """Open the middleware access-request website."""
        display_url(middleware_address())

    def cb_sign_in(self, _button: Gtk.Button) -> None:
        """Use the application's existing FamilySearch sign-in flow."""
        if not config.get("familysearch.middleware.base-url"):
            config.set("familysearch.middleware.base-url", middleware_address())
        viewmanager = getattr(self.uistate, "viewmanager", None)
        if viewmanager is not None:
            self._busy = True
            self._status.set_text(_("Signing in…"))
            self.cb_refresh()
            try:
                viewmanager.login()
            finally:
                self._busy = False
                self.cb_refresh()

    def cb_sign_out(self, _button: Gtk.Button) -> None:
        """Sign out without blocking the Preferences event loop."""
        session = manager.current_session()
        if session is None:
            return
        self._busy = True
        self.cb_refresh()

        def cb_logout() -> None:
            """Return to the interface after the existing logout request ends."""
            try:
                session.logout()
            except Exception:
                LOG.warning("FamilySearch sign-out request failed")
            finally:
                GLib.idle_add(self.cb_signed_out)

        threading.Thread(target=cb_logout, daemon=True).start()

    def cb_signed_out(self) -> bool:
        """Discard signed-out settings and update the main-window indicator."""
        self._busy = False
        manager.invalidate_session()
        viewmanager = getattr(self.uistate, "viewmanager", None)
        if viewmanager is not None:
            viewmanager.statusbar.set_fs_online(False)
        self.cb_refresh()
        return False

    def cb_test(self, _button: Gtk.Button) -> None:
        """Run a bounded, unauthenticated reachability check off the GTK thread."""
        self._busy = True
        generation = self._generation
        address = middleware_address()
        self._status.set_text(_("Testing the middleware connection…"))
        self.cb_refresh()

        def cb_check() -> None:
            """Return the reachability result to the GTK event loop."""
            GLib.idle_add(self.cb_test_finished, generation, check_middleware(address))

        threading.Thread(target=cb_check, daemon=True).start()

    def cb_test_finished(self, generation: int, message: str) -> bool:
        """Ignore test results belonging to destroyed panels or old settings."""
        if not self._destroyed and generation == self._generation:
            self._busy = False
            self._status.set_text(message)
            self.cb_refresh()
        return False

    def cb_refresh(self) -> bool:
        """Reflect existing session state without performing network requests."""
        if self._destroyed:
            return False
        session = manager.current_session()
        signed_in = bool(session and getattr(session, "access_token", None))
        connected = bool(signed_in and getattr(session, "connected", False))
        profile = getattr(session, "_profile", None)
        same_server = getattr(profile, "env", None) == (
            "beta" if selected_server() == 0 else "prod"
        )
        self._account_note.set_text(
            _("Beta requires a separate FamilySearch beta account.")
            if selected_server() == 0
            else _("Production requires your regular FamilySearch account.")
        )
        direct_enabled = os.environ.get(
            "GRAMPS_FS_ENABLE_DIRECT", ""
        ).strip().lower() in ("1", "true", "yes", "on")
        direct = direct_enabled and config.get("familysearch.auth-provider") == "direct"
        key = (
            os.environ.get("GRAMPS_FS_FOUNDATION_ACCESS_CODE", "").strip()
            or self._key.get_text().strip()
        )
        enabled = bool(config.get("familysearch.enable"))
        self._advanced.set_visible(direct_enabled)
        self._sign_in.set_visible(not signed_in)
        self._sign_in.set_sensitive(
            enabled and not self._busy and (direct or bool(key))
        )
        self._sign_out.set_visible(signed_in)
        self._sign_out.set_sensitive(not self._busy)
        self._test.set_visible(not direct and not signed_in)
        self._test.set_sensitive(not self._busy)
        for control in (self._server, self._address, self._key, self._advanced):
            control.set_sensitive(not signed_in and not self._busy)
        self._enabled.set_sensitive(not self._busy)
        self._request.set_visible(not direct and not key)
        if signed_in:
            self._status.set_text(
                _("Sign out before using the selected server.")
                if not same_server
                else (
                    _("Signed in to FamilySearch.")
                    if connected
                    else _("Signed in. The last FamilySearch connection check failed.")
                )
            )
        return not self._destroyed

    def cb_destroy(self, _widget: Gtk.Widget) -> None:
        """Stop observing the session when Preferences closes."""
        self._destroyed = True
        GLib.source_remove(self._timer)
