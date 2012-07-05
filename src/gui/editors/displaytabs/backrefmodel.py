#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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
from gi.repository import GObject
from gi.repository import Gtk

from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
from gen.utils.db import family_name, get_participant_from_event

#-------------------------------------------------------------------------
#
# BackRefModel
#
#-------------------------------------------------------------------------
class BackRefModel(Gtk.ListStore):
    
    dispstr = _('%(part1)s - %(part2)s')

    def __init__(self, sref_list, db):
        Gtk.ListStore.__init__(self, str, str, str, str, str)
        self.db = db
        self.sref_list = sref_list
        self.count = 0
        self.idle = GObject.idle_add(self.load_model().next)

    def destroy(self):
        GObject.source_remove(self.idle)

    def load_model(self):
        """
        Objects can have very large backreferences. To avoid blocking the 
        interface up to the moment that the model is created, this method is 
        called via GObject.idle_add.
        WARNING: a consequence of above is that loading can still be happening
            while the GUI using this model is no longer used. Disconnect any
            methods before closing the GUI.
        """
        self.count = 0
        for ref in self.sref_list:
            self.count += 1
            dtype = ref[0]
            if dtype == 'Person':
                p = self.db.get_person_from_handle(ref[1])
                if not p:
                    continue
                gid = p.gramps_id
                handle = p.handle
                name = name_displayer.display(p)
            elif dtype == 'Family':
                p = self.db.get_family_from_handle(ref[1])
                if not p:
                    continue
                gid = p.gramps_id
                handle = p.handle
                name = family_name(p, self.db)
            elif dtype == 'Source':
                p = self.db.get_source_from_handle(ref[1])
                if not p:
                    continue
                gid = p.gramps_id
                handle = p.handle
                name = p.get_title()
            elif dtype == 'Citation':
                p = self.db.get_citation_from_handle(ref[1])
                if not p:
                    continue
                gid = p.gramps_id
                handle = p.handle
                name = p.get_page()
            elif dtype == 'Event':
                p = self.db.get_event_from_handle(ref[1])
                if not p:
                    continue
                gid = p.gramps_id
                handle = p.handle
                name = p.get_description()
                if name:
                    name = self.dispstr % {'part1': str(p.get_type()),
                                'part2': name}
                else:
                    name = str(p.get_type())
                part = get_participant_from_event(self.db, ref[1])
                if part :
                    name = self.dispstr % {'part1': name,
                                'part2': part}
            elif dtype == 'Place':
                p = self.db.get_place_from_handle(ref[1])
                if not p:
                    continue
                name = p.get_title()
                gid = p.gramps_id
                handle = p.handle
            elif dtype == 'Repository':
                p = self.db.get_repository_from_handle(ref[1])
                if not p:
                    continue
                name = p.get_name()
                gid = p.gramps_id
                handle = p.handle
            else:
                p = self.db.get_object_from_handle(ref[1])
                if not p:
                    continue
                name = p.get_description()
                gid = p.gramps_id
                handle = p.handle

            # dtype is the class name, i.e. is English
            # We need to use localized string in the model.
            # we also need to keep class names to get the object type,
            # but we don't need to show that in the view.
            self.append(row=[_(dtype), gid, name, handle, dtype])
            yield True
        yield False
