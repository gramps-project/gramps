#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

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
import Errors
from GrampsWidgets import SimpleButton
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# BackRefList
#
#-------------------------------------------------------------------------
class BackRefList(EmbeddedList):

    _HANDLE_COL = 3

    _column_names = [
        (_('Type'), 0, 100),
        (_('ID'),  1,  75), 
        (_('Name'), 2, 250), 
        ]
    
    def __init__(self, dbstate, uistate, track, obj, refmodel, callback=None):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('References'), refmodel)
        self._callback = callback
        self.model.connect('row-inserted', self.update_label)

    def update_label(self, *obj):
        if self.model.count > 0:
            self._set_label()
        if self._callback and self.model.count > 1:
            self._callback()

    def right_click(self, obj, event):
        return

    def close(self):
        self.model.close()

    def is_empty(self):
        return self.model.count == 0

    def create_buttons(self, share=False):
        self.edit_btn = SimpleButton(gtk.STOCK_EDIT, self.edit_button_clicked)
        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.edit_btn, _('Edit reference'))

        vbox = gtk.VBox()
        vbox.set_spacing(6)
        vbox.pack_start(self.edit_btn, False)
        vbox.show_all()
        self.pack_start(vbox, False)

    def _selection_changed(self, obj=None):
        if self.get_selected():
            self.edit_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2))

    def find_node(self):
        (model, node) = self.selection.get_selected()
        try:
            return (model.get_value(node, 4), model.get_value(node, 3))
        except:
            return (None, None)
    
    def edit_button_clicked(self, obj):
        (reftype, ref) = self.find_node()
        if reftype == 'Person':
            try:
                from Editors import EditPerson
                
                person = self.dbstate.db.get_person_from_handle(ref)
                EditPerson(self.dbstate, self.uistate, [], person)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Family':
            try:
                from Editors import EditFamily
                
                family = self.dbstate.db.get_family_from_handle(ref)
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Source':
            try:
                from Editors import EditSource
                
                source = self.dbstate.db.get_source_from_handle(ref)
                EditSource(self.dbstate, self.uistate, [], source)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Place':
            try:
                from Editors import EditPlace
                
                place = self.dbstate.db.get_place_from_handle(ref)
                EditPlace(self.dbstate, self.uistate, [], place)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'MediaObject':
            try:
                from Editors import EditMedia
                
                obj = self.dbstate.db.get_object_from_handle(ref)
                EditMedia(self.dbstate, self.uistate, [], obj)
            except Errors.WindowActiveError:
                pass
        elif reftype == 'Event':
            try:
                from Editors import EditEvent
                
                event = self.dbstate.db.get_event_from_handle(ref)
                EditEvent(self.dbstate, self.uistate, [], event)
            except Errors.WindowActiveError:
                pass
