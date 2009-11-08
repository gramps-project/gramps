#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009       Gary Burton
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
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gui.views.treemodels import EventModel
from _BaseSelector import BaseSelector
import config

#-------------------------------------------------------------------------
#
# SelectEvent
#
#-------------------------------------------------------------------------
class SelectEvent(BaseSelector):

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.width_key = 'interface.event-sel-width'
        self.height_key = 'interface.event-sel-height'

    def get_window_title(self):
        return _("Select Event")
        
    def get_model_class(self):
        return EventModel

    def get_column_titles(self):
        return [
            (_('Description'),       250, BaseSelector.TEXT, 0),
            (_('ID'),                75,  BaseSelector.TEXT, 1),
            (_('Type'),              75,  BaseSelector.TEXT, 2),
            (_('Main Participants'), 250, BaseSelector.TEXT, 6),
            (_('Date'),              150, BaseSelector.TEXT, 3),
            (_('Place'),             150, BaseSelector.TEXT, 4)
            ]

    def get_from_handle_func(self):
        return self.db.get_event_from_handle
        
    def get_handle_column(self):
        return 7

    def column_view_names(self):
        """
        Get correct column view names on which model is based
        """
        import DataViews
        return DataViews.EventView.COLUMN_NAMES
