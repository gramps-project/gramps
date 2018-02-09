#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2018        Nick Hall
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

__all__ = ["ShadeBox"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.shadebox")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# ShadeBox class
#
#-------------------------------------------------------------------------
class ShadeBox(Gtk.EventBox):
    """
    An EventBox with a shaded background.
    """
    def __init__(self, use_shade):
        Gtk.EventBox.__init__(self)
        self.use_shade = use_shade

    def do_draw(self, cr):
        if self.use_shade:
            tv = Gtk.TextView()
            tv_context = tv.get_style_context()
            width = self.get_allocated_width()
            height = self.get_allocated_height()
            Gtk.render_background(tv_context, cr, 0, 0, width, height)
        self.get_child().draw(cr)
