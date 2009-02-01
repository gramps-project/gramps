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
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from TransUtils import sgettext as _
from QuickReports import run_quick_report_by_name
import gen.lib

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class CalendarGramplet(Gramplet):
    def init(self):
        import gtk
        self.set_tooltip(_("Double-click a day for details"))
        self.gui.calendar = gtk.Calendar()
        self.gui.calendar.connect('day-selected-double-click', self.double_click)
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.calendar)
        self.gui.calendar.show()

    def double_click(self, obj):
        # bring up events on this day
        year, month, day = self.gui.calendar.get_date()
        date = gen.lib.Date()
        date.set_yr_mon_day(year, month + 1, day)
        run_quick_report_by_name(self.gui.dbstate, 
                                 self.gui.uistate, 
                                 'onthisday', 
                                 date)

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name="Calendar Gramplet", 
         tname=_("Calendar Gramplet"), 
         height=200,
         content = CalendarGramplet,
         title=_("Calendar"),
         )

