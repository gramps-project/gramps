#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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
Provide merge capabilities for citations.
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
from gramps.gen.utils.string import conf_strings
from gramps.gen.merge import MergeCitationQuery

#-------------------------------------------------------------------------
#
# Gramps constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _('Merge_Citations', 'manual')
_GLADE_FILE = 'mergecitation.glade'

#-------------------------------------------------------------------------
#
# MergeCitation
#
#-------------------------------------------------------------------------
class MergeCitation(ManagedWindow):
    """
    Displays a dialog box that allows the citations to be combined into one.
    """
    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.citation1 = database.get_citation_from_handle(handle1)
        self.citation2 = database.get_citation_from_handle(handle2)

        self.define_glade('mergecitation', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget('citation_title'),
                        _("Merge Citations"))
        self.setup_configs('interface.merge-citation', 500, 250)

        # Detailed Selection widgets
        page1 = self.citation1.get_page()
        page2 = self.citation2.get_page()
        entry1 = self.get_widget("page1")
        entry2 = self.get_widget("page2")
        entry1.set_text(page1)
        entry2.set_text(page2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('page1', 'page2', 'page_btn1', 'page_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("date1")
        entry2 = self.get_widget("date2")
        entry1.set_text(get_date(self.citation1))
        entry2.set_text(get_date(self.citation2))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('date1', 'date2', 'date_btn1',
                    'date_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("confidence1")
        entry2 = self.get_widget("confidence2")
        entry1.set_text(_(conf_strings[self.citation1.get_confidence_level()]))
        entry2.set_text(_(conf_strings[self.citation2.get_confidence_level()]))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('confidence1', 'confidence2', 'confidence_btn1',
                    'confidence_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.citation1.get_gramps_id()
        gramps2 = self.citation2.get_gramps_id()
        entry1 = self.get_widget("gramps1")
        entry2 = self.get_widget("gramps2")
        entry1.set_text(gramps1)
        entry2.set_text(gramps2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('gramps1', 'gramps2', 'gramps_btn1',
                    'gramps_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        # Main window widgets that determine which handle survives
        rbutton1 = self.get_widget("handle_btn1")
        rbutton_label1 = self.get_widget("label_handle_btn1")
        rbutton_label2 = self.get_widget("label_handle_btn2")
        rbutton_label1.set_label(page1 + " [" + gramps1 + "]")
        rbutton_label2.set_label(page2 + " [" + gramps2 + "]")
        rbutton1.connect("toggled", self.on_handle1_toggled)

        self.connect_button('citation_help', self.cb_help)
        self.connect_button('citation_ok', self.cb_merge)
        self.connect_button('citation_cancel', self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """first chosen citation changes"""
        if obj.get_active():
            self.get_widget("page_btn1").set_active(True)
            self.get_widget("date_btn1").set_active(True)
            self.get_widget("confidence_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("page_btn2").set_active(True)
            self.get_widget("date_btn2").set_active(True)
            self.get_widget("confidence_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage = WIKI_HELP_PAGE, section = WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Performs the merge of the citations when the merge button is clicked.
        """
        self.uistate.set_busy_cursor(True)
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.citation1
            titanic = self.citation2
        else:
            phoenix = self.citation2
            titanic = self.citation1

        if self.get_widget("page_btn1").get_active() ^ use_handle1:
            phoenix.set_page(titanic.get_page())
        if self.get_widget("date_btn1").get_active() ^ use_handle1:
            phoenix.set_date_object(titanic.get_date_object())
        if self.get_widget("confidence_btn1").get_active() ^ use_handle1:
            phoenix.set_confidence_level(titanic.get_confidence_level())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        query = MergeCitationQuery(self.dbstate, phoenix, titanic)
        query.execute()
        # Add the selected handle to history so that when merge is complete,
        # phoenix is the selected row.
        self.uistate.set_active(phoenix.get_handle(), 'Citation')
        self.uistate.set_busy_cursor(False)
        self.close()
