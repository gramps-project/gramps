#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Nick Hall
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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import time
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ToolTips
import GrampsLocale

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# PlaceBaseModel
#
#-------------------------------------------------------------------------
class PlaceBaseModel(object):

    HANDLE_COL = 12

    def __init__(self, db):
        self.gen_cursor = db.get_place_cursor
        self.map = db.get_raw_place_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_parish,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_latitude,
            self.column_longitude,
            self.column_change,
            self.column_street,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_parish,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.sort_latitude,
            self.sort_longitude,
            self.sort_change,
            self.column_street,
            self.column_handle,
            ]

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self, data):
        return unicode(data[0])

    def column_name(self, data):
        return unicode(data[2])

    def __format_degrees(self, angle, sign_str):
        """
        Format a decimal as degrees, minutes and seconds.
        If the value is not a decimal leave it unformatted.
        """
        try:
            angle = float(angle)
        except ValueError:
            return angle

        if angle >= 0:
            sign = sign_str[0]
        else:
            sign = sign_str[1]
        seconds = abs(int(angle * 60 * 60))
        minutes = seconds / 60
        seconds %= 60
        degrees = minutes / 60
        minutes %= 60

        string = unicode(degrees) + u'\u00b0 ' + \
                 unicode(minutes) + u'\u2032 ' + \
                 unicode(seconds) + u'\u2033 ' + unicode(sign)

        return string
        
    def column_longitude(self, data):
        return self.__format_degrees(data[3], _('EW'))

    def column_latitude(self, data):
        return self.__format_degrees(data[4], _('NS'))

    def sort_longitude(self, data):
        return unicode(data[3])

    def sort_latitude(self, data):
        return unicode(data[4])

    def column_id(self, data):
        return unicode(data[1])

    def column_parish(self, data):
        try:
            return data[5][1]
        except:
            return u''

    def column_street(self, data):
        try:
            return data[5][0][0]
        except:
            return u''

    def column_city(self, data):
        try:
            return data[5][0][1]
        except:
            return u''
        
    def column_county(self, data):
        try:
            return data[5][0][2]
        except:
            return u''
    
    def column_state(self, data):
        try:
            return data[5][0][3]
        except:
            return u''

    def column_country(self, data):
        try:
            return data[5][0][4]
        except:
            return u''

    def column_postal_code(self, data):
        try:
            return data[5][0][5]
        except:
            return u''

    def sort_change(self, data):
        return "%012x" % data[11]
    
    def column_change(self, data, node):
        return unicode(time.strftime('%x %X',time.localtime(data[11])),
                            GrampsLocale.codeset)

    def column_tooltip(self, data):
        if const.USE_TIPS:
            try:
                t = ToolTips.TipFromFunction(
                    self.db, lambda:
                    self.db.get_place_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.", exc_info=True)
            return t
        else:
            return u''
