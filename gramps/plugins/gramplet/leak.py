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
# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import weakref
import sys

# ------------------------------------------------------------------------
#
# GNOME/GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
import gc

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.dialog import InfoDialog
from gramps.gui.utils import is_right_click, ProgressMeter
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Leak
#
# -------------------------------------------------------------------------
class Leak(Gramplet):
    """
    Shows uncollected objects.
    """

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)

        flags = gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_SAVEALL
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
        # add a listview to the scrollable
        self.list = Gtk.TreeView()
        self.list.set_headers_visible(True)
        self.list.connect("button-press-event", self._button_press)
        self.scroll.add(self.list)
        # make a model
        self.model = Gtk.ListStore(int, str, str)
        self.list.set_model(self.model)

        # set the columns
        self.renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Number"), self.renderer, text=0)
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.list.append_column(column)
        column = Gtk.TreeViewColumn(_("Referrer"), self.renderer, text=1)
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.list.append_column(column)
        column = Gtk.TreeViewColumn(_("Uncollected object"), self.renderer, text=2)
        column.set_resizable(True)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.list.append_column(column)
        self.selection = self.list.get_selection()
        self.top.pack_start(self.scroll, True, True, 6)

        bbox = Gtk.ButtonBox()
        apply_button = Gtk.Button(label=_("Refresh"))
        apply_button.connect("clicked", self.apply_clicked)
        bbox.pack_start(apply_button, False, False, 6)
        self.top.pack_start(bbox, False, False, 6)

        self.top.show_all()

        return self.top

    def main(self):
        self.label.set_text(_("Press Refresh to see initial results"))
        self.model.clear()
        # self.display()    # We should only run this on demand

    def _button_press(self, obj, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            self.referenced_in()
            return True
        elif is_right_click(event):
            self.refers_to()
            return True

    def referenced_in(self):
        model, _iter = self.selection.get_selected()
        if _iter is not None:
            count = model.get_value(_iter, 0)
            gc.collect(2)
            referrers = gc.get_referrers(self.junk[count])
            text = ""
            for referrer in referrers:
                match = ""
                try:
                    if referrer is not self.junk:
                        match = "**** "
                        for indx, junk in enumerate(self.junk):
                            if referrer is junk:
                                match = str(indx) + ": "
                                break
                        match += str(referrer) + "\n"
                except ReferenceError:
                    match += "weakly-referenced object no longer exists %s" % type(
                        referrer
                    )
                except:
                    print(sys.exc_info())
                text += match
            InfoDialog(_("Referrers of %d") % count, text, parent=self.parent)

    def refers_to(self):
        model, _iter = self.selection.get_selected()
        if _iter is not None:
            count = model.get_value(_iter, 0)
            referents = gc.get_referents(self.junk[count])
            text = ""
            for referent in referents:
                match = ""
                try:
                    match = "****: "
                    for indx, junk in enumerate(self.junk):
                        if referent is junk:
                            match = str(indx) + ": "
                            break
                    match += str(referent) + "\n"
                except ReferenceError:
                    match += "%s weakly-referenced object no longer" " exists\n" % type(
                        referent
                    )
                except:
                    print(sys.exc_info())
                text += match
            InfoDialog(_("%d refers to") % count, text, parent=self.parent)

    def display(self):
        try:
            from bsddb3.db import DBError
        except:
            try:
                from berkeleydb.db import DBError
            except:

                class DBError(Exception):
                    """
                    Dummy.
                    """

        self.parent = self.top.get_toplevel()
        progress = ProgressMeter(
            _("Updating display..."), "", parent=self.parent, can_cancel=True
        )
        self.model.clear()
        self.junk = []
        gc.collect(2)
        self.junk = gc.garbage
        self.label.set_text(_("Uncollected Objects: %s") % str(len(self.junk)))
        progress.set_pass(_("Updating display..."), len(self.junk))
        for count in range(0, len(self.junk)):
            if progress.step():
                break
            try:
                refs = []
                referrers = gc.get_referrers(self.junk[count])
                for referrer in referrers:
                    try:
                        if referrer is not self.junk:
                            for indx in range(0, len(self.junk)):
                                if referrer is self.junk[indx]:
                                    refs.append(str(indx) + " ")
                                    break
                    except:
                        print(sys.exc_info())
                if len(refs) > 3:
                    ref = " ".join(refs[0:2]) + "..."
                else:
                    ref = " ".join(refs)
                try:
                    self.model.append((count, ref, str(self.junk[count])))
                except DBError:
                    self.model.append(
                        (count, ref, "db.DB instance at %s" % id(self.junk[count]))
                    )
                except ReferenceError:
                    self.model.append(
                        (
                            count,
                            ref,
                            "weakly-referenced object no longer exists %s"
                            % type(self.junk[count]),
                        )
                    )
                except TypeError:
                    self.model.append(
                        (
                            count,
                            ref,
                            "Object cannot be displayed %s" % type(self.junk[count]),
                        )
                    )
                except:
                    print(sys.exc_info())
            except ReferenceError:
                InfoDialog(
                    _("Reference Error"), "Refresh to correct", parent=self.parent
                )
        progress.close()

    def apply_clicked(self, obj):
        self.display()
