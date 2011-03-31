# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011     Rob G. Healey <robhealey1@gmail.com>
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
# $Id: MediaReferences.py 17002 2011-03-31 04:24:17Z robhealey1 $
#

from gen.plug import Gramplet
from ListModel import ListModel, NOSORT
from gen.ggettext import gettext as _

import Utils
import gtk
from gen.display.name import displayer as _nd
from DateHandler import displayer as _dd

class MediaReferences(Gramplet):
    """
    Displays the Media Back References for this media object...
    """
    def init(self):

        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()

        self.connect_signal('Media', self.update)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        top = gtk.TreeView()
        titles = [(_('Object'),    1, 100),
                  (_('Title'),     2, 250),
                  (_("Gramps ID"), 3, 90)]
        self.model = ListModel(top, titles)
        return top

    def db_changed(self):
        self.dbstate.db.connect('media-update', self.update)
        self.dbstate.db.connect("media-rebuild", self.update)
        self.update()

    def main(self):

        active_handle = self.get_active('Media')
        if not active_handle:
            return

        media = self.dbstate.db.get_object_from_handle(active_handle)
        if not media:
            return

        self.model.clear()
        self.__display_media_references(media)

    def __display_media_references(self, media):
        """
        Load the primary image if it exists.
        """
        db = self.dbstate.db

        handles = db.find_backlink_handles(media.get_handle(), 
                include_classes = ["Person", "Family", "Event", "Place", "Source"])

        for (classname, handle) in handles:
            obj_ = False
            title = False

            # Person link
            if classname == "Person":
                person = db.get_person_from_handle(handle)
                if person:
                    person_name = _nd.display(person)
                    gid = person.get_gramps_id()
                    self.model.add((classname, person_name, gid))

            # Family link
            elif classname == "Family":
                husband = False
                spouse  = False
                family = db.get_family_from_handle(handle)
                if family:
                    gid = family.get_gramps_id()

                    husband_handle = family.get_father_handle()
                    spouse_handle =  family.get_mother_handle()
                    husband = db.get_person_from_handle(husband_handle)
                    spouse  = db.get_person_from_handle(spouse_handle)
                    if husband:
                        husband_name = _nd.display(husband)
                    if spouse:
                        spouse_name = _nd.display(spouse)

                    if husband and spouse:
                        self.model.add((classname, husband_name + " + ", gid))
                        self.model.add(("", spouse_name, "", ""))

                    elif husband:
                        self.model.add((classname, husband_name, gid))

                    elif spouse:
                        self.model.add((classname, spouse_name, gid))
  
            # Event link
            elif classname == "Event":
                event = db.get_event_from_handle(handle)
                if event:
                    gid = event.get_gramps_id()
                    self.model.add((classname, str(event.get_type()), gid))

            # Place link
            elif classname == "Place":
                place = db.get_place_from_handle(handle)
                if place:
                    gid = place.get_gramps_id()
                    self.model.add((classname, place.get_title(), gid))

            # Source link
            elif classname == "Source":
                source = db.get_source_from_handle(handle)
                if source:
                    gid = source.get_gramps_id()
                    self.model.add((classname, source.get_title(), gid))
