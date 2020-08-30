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
Provide merge capabilities for notes.
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
from ..widgets.styledtextbuffer import StyledTextBuffer
from gramps.gen.merge import MergeNoteQuery

#-------------------------------------------------------------------------
#
# Gramps constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _('Merge_Notes', 'manual')
_GLADE_FILE = 'mergenote.glade'

#-------------------------------------------------------------------------
#
# MergeNote
#
#-------------------------------------------------------------------------
class MergeNote(ManagedWindow):
    """
    Displays a dialog box that allows two notes to be combined into one.
    """
    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.no1 = database.get_note_from_handle(handle1)
        self.no2 = database.get_note_from_handle(handle2)

        self.define_glade('mergenote', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget("note_title"),
                        _("Merge Notes"))
        self.setup_configs('interface.merge-note', 600, 250)

        # Detailed selection widgets
        text1 = self.no1.get_styledtext()
        tv1 = self.get_widget("text1")
        tb1 = StyledTextBuffer()
        tv1.set_buffer(tb1)
        tb1.set_text(text1)
        tv1.set_size_request(-1, 60)
        text2 = self.no2.get_styledtext()
        tv2 = self.get_widget("text2")
        tb2 = StyledTextBuffer()
        tv2.set_buffer(tb2)
        tb2.set_text(text2)
        tv2.set_size_request(-1, 60)
        if text1 == text2:
            for widget_name in ('text1', 'text2', 'text_btn1', 'text_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("type1")
        entry2 = self.get_widget("type2")
        entry1.set_text(str(self.no1.get_type()))
        entry2.set_text(str(self.no2.get_type()))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('type1', 'type2', 'type_btn1', 'type_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        format_names = (_('flowed'), _('preformatted'))
        entry1 = self.get_widget("format1")
        entry2 = self.get_widget("format2")
        entry1.set_text(format_names[self.no1.get_format()])
        entry2.set_text(format_names[self.no2.get_format()])
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('format1', 'format2', 'format_btn1',
                    'format_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.no1.get_gramps_id()
        gramps2 = self.no2.get_gramps_id()
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
        text1short = self.no1.get()
        if len(text1short) > 50:
            text1short = text1short[0:47] + "..."
        text2short = self.no2.get()
        if len(text2short) > 50:
            text2short = text2short[0:47] + "..."
        rbutton_label1.set_label("%s [%s]" % (text1short, gramps1))
        rbutton_label2.set_label("%s [%s]" % (text2short, gramps2))
        rbutton1.connect("toggled", self.on_handle1_toggled)

        self.connect_button("note_help", self.cb_help)
        self.connect_button("note_ok", self.cb_merge)
        self.connect_button("note_cancel", self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """ preferred note changes"""
        if obj.get_active():
            self.get_widget("text_btn1").set_active(True)
            self.get_widget("type_btn1").set_active(True)
            self.get_widget("format_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("text_btn2").set_active(True)
            self.get_widget("type_btn2").set_active(True)
            self.get_widget("format_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of the Gramps manual"""
        display_help(webpage = WIKI_HELP_PAGE, section= WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Perform the merge of the notes when the merge button is clicked.
        """
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.no1
            titanic = self.no2
        else:
            phoenix = self.no2
            titanic = self.no1

        if self.get_widget("text_btn1").get_active() ^ use_handle1:
            phoenix.set_styledtext(titanic.get_styledtext())
        if self.get_widget("type_btn1").get_active() ^ use_handle1:
            phoenix.set_type(titanic.get_type())
        if self.get_widget("format_btn1").get_active() ^ use_handle1:
            phoenix.set_format(titanic.get_format())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        query = MergeNoteQuery(self.dbstate, phoenix, titanic)
        query.execute()
        # Add the selected handle to history so that when merge is complete,
        # phoenix is the selected row.
        self.uistate.set_active(phoenix.get_handle(), 'Note')
        self.close()
