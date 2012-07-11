#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Benny Malengier
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

"MenuToolButtonAction class."

__all__ = ["MenuToolButtonAction"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.menutoolbuttonaction")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# MenuToolButtonAction class
#
#-------------------------------------------------------------------------
class MenuToolButtonAction(Gtk.Action):
    """MenuToolButton action class.
    
    (A MenuToolButtonAction with menu item doesn't make any sense, 
     use for toolbar.)
    
    """
    __gtype_name__ = "MenuToolButtonAction"
    
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, 
                    None, #return value
                    ()), # arguments
    }    

    def __init__(self, name, label, tooltip, callback, arrowtooltip):
        """Create a new MenuToolButtonAction instance.
        
        @param name: the name of the action
        @type name: str
        @param tooltip: tooltip string
        @type tooltip: str
        
        """
        GObject.GObject.__init__(self, name=name, label=label, tooltip=tooltip,
                                 stock_id=None)
##TODO GTK3: following is deprecated, must be replaced by 
##        Gtk.MenuToolButton.set_related_action(MenuToolButtonAction) in calling class?
##        self.set_tool_item_type(Gtk.MenuToolButton)
        if callback:
            self.connect('activate', callback)
        self.arrowtooltip = arrowtooltip

