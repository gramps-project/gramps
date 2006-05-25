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
                        _("Select title"))
        
        self.glade.get_widget("title1_text").set_text(self.p1.get_title())
        self.glade.get_widget("title2_text").set_text(self.p2.get_title())
        self.t3 = self.glade.get_widget("title3_text")
        self.t3.set_text(self.p1.get_title())

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
            self.p1.set_title(unicode(self.t3.get_text()))

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
        note = self.p2.get_note()
        if note != "":
            if self.p1.get_note() == "":
                self.p1.set_note(note)
            elif self.p1.get_note() != note:
                self.p1.set_note("%s\n\n%s" % (self.p1.get_note(),note))

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

#-------------------------------------------------------------------------
#
# Merge Sources
#
#-------------------------------------------------------------------------
class MergeSources(ManagedWindow.ManagedWindow):
    """
    Merges to sources into a single source. Displays a dialog box that
    allows the sources to be combined into one.
    """
    def __init__(self, dbstate, uistate, new_handle, old_handle):
        
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self.__class__)

        self.db = dbstate.db
        
        self.new_handle = new_handle
        self.old_handle = old_handle
        self.src1 = self.db.get_source_from_handle(self.new_handle)
        self.src2 = self.db.get_source_from_handle(self.old_handle)

        self.glade = gtk.glade.XML(const.merge_glade,"merge_sources","gramps")

        self.set_window(self.glade.get_widget("merge_sources"),
                        self.glade.get_widget('title'),
                        _("Merge Sources"))

        self.title1 = self.glade.get_widget("title1")
        self.title2 = self.glade.get_widget("title2")
        self.title1.set_text(self.src1.get_title())
        self.title2.set_text(self.src2.get_title())

        self.author1 = self.glade.get_widget("author1")
        self.author2 = self.glade.get_widget("author2")
        self.author1.set_text(self.src1.get_author())
        self.author2.set_text(self.src2.get_author())

        self.abbrev1 = self.glade.get_widget("abbrev1")
        self.abbrev2 = self.glade.get_widget("abbrev2")
        self.abbrev1.set_text(self.src1.get_abbreviation())
        self.abbrev2.set_text(self.src2.get_abbreviation())

        self.pub1 = self.glade.get_widget("pub1")
        self.pub2 = self.glade.get_widget("pub2")
        self.pub1.set_text(self.src1.get_publication_info())
        self.pub2.set_text(self.src2.get_publication_info())

        self.gramps1 = self.glade.get_widget("gramps1")
        self.gramps2 = self.glade.get_widget("gramps2")
        self.gramps1.set_text(self.src1.get_gramps_id())
        self.gramps2.set_text(self.src2.get_gramps_id())
        
        self.glade.get_widget('ok').connect('clicked',self.merge)
        self.glade.get_widget('cancel').connect('clicked',self.close_window)
        self.glade.get_widget('help').connect('clicked',self.help)
        self.show()

    def close_window(self,obj):
        self.close()

    def help(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-merge-sources')

    def merge(self,obj):
        """
        Performs the merge of the sources when the merge button is clicked.
        """

        use_title1 = self.glade.get_widget("title_btn1").get_active()
        use_author1 = self.glade.get_widget("author_btn1").get_active()
        use_abbrev1 = self.glade.get_widget("abbrev_btn1").get_active()
        use_pub1 = self.glade.get_widget("pub_btn1").get_active()
        use_gramps1 = self.glade.get_widget("gramps_btn1").get_active()
        
        if not use_title1:
            self.src1.set_title(self.src2.get_title())

        if not use_author1:
            self.src1.set_author(self.src2.get_author())

        if not use_abbrev1:
            self.src1.set_abbreviation(self.src2.get_abbreviation())

        if not use_pub1:
            self.src1.set_publication_info(self.src2.get_publication_info())

        if not use_gramps1:
            self.src1.set_gramps_id(self.src2.get_gramps_id())

        # Copy photos from src2 to src1
        for photo in self.src2.get_media_list():
            self.src1.add_media_reference(photo)

        # Add notes from P2 to P1
        note = self.src2.get_note()
        if note != "":
            if self.src1.get_note() == "":
                self.src1.set_note(note)
            elif self.src1.get_note() != note:
                self.src1.set_note("%s\n\n%s" % (self.src1.get_note(),note))

        src2_map = self.src2.get_data_map()
        src1_map = self.src1.get_data_map()
        for key in src2_map.keys():
            if not src1_map.has_key(key):
                src1_map[key] = src2_map[key]

        # replace references in other objetcs
        trans = self.db.transaction_begin()

        self.db.remove_source(self.old_handle,trans)
        self.db.commit_source(self.src1,trans)

        # replace handles

        # people
        for handle in self.db.get_person_handles(sort_handles=False):
            person = self.db.get_person_from_handle(handle)
            if person.has_source_reference(self.old_handle):
                person.replace_source_references(self.old_handle,self.new_handle)
                self.db.commit_person(person,trans)

        # family
        for handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(handle)
            if family.has_source_reference(self.old_handle):
                family.replace_source_references(self.old_handle,self.new_handle)
                self.db.commit_family(family,trans)

        # events
        for handle in self.db.get_event_handles():
            event = self.db.get_event_from_handle(handle)
            if event.has_source_reference(self.old_handle):
                event.replace_source_references(self.old_handle,self.new_handle)
		self.db.commit_event(event,trans)

        # sources
        for handle in self.db.get_source_handles():
            source = self.db.get_source_from_handle(handle)
            if source.has_source_reference(self.old_handle):
                source.replace_source_references(self.old_handle,self.new_handle)
                self.db.commit_source(source,trans)

        # places
        for handle in self.db.get_place_handles():
            place = self.db.get_place_from_handle(handle) 
            if place.has_source_reference(self.old_handle):
                place.replace_source_references(self.old_handle,self.new_handle)
                self.db.commit_place(place,trans)

        # media
        for handle in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(handle)
            if obj.has_source_reference(self.old_handle):
                obj.replace_source_references(self.old_handle,self.new_handle)
                self.db.commit_media_object(obj,trans)
        
        self.db.transaction_commit(trans,_("Merge Sources"))
        self.close()
