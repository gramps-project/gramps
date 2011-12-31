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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Provide merge capabilities for media objects.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.lib import Person, Family, Event, Source, Place
from gen.db import DbTxn
from gen.ggettext import sgettext as _
import const
import GrampsDisplay
import ManagedWindow
import DateHandler
from Errors import MergeError

#-------------------------------------------------------------------------
#
# Gramps constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Entering_and_Editing_Data:_Detailed_-_part_3' % \
        const.URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Merge_Media_Objects')
_GLADE_FILE = 'mergemedia.glade'

#-------------------------------------------------------------------------
#
# Merge Media Objects
#
#-------------------------------------------------------------------------
class MergeMediaObjects(ManagedWindow.ManagedWindow):
    """
    Displays a dialog box that allows the media objects to be combined into one.
    """
    def __init__(self, dbstate, uistate, handle1, handle2):
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.dbstate = dbstate
        database = dbstate.db
        self.mo1 = database.get_object_from_handle(handle1)
        self.mo2 = database.get_object_from_handle(handle2)

        self.define_glade('mergeobject', _GLADE_FILE)
        self.set_window(self._gladeobj.toplevel,
                        self.get_widget('object_title'),
                        _("Merge Media Objects"))

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
        entry1.set_text(DateHandler.get_date(self.mo1))
        entry2.set_text(DateHandler.get_date(self.mo2))
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
        GrampsDisplay.help(webpage = WIKI_HELP_PAGE, section = WIKI_HELP_SEC)

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
            # Add second handle to history so that when merge is complete, 
            # phoenix is the selected row.
            self.uistate.viewmanager.active_page.get_history().push(
                    phoenix.get_handle())

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
        self.close()

class MergeMediaQuery(object):
    """
    Create datqabase query to merge two media objects.
    """
    def __init__(self, dbstate, phoenix, titanic):
        self.database = dbstate.db
        self.phoenix = phoenix
        self.titanic = titanic

    def execute(self):
        """
        Merges two media objects into a single object.
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        self.phoenix.merge(self.titanic)

        with DbTxn(_("Merge Media Objects"), self.database) as trans:
            self.database.commit_media_object(self.phoenix, trans)
            for (class_name, handle) in self.database.find_backlink_handles(
                    old_handle):
                if class_name == Person.__name__:
                    person = self.database.get_person_from_handle(handle)
                    assert(person.has_media_reference(old_handle))
                    person.replace_media_references(old_handle, new_handle)
                    self.database.commit_person(person, trans)
                elif class_name == Family.__name__:
                    family = self.database.get_family_from_handle(handle)
                    assert(family.has_media_reference(old_handle))
                    family.replace_media_references(old_handle, new_handle)
                    self.database.commit_family(family, trans)
                elif class_name == Event.__name__:
                    event = self.database.get_event_from_handle(handle)
                    assert(event.has_media_reference(old_handle))
                    event.replace_media_references(old_handle, new_handle)
                    self.database.commit_event(event, trans)
                elif class_name == Source.__name__:
                    source = self.database.get_source_from_handle(handle)
                    assert(source.has_media_reference(old_handle))
                    source.replace_media_references(old_handle, new_handle)
                    self.database.commit_source(source, trans)
                elif class_name == Place.__name__:
                    place = self.database.get_place_from_handle(handle)
                    assert(place.has_media_reference(old_handle))
                    place.replace_media_references(old_handle, new_handle)
                    self.database.commit_place(place, trans)
                else:
                    raise MergeError("Encounter an object of type % s that has "
                            "a media object reference." % class_name)
            self.database.remove_object(old_handle, trans)
