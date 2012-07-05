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
# python modules
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.datehandler
from gui.views.treemodels.flatbasemodel import FlatBaseModel

#-------------------------------------------------------------------------
#
# SourceModel
#
#-------------------------------------------------------------------------
class SourceModel(FlatBaseModel):

    def __init__(self,db,scol=0, order=Gtk.SortType.ASCENDING,search=None,
                 skip=set(), sort_map=None):
        self.map = db.get_raw_source_data
        self.gen_cursor = db.get_source_cursor
        self.fmap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.column_change,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_title,
            self.column_id,
            self.column_author,
            self.column_abbrev,
            self.column_pubinfo,
            self.sort_change,
            ]
        FlatBaseModel.__init__(self,db,scol, order,tooltip_column=7,search=search,
                           skip=skip, sort_map=sort_map)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def do_get_n_columns(self):
        return len(self.fmap)+1

    def column_title(self,data):
        return unicode(data[2])

    def column_handle(self,data):
        return unicode(data[0])

    def column_author(self,data):
        return unicode(data[3])

    def column_abbrev(self,data):
        return unicode(data[7])

    def column_id(self,data):
        return unicode(data[1])

    def column_pubinfo(self,data):
        return unicode(data[4])

    def column_change(self,data):
        return gen.datehandler.format_time(data[8])
    
    def sort_change(self,data):
        return "%012x" % data[8]

    def column_tooltip(self,data):
        return u'Source tooltip'
