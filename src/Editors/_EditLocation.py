#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
#

# $Id: LocEdit.py 6051 2006-03-03 00:38:41Z dallingham $

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
from _EditSecondary import EditSecondary

from GrampsWidgets import *
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# LocationEditor class
#
#-------------------------------------------------------------------------
class EditLocation(EditSecondary):

    def __init__(self,dbstate,uistate,track,location,callback):
        EditSecondary.__init__(self, dbstate, uistate, track,
                               location, callback)

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "loc_edit","gramps")
        self.set_window(self.top.get_widget("loc_edit"),
                        self.top.get_widget('title'),
                        _('Location Editor'))

    def _setup_fields(self):
        self.city   = MonitoredEntry(
            self.top.get_widget("city"),
            self.obj.set_city,
            self.obj.get_city,
            self.db.readonly)
        
        self.state  = MonitoredEntry(
            self.top.get_widget("state"),
            self.obj.set_state,
            self.obj.get_state,
            self.db.readonly)
        
        self.postal = MonitoredEntry(
            self.top.get_widget("postal"),
            self.obj.set_postal_code,
            self.obj.get_postal_code,
            self.db.readonly)
        
        self.phone = MonitoredEntry(
            self.top.get_widget("phone"),
            self.obj.set_phone,
            self.obj.get_phone,
            self.db.readonly)
        
        self.parish = MonitoredEntry(
            self.top.get_widget("parish"),
            self.obj.set_parish,
            self.obj.get_parish,
            self.db.readonly)
        
        self.county = MonitoredEntry(
            self.top.get_widget("county"),
            self.obj.set_county,
            self.obj.get_county,
            self.db.readonly)
        
        self.country = MonitoredEntry(
            self.top.get_widget("country"),
            self.obj.set_country,
            self.obj.get_country,
            self.db.readonly)

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget('button119'))
        self.define_ok_button(self.top.get_widget('button118'),self.save)
        self.define_help_button(self.top.get_widget('button128'),'gramps-edit-complete')
        
    def save(self,*obj):
        if self.callback:
             self.callback(self.obj)
        self.close()

