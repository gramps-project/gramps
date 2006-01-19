#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

import cgi

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

class LinkLabel(gtk.EventBox):

    def __init__(self,label,func,handle):
        gtk.EventBox.__init__(self)
        self.orig_text = cgi.escape(label[0])
        self.gender = label[1]
        text = '<span underline="single">%s</span>' % self.orig_text
        if label[1]:
            text += u' %s' % label[1]
        
        self.label = gtk.Label(text)
        self.label.set_use_markup(True)
        self.label.set_alignment(0,0.5)

        self.add(self.label)
        self.set_visible_window(False)

        self.connect('button-press-event',func,handle)
        self.connect('enter-notify-event',self.enter_text,handle)
        self.connect('leave-notify-event',self.leave_text,handle)
        
    def enter_text(self,obj,event,handle):
        text = '<span foreground="blue" underline="single">%s</span>' % self.orig_text
        if self.gender:
            text += u" %s" % self.gender
        self.label.set_text(text)
        self.label.set_use_markup(True)

    def leave_text(self,obj,event,handle):
        text = '<span underline="single">%s</span>' % self.orig_text
        if self.gender:
            text += u" %s" % self.gender
        self.label.set_text(text)
        self.label.set_use_markup(True)

class IconButton(gtk.EventBox):

    def __init__(self,func,handle,icon=gtk.STOCK_EDIT):
        gtk.EventBox.__init__(self)
        image = gtk.Image()
        image.set_from_stock(icon,gtk.ICON_SIZE_MENU)
        image.show()
        self.add(image)
        self.show()
        self.connect('button-press-event',func,handle)

class SimpleButton(gtk.Button):

    def __init__(self,image,func):
        gtk.Button.__init__(self)
        self.set_relief(gtk.RELIEF_NONE)
        self.add(gtk.image_new_from_stock(image,gtk.ICON_SIZE_BUTTON))
        self.connect('clicked',func)
        self.show()
        
class LinkBox(gtk.HBox):

    def __init__(self,link,button):
        gtk.HBox.__init__(self)
        self.set_spacing(6)
        self.pack_start(link,False)
        self.pack_start(button,False)
        self.show()

class EditLabel(gtk.HBox):
    def __init__(self,text):
        gtk.HBox.__init__(self)
        label = BasicLabel(text)
        self.pack_start(label,False)
        self.pack_start(gtk.image_new_from_stock(gtk.STOCK_EDIT,
                                                 gtk.ICON_SIZE_MENU),False)
        self.set_spacing(4)
#        self.tooltip = gtk.Tooltips()
#        self.tooltip.set_tip(label,_('Click in the cell to change the value'))
#        self.tooltip.enable()
        self.show_all()

class BasicLabel(gtk.Label):

    def __init__(self,text):
        gtk.Label.__init__(self,text)
        self.set_alignment(0,0.5)
        self.show()

class MarkupLabel(gtk.Label):

    def __init__(self,text):
        gtk.Label.__init__(self,text)
        self.set_alignment(0,0.5)
        self.set_use_markup(True)
        self.show()
        
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

class TypeCellRenderer(gtk.CellRendererCombo):

    def __init__(self,values):
        gtk.CellRendererCombo.__init__(self)

        model = gtk.ListStore(str,int)
        for key in values:
            model.append(row=[values[key],key])
        self.set_property('editable',True)
        self.set_property('model',model)
        self.set_property('text-column',0)

