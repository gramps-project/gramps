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

__all__ = ["ExpandCollapseArrow"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

import logging
_LOG = logging.getLogger(".widgets.expandcollapsearrow")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gramps.gen.constfunc import has_display

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
if has_display():
    HAND_CURSOR = Gdk.Cursor.new_for_display(Gdk.Display.get_default(),
                                             Gdk.CursorType.HAND2)

#-------------------------------------------------------------------------
#
# Module functions
#
#-------------------------------------------------------------------------
def realize_cb(widget):
    widget.get_window().set_cursor(HAND_CURSOR)

#-------------------------------------------------------------------------
#
# ExpandCollapseArrow class
#
#-------------------------------------------------------------------------
class ExpandCollapseArrow(Gtk.EventBox):
    """
    Arrow to be used for expand/collapse of sections.

    .. note:: shadow does not work, we indicate action with realize_cb
    """
    def __init__(self, collapsed, onbuttonpress, pair):
        """
        Constructor for the ExpandCollapseArrow class.

        :param collapsed: True if arrow must be shown collapsed,
                          False otherwise
        :type collapsed: bool
        :param onbuttonpress: The callback function for button press
        :type onbuttonpress: callback
        :param pair: user param for onbuttonpress function
        """
        Gtk.EventBox.__init__(self)
        if collapsed :
            self.arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.RIGHT,
                                              shadow_type=Gtk.ShadowType.OUT)
            self.set_tooltip_text(_("Expand this section"))
        else:
            self.arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.DOWN,
                                              shadow_type=Gtk.ShadowType.OUT)
            self.set_tooltip_text(_("Collapse this section"))
        self.add(self.arrow)
        self.connect('button-press-event', onbuttonpress, pair)
        self.connect('realize', realize_cb)
