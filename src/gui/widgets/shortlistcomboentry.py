#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
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

"ShortlistComboEntry class."

__all__ = ["ShortlistComboEntry"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.shortlistcomboentry")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gui.widgets.validatedcomboentry import ValidatedComboEntry

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_GTYPE = {
    str: gobject.TYPE_STRING,
    unicode: gobject.TYPE_STRING,
    int: gobject.TYPE_INT,
    long: gobject.TYPE_INT64,
    float: gobject.TYPE_FLOAT,
}

(COLUMN_ITEM,
 COLUMN_IS_SEP,) = range(2)

#-------------------------------------------------------------------------
#
# ShortlistComboEntry class
#
#-------------------------------------------------------------------------
class ShortlistComboEntry(ValidatedComboEntry):
    """A ComboboxEntry class with optional shortlist.
    """
    __gtype_name__ = "ShortlistComboEntry"
    
    def __init__(self, items, shortlist=True, validator=None):
        if not items:
            raise ValueError
        
        data_type = items[0].__class__
        gtype = _GTYPE.get(data_type, gobject.TYPE_PYOBJECT)
        
        # create the model and insert the items
        model = gtk.ListStore(gtype, gobject.TYPE_BOOLEAN)
        for item in items:
            model.append((item, False))
            
        ValidatedComboEntry.__init__(self, data_type, model,
                                     COLUMN_ITEM, validator)
        if shortlist:
            self._shortlist = []
            self.connect("changed", self._on_combobox_changed)
            
        self.set_row_separator_func(self._is_row_separator)
            
    def _on_combobox_changed(self, combobox):
        if self._internal_change:
            return
        
        if self.get_active_iter():
            model = self.get_model()

            # if first item on shortlist insert a separator row
            if not self._shortlist:
                model.prepend((None, True))
            
            # remove the existing shortlist from the model
            iter = model.get_iter_first()
            for n in range(len(self._shortlist)):
                model.remove(iter)

            # update shortlist
            if self._active_data in self._shortlist:
                self._shortlist.remove(self._active_data)
            self._shortlist.append(self._active_data)
            self._shortlist = self._shortlist[-5:]
            
            # prepend shortlist to model
            for data in self._shortlist:
                model.prepend((data, False))

    def _is_row_separator(self, model, iter):
        return model.get_value(iter, COLUMN_IS_SEP)
