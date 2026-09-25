#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  The Gramps Project
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
HTML Bridge for routing raw web data between WebSearch, HTMLView, and Grizard.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

import logging

LOG = logging.getLogger(".htmlbridge")


# ------------------------------------------------------------
#
# HtmlBridge
#
# ------------------------------------------------------------
class HtmlBridge:
    """
    HtmlBridge handles routing downloaded HTML content from WebSearch
    to either HTMLView or Grizard based on availability.
    """

    @classmethod
    def route_html(cls, url: str, html_content: str) -> None:
        """
        Route HTML content. By default, sends it to HTMLView.
        If Grizard is installed, it also routes to Grizard.

        :param url: The origin URL of the HTML content.
        :type url: str
        :param html_content: The raw HTML content.
        :type html_content: str
        """
        # 1. Default routing path: Send to HTMLView if loaded/active
        try:
            from gramps.plugins.view.htmlview import HTMLView

            HTMLView.set_html_text(html_content)
        except Exception as err:
            LOG.debug("HTMLView is not loaded or active: %s", err)

        # 2. Conditional routing path: Route to Grizard if the addon is installed
        try:
            # Check if Grizard package/modules are installed/importable
            from gramps.gui.grizard.grizardcompare import GrizardCompareWindow
            from gramps.gen.grizard.gedcom import GedGrizard
            from gi.repository import Gtk
            from gramps.gen.const import GRAMPS_LOCALE as glocale
            import gc
            from gramps.gui.viewmanager import ViewManager

            _ = glocale.translation.gettext

            vm = None
            for obj in gc.get_objects():
                if isinstance(obj, ViewManager):
                    vm = obj
                    break

            if vm and vm.dbstate.is_open():
                LOG.info(
                    "Grizard is installed. Routing HTML to Grizard for parsing: %s", url
                )

                chooser = Gtk.FileChooserDialog(
                    title=_("Select File to Compare/Merge with captured HTML data"),
                    transient_for=vm.window,
                    action=Gtk.FileChooserAction.OPEN,
                )
                chooser.add_buttons(
                    Gtk.STOCK_CANCEL,
                    Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OPEN,
                    Gtk.ResponseType.OK,
                )

                # Supported Files
                filter_supported = Gtk.FileFilter()
                filter_supported.set_name(_("Supported Files (*.ged, *.xml, *.gramps)"))
                filter_supported.add_pattern("*.ged")
                filter_supported.add_pattern("*.xml")
                filter_supported.add_pattern("*.gramps")
                chooser.add_filter(filter_supported)

                # GEDCOM Files
                filter_ged = Gtk.FileFilter()
                filter_ged.set_name(_("GEDCOM files (*.ged)"))
                filter_ged.add_pattern("*.ged")
                chooser.add_filter(filter_ged)

                # XML / XML-GEDCOM Files
                filter_xml = Gtk.FileFilter()
                filter_xml.set_name(_("XML Files (*.xml)"))
                filter_xml.add_pattern("*.xml")
                chooser.add_filter(filter_xml)

                # Gramps XML Files
                filter_gramps = Gtk.FileFilter()
                filter_gramps.set_name(_("Gramps XML Files (*.gramps)"))
                filter_gramps.add_pattern("*.gramps")
                chooser.add_filter(filter_gramps)

                response = chooser.run()
                if response == Gtk.ResponseType.OK:
                    filename = chooser.get_filename()
                    chooser.destroy()

                    grizard = GedGrizard(vm.dbstate.db)
                    grizard.run_step("connect", gedcom_path=filename)
                    grizard.run_step("load")

                    compare_win = GrizardCompareWindow(
                        vm.uistate, vm.dbstate, grizard, parent=vm.window
                    )
                    compare_win.show()
                else:
                    chooser.destroy()
        except ImportError:
            # Grizard is not installed, skip gracefully
            LOG.debug("Grizard addon is not installed, skipping Grizard routing.")
