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
Provide merge capabilities for repositories.
"""

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
from gramps.gen.merge import MergeRepositoryQuery

# -------------------------------------------------------------------------
#
# Gramps constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _("Merge_Repositories", "manual")
_GLADE_FILE = "mergerepository.glade"
REPO_NAME = _("Name:", "repo")


# -------------------------------------------------------------------------
#
# MergeRepository
#
# -------------------------------------------------------------------------
class MergeRepository(ManagedWindow):
    """
    Displays a dialog box that allows two repositories to be combined into one.
    """

    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.rp1 = database.get_repository_from_handle(handle1)
        self.rp2 = database.get_repository_from_handle(handle2)

        self.define_glade("mergerepository", _GLADE_FILE)
        self.set_window(
            self._gladeobj.toplevel,
            self.get_widget("repository_title"),
            _("Merge Repositories"),
        )
        self.setup_configs("interface.merge-repository", 500, 250)

        # Detailed selection widgets
        name1 = self.rp1.get_name()
        name2 = self.rp2.get_name()
        for widget_name in ("name_btn1", "name_btn2"):
            self.get_widget(widget_name).set_label(REPO_NAME)
        entry1 = self.get_widget("name1")
        entry2 = self.get_widget("name2")
        entry1.set_text(name1)
        entry2.set_text(name2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("name1", "name2", "name_btn1", "name_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("type1")
        entry2 = self.get_widget("type2")
        entry1.set_text(str(self.rp1.get_type()))
        entry2.set_text(str(self.rp2.get_type()))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ("type1", "type2", "type_btn1", "type_btn2"):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.rp1.get_gramps_id()
        gramps2 = self.rp2.get_gramps_id()
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
        rbutton_label1.set_label("%s [%s]" % (name1, gramps1))
        rbutton_label2.set_label("%s [%s]" % (name2, gramps2))
        rbutton1.connect("toggled", self.on_handle1_toggled)

        self.connect_button("repository_help", self.cb_help)
        self.connect_button("repository_ok", self.cb_merge)
        self.connect_button("repository_cancel", self.close)

        self.show()

    def on_handle1_toggled(self, obj):
        """preferred repository changes"""
        if obj.get_active():
            self.get_widget("name_btn1").set_active(True)
            self.get_widget("type_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("name_btn2").set_active(True)
            self.get_widget("type_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of the Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Perform the merge of the repositories when the merge button is clicked.
        """
        self.uistate.set_busy_cursor(True)
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.rp1
            titanic = self.rp2
        else:
            phoenix = self.rp2
            titanic = self.rp1

        if self.get_widget("name_btn1").get_active() ^ use_handle1:
            phoenix.set_name(titanic.get_name())
        if self.get_widget("type_btn1").get_active() ^ use_handle1:
            phoenix.set_type(titanic.get_type())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        query = MergeRepositoryQuery(self.dbstate, phoenix, titanic)
        query.execute()
        # Add the selected handle to history so that when merge is complete,
        # phoenix is the selected row.
        self.uistate.set_active(phoenix.get_handle(), "Repository")
        self.uistate.set_busy_cursor(False)
        self.close()
