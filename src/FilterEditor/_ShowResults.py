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
import os
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
import gtk.glade
import gobject
import GrampsDisplay

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ManagedWindow

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class ShowResults(ManagedWindow.ManagedWindow):
    def __init__(self, db, uistate, track, handle_list, filtname):

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.filtname = filtname
        self.glade = gtk.glade.XML(const.rule_glade,'test',"gramps")

        self.set_window(
            self.glade.get_widget('test'),
            self.glade.get_widget('title'),
            _('Filter Test'))

        text = self.glade.get_widget('text')

        self.glade.get_widget('close').connect('clicked',self.close_window)

        n = []
        for p_handle in handle_list:
            p = db.get_person_from_handle(p_handle)
            n.append ("%s [%s]\n" % 
                        (p.get_primary_name().get_name(),p.get_gramps_id()))

        n.sort ()
        text.get_buffer().set_text(''.join(n))

        self.show()
            
    def close_window(self,obj):
        self.close()

