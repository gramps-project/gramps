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

from gen.lib import EventType, EventRoleType
from gen.plug import Gramplet
from gen.display.name import displayer as name_displayer
from gen.ggettext import gettext as _
import DateHandler
import Utils
import gtk
import pango

class PersonDetails(Gramplet):
    """
    Displays details for a person.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.gui.tooltip = ''
        self.load_obj = None
        self.load_rect = None
        top = gtk.HBox()
        vbox = gtk.VBox()
        self.obj_photo = gtk.Image()
        self.name = gtk.Label()
        self.name.set_alignment(0, 0)
        self.name.modify_font(pango.FontDescription('sans bold 12'))
        vbox.pack_start(self.name, fill=True, expand=False, padding=10)
        table = gtk.Table(2, 2)
        self.father = self.make_row(table, 0, _('Father'))
        self.mother = self.make_row(table, 1, _('Mother'))
        vbox.pack_start(table, fill=True, expand=False, padding=5)
        table = gtk.Table(4, 2)
        self.birth = self.make_row(table, 0, _('Birth'))
        self.baptism = self.make_row(table, 1, _('Baptism'))
        self.death = self.make_row(table, 2, _('Death'))
        self.burial = self.make_row(table, 3, _('Burial'))
        vbox.pack_start(table, fill=True, expand=False, padding=5)
        table = gtk.Table(1, 2)
        self.occupation = self.make_row(table, 0, _('Occupation'))
        vbox.pack_start(table, fill=True, expand=False, padding=5)
        vbox.show_all()
        top.pack_start(self.obj_photo, fill=True, expand=False, padding=5)
        top.pack_start(vbox, fill=True, expand=True, padding=10)
        return top

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
        self.dbstate.db.connect('person-update', self.update)
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self): # return false finishes
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        if not active_person:
            return

        self.load_person_image(active_person)
        self.name.set_text(name_displayer.display(active_person))
        self.display_parents(active_person)
        self.display_type(active_person, self.birth, EventType.BIRTH)
        self.display_type(active_person, self.baptism, EventType.BAPTISM)
        self.display_type(active_person, self.death, EventType.DEATH)
        self.display_type(active_person, self.burial, EventType.BURIAL)
        occupation_text = self.get_attribute(active_person, 'Occupation')
        self.occupation[1].set_text(occupation_text)

    def display_parents(self, active_person):
        """
        Display the parents of the active person.
        """
        family_handle = active_person.get_main_parents_family_handle()
        if family_handle:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            handle = family.get_father_handle()
            if handle:
                father = self.dbstate.db.get_person_from_handle(handle)
                self.father[1].set_text(name_displayer.display(father))
            else:
                self.father[1].set_text(_('Unknown'))
            handle = family.get_mother_handle()
            if handle:
                mother = self.dbstate.db.get_person_from_handle(handle)
                self.mother[1].set_text(name_displayer.display(mother))
            else:
                self.mother[1].set_text(_('Unknown'))
        else:
                self.father[1].set_text(_('Unknown'))
                self.mother[1].set_text(_('Unknown'))            

    def get_attribute(self, person, attr_key):
        """
        Return an attribute with the given key.
        """
        for attr in person.get_attribute_list():
            if attr.get_type() == attr_key:
                    return attr.get_value()
        return _('Unknown')

    def display_type(self, active_person, widget, event_type):
        """
        Display an event type row.
        """
        event = self.get_event(active_person, event_type)
        if event:
            widget[1].set_text(self.format_event(event))
            widget[0].show()
            widget[1].show()
        else:
            widget[1].set_text('')
            widget[0].hide()
            widget[1].hide()

    def get_event(self, person, event_type):
        """
        Return an event of the given type.
        """
        for event_ref in person.get_event_ref_list():
            if int(event_ref.get_role()) == EventRoleType.PRIMARY:
                event = self.dbstate.db.get_event_from_handle(event_ref.ref)
                if int(event.get_type()) == event_type:
                    return event
        return None

    def format_event(self, event):
        """
        Format the event for display.
        """
        date = DateHandler.get_date(event)
        handle = event.get_place_handle()
        if handle:
            place = self.dbstate.db.get_place_from_handle(handle).get_title()
            retval = _('%s - %s.') % (date, place)
        else:
            retval = _('%s.') % date
        return retval
        
    def load_person_image(self, person):
        """
        Load the primary image if it exists.
        """
        media_list = person.get_media_list()
        if media_list:
            photo = media_list[0]
            object_handle = photo.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(object_handle)
            full_path = Utils.media_path_full(self.dbstate.db, obj.get_path())
            #reload if different media, or different rectangle
            if self.load_obj != full_path or \
                    self.load_rect != photo.get_rectangle():
                mime_type = obj.get_mime_type()
                if mime_type and mime_type.startswith("image"):
                    self.load_photo(full_path, photo.get_rectangle())
                else:
                    self.load_photo(None)
        else:
            self.load_photo(None)

    def load_photo(self, path, rectangle=None):
        """
        Load, scale and display the person's main photo from the path.
        """
        self.load_obj = path
        self.load_rect = rectangle
        if path is None:
            self.obj_photo.hide()
        else:
            try:
                i = gtk.gdk.pixbuf_new_from_file(path)
                width = i.get_width()
                height = i.get_height()

                if rectangle is not None:
                    upper_x = min(rectangle[0], rectangle[2])/100.
                    lower_x = max(rectangle[0], rectangle[2])/100.
                    upper_y = min(rectangle[1], rectangle[3])/100.
                    lower_y = max(rectangle[1], rectangle[3])/100.
                    sub_x = int(upper_x * width)
                    sub_y = int(upper_y * height)
                    sub_width = int((lower_x - upper_x) * width)
                    sub_height = int((lower_y - upper_y) * height)
                    if sub_width > 0 and sub_height > 0:
                        i = i.subpixbuf(sub_x, sub_y, sub_width, sub_height)

                ratio = float(max(i.get_height(), i.get_width()))
                scale = float(190.0)/ratio
                x = int(scale*(i.get_width()))
                y = int(scale*(i.get_height()))
                i = i.scale_simple(x, y, gtk.gdk.INTERP_BILINEAR)
                self.obj_photo.set_from_pixbuf(i)
                self.obj_photo.show()
            except:
                self.obj_photo.hide()
