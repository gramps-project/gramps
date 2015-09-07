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

"Separator classes used for Toolbar."

__all__ = ["SpringSeparatorAction", "SpringSeparatorToolItem"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.springseparator")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# SpringSeparatorToolItem class
#
#-------------------------------------------------------------------------
class SpringSeparatorToolItem(Gtk.SeparatorToolItem):
    """Custom separator toolitem.

    Its only purpose is to push following tool items to the right end
    of the toolbar.

    """
    __gtype_name__ = "SpringSeparatorToolItem"

    def __init__(self):
        Gtk.SeparatorToolItem.__init__(self)

        self.set_draw(False)
        self.set_expand(True)

#-------------------------------------------------------------------------
#
# SpringSeparatorAction class
#
#-------------------------------------------------------------------------
class SpringSeparatorAction(Gtk.Action):
    """Custom Action to hold a SpringSeparatorToolItem."""

    __gtype_name__ = "SpringSeparatorAction"

    def __init__(self, name, label, tooltip, stock_id):
        Gtk.Action.__init__(self, name=name, label=label,
                            tooltip=tooltip, stock_id=stock_id)

## TODO GTK3, How to connect these? Used in styledtexteditor
##SpringSeparatorToolItem.set_related_action(SpringSeparatorAction)
##deprecated: SpringSeparatorAction.set_tool_item_type(SpringSeparatorToolItem)
