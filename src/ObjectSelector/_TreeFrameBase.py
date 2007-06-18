
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

import gtk

class TreeFrameBase(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    def __init__(self):
        gtk.Frame.__init__(self)

    def set_model(self,data_filter=None):
        raise NotImplementedError("Subclasses of TreeFrameBase must implement set_model")

    def get_selection(self):
        raise NotImplementedError("Subclasses of TreeFrameBase must implement get_selection")
    
    def get_tree(self):
        raise NotImplementedError("Subclasses of TreeFrameBase must implement get_tree")

