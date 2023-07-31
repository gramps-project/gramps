#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
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
Provide merge capabilities for places.
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.const import URL_MANUAL_SECT3
from ..display import display_help
from ..managedwindow import ManagedWindow
from gramps.gen.merge import MergePlaceQuery
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.config import config

# -------------------------------------------------------------------------
#
# Gramps constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _("Merge_Places", "manual")
_GLADE_FILE = "mergeplace.glade"
PLACE_NAME = _("Name:", "place")


# -------------------------------------------------------------------------
#
# MergePlace
#
# -------------------------------------------------------------------------
class MergePlace(ManagedWindow):
    """
    Displays a dialog box that allows the places to be combined into one.
    """

    def __init__(self, dbstate, uistate, track, handle1, handle2, callback=None):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.callback = callback
        self.pl1 = database.get_place_from_handle(handle1)
        self.pl2 = database.get_place_from_handle(handle2)

        self.define_glade("mergeplace", _GLADE_FILE)
        self.set_window(
            self._gladeobj.toplevel, self.get_widget("place_title"), _("Merge Places")
        )
        self.setup_configs("interface.merge-place", 500, 250)

        # Detailed selection widgets
        if not config.get("preferences.place-auto"):
            title1 = self.pl1.get_title()
            title2 = self.pl2.get_title()
            entry1 = self.get_widget("title1")
            entry2 = self.get_widget("title2")
            entry1.set_text(title1)
            entry2.set_text(title2)
            if entry1.get_text() == entry2.get_text():
                for widget_name in ("title1", "title2", "title_btn1", "title_btn2"):
                    self.get_widget(widget_name).set_sensitive(False)
            for widget_name in ("title1", "title2", "title_btn1", "title_btn2"):
                self.get_widget(widget_name).show()

        for widget_name in ("name_btn1", "name_btn2"):
            self.get_widget(widget_name).set_label(PLACE_NAME)
        entry1 = self.get_widget("name1")
        entry2 = self.get_widget("name2")
        entry1.set_text(self.pl1.get_name().get_value())
        entry2.set_text(self.pl2.get_name().get_value())
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("name1", "name2", "name_btn1", "name_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("type1")
        entry2 = self.get_widget("type2")
        entry1.set_text(str(self.pl1.get_type()))
        entry2.set_text(str(self.pl2.get_type()))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("type1", "type2", "type_btn1", "type_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("code1")
        entry2 = self.get_widget("code2")
        entry1.set_text(self.pl1.get_code())
        entry2.set_text(self.pl2.get_code())
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("code1", "code2", "code_btn1", "code_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("lat1")
        entry2 = self.get_widget("lat2")
        entry1.set_text(self.pl1.get_latitude())
        entry2.set_text(self.pl2.get_latitude())
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("lat1", "lat2", "lat_btn1", "lat_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("long1")
        entry2 = self.get_widget("long2")
        entry1.set_text(self.pl1.get_longitude())
        entry2.set_text(self.pl2.get_longitude())
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("long1", "long2", "long_btn1", "long_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.pl1.get_gramps_id()
        gramps2 = self.pl2.get_gramps_id()
        entry1 = self.get_widget("gramps1")
        entry2 = self.get_widget("gramps2")
        entry1.set_text(gramps1)
        entry2.set_text(gramps2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("gramps1", "gramps2", "gramps_btn1", "gramps_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        # Main window widgets that determine which handle survives
        title1 = place_displayer.display(database, self.pl1)
        title2 = place_displayer.display(database, self.pl2)
        rbutton1 = self.get_widget("handle_btn1")
        rbutton_label1 = self.get_widget("label_handle_btn1")
        rbutton_label2 = self.get_widget("label_handle_btn2")
        rbutton_label1.set_label(
            title1 + " [" + gramps1 + "] " + str(self.pl1.place_type)
        )
        rbutton_label2.set_label(
            title2 + " [" + gramps2 + "] " + str(self.pl2.place_type)
        )
        rbutton1.connect("toggled", self.on_handle1_toggled)

        self.connect_button("place_help", self.cb_help)
        self.connect_button("place_ok", self.cb_merge)
        self.connect_button("place_cancel", self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """first chosen place changes"""
        if obj.get_active():
            self.get_widget("title_btn1").set_active(True)
            self.get_widget("name_btn1").set_active(True)
            self.get_widget("type_btn1").set_active(True)
            self.get_widget("code_btn1").set_active(True)
            self.get_widget("lat_btn1").set_active(True)
            self.get_widget("long_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("title_btn2").set_active(True)
            self.get_widget("name_btn2").set_active(True)
            self.get_widget("type_btn2").set_active(True)
            self.get_widget("code_btn2").set_active(True)
            self.get_widget("lat_btn2").set_active(True)
            self.get_widget("long_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Performs the merge of the places when the merge button is clicked.
        """
        self.uistate.set_busy_cursor(True)
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.pl1
            titanic = self.pl2
        else:
            phoenix = self.pl2
            titanic = self.pl1

        if self.get_widget("title_btn1").get_active() ^ use_handle1:
            phoenix.set_title(titanic.get_title())
        if self.get_widget("name_btn1").get_active() ^ use_handle1:
            phoenix.set_name(titanic.get_name())
        if self.get_widget("type_btn1").get_active() ^ use_handle1:
            phoenix.set_type(titanic.get_type())
        if self.get_widget("code_btn1").get_active() ^ use_handle1:
            phoenix.set_code(titanic.get_code())
        if self.get_widget("lat_btn1").get_active() ^ use_handle1:
            phoenix.set_latitude(titanic.get_latitude())
        if self.get_widget("long_btn1").get_active() ^ use_handle1:
            phoenix.set_longitude(titanic.get_longitude())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        query = MergePlaceQuery(self.dbstate, phoenix, titanic)
        query.execute()
        # Add the selected handle to history so that when merge is complete,
        # phoenix is the selected row.
        self.uistate.set_active(phoenix.get_handle(), "Place")

        if self.callback:
            self.callback()
        self.uistate.set_busy_cursor(False)
        self.close()
