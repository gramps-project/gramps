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

# $Id: _SelectNote.py $

"""Handling of selection dialog for selecting notes
"""

__author__ = "Benny Malengier"	 
__revision__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Python Modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS Modules
#
#-------------------------------------------------------------------------
from DisplayModels import NoteModel
from _BaseSelector import BaseSelector

#-------------------------------------------------------------------------
#
# SelectNote
#
#-------------------------------------------------------------------------
class SelectNote(BaseSelector):
    """ Class that handles the selection of a note
    """

    def get_window_title(self):
        return _("Select General Note")
        
    def get_model_class(self):
        return NoteModel

    def get_column_titles(self):
        return [
            (_('ID'),     75, BaseSelector.TEXT),
            (_('Type'), 0, BaseSelector.NONE),
            (_('Marker'), 0, BaseSelector.NONE),
            (_('Preview'), 350, BaseSelector.TEXT)
            ]
            
    def get_from_handle_func(self):
        return self.db.get_note_from_handle
        
    def get_handle_column(self):
        return 4
    
    def column_order(self):
        """
        returns a tuple indicating the column order
        """
        return self.db.get_note_column_order()
    
    def column_view_names(self):
        """
        Get correct column view names on which model is based
        """
        import DataViews
        return DataViews.NoteView.COLUMN_NAMES
    