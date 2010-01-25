#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
from gen.ggettext import sgettext as _
import const
import GrampsDisplay
import ManagedWindow
from glade import Glade

#-------------------------------------------------------------------------
#
# GRAMPS constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Entering_and_Editing_Data:_Detailed_-_part_3' % const.URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Merge_Places')
_GLADE_FILE = 'mergedata.glade'

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

        self.glade = Glade(_GLADE_FILE, toplevel='mergeplace')
        self.set_window(self.glade.toplevel,
                        self.glade.get_object('place_title'),
                        _("Merge Places"))
        
        title1_text = self.glade.get_object("title1_text")
        title2_text = self.glade.get_object("title2_text")
        self.title3_entry = self.glade.get_object("title3_text")

        title1_text.set_text(self.p1.get_title())
        title2_text.set_text(self.p2.get_title())
        self.title3_entry.set_text(self.p1.get_title())

        self.glade.get_object('place_cancel').connect('clicked', self.close_window)
        self.glade.get_object('place_ok').connect('clicked', self.merge)
        self.glade.get_object('place_help').connect('clicked', self.help)
        
        self.show()

    def close_window(self, obj):
        self.close()
        
    def build_menu_names(self, obj):
        return (_('Merge Places'),None)

    def help(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help(webpage = WIKI_HELP_PAGE, section = WIKI_HELP_SEC)

    def merge(self, obj):
        """
        Performs the merge of the places when the merge button is clicked.
        """
        t2active = self.glade.get_object("place2").get_active()

        if t2active:
            self.p1.set_title(self.p2.get_title())
        elif self.glade.get_object("place3").get_active():
            self.p1.set_title(unicode(self.title3_entry.get_text()))

        # Set longitude
        if self.p1.get_longitude() == "" and self.p2.get_longitude() != "":
            self.p1.set_longitude(self.p2.get_longitude())

        # Set latitude
        if self.p1.get_latitude() == "" and self.p2.get_latitude() != "":
            self.p1.set_latitude(self.p2.get_latitude())

        # Add URLs from P2 to P1
        map(self.p1.add_url, self.p2.get_url_list())

        # Copy photos from P2 to P1
        map(self.p1.add_media_reference, self.p2.get_media_list())

        # Copy sources from P2 to P1
        map(self.p1.add_source_reference, self.p2.get_source_references())

        # Add notes from P2 to P1
        self.p1.set_note_list(self.p1.get_note_list() + 
                              self.p2.get_note_list())
            
        if t2active:
            lst = [self.p1.get_main_location()] + \
                   self.p1.get_alternate_locations()
            self.p1.set_main_location(self.p2.get_main_location())
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)
        else:
            lst = [self.p2.get_main_location()] + \
                   self.p2.get_alternate_locations()
            for l in lst:
                if not l.is_empty():
                    self.p1.add_alternate_locations(l)

        # remove old and commit new source
        trans = self.db.transaction_begin()

        self.db.remove_place(self.old_handle,trans)
        self.db.commit_place(self.p1,trans)

        # replace references in other objetcs
        # people
        for person in self.db.iter_people():
            if person.has_handle_reference('Place',self.old_handle):
                person.replace_handle_reference('Place',
                                        self.old_handle,self.new_handle)
                self.db.commit_person(person,trans)

        # families
        for family in self.db.iter_families():
            if family.has_handle_reference('Place',self.old_handle):
                family.replace_handle_reference('Place',
                                        self.old_handle,self.new_handle)
                self.db.commit_family(family,trans)

        # events
        for event in self.db.iter_events():
            if event.has_handle_reference('Place',self.old_handle):
                event.replace_handle_reference('Place',
                                        self.old_handle,self.new_handle)
                self.db.commit_event(event,trans)

        self.db.transaction_commit(trans,_("Merge Places"))
        self.close()
