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
Provide a python evaluation window
"""
#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import sys
from io import StringIO
import traceback

#-------------------------------------------------------------------------
#
# Gtk modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# PythonEvaluation
#
#-------------------------------------------------------------------------
class PythonEvaluation(Gramplet):
    """
    Allows the user to evaluate python code.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top.set_border_width(6)

        self.ebuf = self.__add_text_view(_("Evaluation"))
        self.dbuf = self.__add_text_view(_("Output"))
        self.error = self.__add_text_view(_("Error"))

        bbox = Gtk.ButtonBox()
        apply_button = Gtk.Button(label=_("Apply"))
        apply_button.connect('clicked', self.apply_clicked)
        bbox.pack_start(apply_button, False, False, 6)
        clear_button = Gtk.Button(label=_("Clear"))
        clear_button.connect('clicked', self.clear_clicked)
        bbox.pack_start(clear_button, False, False, 6)
        self.top.pack_start(bbox, False, False, 6)

        self.top.show_all()

        return self.top

    def __add_text_view(self, name):
        """
        Add a text view to the interface.
        """
        label = Gtk.Label(halign=Gtk.Align.START)
        label.set_markup('<b>%s</b>' % name)
        self.top.pack_start(label, False, False, 6)
        swin = Gtk.ScrolledWindow()
        swin.set_shadow_type(Gtk.ShadowType.IN)
        tview = Gtk.TextView()
        swin.add(tview)
        self.top.pack_start(swin, True, True, 6)
        return tview.get_buffer()

    def apply_clicked(self, obj):
        text = str(self.ebuf.get_text(self.ebuf.get_start_iter(),
                                      self.ebuf.get_end_iter(), False))

        outtext = StringIO()
        errtext = StringIO()
        sys.stdout = outtext
        sys.stderr = errtext
        try:
            exec(text)
        except:
            traceback.print_exc()
        self.dbuf.set_text(outtext.getvalue())
        self.error.set_text(errtext.getvalue())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def clear_clicked(self, obj):
        self.dbuf.set_text("")
        self.ebuf.set_text("")
        self.error.set_text("")
