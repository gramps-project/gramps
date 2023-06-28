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
Provide merge capabilities for media objects.
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
from gramps.gen.merge import MergeMediaQuery

#-------------------------------------------------------------------------
#
# Gramps constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT3
WIKI_HELP_SEC = _('Merge_Media_Objects', 'manual')
_GLADE_FILE = 'mergemedia.glade'

#-------------------------------------------------------------------------
#
# MergeMedia
#
#-------------------------------------------------------------------------
class MergeMedia(ManagedWindow):
    """
    Displays a dialog box that allows the media objects to be combined into one.
    """
    def __init__(self, dbstate, uistate, track, handle1, handle2):
        ManagedWindow.__init__(self, uistate, track, self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.mo1 = database.get_media_from_handle(handle1)
        self.mo2 = database.get_media_from_handle(handle2)

        self.define_glade('mergeobject', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget('object_title'),
                        _("Merge Media Objects"))
        self.setup_configs('interface.merge-media', 500, 250)

        # Detailed selection Widgets
        desc1 = self.mo1.get_description()
        desc2 = self.mo2.get_description()
        entry1 = self.get_widget("desc1")
        entry2 = self.get_widget("desc2")
        entry1.set_text(desc1)
        entry2.set_text(desc2)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('desc1', 'desc2', 'desc_btn1', 'desc_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("path1")
        entry2 = self.get_widget("path2")
        entry1.set_text(self.mo1.get_path())
        entry2.set_text(self.mo2.get_path())
        entry1.set_position(-1)
        entry2.set_position(-1)
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('path1', 'path2', 'path_btn1', 'path_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        entry1 = self.get_widget("date1")
        entry2 = self.get_widget("date2")
        entry1.set_text(get_date(self.mo1))
        entry2.set_text(get_date(self.mo2))
        if entry1.get_text() == entry2.get_text():
            for widget_name in ('date1', 'date2', 'date_btn1', 'date_btn2'):
                self.get_widget(widget_name).set_sensitive(False)

        gramps1 = self.mo1.get_gramps_id()
        gramps2 = self.mo2.get_gramps_id()
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
        rbutton_label1.set_label("%s [%s]" % (desc1, gramps1))
        rbutton_label2.set_label("%s [%s]" % (desc2, gramps2))
        rbutton1.connect('toggled', self.on_handle1_toggled)

        self.connect_button('object_help', self.cb_help)
        self.connect_button('object_ok', self.cb_merge)
        self.connect_button('object_cancel', self.close)
        self.show()

    def on_handle1_toggled(self, obj):
        """ first chosen media object changes"""
        if obj.get_active():
            self.get_widget("path_btn1").set_active(True)
            self.get_widget("desc_btn1").set_active(True)
            self.get_widget("date_btn1").set_active(True)
            self.get_widget("gramps_btn1").set_active(True)
        else:
            self.get_widget("path_btn2").set_active(True)
            self.get_widget("desc_btn2").set_active(True)
            self.get_widget("date_btn2").set_active(True)
            self.get_widget("gramps_btn2").set_active(True)

    def cb_help(self, obj):
        """Display the relevant portion of the Gramps manual"""
        display_help(webpage = WIKI_HELP_PAGE, section = WIKI_HELP_SEC)

    def cb_merge(self, obj):
        """
        Perform the merge of the media objects when the merge button is clicked.
        """
        use_handle1 = self.get_widget("handle_btn1").get_active()
        if use_handle1:
            phoenix = self.mo1
            titanic = self.mo2
        else:
            phoenix = self.mo2
            titanic = self.mo1

        if self.get_widget("path_btn1").get_active() ^ use_handle1:
            phoenix.set_path(titanic.get_path())
            phoenix.set_mime_type(titanic.get_mime_type())
        if self.get_widget("desc_btn1").get_active() ^ use_handle1:
            phoenix.set_description(titanic.get_description())
        if self.get_widget("date_btn1").get_active() ^ use_handle1:
            phoenix.set_date_object(titanic.get_date_object())
        if self.get_widget("gramps_btn1").get_active() ^ use_handle1:
            phoenix.set_gramps_id(titanic.get_gramps_id())

        query = MergeMediaQuery(self.dbstate, phoenix, titanic)
        query.execute()
        # Add the selected handle to history so that when merge is complete,
        # phoenix is the selected row.
        self.uistate.set_active(phoenix.get_handle(), 'Media')
        self.close()
