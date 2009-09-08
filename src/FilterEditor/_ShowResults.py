#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2008  Donald N. Allingham
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
Custom Filter Editor tool.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import locale
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".FilterEdit")

#-------------------------------------------------------------------------
#
# GTK/GNOME 
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ManagedWindow
from BasicUtils import name_displayer as _nd
import Utils

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class ShowResults(ManagedWindow.ManagedWindow):
    def __init__(self, db, uistate, track, handle_list, filtname, namespace):

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.db = db
        self.filtname = filtname
        self.namespace = namespace
        self.define_glade('test', const.RULE_GLADE,)
        self.set_window(
            self.get_widget('test'),
            self.get_widget('title'),
            _('Filter Test'))

        render = gtk.CellRendererText()
        
        tree = self.get_widget('list')
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        tree.set_model(model)

        column_n = gtk.TreeViewColumn(_('Name'), render, text=0)
        tree.append_column(column_n)

        column_n = gtk.TreeViewColumn(_('ID'), render, text=1)
        tree.append_column(column_n)

        self.get_widget('close').connect('clicked', self.close)

        new_list = [self.sort_val_from_handle(h) for h in handle_list]
        new_list.sort(lambda x, y: locale.strcoll(x[0], y[0]))
        handle_list = [ h[1] for h in new_list ]

        for handle in handle_list:
            name, gid = self.get_name_id(handle)
            model.append(row=[name, gid])

        self.show()

    def get_name_id(self, handle):
        if self.namespace == 'Person':
            person = self.db.get_person_from_handle(handle)
            name = _nd.sorted(person)
            gid = person.get_gramps_id()
        elif self.namespace == 'Family':
            family = self.db.get_family_from_handle(handle)
            name = Utils.family_name(family, self.db)
            gid = family.get_gramps_id()
        elif self.namespace == 'Event':
            event = self.db.get_event_from_handle(handle)
            name = event.get_description()
            gid = event.get_gramps_id()
        elif self.namespace == 'Source':
            source = self.db.get_source_from_handle(handle)
            name = source.get_title()
            gid = source.get_gramps_id()
        elif self.namespace == 'Place':
            place = self.db.get_place_from_handle(handle)
            name = place.get_title()
            gid = place.get_gramps_id()
        elif self.namespace == 'MediaObject':
            obj = self.db.get_object_from_handle(handle)
            name = obj.get_description()
            gid = obj.get_gramps_id()
        elif self.namespace == 'Repository':
            repo = self.db.get_repository_from_handle(handle)
            name = repo.get_name()
            gid = repo.get_gramps_id()
        elif self.namespace == 'Note':
            note = self.db.get_note_from_handle(handle)
            name = note.get().replace('\n', ' ')
            #String must be unicode for truncation to work for non ascii characters
            name = unicode(name)
            if len(name) > 80:
                name = name[:80]+"..."
            gid = note.get_gramps_id()
        return (name, gid)
        
    def sort_val_from_handle(self, handle):
        if self.namespace == 'Person':
            name = self.db.get_person_from_handle(handle).get_primary_name()
            sortname = _nd.sort_string(name)
        elif self.namespace == 'Family':
            sortname = Utils.family_name(
                self.db.get_family_from_handle(handle),self.db)
        elif self.namespace == 'Event':
            sortname = self.db.get_event_from_handle(handle).get_description()
        elif self.namespace == 'Source':
            sortname = self.db.get_source_from_handle(handle).get_title()
        elif self.namespace == 'Place':
            sortname = self.db.get_place_from_handle(handle).get_title()
        elif self.namespace == 'MediaObject':
            sortname = self.db.get_object_from_handle(handle).get_description()
        elif self.namespace == 'Repository':
            sortname = self.db.get_repository_from_handle(handle).get_name()
        elif self.namespace == 'Note':
            gid = self.db.get_note_from_handle(handle).get_gramps_id()
            sortname = gid
        return (sortname, handle)
