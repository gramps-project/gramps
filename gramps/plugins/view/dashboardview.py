#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
DashboardView interface — supports multiple named dashboards.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import configparser
import hashlib
import os
import shutil

from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import VERSION_DIR
from gramps.gui.views.pageview import PageView
from gramps.gui.widgets.grampletpane import GrampletPane

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
DASHBOARDS_CONFIG = os.path.join(VERSION_DIR, "dashboards.ini")

# The legacy single-dashboard config name (no dashboard suffix).
_LEGACY_CONFIG = "Gramplets_dashboardview_gramplets"


def _config_name(dashboard_name):
    """
    Return a filesystem-safe GrampletPane configfile stem for a dashboard name.

    The human-readable name is stored in dashboards.ini; the filename only
    needs to be unique and stable, so we use a short SHA-256 digest to avoid
    any issues with Unicode, spaces, or characters forbidden on Windows/Linux.
    """
    digest = hashlib.sha256(dashboard_name.encode("utf-8")).hexdigest()[:16]
    return "Gramplets_dashboardview_%s_gramplets" % digest


class DashboardView(PageView):
    """
    DashboardView interface — hosts one GrampletPane at a time, chosen from
    a named list of dashboards the user can create, rename, and delete.
    """

    def __init__(self, pdata, dbstate, uistate):
        """
        Create a DashboardView, with the current dbstate and uistate
        """
        PageView.__init__(self, _("Dashboard"), pdata, dbstate, uistate)
        self.ui_def = []  # No special menu for Dashboard, Popup in GrampletPane
        self._dashboard_names = []
        self._current_name = None
        self._pane_container = None

    # ------------------------------------------------------------------ #
    #  Dashboard-list persistence                                          #
    # ------------------------------------------------------------------ #

    def _load_dashboard_list(self):
        """
        Return (names, active_name).

        On the very first run (no dashboards.ini) we copy the legacy
        gramplet config so old customisations are preserved.
        """
        default_name = _("Dashboard")
        if os.path.exists(DASHBOARDS_CONFIG):
            cfg = configparser.ConfigParser()
            cfg.read(DASHBOARDS_CONFIG)
            raw = cfg.get("General", "dashboards", fallback=default_name)
            names = [n.strip() for n in raw.split(",") if n.strip()]
            if not names:
                names = [default_name]
            active = cfg.get("General", "active", fallback=names[0])
            if active not in names:
                active = names[0]
        else:
            names = [default_name]
            active = default_name
            # Copy legacy config → new naming convention (backwards compat).
            legacy_path = os.path.join(VERSION_DIR, "%s.ini" % _LEGACY_CONFIG)
            new_path = os.path.join(VERSION_DIR, "%s.ini" % _config_name(default_name))
            if os.path.exists(legacy_path) and not os.path.exists(new_path):
                shutil.copy2(legacy_path, new_path)
            self._save_dashboard_list(names, active)
        return names, active

    def _save_dashboard_list(self, names, active):
        cfg = configparser.ConfigParser()
        cfg["General"] = {
            "dashboards": ", ".join(names),
            "active": active,
        }
        with open(DASHBOARDS_CONFIG, "w") as fh:
            cfg.write(fh)

    # ------------------------------------------------------------------ #
    #  PageView interface                                                  #
    # ------------------------------------------------------------------ #

    def build_interface(self):
        """
        Builds the container widget for the interface.
        Returns a gtk container widget.
        """
        top = self.build_widget()
        top.show_all()
        return top

    def build_widget(self):
        """
        Builds the container widget for the interface. Must be overridden by the
        the base class. Returns a gtk container widget.
        """
        self._dashboard_names, self._current_name = self._load_dashboard_list()

        # ── Selector bar (lives in the status bar, not the view) ────────
        self._selector_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        self._combo = Gtk.ComboBoxText()
        for name in self._dashboard_names:
            self._combo.append_text(name)
        active_idx = (
            self._dashboard_names.index(self._current_name)
            if self._current_name in self._dashboard_names
            else 0
        )
        self._combo.set_active(active_idx)
        self._combo.connect("changed", self._on_combo_changed)
        self._selector_bar.pack_start(self._combo, False, False, 0)

        add_btn = Gtk.Button.new_from_icon_name("list-add", Gtk.IconSize.BUTTON)
        add_btn.set_tooltip_text(_("Create new dashboard"))
        add_btn.connect("clicked", self._on_add_dashboard)
        self._selector_bar.pack_start(add_btn, False, False, 0)

        self._rename_btn = Gtk.Button.new_from_icon_name(
            "document-edit", Gtk.IconSize.BUTTON
        )
        self._rename_btn.set_tooltip_text(_("Rename current dashboard"))
        self._rename_btn.connect("clicked", self._on_rename_dashboard)
        self._selector_bar.pack_start(self._rename_btn, False, False, 0)

        self._delete_btn = Gtk.Button.new_from_icon_name(
            "list-remove", Gtk.IconSize.BUTTON
        )
        self._delete_btn.set_tooltip_text(_("Delete current dashboard"))
        self._delete_btn.connect("clicked", self._on_delete_dashboard)
        self._selector_bar.pack_start(self._delete_btn, False, False, 0)

        # ── Container for the active GrampletPane ───────────────────────
        self._pane_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget = self._make_pane(self._current_name)
        self._pane_container.pack_start(self.widget, True, True, 0)

        self._update_button_sensitivity()
        return self._pane_container

    def build_tree(self):
        """
        Rebuilds the current display.
        """
        pass

    def get_title(self):
        """
        Used to set the titlebar in the configuration window.
        """
        return _("Dashboard")

    def get_stock(self):
        """
        Return image associated with the view, which is used for the
        icon for the button.
        """
        return "gramps-gramplet"

    def get_viewtype_stock(self):
        """Type of view in category"""
        return "gramps-gramplet"

    def define_actions(self):
        """
        Defines the UIManager actions. Called by the ViewManager to set up the
        View. The user typically defines self.action_list and
        self.action_toggle_list in this function.
        """
        pass

    def set_inactive(self):
        self.active = False
        self.widget.set_inactive()
        self.uistate.status.clear_view_widget()

    def set_active(self):
        new_title = "%s - %s - Gramps" % (
            self.dbstate.db.get_dbname(),
            self.get_title(),
        )
        self.uistate.window.set_title(new_title)
        self.active = True
        self.widget.set_active()
        self.uistate.status.set_view_widget(self._selector_bar)

    def on_delete(self):
        self.uistate.status.clear_view_widget()
        self.widget.on_delete()
        self._config.save()

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return self.widget.can_configure()

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the
        notebook pages of the Configure dialog

        :return: list of functions
        """
        return self.widget._get_configure_page_funcs()

    def navigation_type(self):
        """
        Return a description of the specific nav_type items that are
        associated with this view. None means that there is no specific
        type.
        """
        return None

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _make_pane(self, name, blank=False):
        kwargs = {"default_gramplets": []} if blank else {}
        return GrampletPane(
            _config_name(name), self, self.dbstate, self.uistate, **kwargs
        )

    def _update_button_sensitivity(self):
        self._delete_btn.set_sensitive(len(self._dashboard_names) > 1)

    def _switch_to(self, name, blank=False):
        """Save current pane, swap in the named pane."""
        if name == self._current_name:
            return
        # Dock any floating gramplet windows before saving so they are not
        # saved as "detached" and don't orphan themselves on the hidden pane.
        for gramplet in list(self.widget.detached_gramplets):
            if gramplet.detached_window:
                gramplet.detached_window.close()
        # Save and remove current pane.
        self.widget.on_delete()
        self._pane_container.remove(self.widget)
        # Build and show the new pane.
        self._current_name = name
        self.widget = self._make_pane(name, blank=blank)
        self._pane_container.pack_start(self.widget, True, True, 0)
        self.widget.show_all()
        if self.active:
            self.widget.set_active()
        self._save_dashboard_list(self._dashboard_names, self._current_name)
        self._update_button_sensitivity()

    def _rebuild_combo(self):
        """Repopulate the combo from _dashboard_names without firing signals."""
        self._combo.handler_block_by_func(self._on_combo_changed)
        self._combo.remove_all()
        for name in self._dashboard_names:
            self._combo.append_text(name)
        self._combo.set_active(self._dashboard_names.index(self._current_name))
        self._combo.handler_unblock_by_func(self._on_combo_changed)

    def _ask_name(self, title, default=""):
        """
        Show a modal dialog with a text entry.
        Returns the entered string, or None if cancelled / empty.
        """
        dialog = Gtk.Dialog()
        dialog.set_title(title)
        dialog.set_transient_for(self.uistate.window)
        dialog.set_modal(True)
        dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("OK"), Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        entry = Gtk.Entry()
        entry.set_text(default)
        entry.set_activates_default(True)

        content = dialog.get_content_area()
        content.set_spacing(6)
        content.set_border_width(8)
        content.add(Gtk.Label(label=_("Dashboard name:")))
        content.add(entry)
        dialog.show_all()

        response = dialog.run()
        name = entry.get_text().strip() if response == Gtk.ResponseType.OK else None
        dialog.destroy()
        return name if name else None

    # ------------------------------------------------------------------ #
    #  Signal handlers                                                     #
    # ------------------------------------------------------------------ #

    def _on_combo_changed(self, combo):
        idx = combo.get_active()
        if idx >= 0:
            self._switch_to(self._dashboard_names[idx])

    def _on_add_dashboard(self, _btn):
        name = self._ask_name(_("New Dashboard"))
        if not name:
            return
        if name in self._dashboard_names:
            # Already exists — just navigate to it.
            self._combo.set_active(self._dashboard_names.index(name))
            return
        self._dashboard_names.append(name)
        self._save_dashboard_list(self._dashboard_names, name)
        self._combo.append_text(name)
        # Switch directly so we can pass blank=True (new dashboard starts empty).
        self._switch_to(name, blank=True)
        self._rebuild_combo()

    def _on_rename_dashboard(self, _btn):
        old_name = self._current_name
        new_name = self._ask_name(_("Rename Dashboard"), default=old_name)
        if not new_name or new_name == old_name:
            return
        if new_name in self._dashboard_names:
            return  # Name already taken; ignore silently.

        # Move the config file on disk.
        old_path = os.path.join(VERSION_DIR, "%s.ini" % _config_name(old_name))
        new_path = os.path.join(VERSION_DIR, "%s.ini" % _config_name(new_name))
        if os.path.exists(old_path):
            shutil.copy2(old_path, new_path)
            os.remove(old_path)

        # Update the live pane so it saves to the new path.
        self.widget.configfile = new_path

        idx = self._dashboard_names.index(old_name)
        self._dashboard_names[idx] = new_name
        self._current_name = new_name
        self._rebuild_combo()
        self._save_dashboard_list(self._dashboard_names, self._current_name)

    def _on_delete_dashboard(self, _btn):
        if len(self._dashboard_names) <= 1:
            return
        name = self._current_name
        dialog = Gtk.MessageDialog(
            transient_for=self.uistate.window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Are you sure you want to delete this dashboard?"),
        )
        dialog.format_secondary_text(
            _('"%s" and all its gramplets will be removed.') % name
        )
        response = dialog.run()
        dialog.destroy()
        if response != Gtk.ResponseType.YES:
            return
        idx = self._dashboard_names.index(name)
        # Pick an adjacent dashboard to switch to.
        new_idx = idx - 1 if idx > 0 else 1
        new_name = self._dashboard_names[new_idx]

        # Switch away (saves and removes current pane).
        self._switch_to(new_name)

        # Remove the deleted dashboard from the list and disk.
        self._dashboard_names.remove(name)
        path = os.path.join(VERSION_DIR, "%s.ini" % _config_name(name))
        if os.path.exists(path):
            os.remove(path)

        self._rebuild_combo()
        self._save_dashboard_list(self._dashboard_names, self._current_name)
