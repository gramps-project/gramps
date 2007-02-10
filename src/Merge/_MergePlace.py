#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import GrampsDisplay
import ManagedWindow

#-------------------------------------------------------------------------
#
# Merge Places
#
#-------------------------------------------------------------------------
class MergePlaces(ManagedWindow.ManagedWindow):
    """
    Merges to places into a single place. Displays a dialog box that
    allows the places to be combined into one.
    """
    def __init__(self, dbstate, uistate, new_handle, old_handle):

        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)

        self.db = dbstate.db
        self.new_handle = new_handle
        self.old_handle = old_handle
        self.p1 = self.db.get_place_from_handle(self.new_handle)
        self.p2 = self.db.get_place_from_handle(self.old_handle)

        self.glade = gtk.glade.XML(const.merge_glade,"merge_places","gramps")
        self.set_window(self.glade.get_widget("merge_places"),
                        self.glade.get_widget('title'),
                        _("Merge Places"))
        
        title1_text = self.glade.get_widget("title1_text")
        title2_text = self.glade.get_widget("title2_text")
        self.title3_entry = self.glade.get_widget("title3_text")

        title1_text.set_text(self.p1.get_title())
        title2_text.set_text(self.p2.get_title())
        self.title3_entry.set_text(self.p1.get_title())

        self.note_p1 = self.glade.get_widget('note_p1')
        self.note_p2 = self.glade.get_widget('note_p2')
        self.note_merge = self.glade.get_widget('note_merge')
        self.note_title = self.glade.get_widget('note_title')

        self.note_conflict = (self.p1.get_note(markup=True) and
                              self.p2.get_note(markup=True))
        if self.note_conflict:
            self.note_title.show()
            self.note_p1.show()
            self.note_p2.show()
            self.note_merge.show()

        self.glade.get_widget('cancel').connect('clicked', self.close_window)
        self.glade.get_widget('ok').connect('clicked', self.merge)
        self.glade.get_widget('help').connect('clicked', self.help)
        
        self.show()

    def close_window(self, obj):
        self.close()
        
    def build_menu_names(self,obj):
        return (_('Merge Places'),None)

    def help(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-merge-places')

    def merge(self,obj):
        """
        Performs the merge of the places when the merge button is clicked.
        """
        t2active = self.glade.get_widget("title2").get_active()

        if t2active:
            self.p1.set_title(self.p2.get_title())
        elif self.glade.get_widget("title3").get_active():
            self.p1.set_title(unicode(self.title3_entry.get_text()))

        # Set longitude
        if self.p1.get_longitude() == "" and self.p2.get_longitude() != "":
            self.p1.set_longitude(self.p2.get_longitude())

        # Set latitude
        if self.p1.get_latitude() == "" and self.p2.get_latitude() != "":
            self.p1.set_latitude(self.p2.get_latitude())

        # Add URLs from P2 to P1
        for url in self.p2.get_url_list():
            self.p1.add_url(url)

        # Copy photos from P2 to P1
        for photo in self.p2.get_media_list():
            self.p1.add_media_reference(photo)

        # Copy sources from P2 to P1
        for source in self.p2.get_source_references():
            self.p1.add_source(source)

        # Add notes from P2 to P1
        if self.note_conflict:
            note1 = self.p1.get_note(markup=True)
            note2 = self.p2.get_note(markup=True)
            if self.note_p2.get_active():
                self.p1.set_note(note2)
            elif self.note_merge.get_active():
                self.p1.set_note("%s\n\n%s" % (note1,note2))
        else:
            note = self.p2.get_note(markup=True)
            if note != "" and self.p1.get_note(markup=True) == "":
                self.p1.set_note(note)
            
        if t2active:
            lst = [self.p1.get_main_location()] + self.p1.get_alternate_locations()
            self.p1.set_main_location(self.p2.get_main_location())
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)
        else:
            lst = [self.p2.get_main_location()] + self.p2.get_alternate_locations()
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)

        # remove old and commit new source
        trans = self.db.transaction_begin()

        self.db.remove_place(self.old_handle,trans)
        self.db.commit_place(self.p1,trans)

        # replace references in other objetcs
        # people
        for handle in self.db.get_person_handles(sort_handles=False):
            person = self.db.get_person_from_handle(handle)
            if person.has_handle_reference('Place',self.old_handle):
                person.replace_handle_reference('Place',self.old_handle,self.new_handle)
                self.db.commit_person(person,trans)
        # families
        for handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(handle)
            if family.has_handle_reference('Place',self.old_handle):
                family.replace_handle_reference('Place',self.old_handle,self.new_handle)
                self.db.commit_family(family,trans)
        # events
        for handle in self.db.get_event_handles():
            event = self.db.get_event_from_handle(handle)
            if event.has_handle_reference('Place',self.old_handle):
                event.replace_handle_reference('Place',self.old_handle,self.new_handle)
                self.db.commit_event(event,trans)

        self.db.transaction_commit(trans,_("Merge Places"))
        self.close()
