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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# $Id$

"""
AgeOnDateGramplet computes the age for everyone thought to be alive 
on a particular date.
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import Gramplet
from TransUtils import sgettext as _
import DateHandler
from QuickReports import run_quick_report_by_name

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
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
        import gtk
        # GUI setup:
        self.set_tooltip(_("Enter a date, click Run"))
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        # label, entry
        description = gtk.TextView()
        description.set_wrap_mode(gtk.WRAP_WORD)
        description.set_editable(False)
        buffer = description.get_buffer()
        buffer.set_text(_("Enter a date in the entry below and click Run."
                          " This will compute the ages for everyone in your"
                          " Family Tree on that date. You can then sort by"
                          " the age column, and double-click the row to view"
                          " or edit."))
        label = gtk.Label()
        label.set_text(_("Date") + ":")
        self.entry = gtk.Entry()
        button = gtk.Button(_("Run"))
        button.connect("clicked", self.run)
        ##self.filter = 
        hbox.pack_start(label, False)
        hbox.pack_start(self.entry, True)
        vbox.pack_start(description, True)
        vbox.pack_start(hbox, False)
        vbox.pack_start(button, False)
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(vbox)
        vbox.show_all()

    def post_init(self):
        self.disconnect("active-changed")

    def run(self, obj):
        """
        Method that is run when you click the Run button.
        The date is retrieved from the entry box, parsed as a date,
        and then handed to the quick report.
        """
        text = self.entry.get_text()
        date = DateHandler.parser.parse(text)
        run_quick_report_by_name(self.gui.dbstate, 
                                 self.gui.uistate, 
                                 'ageondate', 
                                 date)
