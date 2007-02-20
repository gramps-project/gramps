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

from gettext import gettext as _

import gtk
import gobject

from TreeViews import PersonTreeView

from BasicUtils import NameDisplay

from _TreeFrameBase import TreeFrameBase

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    _('Spouse'),
    _('Last Change'),
    _('Cause of Death'),
    ]


class PersonTreeFrame(TreeFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5


    def __init__(self,dbstate):
	TreeFrameBase.__init__(self)

        self._dbstate = dbstate
        self._selection = None
        self._model = None
        self._data_filter = None

        self._tree = PersonTreeView(dbstate.db)
        self._tree.set_rules_hint(True)
        self._tree.set_headers_visible(True)

        self._tree.connect('row-activated',self._on_row_activated)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        scrollwindow.add(self._tree)

        self.add(scrollwindow)

        self.change_db(self._dbstate.db)

    def _on_row_activated(self,widget,path,col):
        """Expand / colapse row"""

        if self._tree.row_expanded(path):
            self._tree.collapse_row(path)
        else:
            self._tree.expand_row(path,False)

    def change_db(self,db):
        self.set_model()

    def set_model(self,data_filter=None):

        if data_filter is None:
            self._tree.get_selection().unselect_all()
            self._tree.clear_filter()
        else:
            self._tree.set_filter(data_filter)
            
        self._selection = self._tree.get_selection()

        # expand the first row so that the tree is a sensible size.
        self._tree.expand_row((0,),False)

    def get_selection(self):
        return self._selection
    
    def get_tree(self):
        return self._tree

if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonTreeFrame)

if __name__ == "__main__":

    w = ObjectSelectorWindow()
    w.show_all()
    w.connect("destroy", gtk.main_quit)

    gtk.main()
