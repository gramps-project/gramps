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
from gen.ggettext import gettext as _
import logging
_LOG = logging.getLogger(".widgets.labels")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.constfunc import has_display, win
from gui.utils import rgb_to_hex

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
if has_display():
    HAND_CURSOR = Gdk.Cursor.new(Gdk.CursorType.HAND2)

#-------------------------------------------------------------------------
#
# Module functions
#
#-------------------------------------------------------------------------
def realize_cb(widget):
    widget.get_root_window().set_cursor(HAND_CURSOR)

#-------------------------------------------------------------------------
#
# LinkLabel class
#
#-------------------------------------------------------------------------
class LinkLabel(Gtk.EventBox):

    def __init__(self, label, func, handle, emph=False, theme="CLASSIC"):
        self.theme = theme
        self.emph = emph

        GObject.GObject.__init__(self)
        
        st_cont = self.get_style_context()
        col = st_cont.lookup_color('link_color')
        if col[0]:
            self.color = rgb_to_hex((col[1].red, col[1].green, col[1].blue))
        else:
            self.color = 'blue'

        if emph:
            #emphasize a link
            if theme == "CLASSIC":
                format = 'underline="single" weight="heavy" style="italic"'
            elif theme == "WEBPAGE":
                format = 'foreground="' + self.color + '" weight="heavy"'
            else:
                raise AttributeError("invalid theme: '%s'" % theme)
        elif emph is None:
            #emphasize, but not a link
            if theme == "CLASSIC":
                format = 'weight="heavy"'
            elif theme == "WEBPAGE":
                format = 'weight="heavy"'
            else:
                raise AttributeError("invalid theme: '%s'" % theme)
        else:
            #no emphasize, a link
            if theme == "CLASSIC":
                format = 'underline="single"'
            elif theme == "WEBPAGE":
                format = 'foreground="' + self.color + '"'
            else:
                raise AttributeError("invalid theme: '%s'" % theme)

        self.orig_text = cgi.escape(label[0])
        self.gender = label[1]
        self.decoration = format
        text = '<span %s>%s</span>' % (self.decoration, self.orig_text)

        if func:
            msg = _('Click to make this person active\n'
                    'Right click to display the edit menu\n'
                    'Click Edit icon (enable in configuration dialog) to edit')

            self.set_tooltip_text(msg)
        
        self.label = Gtk.Label(label=text)
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)

        hbox = Gtk.HBox()
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
        if self.emph:
            #emphasize a link
            if self.theme == "CLASSIC":
                format = 'foreground="' + self.color + '" underline="single" '\
                         'weight="heavy" style="italic"'
            elif self.theme == "WEBPAGE":
                format = 'underline="single" foreground="' + self.color + '" '\
                         'weight="heavy"'
            else:
                raise AttributeError("invalid theme: '%s'" % theme)
        elif self.emph is None:
            # no link, no change on enter_text
            if self.theme == "CLASSIC":
                format = 'weight="heavy"'
            elif self.theme == "WEBPAGE":
                format = 'weight="heavy"'
            else:
                raise AttributeError("invalid theme: '%s'" % theme)
        else:
            #no emphasize, a link
            if self.theme == "CLASSIC":
                format = 'foreground="' + self.color + '" underline="single"'
            elif self.theme == "WEBPAGE":
                format = 'underline="single" foreground="' + self.color + '"'
            else:
                raise AttributeError("invalid theme: '%s'" % theme)
        
        text = '<span %s>%s</span>' % (format, self.orig_text)
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
class EditLabel(Gtk.HBox):
    def __init__(self, text):
        GObject.GObject.__init__(self)
        label = BasicLabel(text)
        self.pack_start(label, False, True, 0)
        self.pack_start(Gtk.Image.new_from_stock(Gtk.STOCK_EDIT, 
                                                 Gtk.IconSize.MENU), False)
        self.set_spacing(4)
        self.show_all()

#-------------------------------------------------------------------------
#
# BasicLabel class
#
#-------------------------------------------------------------------------
class BasicLabel(Gtk.Label):

    def __init__(self, text, ellipsize=Pango.EllipsizeMode.NONE):
        GObject.GObject.__init__(self, label=text)
        self.set_alignment(0, 0.5)
        self.set_ellipsize(ellipsize)
        self.show()

#-------------------------------------------------------------------------
#
# GenderLabel class
#
#-------------------------------------------------------------------------
class GenderLabel(Gtk.Label):

    def __init__(self, text):
        GObject.GObject.__init__(self, label=text)
        self.set_alignment(0, 0.5)
        if win():
            pangoFont = Pango.FontDescription('Arial')
            self.modify_font(pangoFont)
        self.show()

#-------------------------------------------------------------------------
#
# MarkupLabel class
#
#-------------------------------------------------------------------------
class MarkupLabel(Gtk.Label):

    def __init__(self, text, x_align=0, y_align=0.5):
        GObject.GObject.__init__(self, label=text)
        self.set_alignment(x_align, y_align)
        self.set_use_markup(True)
        self.show_all()

#-------------------------------------------------------------------------
#
# DualMarkupLabel class
#
#-------------------------------------------------------------------------
class DualMarkupLabel(Gtk.HBox):

    def __init__(self, text, alt, x_align=0, y_align=0.5):
        GObject.GObject.__init__(self)
        label = Gtk.Label(label=text)
        label.set_alignment(x_align, y_align)
        label.set_use_markup(True)

        self.pack_start(label, False, False, 0)
        b = GenderLabel(alt)
        b.set_use_markup(True)
        self.pack_start(b, False, False, 4)
        self.show()
