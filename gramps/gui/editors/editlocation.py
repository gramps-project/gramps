#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2010       Nick Hall
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
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from editsecondary import EditSecondary
from ..glade import Glade
from gramps.gen.errors import ValidationError
from gramps.gen.utils.place import conv_lat_lon
from ..widgets import MonitoredEntry, LocationEntry
from gramps.gen.ggettext import gettext as _
from ..selectors import SelectorFactory
from ..dialog import ErrorDialog

SelectLocation = SelectorFactory('Location')

from gi.repository import Gtk

LOCATIONTYPES = [_('Country'), _('State'), _('County'), _('City'), 
                 _('Parish'), _('Locality'), _('Street')]

#-------------------------------------------------------------------------
#
# EditLocation class
#
#-------------------------------------------------------------------------
class EditLocation(EditSecondary):

    def __init__(self,dbstate,uistate,track,location,callback):
        EditSecondary.__init__(self, dbstate, uistate, track,
                               location, callback)

    def _local_init(self):
        self.width_key = 'interface.location-width'
        self.height_key = 'interface.location-height'
        self.top = Glade()
        self.set_window(self.top.toplevel, None, _('Location Editor'))

    def _setup_fields(self):
        self.name = MonitoredEntry(self.top.get_object("entry1"),
                                          self.obj.set_name,
                                          self.obj.get_name, 
                                          self.db.readonly)
                                          
        self.longitude = MonitoredEntry(
            self.top.get_object("lon_entry"),
            self.obj.set_longitude, self.obj.get_longitude,
            self.db.readonly)
        self.longitude.connect("validate", self._validate_coordinate, "lon")
        #force validation now with initial entry
        self.top.get_object("lon_entry").validate(force=True)

        self.latitude = MonitoredEntry(
            self.top.get_object("lat_entry"),
            self.obj.set_latitude, self.obj.get_latitude,
            self.db.readonly)
        self.latitude.connect("validate", self._validate_coordinate, "lat")
        #force validation now with initial entry
        self.top.get_object("lat_entry").validate(force=True)

        self.loc_type = self.top.get_object('combobox1')
        active_iter = None
        model = Gtk.ListStore(int, str)
        for key, value in enumerate(LOCATIONTYPES):
            _iter = model.append((key+1, value))
            if key+1 == self.obj.get_type():
                active_iter = _iter
        self.loc_type.set_model(model)
        cell = Gtk.CellRendererText()
        self.loc_type.pack_start(cell, True)
        self.loc_type.add_attribute(cell, 'text', 1)
        if active_iter is not None:
            self.loc_type.set_active_iter(active_iter)
        
        self.parent = self.top.get_object('label4')
        parent_loc = self.db.get_location_from_handle(self.obj.parent)
        if parent_loc:
            self.parent.set_text(parent_loc.get_name())
        else:
            self.parent.set_text(_('None'))

        button = self.top.get_object('button1')
        button.connect('clicked', self.select_parent)

        self.sibling_names = []
        for handle in self.db.find_location_child_handles(self.obj.parent):
            location = self.db.get_location_from_handle(handle)
            name = location.get_name()
            if name != self.obj.get_name():
                self.sibling_names.append(name)

    def _validate_coordinate(self, widget, text, typedeg):
        if (typedeg == 'lat') and not conv_lat_lon(text, "0", "ISO-D"):
            return ValidationError(_(u"Invalid latitude (syntax: 18\u00b09'") +
                                   _('48.21"S, -18.2412 or -18:9:48.21)'))
        elif (typedeg == 'lon') and not conv_lat_lon("0", text, "ISO-D"):
            return ValidationError(_(u"Invalid longitude (syntax: 18\u00b09'") +
                                   _('48.21"E, -18.2412 or -18:9:48.21)'))

    def select_parent(self, button):
        skip_list = []
        sel = SelectLocation(self.dbstate, self.uistate, self.track)
        parent = sel.run()
        if parent:
            self.parent.set_text(parent.get_name())
            self.obj.parent = parent.get_handle()

    def _connect_signals(self):
        self.ok_button = self.top.get_object('button118')
        self.define_cancel_button(self.top.get_object('button119'))
        self.define_ok_button(self.ok_button, self.save)
        self.define_help_button(self.top.get_object('button128'))
        
    def save(self,*obj):

        self.ok_button.set_sensitive(False)
        
        model = self.loc_type.get_model()
        loc_type = model.get_value(self.loc_type.get_active_iter(), 0)
        self.obj.set_type(loc_type)
        
        if self.obj.get_name().strip() == '':
            msg1 = _("Cannot save location. Name not entered.")
            msg2 = _("You must enter a name before saving.'") 
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return

        if self.obj.get_name() in self.sibling_names:
            msg1 = _("Cannot save location. Name already exists.")
            msg2 = _("You have attempted to use a name that is already "
                         "used at this level in the location hierarchy.'") 
            ErrorDialog(msg1, msg2)
            self.ok_button.set_sensitive(True)
            return

        if not self.obj.handle:
            with DbTxn(_("Add Location (%s)") % self.obj.get_name(),
                       self.db) as trans:
                self.db.add_location(self.obj, trans)
        else:
            orig = self.db.get_location_from_handle(self.obj.handle)
            if self.obj.parent != orig.parent:
                # Location has moved in the tree
                for handle in self.db.find_location_child_handles(self.obj.parent):
                    location = self.db.get_location_from_handle(handle)
                    name = location.get_name()
                    if name == self.obj.get_name():
                        with DbTxn(_("Merge Location (%s)") % self.obj.get_name(),
                                    self.db) as trans:
                            self.merge(location, self.obj, trans)
            
            if cmp(self.obj.serialize(), orig.serialize()):
                with DbTxn(_("Edit Location (%s)") % self.obj.get_name(),
                           self.db) as trans:
                    self.db.commit_location(self.obj, trans)

        if self.callback:
            self.callback(self.obj)
        self.close()

    def merge(self, location1, location2, trans):
        """
        Merge location2 into location1.
        """
        children = {}
        for handle in self.db.find_location_child_handles(location1.handle):
            child = self.db.get_location_from_handle(handle)
            children[child.get_name()] = child.handle

        for handle in self.db.find_location_child_handles(location2.handle):
            child2 = self.db.get_location_from_handle(handle)
            if child2.get_name() in children:
                handle = children[child2.get_name()]
                child1 = self.db.get_location_from_handle(handle)
                self.merge(child1, child2, trans)
            else:
                child2.parent = location1.handle
                self.db.commit_location(child2, trans)
                
        self.db.remove_location(location2.handle, trans)
