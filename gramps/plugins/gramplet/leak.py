#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Show uncollected objects in a window.
"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
import gc

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.dialog import InfoDialog
from gramps.gui.utils import is_right_click

#-------------------------------------------------------------------------
#
# Leak
#
#-------------------------------------------------------------------------
class Leak(Gramplet):
    """
    Shows uncollected objects.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)

        flags = gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_SAVEALL
        if hasattr(gc, "DEBUG_OBJECTS"):
            flags = flags | gc.DEBUG_OBJECTS
        gc.set_debug(flags)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top.set_border_width(6)

        self.label = Gtk.Label(halign=Gtk.Align.START)
        self.top.pack_start(self.label, False, False, 6)

        self.scroll = Gtk.ScrolledWindow()
        #add a listview to the scrollable
        self.list = Gtk.TreeView()
        self.list.set_headers_visible(True)
        self.list.connect('button-press-event', self._button_press)
        self.scroll.add(self.list)
        #make a model
        self.modeldata = []
        self.model = Gtk.ListStore(int, str)
        self.list.set_model(self.model)

        #set the columns
        self.renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_('Number'), self.renderer, text=0)
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.list.append_column(column)
        column = Gtk.TreeViewColumn(_('Uncollected object'), self.renderer,
                                    text=1)
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.list.append_column(column)
        self.selection = self.list.get_selection()
        self.top.pack_start(self.scroll, True, True, 6)

        bbox = Gtk.ButtonBox()
        apply_button = Gtk.Button(label=_("Refresh"))
        apply_button.connect('clicked', self.apply_clicked)
        bbox.pack_start(apply_button, False, False, 6)
        self.top.pack_start(bbox,  False, False, 6)

        self.top.show_all()

        return self.top

    def main(self):
        self.display()

    def _button_press(self, obj, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            self.referenced_in()
            return True
        elif is_right_click(event):
            self.refers_to()
            return True

    def referenced_in(self):
        model, iter = self.selection.get_selected()
        if iter is not None:
            count = model.get_value(iter, 0)
            referrers = gc.get_referrers(self.modeldata[count])
            text = ""
            for referrer in referrers:
                try:
                    text += str(referrer) + '\n'
                except ReferenceError:
                    pass
            InfoDialog(_('Referrers of %d') % count, text,
                        parent=self.uistate.window)

    def refers_to(self):
        model, iter = self.selection.get_selected()
        if iter is not None:
            count = model.get_value(iter, 0)
            referents = gc.get_referents(self.modeldata[count])
            text = ""
            for referent in referents:
                try:
                    text += str(referent) + '\n'
                except ReferenceError:
                    pass
            InfoDialog(_('%d refers to') % count, text,
                        parent=self.uistate.window)

    def display(self):
        try:
            from bsddb3.db import DBError
        except:
            class DBError(Exception):
                """
                Dummy.
                """
        gc.collect(2)
        self.model.clear()
        count = 0
        if len(gc.garbage):
            for each in gc.garbage:
                try:
                    self.modeldata.append(each)
                    self.model.append((count, str(each)))
                except DBError:
                    self.modeldata.append(each)
                    self.model.append((count, 'db.DB instance at %s' % id(each)))
                except ReferenceError:
                    pass
                count += 1
        self.label.set_text(_('Uncollected Objects: %s') % str(len(gc.garbage)))

    def apply_clicked(self, obj):
        self.display()
