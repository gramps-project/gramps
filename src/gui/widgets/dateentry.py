#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013        Nick Hall
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

# $Id$

__all__ = ["DateEntry"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.dateentry")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gui.widgets.monitoredwidgets import MonitoredDate
from gui.widgets.validatedmaskedentry import ValidatableMaskedEntry
from gen.lib.date import Date

#-------------------------------------------------------------------------
#
# DateEntry class
#
#-------------------------------------------------------------------------
class DateEntry(gtk.HBox):
    
    def __init__(self, uistate, track):
        gtk.HBox.__init__(self)
        self.entry = ValidatableMaskedEntry()
        self.pack_start(self.entry, True, True, 0)
        image = gtk.Image()
        image.set_from_stock('gramps-date-edit', gtk.ICON_SIZE_BUTTON)
        button = gtk.Button() 
        button.set_image(image)
        button.set_relief(gtk.RELIEF_NORMAL)
        self.pack_start(button, False, True, 0)
        self.date = Date()
        self.date_entry = MonitoredDate(self.entry, button, self.date, 
                                        uistate, track)
        self.show_all()

    def get_text(self):
        return self.entry.get_text()

    def set_text(self, text):
        self.entry.set_text(text)
