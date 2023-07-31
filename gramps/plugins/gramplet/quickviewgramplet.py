# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2011       Tim G L Lyons
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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.plug.quick import run_quick_report_by_name, get_quick_report_list
from gramps.gen.plug import (
    CATEGORY_QR_PERSON,
    CATEGORY_QR_FAMILY,
    CATEGORY_QR_EVENT,
    CATEGORY_QR_SOURCE,
    CATEGORY_QR_NOTE,
    CATEGORY_QR_PLACE,
    CATEGORY_QR_MEDIA,
    CATEGORY_QR_REPOSITORY,
    CATEGORY_QR_CITATION,
    CATEGORY_QR_SOURCE_OR_CITATION,
)
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# QuickViewGramplet class
#
# ------------------------------------------------------------------------
class QuickViewGramplet(Gramplet):
    def active_changed(self, handle):
        self.update()

    def db_changed(self):
        self.connect_signal("Person", self._active_changed)
        self.connect_signal("Family", self._active_changed)
        self.connect_signal("Event", self._active_changed)
        self.connect_signal("Place", self._active_changed)
        self.connect_signal("Source", self._active_changed)
        self.connect_signal("Citation", self._active_changed)
        self.connect_signal("Repository", self._active_changed)
        self.connect_signal("Media", self._active_changed)
        self.connect_signal("Note", self._active_changed)

    def clear_text(self):
        self.gui.textview.get_buffer().set_text("")

    def on_load(self):
        if len(self.gui.data) != 2:
            self.gui.data[:] = ["Person", None]

    def save_update_options(self, widget=None):
        qv_type = self.get_option(_("View Type"))
        quick_type = qv_type.get_value()
        qv_option = self.get_option(_("Quick Views"))
        quick_view = qv_option.get_value()
        self.gui.data[:] = [quick_type, quick_view]
        self.update()

    def main(self):
        quick_type = self.gui.data[0]
        qv_option = self.get_option(_("Quick Views"))
        quick_view = self.gui.data[1] or qv_option.get_value()
        try:
            active_handle = self.get_active(quick_type)
        except:
            active_handle = None
        if active_handle:
            docman = run_quick_report_by_name(
                self.gui.dbstate,
                self.gui.uistate,
                quick_view,
                active_handle,
                container=self.gui.textview,
            )
            if docman:
                self.set_has_data(docman.document.has_data)
        else:
            self.clear_text()
            self.set_has_data(False)

    def update_has_data(self):
        """
        Update the has_data indicator when gramplet is not visible.
        """
        self.main()

    def build_options(self):
        from gramps.gen.plug.menu import EnumeratedListOption

        # Add types:
        type_list = EnumeratedListOption(_("View Type"), self.gui.data[0])
        for item in [
            ("Person", _("Person")),
            ("Event", _("Event")),
            ("Family", _("Family")),
            ("Media", _("Media")),
            ("Note", _("Note")),
            ("Place", _("Place")),
            ("Repository", _("Repository")),
            ("Source", _("Source")),
            ("Citation", _("Citation")),
        ]:
            type_list.add_item(item[0], item[1])
        # Add particular lists:
        qv_list = get_quick_report_list(CATEGORY_QR_PERSON)
        if self.gui.data[1] is None:
            self.gui.data[1] = qv_list[0].id
        list_option = EnumeratedListOption(_("Quick Views"), self.gui.data[1])
        for pdata in qv_list:
            list_option.add_item(pdata.id, pdata.name)
        self.add_option(type_list)
        self.add_option(list_option)
        type_widget = self.get_option_widget(_("View Type"))
        type_widget.value_changed = self.rebuild_option_list
        self.rebuild_option_list()  # call for initial setting

    def rebuild_option_list(self):
        code_map = {
            "Person": CATEGORY_QR_PERSON,
            "Family": CATEGORY_QR_FAMILY,
            "Event": CATEGORY_QR_EVENT,
            "Source": CATEGORY_QR_SOURCE,
            "Citation": CATEGORY_QR_CITATION,
            "Source or Citation": CATEGORY_QR_SOURCE_OR_CITATION,
            "Place": CATEGORY_QR_PLACE,
            "Media": CATEGORY_QR_MEDIA,
            "Note": CATEGORY_QR_NOTE,
            "Repository": CATEGORY_QR_REPOSITORY,
        }
        qv_option = self.get_option(_("View Type"))
        list_option = self.get_option(_("Quick Views"))
        list_option.clear()
        qv_list = get_quick_report_list(code_map[qv_option.get_value()])
        for pdata in qv_list:
            list_option.add_item(pdata.id, pdata.name)
