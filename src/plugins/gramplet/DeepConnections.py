# encoding: utf-8
#
# Gramps - a GTK+/GNOME based genealogy program 
#
# Copyright (C) 2009 Doug Blank <doug.blank@gmail.com>
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

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.lib import EventType, FamilyRelType
from BasicUtils import name_displayer
from DataViews import register, Gramplet
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# The Gramplet
#
#------------------------------------------------------------------------
class DeepConnectionsGramplet(Gramplet):
    """
    Finds deep connections people the home person and the active person.
    """
    def init(self):
        self.set_tooltip(_("Double-click name for details"))
        self.set_text(_("No Family Tree loaded."))
        self.set_use_markup(True)
        self.gui.get_container_widget().remove(self.gui.textview)
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        pause_button = gtk.Button(_("Pause"))
        pause_button.connect("clicked", self.interrupt)
        continue_button = gtk.Button(_("Continue"))
        continue_button.connect("clicked", self.resume)
        hbox.pack_start(pause_button, True)
        hbox.pack_start(continue_button, True)
        vbox.pack_start(self.gui.textview, True)
        vbox.pack_start(hbox, False)
        self.gui.get_container_widget().add_with_viewport(vbox)
        vbox.show_all()

    def get_relatives(self, person_handle, path):
        """
        Gets all of the direct relatives of person_handle.
        """
        retval = []
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person is None: return []
        family_list = person.get_family_handle_list()
        for family_handle in family_list:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            children = family.get_child_ref_list()
            for child_ref in children:
                retval += [(child_ref.ref, (path, (_("child"), person_handle)))]
            husband = family.get_father_handle()
            if husband:
                retval += [(husband, (path, (_("husband"), person_handle)))]
            wife = family.get_mother_handle()
            if wife:
                retval += [(wife, (path, (_("wife"), person_handle)))]
        parent_family_list = person.get_parent_family_handle_list()
        for family_handle in parent_family_list:
            family = self.dbstate.db.get_family_from_handle(family_handle)
            children = family.get_child_ref_list()
            for child_ref in children:
                retval += [(child_ref.ref, (path, (_("sibling"), person_handle)))]
            husband = family.get_father_handle()
            if husband:
                retval += [(husband, (path, (_("father"), person_handle)))]
            wife = family.get_mother_handle()
            if wife:
                retval += [(wife, (path, (_("mother"), person_handle)))]
        return retval

    def active_changed(self, handle):
        """
        Update the gramplet on active person change.
        """
        self.update()

    def pretty_print(self, path):
        """
        Print a path to a person, with links.
        """
        more_path, relation = path
        text, handle = relation
        person = self.dbstate.db.get_person_from_handle(handle)
        name = person.get_primary_name()
        if text != "self":
            self.append_text(_("\n   who is a %s of ") % text)
            self.link(name_displayer.display_name(name), "Person", handle)
            if more_path is not None:
                self.pretty_print(more_path)

    def main(self):
        """
        Main method.
        """
        self.total_relations_found = 0
        yield True
        default_person = self.dbstate.db.get_default_person()
        active_person = self.dbstate.get_active_person()
        if default_person == None:
            self.set_text(_("No Home Person set."))
            return
        if active_person == None:
            self.set_text(_("No Active Person set."))
            return
        self.cache = {} 
        self.queue = [(default_person.handle, (None, (_("self"), default_person.handle)))]
        default_name = default_person.get_primary_name()
        active_name = active_person.get_primary_name()
        self.set_text("")
        self.render_text(_("Looking for relationship between\n" +
                           "  <b>%s</b> (Home Person) and\n" +
                           "  <b>%s</b> (Active Person)...\n") %
                         (name_displayer.display_name(default_name), 
                          name_displayer.display_name(active_name)))
        yield True
        while self.queue:
            current_handle, current_path = self.queue.pop(0)
            if current_handle == active_person.handle: 
                self.total_relations_found += 1
                self.append_text(_("Found relation #%d: \n   ") % self.total_relations_found)

                self.link(name_displayer.display_name(active_name), "Person", active_person.handle)
                self.pretty_print(current_path)
                self.append_text("\n")
                if default_person.handle != active_person.handle:
                    self.append_text(_("Paused.\nPress Continue to search for additional relations.\n"))
                    self.pause()
                    yield False
                else:
                    break
            elif current_handle in self.cache: 
                continue
            self.cache[current_handle] = 1
            relatives = self.get_relatives(current_handle, current_path)
            for (person_handle, path) in relatives:
                if person_handle is not None and person_handle not in self.cache: 
                    self.queue.append( (person_handle, path))
            yield True
        self.append_text(_("\nSearch completed. %d relations found.") % self.total_relations_found)
        yield False
        
#------------------------------------------------------------------------
#
# Register the gramplet
#
#------------------------------------------------------------------------
register(
        type = "gramplet", 
        name = "Deep Connections Gramplet", 
        tname =_("Deep Connections Gramplet"), 
        height = 230,
        expand = True,
        content = DeepConnectionsGramplet,
        title = _("Deep Connections"))
