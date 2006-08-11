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
import time
from gettext import gettext as _
import logging
log = logging.getLogger(".")

try:
    set()
except:
    from sets import Set as set

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
import DateHandler
import RelLib
from _BaseModel import BaseModel

#-------------------------------------------------------------------------
#
# MediaModel
#
#-------------------------------------------------------------------------
class MediaModel(BaseModel):

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_media_cursor
        self.map = db.get_raw_object_data
        
        self.fmap = [
            self.column_description,
            self.column_id,
            self.column_mime,
            self.column_path,
            self.column_change,
            self.column_date,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_description,
            self.column_id,
            self.column_mime,
            self.column_path,
            self.sort_change,
            self.column_date,
            self.column_handle,
            ]
        BaseModel.__init__(self, db, scol, order, tooltip_column=7,
                           search=search, skip=skip, sort_map=sort_map)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_description(self,data):
        try:
            return unicode(data[4])
        except:
            return unicode(data[4],'latin1')

    def column_path(self,data):
        try:
            return unicode(data[2])
        except:
            return unicode(data[2].encode('iso-8859-1'))

    def column_mime(self,data):
        if data[3]:
            return unicode(data[3])
        else:
            return _('Note')

    def column_id(self,data):
        return unicode(data[1])

    def column_date(self,data):
        if data[9]:
            date = RelLib.Date()
            date.unserialize(data[9])
            return unicode(DateHandler.displayer.display(date))
        return u''

    def column_handle(self,data):
        return unicode(data[0])

    def sort_change(self,data):
        return "%012x" % data[8]

    def column_change(self,data):
        return unicode(time.strftime('%x %X',time.localtime(data[8])),
                       GrampsLocale.codeset)

    def column_tooltip(self,data):
        if const.use_tips:
            try:
                t = ToolTips.TipFromFunction(self.db, lambda:
                                             self.db.get_object_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.", exc_info=True)
            return t
        else:
            return u''
