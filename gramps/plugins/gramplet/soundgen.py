#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""Tools/Utilities/Generate SoundEx Codes"""

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
from gramps.gen.soundex import soundex
from gramps.gui.autocomp import fill_combo
from gramps.gen.plug import Gramplet
from gramps.gen.constfunc import cuni
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# SoundGen
#
#-------------------------------------------------------------------------
class SoundGen(Gramplet):
    """
    Generates SoundEx codes.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        grid = Gtk.Grid()
        grid.set_border_width(6)
        grid.set_row_spacing(6)
        grid.set_column_spacing(20)
        label1 = Gtk.Label(_("Name:"))
        label1.set_alignment(0, 0.5)
        grid.attach(label1, 0, 0, 1, 1)
        label2 = Gtk.Label(_("SoundEx code:"))
        label2.set_alignment(0, 0.5)
        grid.attach(label2, 0, 1, 1, 1)
        self.autocomp = Gtk.ComboBox.new_with_entry()
        grid.attach(self.autocomp, 1, 0, 1, 1)
        self.value = Gtk.Label()
        self.value.set_alignment(0, 0.5)
        grid.attach(self.value, 1, 1, 1, 1)
        self.name = self.autocomp.get_child()

        self.name.connect('changed', self.on_apply_clicked)

        grid.show_all()
        return grid

    def db_changed(self):
        if not self.dbstate.open:
            return

        names = []
        person = None
        for person in self.dbstate.db.iter_people():
            lastname = person.get_primary_name().get_surname()
            if lastname not in names:
                names.append(lastname)

        names.sort()

        fill_combo(self.autocomp, names)

        if person:
            n = person.get_primary_name().get_surname()
            self.name.set_text(n)
            try:
                se_text = soundex(n)
            except UnicodeEncodeError:
                se_text = soundex('')
            self.value.set_text(se_text)
        else:
            self.name.set_text("")

    def on_apply_clicked(self, obj):
        try:
            se_text = soundex(cuni(obj.get_text()))
        except UnicodeEncodeError:
            se_text = soundex('')
        self.value.set_text(se_text)
