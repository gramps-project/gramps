#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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


__author__ = "Donald N. Allingham"
__revision__ = "$Revision$"


#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import DateHandler
from RelLib import Event
from _BaseSelector import BaseSelector

#-------------------------------------------------------------------------
#
# SelectEvent
#
#-------------------------------------------------------------------------
class SelectEvent(BaseSelector):

    def get_column_titles(self):
        return [(_('Description'), 4, 250), (_('ID'), 1, 75),
                (_('Type'), 2, 75), (_('Date'), 3, 150) ]

    def get_from_handle_func(self):
        return self.db.get_event_from_handle
        
    def get_cursor_func(self):
        return self.db.get_event_cursor

    def get_class_func(self):
        return Event

    def get_model_row_data(self,obj):
        desc = obj.get_description()
        the_id = obj.get_gramps_id()
        name = str(obj.get_type())
        date = DateHandler.get_date(obj)
        return [desc, the_id, name, date]
