#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009       Gary Burton
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
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gui.views.treemodels import PeopleModel
from _BaseSelector import BaseSelector
import config

#-------------------------------------------------------------------------
#
# SelectEvent
#
#-------------------------------------------------------------------------
class SelectPerson(BaseSelector):

    def __init__(self, dbstate, uistate, track=[], title = None, filter = None,
                 skip=set(), show_search_bar = False):

        # SelectPerson may have a title passed to it which should be used
        # instead of the default defined for get_window_title()
        if title is not None:
            self.title = title

        BaseSelector.__init__(self, dbstate, uistate, track, filter,
                              skip, show_search_bar)

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.width_key = 'interface.person-sel-width'
        self.height_key = 'interface.person-sel-height'
        self.tree.connect('key-press-event', self._key_press)
        self.showall.connect('toggled',self.show_toggle)

    def get_window_title(self):
        return _("Select Person")
        
    def get_model_class(self):
        return PeopleModel

    def get_column_titles(self):
        return [
            (_('Name'),         250, BaseSelector.TEXT,   0),
            (_('ID'),            75, BaseSelector.TEXT,   1),
            (_('Gender'),        75, BaseSelector.TEXT,   2),
            (_('Birth Date'),   150, BaseSelector.MARKUP, 3),
            (_('Birth Place'),  150, BaseSelector.MARKUP, 4),
            (_('Death Date'),   150, BaseSelector.MARKUP, 5),
            (_('Death Place'),  150, BaseSelector.MARKUP, 6),
            (_('Spouse'),       150, BaseSelector.TEXT,   7),
            (_('Last Change'),  150, BaseSelector.TEXT,   8)
            ]

    def get_from_handle_func(self):
        return self.db.get_person_from_handle
        
    def get_handle_column(self):
        return PeopleModel.COLUMN_INT_ID

    def exact_search(self):
        """
        Returns a tuple indicating columns requiring an exact search
        """
        return (2,) # Gender ('female' contains the string 'male')

    def _on_row_activated(self, treeview, path, view_col):
        store, paths = self.selection.get_selected_rows()
        if paths and len(paths[0]) == 2 :
            self.window.response(gtk.RESPONSE_OK)

    def _key_press(self, obj, event):
        if not event.state or event.state  in (gtk.gdk.MOD2_MASK, ):
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                store, paths = self.selection.get_selected_rows()
                if paths and len(paths[0]) == 1 :
                    if self.tree.row_expanded(paths[0]):
                        self.tree.collapse_row(paths[0])
                    else:
                        self.tree.expand_row(paths[0], 0)
                    return True
        return False
