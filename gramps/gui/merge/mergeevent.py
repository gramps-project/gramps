#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Michiel D. Nauta
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
Provide merge capabilities for events.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_SECT3
from ..display import display_help
from ..managedwindow import ManagedWindow
from gramps.gen.datehandler import get_date
from gramps.gen.utils.db import get_participant_from_event
from gramps.gen.merge import MergeEventQuery

#-------------------------------------------------------------------------
#
# Gramps constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _('Merge_Events', 'manual')
_GLADE_FILE = 'mergeevent.glade'

#-------------------------------------------------------------------------
#
# MergeEvent
#
#-------------------------------------------------------------------------
class MergeEvent(ManagedWindow):
    """
    Displays a dialog box that allows the events to be combined into one.
    """
    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.ev1 = database.get_event_from_handle(handle1)
        self.ev2 = database.get_event_from_handle(handle2)

        self.define_glade('mergeevent', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget("event_title"),
                        _("Merge Events"))
        self.setup_configs('interface.merge-event', 500, 250)

        # Detailed selection widgets
        type1 = str(self.ev1.get_type())
        type2 = str(self.ev2.get_type())
        entry1 = self.get_widget("type1")
        entry2 = self.get_widget("type2")
        entry1.set_text(type1)
        entry2.set_text(type2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('type1', 'type2', 'type_btn1', 'type_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("date1")
        entry2 = self.get_widget("date2")
        entry1.set_text(get_date(self.ev1))
        entry2.set_text(get_date(self.ev2))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('date1', 'date2', 'date_btn1', 'date_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        place1 = self.ev1.get_place_handle()
        if place1:
            place1 = database.get_place_from_handle(place1)
        place2 = self.ev2.get_place_handle()
        if place2:
            place2 = database.get_place_from_handle(place2)
        place1 = place1.get_title() if place1 else ""
        place2 = place2.get_title() if place2 else ""
        entry1 = self.get_widget("place1")
        entry2 = self.get_widget("place2")
        entry1.set_text(place1)
        entry2.set_text(place2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('place1', 'place2', 'place_btn1', 'place_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("desc1")
        entry2 = self.get_widget("desc2")
        entry1.set_text(self.ev1.get_description())
        entry2.set_text(self.ev2.get_description())
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('desc1', 'desc2', 'desc_btn1', 'desc_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.ev1.get_gramps_id()
        gramps2 = self.ev2.get_gramps_id()
        entry1 = self.get_widget("gramps1")
        entry2 = self.get_widget("gramps2")
        entry1.set_text(gramps1)
        entry2.set_text(gramps2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('gramps1', 'gramps2', 'gramps_btn1',
                    'gramps_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        # Main window widgets that determine which handle survives
        ppant1 = get_participant_from_event(database, handle1)
        ppant2 = get_participant_from_event(database, handle2)
        rbutton1 = self.get_widget("handle_btn1")
        rbutton_label1 = self.get_widget("label_handle_btn1")
        rbutton_label2 = self.get_widget("label_handle_btn2")
        rbutton_label1.set_label("%s %s [%s]" % (type1, ppant1, gramps1))
        rbutton_label2.set_label("%s %s [%s]" % (type2, ppant2, gramps2))
        rbutton1.connect("toggled", self.on_handle1_toggled)

        self.connect_button("event_help", self.cb_help)
        self.connect_button("event_ok", self.cb_merge)
        self.connect_button("event_cancel", self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """Preferred event changes"""
        if obj.get_active():
            self.get_widget("type_btn1").set_active(True)
            self.get_widget("date_btn1").set_active(True)
            self.get_widget("place_btn1").set_active(True)
            self.get_widget("desc_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("type_btn2").set_active(True)
            self.get_widget("date_btn2").set_active(True)
            self.get_widget("place_btn2").set_active(True)
            self.get_widget("desc_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of the Gramps manual"""
        display_help(webpage = WIKI_HELP_PAGE, section = WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Perform the merge of the events when the merge button is clicked.
        """
        self.uistate.set_busy_cursor(True)
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.ev1
            titanic = self.ev2
        else:
            phoenix = self.ev2
            titanic = self.ev1

        if self.get_widget("type_btn1").get_active() ^ use_handle1:
            phoenix.set_type(titanic.get_type())
        if self.get_widget("date_btn1").get_active() ^ use_handle1:
            phoenix.set_date_object(titanic.get_date_object())
        if self.get_widget("place_btn1").get_active() ^ use_handle1:
            phoenix.set_place_handle(titanic.get_place_handle())
        if self.get_widget("desc_btn1").get_active() ^ use_handle1:
            phoenix.set_description(titanic.get_description())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())
        # cause is deprecated.

        query = MergeEventQuery(self.dbstate, phoenix, titanic)
        query.execute()
        # Add the selected handle to history so that when merge is complete,
        # phoenix is the selected row.
        self.uistate.set_active(phoenix.get_handle(), 'Event')
        self.uistate.set_busy_cursor(False)
        self.close()
