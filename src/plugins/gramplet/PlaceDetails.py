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

from gen.plug import Gramplet
from gui.widgets import LocationBox, Photo
from gen.ggettext import gettext as _
from PlaceUtils import conv_lat_lon
import Utils
import gtk
import pango

class PlaceDetails(Gramplet):
    """
    Displays details for a place.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = gtk.HBox()
        vbox = gtk.VBox()
        self.photo = Photo(190.0)
        self.title = gtk.Label()
        self.title.set_alignment(0, 0)
        self.title.modify_font(pango.FontDescription('sans bold 12'))
        vbox.pack_start(self.title, fill=True, expand=False, padding=7)
        table = gtk.Table(4, 2)
        self.location = LocationBox()
        label = gtk.Label(_('Location') + ':')
        label.set_alignment(1, 0)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=10)
        table.attach(self.location, 1, 2, 0, 1, xoptions=gtk.FILL)
        table.attach(gtk.Label(), 0, 1, 1, 2, xoptions=gtk.FILL)
        self.latitude = self.make_row(table, 2, _('Latitude'))
        self.longitude = self.make_row(table, 3, _('Longitude'))
        vbox.pack_start(table, fill=True, expand=False)
        self.top.pack_start(self.photo, fill=True, expand=False, padding=5)
        self.top.pack_start(vbox, fill=True, expand=False, padding=10)
        self.top.show_all()
        return self.top

    def make_row(self, table, row, title):
        """
        Make a row in a table.
        """
        label = gtk.Label(title + ':')
        label.set_alignment(1, 0)
        widget = gtk.Label()
        widget.set_alignment(0, 0)
        table.attach(label, 0, 1, row, row + 1, xoptions=gtk.FILL, xpadding=10)
        table.attach(widget, 1, 2, row, row + 1)
        return (label, widget)

    def db_changed(self):
        self.dbstate.db.connect('place-update', self.update)
        self.connect_signal('Place', self.update)
        self.update()

    def update_has_data(self): 
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        self.set_has_data(active_person is not None)

    def main(self):
        active_handle = self.get_active('Place')
        place = self.dbstate.db.get_place_from_handle(active_handle)
        self.top.hide()
        if place:
            self.display_place(place)
            self.set_has_data(True)
        else:
            self.display_empty()
            self.set_has_data(False)
        self.top.show()

    def display_place(self, place):
        """
        Display details of the active place.
        """
        self.load_place_image(place)
        self.title.set_text(place.get_title())
        self.location.set_location(place.get_main_location())
        lat, lon = conv_lat_lon(place.get_latitude(),
                                place.get_longitude(),
                                format='DEG')
        self.latitude[1].set_text('')
        self.longitude[1].set_text('')
        if lat:
            self.latitude[1].set_text(lat)
        if lon:
            self.longitude[1].set_text(lon)

    def display_empty(self):
        """
        Display empty details when no repository is selected.
        """
        self.photo.set_image(None)
        self.title.set_text('')
        self.location.set_location(None)
        self.latitude[1].set_text('')
        self.longitude[1].set_text('')

    def load_place_image(self, place):
        """
        Load the primary image if it exists.
        """
        media_list = place.get_media_list()
        if media_list:
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(object_handle)
            full_path = Utils.media_path_full(self.dbstate.db, obj.get_path())
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                self.photo.set_image(full_path, media_ref.get_rectangle())
            else:
                self.photo.set_image(None)
        else:
            self.photo.set_image(None)
