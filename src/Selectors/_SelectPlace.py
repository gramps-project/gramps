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

# $Id: SelectEvent.py 6155 2006-03-16 20:24:27Z rshura $

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
from RelLib import Place
from _BaseSelector import BaseSelector

#-------------------------------------------------------------------------
#
# SelectPlace
#
#-------------------------------------------------------------------------
class SelectPlace(BaseSelector):

    def get_column_titles(self):
        return [(_('Title'),4,350), (_('ID'),1,50)]

    def get_from_handle_func(self):
        return self.db.get_place_from_handle
        
    def get_cursor_func(self):
        return self.db.get_place_cursor

    def get_class_func(self):
        return Place

    def get_model_row_data(self,obj):
        name = obj.get_title()
        the_id = obj.get_gramps_id()
        return [name,the_id]
