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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"ValueToolItem class."

__all__ = ["ValueToolItem"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.valuetoolitem")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk


#-------------------------------------------------------------------------
#
# ValueToolItem class
#
#-------------------------------------------------------------------------
class ValueToolItem(Gtk.ToolItem):
    """ValueToolItem is an abstract toolbar proxy for ValueAction.

    For each kind of widget a separete tool item proxy has to be
    subclassed from this ValueToolItem.

    """
    __gtype_name__ = "ValueToolItem"

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST,
                    None, #return value
                    ()), # arguments
    }

    def __init__(self, data_type, args):
        Gtk.ToolItem.__init__(self)

        self._data_type = data_type

        self._create_widget(*args)

    def _on_widget_changed(self, widget):
        self.emit('changed')

    def _create_widget(self, args):
        """Create the apropriate widget for the actual proxy."""
        raise NotImplementedError

    def set_value(self, value):
        """Set new value for the proxied widget.

        The method is responsible converting the data type between action and
        widget.

        """
        raise NotImplementedError

    def get_value(self):
        """Get value from the proxied widget.

        The method is responsible converting the data type between action and
        widget.

        """
        raise NotImplementedError
