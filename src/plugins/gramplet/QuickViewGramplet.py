# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# $Id$

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------


#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import Gramplet
from gen.ggettext import sgettext as _
from QuickReports import run_quick_report_by_name, get_quick_report_list
from gen.plug  import (CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY,
                         CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE, 
                         CATEGORY_QR_MISC, CATEGORY_QR_PLACE, CATEGORY_QR_MEDIA,
                         CATEGORY_QR_REPOSITORY)

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class QuickViewGramplet(Gramplet):
    def active_changed(self, handle):
        self.update()

    def post_init(self):
        self.connect_signal('Family', self._active_changed)
        self.connect_signal('Event', self._active_changed)
        self.connect_signal('Place', self._active_changed)
        self.connect_signal('Source', self._active_changed)
        self.connect_signal('Repository', self._active_changed)
        self.connect_signal('Media', self._active_changed)
        self.connect_signal('Note', self._active_changed)

    def on_load(self):
        if len(self.gui.data) != 2:
            self.gui.data[:] = ["Person", None]

    def on_save(self):
        qv_type = self.get_option(_("View Type"))
        quick_type = qv_type.get_value()
        qv_option = self.get_option(_("Quick Views"))
        quick_view = qv_option.get_value()
        self.gui.data[:] = [quick_type, quick_view]

    def main(self):
        qv_type = self.get_option(_("View Type"))
        quick_type = qv_type.get_value()
        qv_option = self.get_option(_("Quick Views"))
        quick_view = qv_option.get_value()
        try:
            active_handle = self.get_active(quick_type)
        except:
            active_handle = None
        if active_handle:
            run_quick_report_by_name(self.gui.dbstate, 
                                     self.gui.uistate, 
                                     quick_view,
                                     active_handle,
                                     container=self.gui.textview)

    def build_options(self):
        from gen.plug.menu import EnumeratedListOption
        # Add types:
        type_list = EnumeratedListOption(_("View Type"), self.gui.data[0])
        for item in [("Person", _("Person")), 
                     ("Event", _("Event")), 
                     ("Family", _("Family")), 
                     ("Media", _("Media")), 
                     ("Place", _("Place")), 
                     ("Repository", _("Repository")),
                     ("Source", _("Source")), 
                     ]:
            type_list.add_item(item[0], item[1])
        # Add particular lists:
        qv_list = get_quick_report_list(CATEGORY_QR_PERSON)
        if self.gui.data[1] is None:
            self.gui.data[1] = qv_list[0].id
        list_option = EnumeratedListOption(_("Quick Views"), 
                                           self.gui.data[1])
        for pdata in qv_list:
            list_option.add_item(pdata.id, pdata.name)
        self.add_option(type_list)
        self.add_option(list_option)
        type_widget = self.get_option_widget(_("View Type"))
        type_widget.value_changed = self.rebuild_option_list

    def rebuild_option_list(self):
        code_map = {"Person": CATEGORY_QR_PERSON, 
                    "Family": CATEGORY_QR_FAMILY,
                    "Event": CATEGORY_QR_EVENT, 
                    "Source": CATEGORY_QR_SOURCE, 
                    "Place": CATEGORY_QR_PLACE, 
                    "Media": CATEGORY_QR_MEDIA,
                    "Repository": CATEGORY_QR_REPOSITORY}
        qv_option = self.get_option(_("View Type"))
        list_option = self.get_option(_("Quick Views"))
        list_option.clear()
        qv_list = get_quick_report_list(code_map[qv_option.get_value()])
        for pdata in qv_list:
            list_option.add_item(pdata.id, pdata.name)
