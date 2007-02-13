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
# $Id: _PlaceModel.py 8011 2007-01-29 19:13:15Z dallingham $

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import time
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ToolTips
import GrampsLocale
from _BaseModel import BaseModel

#-------------------------------------------------------------------------
#
# PlaceModel
#
#-------------------------------------------------------------------------
class NoteModel(BaseModel):

    HANDLE_COL = 2

    def __init__(self,db,scol=0,order=gtk.SORT_ASCENDING,search=None,
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_place_cursor
        self.map = db.get_raw_place_data
        self.fmap = [
            self.column_id,
            self.column_preview,
            self.column_handle,
            ]
        self.smap = [
            self.column_id,
            self.column_preview,
            self.column_handle,
            ]
        BaseModel.__init__(self, db, scol, order,
                           search=search, skip=skip, sort_map=sort_map)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self,data):
        return "<Place Holder>"

    def column_id(self,data):
        return "<Place Holder>"

    def column_preview(self,data):
        return "<Place Holder>"

    def sort_change(self,data):
        return "<Place Holder>"
    
    def column_change(self,data):
        return "<Place Holder>"

    def column_tooltip(self,data):
        return ''
