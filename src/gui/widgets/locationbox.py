# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
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
#

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# LocationBox class
#
#-------------------------------------------------------------------------
class LocationBox(gtk.VBox):
    """
    Displays a location.
    """
    def __init__(self):
        gtk.VBox.__init__(self)

        self.__street = self.__create_label()
        self.__locality = self.__create_label()
        self.__city = self.__create_label()
        self.__county = self.__create_label()
        self.__state = self.__create_label()
        self.__country = self.__create_label()
        self.__postal_code = self.__create_label()

    def set_location(self, location):
        """
        Set the location to be displayed.
        """
        if location is not None:
            self.__set_line(self.__street, location.get_street())
            self.__set_line(self.__locality, location.get_locality())
            self.__set_line(self.__city, location.get_city())
            self.__set_line(self.__county, location.get_county())
            self.__set_line(self.__state, location.get_state())
            self.__set_line(self.__country, location.get_country())
            self.__set_line(self.__postal_code, location.get_postal_code())
        else:
            self.__set_line(self.__street, '')
            self.__set_line(self.__locality, '')
            self.__set_line(self.__city, '')
            self.__set_line(self.__county, '')
            self.__set_line(self.__state, '')
            self.__set_line(self.__country, '')
            self.__set_line(self.__postal_code, '')

    def __create_label(self):
        """
        Create a label to display a single line of the location.
        """
        label = gtk.Label()
        label.set_alignment(0, 0)
        self.pack_start(label, False, False)
        return label
        
    def __set_line(self, label, value):
        """
        Display a single line of the location.
        """
        if value:
            label.set_text(value)
            label.show()
        else:
            label.hide()
