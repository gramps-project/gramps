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

# $Id: _SelectObject.py 6687 2006-05-17 04:43:53Z rshura $

#
# Written by Alex Roitman, 
# largely based on the MediaView and SelectPerson by Don Allingham
#

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
from DisplayModels import MediaModel
from _BaseSelector import BaseSelector

#-------------------------------------------------------------------------
#
# SelectObject
#
#-------------------------------------------------------------------------
class SelectObject(BaseSelector):

    def get_window_title(self):
        return _("Select Media Object")
        
    def get_model_class(self):
        return MediaModel

    def get_from_handle_func(self):
        return self.db.get_object_from_handle
        
    def get_handle_column(self):
        return 6

    def get_column_titles(self):
        return [
            (_('Title'), 350, BaseSelector.TEXT),
            (_('ID'),     75, BaseSelector.TEXT),
            (_('Type'),   75, BaseSelector.TEXT),
            ]
