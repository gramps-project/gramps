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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
DashboardView interface.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.views.pageview import PageView
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gui.widgets.grampletpane import GrampletPane


class DashboardView(PageView):
    """
    DashboardView interface
    """

    def __init__(self, pdata, dbstate, uistate):
        """
        Create a DashboardView, with the current dbstate and uistate
        """
        PageView.__init__(self, _("Dashboard"), pdata, dbstate, uistate)
        self.ui_def = []  # No special menu for Dashboard, Popup in GrampletPane

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
        # load the user's gramplets and set columns, etc
        self.widget = GrampletPane(
            "Gramplets_dashboardview_gramplets", self, self.dbstate, self.uistate
        )
        return self.widget

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

    def set_active(self):
        new_title = "%s - %s - Gramps" % (
            self.dbstate.db.get_dbname(),
            self.get_title(),
        )
        self.uistate.window.set_title(new_title)
        self.active = True
        self.widget.set_active()

    def on_delete(self):
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
