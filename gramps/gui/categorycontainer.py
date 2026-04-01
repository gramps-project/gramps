#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Doug Blank <doug.blank@gmail.com>
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
Provides CategoryContainer, which holds the shared sidebar and bottombar
for all view modes within a category.
"""

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from .widgets.grampletbar import GrampletBar


class CategoryContainer:
    """
    Holds the shared sidebar and bottombar GrampletBars for all view modes
    within a single category (e.g. People, Families).  When the user
    switches between modes in the same category only the main content widget
    is swapped; the sidebar and bottombar stay alive and connected.
    """

    def __init__(self, dbstate, uistate, category, defaults, initial_pageview=None):
        """
        :param dbstate: the database state
        :param uistate: the UI display state
        :param category: category name string, e.g. ``"People"``
        :param defaults: 2-tuple ``(sidebar_defaults, bottombar_defaults)``
        :param initial_pageview: the first PageView for this category, passed
            to GrampletBar so that gramplets have a valid view reference during
            their own initialization.
        """
        self.category = category
        self.current_view = None  # the PageView whose content is currently shown

        # ---- shared layout -------------------------------------------------
        self.hpane = Gtk.Paned()
        self.vpane = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.sidebar = GrampletBar(
            dbstate,
            uistate,
            initial_pageview,
            category + "_sidebar",
            defaults[0],
            Gtk.Orientation.VERTICAL,
        )
        self.bottombar = GrampletBar(
            dbstate,
            uistate,
            initial_pageview,
            category + "_bottombar",
            defaults[1],
            Gtk.Orientation.HORIZONTAL,
        )

        self.vpane.pack1(self.content_area, resize=True, shrink=False)
        self.vpane.pack2(self.bottombar, resize=False, shrink=False)
        self.hpane.pack1(self.vpane, resize=True, shrink=False)
        self.hpane.pack2(self.sidebar, resize=False, shrink=False)
        self.hpane.show()
        self.vpane.show()
        self.content_area.show()

        # ---- slider position config ----------------------------------------
        self._config = config.register_manager(
            category + "_container", use_config_path=True
        )
        self._config.register("vpane.slider-position", -1)
        self._config.init()

        self.vpane.set_position(self._config.get("vpane.slider-position"))
        self.vpane.connect(
            "notify::position", self._position_changed, "vpane.slider-position"
        )

        # hpane slider needs the widget to be drawn first (requires width)
        self._hpane_sig = self.hpane.connect("draw", self._setup_hpane_slider)

    # -------------------------------------------------------------------------
    # Slider helpers
    # -------------------------------------------------------------------------

    def _setup_hpane_slider(self, widget, _dummy):
        """One-shot: set up the hpane slider after the first draw."""
        widget.disconnect(self._hpane_sig)
        self._config.register("hpane.slider-position", -1)
        saved = self._config.get("hpane.slider-position")
        if saved == -1:
            # Compute a sensible default from the sidebar's natural width
            width = widget.get_allocated_width()
            side_ch = self.sidebar.get_children()
            try:
                vp_ch = side_ch[0].get_children()
                ch_width = vp_ch[0].get_preferred_width()[0] + 3
            except AttributeError:
                ch_width = 300
            saved = width - min(ch_width, 400)
        widget.set_position(saved)
        widget.connect(
            "notify::position", self._position_changed, "hpane.slider-position"
        )

    def _position_changed(self, widget, _position, setting):
        """Persist slider position whenever it moves."""
        self._config.set(setting, widget.get_position())

    # -------------------------------------------------------------------------
    # Public interface
    # -------------------------------------------------------------------------

    def get_display(self):
        """Return the top-level widget to be placed in the notebook."""
        return self.hpane

    def set_view(self, page_view):
        """
        Switch the visible content to *page_view*.

        The outgoing widget is hidden (not removed) so GTK preserves its
        realized state, scroll position, and selection.  All mode widgets
        live in ``content_area`` simultaneously; only one is visible at a
        time.  The active filter is propagated to the incoming view so both
        modes always reflect the same filter.

        Also updates the GrampletBars' ``pageview`` reference so that
        gramplets always see the currently active mode.
        """
        if self.current_view is not None:
            # Propagate the active filter to the incoming view so that both
            # modes always show the same filtered data.  Only mark dirty when
            # the filter has actually changed so we avoid unnecessary rebuilds.
            old_filter = getattr(self.current_view, "generic_filter", None)
            if getattr(page_view, "generic_filter", None) is not old_filter:
                page_view.generic_filter = old_filter
                page_view.dirty = True

            # Hide (not remove) the outgoing widget so GTK preserves its
            # realized state, scroll position, and selection.  Removing it
            # would cause an unrealize which resets the GtkScrolledWindow
            # position to zero and requires complex scroll-timing workarounds.
            old_widget = self.current_view.get_content_widget()
            if old_widget is not None:
                old_widget.hide()

        # Keep GrampletBar.pageview in sync with the active mode
        self.sidebar.pageview = page_view
        self.bottombar.pageview = page_view

        new_widget = page_view.get_content_widget()
        if new_widget.get_parent() != self.content_area:
            self.content_area.pack_start(new_widget, True, True, 0)
        new_widget.show_all()
        self.current_view = page_view

        # Let the new view react to the current sidebar visibility
        page_view.sidebar_toggled(self.sidebar.get_property("visible"))

    def set_active(self):
        """Called when this category becomes the active (visible) category."""
        self.sidebar.set_active()
        self.bottombar.set_active()

    def set_inactive(self):
        """Called when this category is hidden in favour of another category."""
        self.sidebar.set_inactive()
        self.bottombar.set_inactive()

    def on_delete(self):
        """Called on application shutdown to persist gramplet state."""
        self.sidebar.on_delete()
        self.bottombar.on_delete()
        self._config.save()
