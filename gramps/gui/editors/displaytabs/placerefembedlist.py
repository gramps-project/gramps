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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import Place, PlaceRef
from gramps.gen.errors import WindowActiveError
from ...dialog import ErrorDialog
from ...ddtargets import DdTargets
from .placerefmodel import PlaceRefModel
from .embeddedlist import EmbeddedList, TEXT_COL
from ...selectors import SelectorFactory
from ...dbguielement import DbGUIElement


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class PlaceRefEmbedList(DbGUIElement, EmbeddedList):

    _HANDLE_COL = 4
    _DND_TYPE = DdTargets.PLACEREF
    _DND_EXTRA = DdTargets.PLACE_LINK

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('ID'),   0, 75, TEXT_COL, -1, None),
        (_('Name'), 1, 250, TEXT_COL, -1, None),
        (_('Type'), 2, 100, TEXT_COL, -1, None),
        (_('Date'), 3, 150, TEXT_COL, -1, None),
        ]

    def __init__(self, dbstate, uistate, track, data, handle, callback):
        self.data = data
        self.handle = handle
        self.callback = callback
        DbGUIElement.__init__(self, dbstate.db)
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Enclosed By'), PlaceRefModel,
                              share_button=True, move_buttons=True)

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        #note: place-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
            {'place-update': self.place_change,  # change to place we track
             'place-delete': self.place_delete,  # delete of place we track
             })
        self.callman.connect_all(keys=['place'])

    def place_change(self, *obj):
        """
        Callback method called when a tracked place changes (description
        changes...)
        """
        self.rebuild()

    def place_delete(self, hndls):
        """
        Callback method called when a tracked place is deleted.
        There are two possibilities:
        * a tracked non-workgroup place is deleted, just rebuilding the view
            will correct this.
        * a workgroup place is deleted. The place must be removed from the
            obj so that no inconsistent data is shown.
        """
        for handle in hndls:
            ref_list = [pref.ref for pref in self.data]
            indexlist = []
            last = -1
            while True:
                try:
                    last = ref_list.index(handle, last + 1)
                    indexlist.append(last)
                except ValueError:
                    break
            #remove the deleted workgroup places from the object
            for index in reversed(indexlist):
                del self.data[index]
        #now rebuild the display tab
        self.rebuild()

    def get_data(self):
        self.callman.register_handles(
            {'place': [pref.ref for pref in self.data]})
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2), (1, 3))

    def get_skip_list(self, handle):
        todo = [handle]
        skip = [handle]
        while todo:
            handle = todo.pop()
            for child in self.dbstate.db.find_backlink_handles(handle,
                                                               ['Place']):
                if child[1] not in skip:
                    todo.append(child[1])
                    skip.append(child[1])
        return skip

    def add_button_clicked(self, obj):
        ref = PlaceRef()
        place = Place()
        try:
            from .. import EditPlaceRef
            EditPlaceRef(self.dbstate, self.uistate, self.track,
                         place, ref, self.add_callback)
        except WindowActiveError:
            pass

    def add_callback(self, ref, place):
        ref.ref = place.handle
        data = self.get_data()
        data.append(ref)
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def share_button_clicked(self, obj):
        SelectPlace = SelectorFactory('Place')

        sel = SelectPlace(self.dbstate, self.uistate, self.track,
                          skip=self.get_skip_list(self.handle))
        place = sel.run()
        if place:
            ref = PlaceRef()
            try:
                from .. import EditPlaceRef
                EditPlaceRef(self.dbstate, self.uistate, self.track,
                             place, ref, self.add_callback)
            except WindowActiveError:
                pass

    def edit_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            place = self.dbstate.db.get_place_from_handle(ref.ref)
            try:
                from .. import EditPlaceRef
                EditPlaceRef(self.dbstate, self.uistate, self.track,
                             place, ref, self.edit_callback)
            except WindowActiveError:
                pass

    def edit_callback(self, ref, place):
        self.rebuild()

    def post_rebuild(self, prebuildpath):
        self.callback()

    def handle_extra_type(self, objtype, obj):
        if obj in self.get_skip_list(self.handle):
            ErrorDialog(_("Place cycle detected"),
                        _("The place you are adding is already enclosed by "
                          "this place"),
                        parent=self.uistate.window)
            return
        place = self.dbstate.db.get_place_from_handle(obj)
        placeref = PlaceRef()
        try:
            from .. import EditPlaceRef
            EditPlaceRef(self.dbstate, self.uistate, self.track,
                         place, placeref, self.add_callback)
        except WindowActiveError:
            pass
