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

"Widget classes used for Toolbar."

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.toolbarwidgets")

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
from widgets.multitypecomboentry import MultiTypeComboEntry

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
(COLUMN_ITEM,
 COLUMN_IS_SEP,) = range(2)

#-------------------------------------------------------------------------
#
# ComboToolItem class
#
#-------------------------------------------------------------------------
class ComboToolItem(gtk.ToolItem):
    
    __gtype_name__ = "ComboToolItem"
    
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, 
                    gobject.TYPE_NONE, #return value
                    ()), # arguments
    }    

    def __init__(self, model, editable, validator=None):
        gtk.ToolItem.__init__(self)
        
        self.set_border_width(2)
        self.set_homogeneous(False)
        self.set_expand(False)
        
        combo_entry = MultiTypeComboEntry(model, COLUMN_ITEM, validator)
        combo_entry.set_focus_on_click(False)
        combo_entry.set_entry_editable(editable)
        combo_entry.show()
        self.add(combo_entry)
        
        combo_entry.connect('changed', self._on_combo_changed)
    
    def _on_combo_changed(self, combo_entry):
        self.emit('changed')
        
    def set_active_iter(self, iter):
        self.child.set_active_iter(iter)
        
    def get_active_iter(self):
        return self.child.get_active_iter()
    
    def set_active_text(self, text):
        self.child.set_active_text(text)
    
    def get_active_text(self):
        return self.child.get_active_text()
    
#-------------------------------------------------------------------------
#
# ComboToolAction class
#
#-------------------------------------------------------------------------
class ComboToolAction(gtk.Action):
    
    __gtype_name__ = "ComboToolAction"
    
    def __init__(self, name, label, tooltip, stock_id, items,
                 default=None, sortable=True, editable=True,
                 validator=None):

        gtk.Action.__init__(self, name, label, tooltip, stock_id)
        
        # create the model and insert the items
        self.model = gtk.ListStore(gobject.TYPE_STRING,
                                   gobject.TYPE_BOOLEAN)
        for item in items:
            self.model.append((item, False))
            
        # sort the rows if allowed
        if sortable:
            self.model.set_sort_column_id(COLUMN_ITEM, gtk.SORT_ASCENDING)
            self.model.sort_column_changed()

        # set the first row (after sorting) as default if default was not set
        if (default is None) or (default not in items):
            self.default = self.model.get_value(self.model.get_iter_first(),
                                                COLUMN_ITEM)
        else:
            self.default = default

        self.set_active_value(self.default)
        
        # set the first row as separator
        self.model.set_value(self.model.get_iter_first(), COLUMN_IS_SEP, True)

        # remember initial parameters
        self.editable = editable
        self.validator = validator
        
    def do_create_tool_item(self):
        """Create a toolbar item widget that proxies for the given action.
        
        Override the default method, to be able to pass the required
        parameters to the proxy's constructor.
        
        @returns: a toolbar item connected to the action.
        @returntype: ComboToolItem
        
        """
        combo = ComboToolItem(self.model, self.editable, self.validator)
        self.connect_proxy(combo)
        return combo
        
    def connect_proxy(self, proxy):
        """Connect a widget to an action object as a proxy.
        
        @param proxy: widget to be connected
        @type proxy: gtk.Widget
        
        """
        if isinstance(proxy, ComboToolItem):
            # do this before hand, so that we don't call the "changed" handler
            proxy.set_active_iter(self.active_iter)
            proxy.connect('changed', self._on_proxy_changed)

        # if this is called the proxy will appear on the proxy list twice. why?
        #gtk.Action.connect_proxy(self, proxy)

    def _on_proxy_changed(self, proxy):
        """Signal handler.
        
        Called when any of the proxies is changed.
        
        """
        # blocking proxies when they are synchronized from the action
        if self._internal_change:
            return
        
        # get active value from the changed proxy
        if isinstance(proxy, ComboToolItem):
            iter = proxy.get_active_iter()

            if iter is not None:
                value = self.model.get_value(iter, COLUMN_ITEM)
            else:
                value = proxy.get_active_text()

            self.set_active_value(value)
            
            # emit the 'activate' signal
            self.activate()

    def set_active_value(self, value):
        """Set the active value of the action.
        
        Depending wheter the new value is in the model the active_iter
        attribute is set to position or set to None. The active_value
        attribute will contain the new value independently.
        
        Proxies are also updated accordingly.
        
        """
        # check first if the value is in the model
        iter = self.model.get_iter_first()
        while iter:
            if self.model.get_value(iter, COLUMN_ITEM) == value:
                break
            iter = self.model.iter_next(iter)

        # here iter either points to the model or is set to None
        self.active_value = value
        self.active_iter = iter
            
        # update the proxies with signalling loop cut
        self._internal_change = True
        
        for proxy in self.get_proxies():
            if isinstance(proxy, ComboToolItem):
                if self.active_iter is not None:
                    proxy.set_active_iter(self.active_iter)
                else:
                    proxy.set_active_text(self.active_value)
            else:
                _LOG.warning("Don't know how to activate %s widget" %
                             proxy.__class__)

        self._internal_change = False

    def get_active_value(self):
        return self.active_value
    
ComboToolAction.set_tool_item_type(ComboToolItem)

#-------------------------------------------------------------------------
#
# SpringSeparatorToolItem class
#
#-------------------------------------------------------------------------
class SpringSeparatorToolItem(gtk.SeparatorToolItem):
    """Custom separator toolitem.
    
    Its only purpose is to push following tool items to the right end
    of the toolbar.
    
    """
    __gtype_name__ = "SpringSeparatorToolItem"
    
    def __init__(self):
        gtk.SeparatorToolItem.__init__(self)
        
        self.set_draw(False)
        self.set_expand(True)
        
#-------------------------------------------------------------------------
#
# SpringSeparatorAction class
#
#-------------------------------------------------------------------------
class SpringSeparatorAction(gtk.Action):
    """Custom Action to hold a SpringSeparatorToolItem."""
    
    __gtype_name__ = "SpringSeparatorAction"
    
    def __init__(self, name, label, tooltip, stock_id):
        gtk.Action.__init__(self, name, label, tooltip, stock_id)

SpringSeparatorAction.set_tool_item_type(SpringSeparatorToolItem)

