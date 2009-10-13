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

__all__ = ["LinkLabel", "EditLabel", "BasicLabel", "GenderLabel",
           "MarkupLabel", "DualMarkupLabel"]

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
import cgi

import logging
_LOG = logging.getLogger(".widgets.labels")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import Config

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
# LinkLabel class
#
#-------------------------------------------------------------------------
class LinkLabel(gtk.EventBox):

    def __init__(self, label, func, handle, decoration=None):
        if decoration is None:
            relation_display_theme = Config.get(Config.RELATION_DISPLAY_THEME)
            if relation_display_theme == "CLASSIC":
                decoration = 'underline="single"'
            elif relation_display_theme == "WEBPAGE":
                decoration = 'foreground="blue"'
            else:
                raise AttributeError("invalid relation-display-theme: '%s'" % relation_display_theme)

        gtk.EventBox.__init__(self)
        self.orig_text = cgi.escape(label[0])
        self.gender = label[1]
        self.decoration = decoration
        text = '<span %s>%s</span>' % (self.decoration, self.orig_text)

        if func:
            msg = _('Click to make the active person\n'
                    'Right click to display the edit menu')
            if not Config.get(Config.RELEDITBTN):
                msg += "\n" + _('Edit icons can be enabled in the Preferences dialog')

            self.set_tooltip_text(msg)
        
        self.label = gtk.Label(text)
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)

        hbox = gtk.HBox()
        hbox.pack_start(self.label, False, False, 0)
        if label[1]:
            hbox.pack_start(GenderLabel(label[1]), False, False, 0)
            hbox.set_spacing(4)
        self.add(hbox)

        if func:
            self.connect('button-press-event', func, handle)
            self.connect('enter-notify-event', self.enter_text, handle)
            self.connect('leave-notify-event', self.leave_text, handle)
            self.connect('realize', realize_cb)

    def set_padding(self, x, y):
        self.label.set_padding(x, y)
        
    def enter_text(self, obj, event, handle):
        relation_display_theme = Config.get(Config.RELATION_DISPLAY_THEME)
        if relation_display_theme == "CLASSIC":
            text = '<span foreground="blue" %s>%s</span>' % (self.decoration, self.orig_text)
        elif relation_display_theme == "WEBPAGE":
            text = '<span underline="single" %s>%s</span>' % (self.decoration, self.orig_text)
        else:
            raise AttributeError("invalid relation-display-theme: '%s'" % relation_display_theme)
        self.label.set_text(text)
        self.label.set_use_markup(True)

    def leave_text(self, obj, event, handle):
        text = '<span %s>%s</span>' % (self.decoration, self.orig_text)
        self.label.set_text(text)
        self.label.set_use_markup(True)

#-------------------------------------------------------------------------
#
# EditLabel class
#
#-------------------------------------------------------------------------
class EditLabel(gtk.HBox):
    def __init__(self, text):
        gtk.HBox.__init__(self)
        label = BasicLabel(text)
        self.pack_start(label, False)
        self.pack_start(gtk.image_new_from_stock(gtk.STOCK_EDIT, 
                                                 gtk.ICON_SIZE_MENU), False)
        self.set_spacing(4)
        self.show_all()

#-------------------------------------------------------------------------
#
# BasicLabel class
#
#-------------------------------------------------------------------------
class BasicLabel(gtk.Label):

    def __init__(self, text, ellipsize=pango.ELLIPSIZE_NONE):
        gtk.Label.__init__(self, text)
        self.set_alignment(0, 0.5)
        self.set_ellipsize(ellipsize)
        self.show()

#-------------------------------------------------------------------------
#
# GenderLabel class
#
#-------------------------------------------------------------------------
class GenderLabel(gtk.Label):

    def __init__(self, text):
        gtk.Label.__init__(self, text)
        self.set_alignment(0, 0.5)
        if os.sys.platform == "win32":
            pangoFont = pango.FontDescription('Arial')
            self.modify_font(pangoFont)
        self.show()

#-------------------------------------------------------------------------
#
# MarkupLabel class
#
#-------------------------------------------------------------------------
class MarkupLabel(gtk.Label):

    def __init__(self, text, x_align=0, y_align=0.5):
        gtk.Label.__init__(self, text)
        self.set_alignment(x_align, y_align)
        self.set_use_markup(True)
        self.show_all()

#-------------------------------------------------------------------------
#
# DualMarkupLabel class
#
#-------------------------------------------------------------------------
class DualMarkupLabel(gtk.HBox):

    def __init__(self, text, alt, x_align=0, y_align=0.5):
        gtk.HBox.__init__(self)
        label = gtk.Label(text)
        label.set_alignment(x_align, y_align)
        label.set_use_markup(True)

        self.pack_start(label, False, False, 0)
        b = GenderLabel(alt)
        b.set_use_markup(True)
        self.pack_start(b, False, False, 4)
        self.show()
