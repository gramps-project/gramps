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

# $Id$

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import DateHandler

#-------------------------------------------------------------------------
#
# LdsModel
#
#-------------------------------------------------------------------------
class LdsModel(gtk.ListStore):

    _HANDLE_COL = 5

    def __init__(self, lds_list, db):
        gtk.ListStore.__init__(self, str, str, str, str, str, object)

        import LdsUtils

        self.db = db
        for lds_ord in lds_list:
            self.append(row=[
                lds_ord.type2str(), 
                DateHandler.get_date(lds_ord), 
                lds_ord.status2str(), 
                LdsUtils.temple_to_abrev.get(lds_ord.get_temple(),
                                             _("unknown")), 
                self.column_place(lds_ord), 
                lds_ord, 
                ])

    def column_place(self, lds_ord):
        if lds_ord:
            place_handle = lds_ord.get_place_handle()
            if place_handle:
                return self.db.get_place_from_handle(place_handle).get_title()
        return u""
