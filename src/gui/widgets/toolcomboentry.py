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

"ToolComboEntry class."

__all__ = ["ToolComboEntry"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.toolcomboentry")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
#import gobject
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gui.widgets.valuetoolitem import ValueToolItem
from gui.widgets.shortlistcomboentry import ShortlistComboEntry

#-------------------------------------------------------------------------
#
# ToolEntry class
#
#-------------------------------------------------------------------------
class ToolComboEntry(ValueToolItem):
    """Tool bar item containing a ShortlistComboEntry widget."""
    __gtype_name__ = "ToolComboEntry"
    
    def _create_widget(self, items, editable, shortlist=True, validator=None):
        self.set_border_width(2)
        self.set_homogeneous(False)
        self.set_expand(False)
        
        combo = ShortlistComboEntry(items, shortlist, validator)
        combo.set_focus_on_click(False)
        combo.set_entry_editable(editable)
        combo.show()
        self.add(combo)
        
        combo.connect('changed', self._on_widget_changed)

    def set_value(self, value):
        self.child.set_active_data(value)
    
    def get_value(self):
        return self.child.get_active_data()