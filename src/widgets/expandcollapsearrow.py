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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

import logging
_LOG = logging.getLogger(".widgets.expandcollapsearrow")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
HAND_CURSOR = gtk.gdk.Cursor(gtk.gdk.HAND2)

#-------------------------------------------------------------------------
#
# Module functions
#
#-------------------------------------------------------------------------
def realize_cb(widget):
    widget.window.set_cursor(HAND_CURSOR)

#-------------------------------------------------------------------------
#
# ExpandCollapseArrow class
#
#-------------------------------------------------------------------------
class ExpandCollapseArrow(gtk.EventBox):
    """
        Arrow to be used for expand/collapse of sections.
        Note: shadow does not work, we indicate action with realize_cb
    """
    def __init__(self, collapsed, onbuttonpress, pair):
        """
        Constructor for the ExpandCollapseArrow class.

        @param collapsed: True if arrow must be shown collapsed, 
                        False otherwise
        @type collapsed: bool
        @param onbuttonpress: The callback function for button press
        @type onbuttonpress:  callback
        @param pair: user param for onbuttonpress function
        """
        gtk.EventBox.__init__(self)
        self.tooltips = gtk.Tooltips()
        if collapsed :
            self.arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
            self.tooltips.set_tip(self, _("Expand this section"))
        else:
            self.arrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
            self.tooltips.set_tip(self, _("Collapse this section"))
        self.add(self.arrow)
        self.connect('button-press-event', onbuttonpress, pair)
        self.connect('realize', realize_cb)
