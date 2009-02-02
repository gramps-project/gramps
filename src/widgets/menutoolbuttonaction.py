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

# $Id: menutoolbuttonaction 10763 2008-05-27 19:53:25Z zfoldvar $

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
import gobject
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# ValueAction class
#
#-------------------------------------------------------------------------
class MenuToolButtonAction(gtk.Action):
    """MenuToolButton action class.
    
    (A MenuToolButtonAction with menu item doesn't make any sense, 
     use for toolbar.)
    
    """
    __gtype_name__ = "MenuToolButtonAction"
    
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, 
                    gobject.TYPE_NONE, #return value
                    ()), # arguments
    }    

    def __init__(self, name, label, tooltip, callback, arrowtooltip):
        """Create a new MenuToolButtonAction instance.
        
        @param name: the name of the action
        @type name: str
        @param tooltip: tooltip string
        @type tooltip: str
        
        """
        gtk.Action.__init__(self, name, label, tooltip, None)
        
        self.set_tool_item_type(gtk.MenuToolButton)
        if callback:
            self.connect('activate', callback)
        self.arrowtooltip = arrowtooltip

