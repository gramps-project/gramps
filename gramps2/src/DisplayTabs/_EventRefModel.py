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
# EventRefModel
#
#-------------------------------------------------------------------------
class EventRefModel(gtk.ListStore):

    def __init__(self, event_list, db):
        gtk.ListStore.__init__(self, str, str, str, str, str, str, object)
        self.db = db
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            self.append(row=[
                str(event.get_type()), 
                event.get_description(), 
                event.get_gramps_id(), 
                self.column_date(event_ref), 
                self.column_place(event_ref), 
                self.column_role(event_ref), 
                event_ref
                ])

    def column_role(self, event_ref):
        return str(event_ref.get_role())

    def column_date(self, event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        return DateHandler.get_date(event)

    def column_place(self, event_ref):
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""
