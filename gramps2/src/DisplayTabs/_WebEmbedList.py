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

# $Id$

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import RelLib
import Errors
from DdTargets import DdTargets
from _WebModel import WebModel
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class WebEmbedList(EmbeddedList):

    _HANDLE_COL = 3
    _DND_TYPE   = DdTargets.URL

    _column_names = [
        (_('Type')       , 0, 100), 
        (_('Path')       , 1, 200), 
        (_('Description'), 2, 150), 
        ]
    
    def __init__(self, dbstate, uistate, track, data):
        self.data = data
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('Internet'), WebModel)

    def get_icon_name(self):
        return (0,'stock_insert-url')

    def get_data(self):
        return self.data

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2))

    def add_button_clicked(self, obj):
        url = RelLib.Url()
        try:
            from Editors import EditUrl
            
            EditUrl(self.dbstate, self.uistate, self.track, 
                    '', url, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_callback(self, url):
        self.get_data().append(url)
        self.rebuild()

    def edit_button_clicked(self, obj):
        url = self.get_selected()
        if url:
            try:
                from Editors import EditUrl
                
                EditUrl(self.dbstate, self.uistate, self.track, 
                        '', url, self.edit_callback)
            except Errors.WindowActiveError:
                pass

    def edit_callback(self, url):
        self.rebuild()
