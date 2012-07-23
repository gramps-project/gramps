#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Zsolt Foldvari
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

__all__ = ["Statusbar"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".widgets.statusbar")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Statusbar class
#
#-------------------------------------------------------------------------
class Statusbar(Gtk.HBox):
    """Custom Statusbar with flexible number of "bars".
    
    Statusbar can have any number of fields included, each identified
    by it's own bar id. It has by default one field with id = 0. This
    defult field is used when no bar id is given in the relevant (push, pop, 
    etc.) methods, thus Statusbar behaves as a single Gtk.Statusbar.
    
    To add a new field use the "insert" method. Using the received bar id
    one can push, pop and remove messages to/from this newly inserted field.
    
    """
    __gtype_name__ = 'Statusbar'

    ##__gsignals__ = {
        ##'text-popped': , 
        ##'text-pushed': , 
    ##}

    __gproperties__ = {
        'has-resize-grip': (GObject.TYPE_BOOLEAN, 
                            'Resize grip', 
                            'Whether resize grip is visible', 
                            True, 
                            GObject.PARAM_READWRITE), 
    }
    
    def __init__(self):
        GObject.GObject.__init__(self)
        # initialize property values
        self.__has_resize_grip = True
        # create the main statusbar with id #0
        main_bar = Gtk.Statusbar()
        main_bar.show()
        self.pack_start(main_bar, True, True, 0)
        self._bars = {0: main_bar}

##TODO GTK3: statusbar no longer has resize grip methods, depracate this part
##           of Gramps Statusbar??
##        self._set_resize_grip()
##
##    # Virtual methods
##
##    def do_get_property(self, prop):
##        """Return the gproperty's value.
##        """
##        if prop.name == 'has-resize-grip':
##            return self.__has_resize_grip
##        else:
##            raise AttributeError, 'unknown property %s' % prop.name
##
##    def do_set_property(self, prop, value):
##        """Set the property of writable properties.
##        """
##        if prop.name == 'has-resize-grip':
##            self.__has_resize_grip = value
##            self._set_resize_grip()
##        else:
##            raise AttributeError, 'unknown or read only property %s' % prop.name
##
##    # Private
##    
##    def _set_resize_grip(self):
##        """Set the resize grip for the statusbar.
##        
##        Resize grip is disabled for all statusbars except the last one, 
##        which is set according to the "has-resize-grip" propery.
##        
##        """
##        for bar in self.get_children():
##            bar.set_has_resize_grip(False)
##        
##        bar.set_has_resize_grip(self.get_property('has-resize-grip'))

    def _get_next_id(self):
        """Get next unused statusbar id.
        """
        id = 1
        while id in self._bars:
            id = id + 1
            
        return id

    # Public API
    
    def insert(self, index=-1, min_width=None, ralign=False):
        """Insert a new statusbar.
        
        Create a new statusbar and insert it at the given index. Index starts
        from '0'. If index is negative the new statusbar is appended.
        The new bar_id is returned.
        
        """
        new_bar = Gtk.Statusbar()
        new_bar.show()
        self.pack_start(new_bar, True, True, 0)
        self.reorder_child(new_bar, index)
##TODO GTK3: statusbar no longer has resize grip methods, depracate this part
##           of Gramps Statusbar??
##        self._set_resize_grip()
        
        if ralign:
            frame = new_bar.get_children()[0]
            obj = frame.get_children()[0]      
            # obj is HBox
            obj = obj.get_children()[0]
##TODO GTK3: Check if following give expected alignment in statusbar
            obj.valign = Gtk.Align(value=Gtk.Align.CENTER)
            obj.halign = Gtk.Align(value=Gtk.Align.END)    
        
        new_bar_id = self._get_next_id()
        self._bars[new_bar_id] = new_bar
        
        return new_bar_id
    
    def get_context_id(self, context_description, bar_id=0):
        """Return a new or existing context identifier.
        
        The target statusbar is identified by bar_id created when statusbar
        was added.
        Existence of the bar_id is not checked as giving a wrong id is
        programming fault.
        
        """
        return self._bars[bar_id].get_context_id(context_description)

    def push(self, context_id, text, bar_id=0):
        """Push message onto a statusbar's stack.
        
        The target statusbar is identified by bar_id created when statusbar
        was added.
        Existence of the bar_id is not checked as giving a wrong id is
        programming fault.
        
        """
        # HACK: add an extra space so grip doesn't overlap
        return self._bars[bar_id].push(context_id, text + " ")

    def pop(self, context_id, bar_id=0):
        """Remove the top message from a statusbar's stack.
        
        The target statusbar is identified by bar_id created when statusbar
        was added.
        Existence of the bar_id is not checked as giving a wrong id is
        programming fault.
        
        """
        self._bars[bar_id].pop(context_id)

    def remove(self, context_id, message_id, bar_id=0):
        """Remove the message with the specified message_id.
        
        Remove the message with the specified message_id and context_id
        from the statusbar's stack, which is identified by bar_id.
        Existence of the bar_id is not checked as giving a wrong id is
        programming fault.
        
        """
        self._bars[bar_id].remove(context_id, message_id)
    
    def set_has_resize_grip(self, setting):
        """Mirror Gtk.Statusbar functionaliy.
        """
        self.set_property('has-resize-grip', setting)
    
    def get_has_resize_grip(self):
        """Mirror Gtk.Statusbar functionaliy.
        """
        return self.get_property('has-resize-grip')

def main(args):
    win = Gtk.Window()
    win.set_title('Statusbar test window')
    win.set_position(Gtk.WindowPosition.CENTER)
    def cb(window, event):
        Gtk.main_quit()
    win.connect('delete-event', cb)

    vbox = Gtk.VBox()
    win.add(vbox)

    statusbar = Statusbar()
    vbox.pack_end(statusbar, False, True, 0)
    
    statusbar.push(1, "My statusbar")
    
    my_statusbar = statusbar.insert()
    statusbar.push(1, "Testing width", my_statusbar)
    
    yet_another_statusbar = statusbar.insert()
    statusbar.push(1, "A short one", yet_another_statusbar)

    last_statusbar = statusbar.insert(ralign=True)
    statusbar.push(1, "The last statusbar", 
                   last_statusbar)
    
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    import sys
    # fall back to root logger for testing
    log = logging
    sys.exit(main(sys.argv))
