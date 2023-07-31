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
Provide merge capabilities for families.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.const import URL_MANUAL_SECT3
from ..display import display_help
from gramps.gen.errors import MergeError
from ..dialog import ErrorDialog
from ..managedwindow import ManagedWindow
from gramps.gen.merge import MergePersonQuery, MergeFamilyQuery

# -------------------------------------------------------------------------
#
# Gramps constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _("Merge_Families", "manual")
_GLADE_FILE = "mergefamily.glade"


# -------------------------------------------------------------------------
#
# MergeFamily
#
# -------------------------------------------------------------------------
class MergeFamily(ManagedWindow):
    """
    Merges two families into a single family. Displays a dialog box that allows
    the families to be combined into one.
    """

    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.database = dbstate.db
        self.fy1 = self.database.get_family_from_handle(handle1)
        self.fy2 = self.database.get_family_from_handle(handle2)

        self.define_glade("mergefamily", _GLADE_FILE)
        self.set_window(
            self._gladeobj.toplevel,
            self.get_widget("family_title"),
            _("Merge Families"),
        )
        self.setup_configs("interface.merge-family", 500, 250)

        # Detailed selection widgets
        father1 = self.fy1.get_father_handle()
        father2 = self.fy2.get_father_handle()
        if father1:
            father1 = self.database.get_person_from_handle(father1)
        if father2:
            father2 = self.database.get_person_from_handle(father2)
        father_id1 = father1.get_gramps_id() if father1 else ""
        father_id2 = father2.get_gramps_id() if father2 else ""
        father1 = name_displayer.display(father1) if father1 else ""
        father2 = name_displayer.display(father2) if father2 else ""
        entry1 = self.get_widget("father1")
        entry2 = self.get_widget("father2")
        entry1.set_text("%s [%s]" % (father1, father_id1))
        entry2.set_text("%s [%s]" % (father2, father_id2))
        deactivate = False
        if father_id1 == "" and father_id2 == "":
            deactivate = True
        elif father_id2 == "":
            self.get_widget("father_btn1").set_active(True)
            deactivate = True
        elif father_id1 == "":
            self.get_widget("father_btn2").set_active(True)
            deactivate = True
        elif entry1.get_text() == entry2.get_text():
            deactivate = True
        if deactivate:
            for widget_name in ("father1", "father2", "father_btn1", "father_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        mother1 = self.fy1.get_mother_handle()
        mother2 = self.fy2.get_mother_handle()
        if mother1:
            mother1 = self.database.get_person_from_handle(mother1)
        if mother2:
            mother2 = self.database.get_person_from_handle(mother2)
        mother_id1 = mother1.get_gramps_id() if mother1 else ""
        mother_id2 = mother2.get_gramps_id() if mother2 else ""
        mother1 = name_displayer.display(mother1) if mother1 else ""
        mother2 = name_displayer.display(mother2) if mother2 else ""
        entry1 = self.get_widget("mother1")
        entry2 = self.get_widget("mother2")
        entry1.set_text("%s [%s]" % (mother1, mother_id1))
        entry2.set_text("%s [%s]" % (mother2, mother_id2))
        deactivate = False
        if mother_id1 == "" and mother_id2 == "":
            deactivate = True
        elif mother_id1 == "":
            self.get_widget("mother_btn2").set_active(True)
            deactivate = True
        elif mother_id2 == "":
            self.get_widget("mother_btn1").set_active(True)
            deactivate = True
        elif entry1.get_text() == entry2.get_text():
            deactivate = True
        if deactivate:
            for widget_name in ("mother1", "mother2", "mother_btn1", "mother_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("rel1")
        entry2 = self.get_widget("rel2")
        entry1.set_text(str(self.fy1.get_relationship()))
        entry2.set_text(str(self.fy2.get_relationship()))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("rel1", "rel2", "rel_btn1", "rel_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.fy1.get_gramps_id()
        gramps2 = self.fy2.get_gramps_id()
        entry1 = self.get_widget("gramps1")
        entry2 = self.get_widget("gramps2")
        entry1.set_text(gramps1)
        entry2.set_text(gramps2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("gramps1", "gramps2", "gramps_btn1", "gramps_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        # Main window widgets that determine which handle survives
        rbutton1 = self.get_widget("handle_btn1")
        rbutton_label1 = self.get_widget("label_handle_btn1")
        rbutton_label2 = self.get_widget("label_handle_btn2")
        add = _("and")
        rbutton_label1.set_label("%s %s %s [%s]" % (father1, add, mother1, gramps1))
        rbutton_label2.set_label("%s %s %s [%s]" % (father2, add, mother2, gramps2))
        rbutton1.connect("toggled", self.on_handle1_toggled)

        self.connect_button("family_help", self.cb_help)
        self.connect_button("family_ok", self.cb_merge)
        self.connect_button("family_cancel", self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """Preferred family changes"""
        if obj.get_active():
            father1_text = self.get_widget("father1").get_text()
            if father1_text != " []" or self.get_widget("father2").get_text() == " []":
                self.get_widget("father_btn1").set_active(True)
            mother1_text = self.get_widget("mother1").get_text()
            if mother1_text != " []" or self.get_widget("mother2").get_text() == " []":
                self.get_widget("mother_btn1").set_active(True)
            self.get_widget("rel_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            father2_text = self.get_widget("father2").get_text()
            if father2_text != " []" or self.get_widget("father1").get_text() == " []":
                self.get_widget("father_btn2").set_active(True)
            mother2_text = self.get_widget("mother2").get_text()
            if mother2_text != " []" or self.get_widget("mother1").get_text() == " []":
                self.get_widget("mother_btn2").set_active(True)
            self.get_widget("rel_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of the Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Perform the merge of the families when the merge button is clicked.
        """
        self.uistate.set_busy_cursor(True)
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.fy1
            titanic = self.fy2
        else:
            phoenix = self.fy2
            titanic = self.fy1

        phoenix_fh = phoenix.get_father_handle()
        phoenix_mh = phoenix.get_mother_handle()

        if self.get_widget("father_btn1").get_active() ^ use_handle1:
            phoenix_fh = titanic.get_father_handle()
        if self.get_widget("mother_btn1").get_active() ^ use_handle1:
            phoenix_mh = titanic.get_mother_handle()
        if self.get_widget("rel_btn1").get_active() ^ use_handle1:
            phoenix.set_relationship(titanic.get_relationship())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        try:
            query = MergeFamilyQuery(
                self.database, phoenix, titanic, phoenix_fh, phoenix_mh
            )
            query.execute()
            # Add the selected handle to history so that when merge is complete,
            # phoenix is the selected row.
            self.uistate.set_active(phoenix.get_handle(), "Family")
        except MergeError as err:
            ErrorDialog(_("Cannot merge people"), str(err), parent=self.window)
        self.uistate.set_busy_cursor(False)
        self.close()
