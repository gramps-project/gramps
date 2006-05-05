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
import gobject
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import NameDisplay
import Utils

#-------------------------------------------------------------------------
#
# BackRefModel
#
#-------------------------------------------------------------------------
class BackRefModel(gtk.ListStore):

    def __init__(self, sref_list, db):
        gtk.ListStore.__init__(self, str, str, str, str)
        self.db = db
        self.sref_list = sref_list
        self.idle = 0
        self.count = 0
        self.idle = gobject.idle_add(self.load_model().next)

    def close(self):
        gobject.source_remove(self.idle)

    def load_model(self):
        self.count = 0
        for ref in self.sref_list:
            self.count += 1
            dtype = ref[0]
            if dtype == 'Person':
                p = self.db.get_person_from_handle(ref[1])
                gid = p.gramps_id
                handle = p.handle
                name = NameDisplay.displayer.display(p)
            elif dtype == 'Family':
                p = self.db.get_family_from_handle(ref[1])
                gid = p.gramps_id
                handle = p.handle
                name = Utils.family_name(p, self.db)
            elif dtype == 'Source':
                p = self.db.get_source_from_handle(ref[1])
                gid = p.gramps_id
                handle = p.handle
                name = p.get_title()
            elif dtype == 'Event':
                p = self.db.get_event_from_handle(ref[1])
                gid = p.gramps_id
                name = p.get_description()
                handle = p.handle
                if not name:
                    name = str(p.get_type())
            elif dtype == 'Place':
                p = self.db.get_place_from_handle(ref[1])
                name = p.get_title()
                gid = p.gramps_id
                handle = p.handle
            else:
                p = self.db.get_object_from_handle(ref[1])
                name = p.get_description()
                gid = p.gramps_id
                handle = p.handle

            self.append(row=[dtype, gid, name, handle])
            yield True
        yield False
