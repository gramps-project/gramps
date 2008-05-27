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

__all__ = ["IntEdit", "TypeCellRenderer"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".widgets.unused")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

#-------------------------------------------------------------------------
#
# IntEdit class
#
#-------------------------------------------------------------------------
# FIXME isn't used anywhere
class IntEdit(gtk.Entry):
    """An gtk.Edit widget that only allows integers."""
    
    def __init__(self):
        gtk.Entry.__init__(self)

        self._signal = self.connect("insert_text", self.insert_cb)

    def insert_cb(self, widget, text, length, *args):        
        # if you don't do this, garbage comes in with text
        text = text[:length]
        pos = widget.get_position()
        # stop default emission
        widget.emit_stop_by_name("insert_text")
        gobject.idle_add(self.insert, widget, text, pos)

    def insert(self, widget, text, pos):
        if len(text) > 0 and text.isdigit():            
            # the next three lines set up the text. this is done because we
            # can't use insert_text(): it always inserts at position zero.
            orig_text = widget.get_text()            
            new_text = orig_text[:pos] + text + orig_text[pos:]
            # avoid recursive calls triggered by set_text
            widget.handler_block(self._signal)
            # replace the text with some new text
            widget.set_text(new_text)
            widget.handler_unblock(self._signal)
            # set the correct position in the widget
            widget.set_position(pos + len(text))

#-------------------------------------------------------------------------
#
# TypeCellRenderer class
#
#-------------------------------------------------------------------------
# FIXME isn't used anywhere, though it is mentioned in _EditFamily.py
class TypeCellRenderer(gtk.CellRendererCombo):

    def __init__(self, values):
        gtk.CellRendererCombo.__init__(self)

        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        for key in values:
            model.append(row=[values[key], key])
        self.set_property('editable', True)
        self.set_property('model', model)
        self.set_property('text-column', 0)

