#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

# $Id: _FilterEditor.py 6840 2006-06-01 22:37:13Z dallingham $

"""
Custom Filter Editor tool.
"""

__author__ = "Don Allingham"

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

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ManagedWindow
import NameDisplay

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class ShowResults(ManagedWindow.ManagedWindow):
    def __init__(self, db, uistate, track, handle_list, filtname):

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.filtname = filtname
        self.define_glade('test', const.rule_glade,)
        self.set_window(
            self.get_widget('test'),
            self.get_widget('title'),
            _('Filter Test'))

        nd = NameDisplay.displayer
        render = gtk.CellRendererText()
        
        tree = self.get_widget('list')
        model = gtk.ListStore(str, str)
        tree.set_model(model)

        column_n = gtk.TreeViewColumn(_('Name'), render, text=0)
        tree.append_column(column_n)

        column_n = gtk.TreeViewColumn(_('ID'), render, text=1)
        tree.append_column(column_n)

        self.get_widget('close').connect('clicked',self.close_window)

        new_list = [self.sort_val_from_handle(db, h) for h in handle_list]
        new_list.sort()
        handle_list = [ h[1] for h in new_list ]

        for p_handle in handle_list:
            person = db.get_person_from_handle(p_handle)
            name = nd.sorted(person)
            gid = person.get_gramps_id()
            
            model.append(row=[name, gid])

        self.show()

    def sort_val_from_handle(self, db, h):
        n = db.get_person_from_handle(h).get_primary_name()
        return (locale.strxfrm(NameDisplay.displayer.sort_string(n)),h)
    
    def close_window(self,obj):
        self.close()

