#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2008  The Gramps Developers
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
_LOG = logging.getLogger(".widgets.buttons")

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
# STOCK_INFO was added only in Gtk 2.8
try:
    INFO_ICON = gtk.STOCK_INFO
except AttributeError:
    INFO_ICON = gtk.STOCK_DIALOG_INFO

    
#-------------------------------------------------------------------------
#
# IconButton class
#
#-------------------------------------------------------------------------
class IconButton(gtk.Button):

    def __init__(self, func, handle, icon=gtk.STOCK_EDIT, 
                 size=gtk.ICON_SIZE_MENU):
        gtk.Button.__init__(self)
        image = gtk.Image()
        image.set_from_stock(icon, size)
        image.show()
        self.add(image)
        self.set_relief(gtk.RELIEF_NONE)
        self.show()

        if func:
            self.connect('button-press-event', func, handle)
            self.connect('key-press-event', func, handle)

#-------------------------------------------------------------------------
#
# WarnButton class
#
#-------------------------------------------------------------------------
class WarnButton(gtk.Button):
    def __init__(self):
        gtk.Button.__init__(self)

        image = gtk.Image()
        image.set_from_stock(INFO_ICON, gtk.ICON_SIZE_MENU)
        image.show()
        self.add(image)

        self.set_relief(gtk.RELIEF_NONE)
        self.show()
        self.func = None
        self.hide()

    def on_clicked(self, func):
        self.connect('button-press-event', self._button_press)
        self.func = func

    def _button_press(self, obj, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.func(obj)

#-------------------------------------------------------------------------
#
# SimpleButton class
#
#-------------------------------------------------------------------------
class SimpleButton(gtk.Button):

    def __init__(self, image, func):
        gtk.Button.__init__(self)
        self.set_relief(gtk.RELIEF_NONE)
        self.add(gtk.image_new_from_stock(image, gtk.ICON_SIZE_BUTTON))
        self.connect('clicked', func)
        self.show()
        
#-------------------------------------------------------------------------
#
# PrivacyButton class
#
#-------------------------------------------------------------------------
class PrivacyButton:

    def __init__(self, button, obj, readonly=False):
        self.button = button
        self.button.connect('toggled', self._on_toggle)
        self.tooltips = gtk.Tooltips()
        self.obj = obj
        self.set_active(obj.get_privacy())
        self.button.set_sensitive(not readonly)

    def set_sensitive(self, val):
        self.button.set_sensitive(val)

    def set_active(self, val):
        self.button.set_active(val)
        self._on_toggle(self.button)

    def get_active(self):
        return self.button.get_active()

    def _on_toggle(self, obj):
        child = obj.child
        if child:
            obj.remove(child)
        image = gtk.Image()
        if obj.get_active():
#            image.set_from_icon_name('stock_lock', gtk.ICON_SIZE_MENU)
            image.set_from_stock('gramps-lock', gtk.ICON_SIZE_MENU)
            self.tooltips.set_tip(obj, _('Record is private'))
            self.obj.set_privacy(True)
        else:
#            image.set_from_icon_name('stock_lock-open', gtk.ICON_SIZE_MENU)
            image.set_from_stock('gramps-unlock', gtk.ICON_SIZE_MENU)
            self.tooltips.set_tip(obj, _('Record is public'))
            self.obj.set_privacy(False)
        image.show()
        obj.add(image)
