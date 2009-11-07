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
from TransUtils import sgettext as _
from QuickReports import run_quick_report_by_name, get_quick_report_list
from gen.plug  import (CATEGORY_QR_PERSON, CATEGORY_QR_FAMILY,
                         CATEGORY_QR_EVENT, CATEGORY_QR_SOURCE, 
                         CATEGORY_QR_MISC, CATEGORY_QR_PLACE, 
                         CATEGORY_QR_REPOSITORY)

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class QuickViewGramplet(Gramplet):
    def active_changed(self, handle):
        self.update()
        
    def main(self):
        qv_type = self.get_option(_("View Type"))
        quick_type = qv_type.get_value()
        qv_option = self.get_option(_("Quick Views"))
        quick_view = qv_option.get_value()
        if quick_type == CATEGORY_QR_PERSON:
            active = self.dbstate.get_active_person()
            if active:
                run_quick_report_by_name(self.gui.dbstate, 
                                         self.gui.uistate, 
                                         quick_view,
                                         active.handle,
                                         container=self.gui.textview)
        else:
            active_list = []
            for item in self.gui.uistate.viewmanager.pages:
                if (item.get_title() == _("Families") and
                    quick_type == CATEGORY_QR_FAMILY):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Events") and
                    quick_type == CATEGORY_QR_EVENT):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Sources") and
                    quick_type == CATEGORY_QR_SOURCE):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Places") and
                    quick_type == CATEGORY_QR_PLACE):
                    active_list = item.selected_handles()
                elif (item.get_title() == _("Repositories") and
                    quick_type == CATEGORY_QR_REPOSITORY):
                    active_list = item.selected_handles()
            if len(active_list) > 0:
                run_quick_report_by_name(self.gui.dbstate, 
                                         self.gui.uistate, 
                                         quick_view,
                                         active_list[0],
                                         container=self.gui.textview)

    def build_options(self):
        from gen.plug.menu import EnumeratedListOption
        # Add types:
        type_list = EnumeratedListOption(_("View Type"), CATEGORY_QR_PERSON)
        for item in [(CATEGORY_QR_PERSON, _("Person")), 
                     #TODO: add these once they have active change signals
                     #(CATEGORY_QR_FAMILY, _("Family")), 
                     #(CATEGORY_QR_EVENT, _("Event")), 
                     #(CATEGORY_QR_SOURCE, _("Source")), 
                     #(CATEGORY_QR_PLACE, _("Place")), 
                     #(CATEGORY_QR_REPOSITORY, _("Repository")),
                     ]:
            type_list.add_item(item[0], item[1])
        # Add particular lists:
        qv_list = get_quick_report_list(CATEGORY_QR_PERSON)
        list_option = EnumeratedListOption(_("Quick Views"), 
                                           qv_list[0].id)
        for pdata in qv_list:
            list_option.add_item(pdata.id, pdata.name)
        self.add_option(type_list)
        self.add_option(list_option)
        type_widget = self.get_option_widget(_("View Type"))
        type_widget.value_changed = self.rebuild_option_list

    def rebuild_option_list(self):
        qv_option = self.get_option(_("View Type"))
        list_option = self.get_option(_("Quick Views"))
        list_option.clear()
        qv_list = get_quick_report_list(qv_option.get_value())
        for pdata in qv_list:
            list_option.add_item(pdata.id, pdata.name)
