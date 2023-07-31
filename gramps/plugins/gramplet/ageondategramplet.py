# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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

"""
AgeOnDateGramplet computes the age for everyone thought to be alive
on a particular date.
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.datehandler import parser
from gramps.gui.plug.quick import run_quick_report_by_name
from gramps.gen.const import COLON, GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AgeOnDateGramplet class
#
# ------------------------------------------------------------------------
class AgeOnDateGramplet(Gramplet):
    """
    Gramplet that computes ages on a particular date for everyone
    thought to be alive.
    """

    def init(self):
        """
        Constructs the GUI, consisting of a message, an entry, and
        a Run button.
        """
        from gi.repository import Gtk

        # GUI setup:
        self.set_tooltip(_("Enter a date, click Run"))
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox = Gtk.Box()
        # label, entry
        description = Gtk.TextView()
        description.set_wrap_mode(Gtk.WrapMode.WORD)
        description.set_editable(False)
        buffer = description.get_buffer()
        buffer.set_text(
            _(
                "Enter a valid date (like YYYY-MM-DD) in the"
                " entry below and click Run. This will compute"
                " the ages for everyone in your Family Tree on"
                " that date. You can then sort by the age column,"
                " and double-click the row to view or edit."
            )
        )
        label = Gtk.Label()
        label.set_text(_("Date") + COLON)
        self.entry = Gtk.Entry()
        button = Gtk.Button(label=_("Run"))
        button.connect("clicked", self.run)
        ##self.filter =
        vbox.pack_start(hbox, False, True, 0)
        vbox.pack_start(button, False, True, 0)
        hbox.pack_start(label, False, True, 0)
        hbox.pack_start(self.entry, True, True, 0)
        vbox.pack_start(description, True, True, 0)
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(vbox)
        vbox.show_all()

    def run(self, obj):
        """
        Method that is run when you click the Run button.
        The date is retrieved from the entry box, parsed as a date,
        and then handed to the quick report.
        """
        text = self.entry.get_text()
        date = parser.parse(text)
        run_quick_report_by_name(self.gui.dbstate, self.gui.uistate, "ageondate", date)
