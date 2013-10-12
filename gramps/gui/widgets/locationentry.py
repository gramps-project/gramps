# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Nick Hall
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
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.get_translation().gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
LOCATIONTYPES = [_('Country'), _('State'), _('County'), _('City'), 
                 _('Parish'), _('Locality'), _('Street')]
MAX_LEVELS = 7

#-------------------------------------------------------------------------
#
# LocationEntry class
#
#-------------------------------------------------------------------------
class LocationEntry(object):
    """
    Allows the hierarchical entry of a location.
    """
    def __init__(self, table, db, handle):
        
        self.db = db
        self.widgets = []
        self.labels = []
        self.types = [-1] * MAX_LEVELS
        self.signals = []

        table.set_col_spacings(10)
        
        for row in range(MAX_LEVELS):
            widget = self.create_widget(table, row)
            sig_id = widget.connect('changed', self.changed_cb, row)
            self.signals.append(sig_id)

        if handle:
            locs = []
            loc = db.get_location_from_handle(handle)
            while loc.parent != str(None):
                locs.append(loc)
                loc = db.get_location_from_handle(loc.parent)
            locs.append(loc)
            locs.reverse()
            
            for row, loc in enumerate(locs):
                self.populate_widget(row, loc.parent, loc.handle)
        else:
            self.populate_widget(0, None, None)
            
    def create_widget(self, table, row):
        model = Gtk.ListStore(str, str, int)
        widget = Gtk.ComboBox.new_with_model_and_entry(model)
        widget.set_entry_text_column(1)
        widget.set_sensitive(False)
        label = Gtk.Label()
        label.set_alignment(1, 0.5)
        label.show()
        table.attach(label, 0, 1, row, row+1, xoptions=Gtk.AttachOptions.FILL, yoptions=0)
        self.labels.append(label)
        table.attach(widget, 1, 2, row, row+1, yoptions=0)
        self.widgets.append(widget)
        return widget

    def populate_widget(self, row, parent_handle, default):
        widget = self.widgets[row]
        model = widget.get_model()
        widget.set_model(None)
        model.clear()
        active_iter = None
        children = self.db.find_location_child_handles(str(parent_handle))
        loc_type = None
        has_children = False
        for handle in children:
            child = self.db.get_location_from_handle(handle)
            iter_ = model.append((handle, child.name, child.get_type()))
            if handle == default:
                active_iter = iter_
                loc_type = child.get_type()
            has_children = True
        model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        widget.set_model(model)
        widget.get_child().set_text('')
        if active_iter is not None:
            widget.set_active_iter(active_iter)
        widget.set_sensitive(True)
        if has_children:
            if loc_type is None:
                loc_type = child.get_type()
            self.set_label(row, loc_type)
        else:
            if parent_handle:
                parent = self.db.get_location_from_handle(parent_handle)            
                if parent.get_type() < len(LOCATIONTYPES):
                    self.set_label(row, parent.get_type() + 1)
            else:
                self.set_label(row, 1)

    def set_label(self, row, loc_type):
        self.types[row] = loc_type
        label_text = '%s:' % LOCATIONTYPES[loc_type - 1]
        self.labels[row].set_label(label_text)

    def clear_widget(self, row):
        widget = self.widgets[row]
        widget.get_child().set_text('')
        model = widget.get_model()
        model.clear()

    def changed_cb(self, widget, row):
        self.disable_signals()
        if widget.get_active() == -1:
            # Text entry
            if row+1 < MAX_LEVELS:
                self.clear_widget(row+1)
                if self.types[row] < len(LOCATIONTYPES):
                    self.widgets[row+1].set_sensitive(True)
                    self.set_label(row + 1, self.types[row] + 1)
        else:
            # New selection
            model = widget.get_model()
            parent = model.get_value(widget.get_active_iter(), 0)
            loc_type = model.get_value(widget.get_active_iter(), 2)
            self.set_label(row, loc_type)
            if row+1 < MAX_LEVELS:
                if self.types[row] < len(LOCATIONTYPES):
                    self.populate_widget(row+1, parent, None)
                else:
                    self.clear_widget(row+1)
                    self.widgets[row+1].set_sensitive(False)
                    self.labels[row+1].set_label('')
                
        # Clear rows below the active row
        for row in range(row+2, MAX_LEVELS):
            widget = self.widgets[row]
            self.clear_widget(row)
            widget.set_sensitive(False)
            self.labels[row].set_label('')

        self.enable_signals()

    def enable_signals(self):
        for row in range(MAX_LEVELS):
            self.widgets[row].handler_unblock(self.signals[row])

    def disable_signals(self):
        for row in range(MAX_LEVELS):
            self.widgets[row].handler_block(self.signals[row])

    def get_result(self):
        handle = None
        new_locations = []
        for row in range(MAX_LEVELS):
            widget = self.widgets[row]
            if widget.get_active() == -1:
                # New name
                new_name = widget.get_child().get_text().strip()
                if new_name:
                    new_locations.append((self.types[row], new_name))
            else:
                # Existing location
                model = widget.get_model()
                handle = model.get_value(widget.get_active_iter(), 0)
        return (handle, new_locations)
