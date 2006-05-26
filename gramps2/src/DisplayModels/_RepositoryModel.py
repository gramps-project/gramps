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
import RelLib
from _BaseModel import BaseModel

#-------------------------------------------------------------------------
#
# RepositoryModel
#
#-------------------------------------------------------------------------
class RepositoryModel(BaseModel):

    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set()):
        self.gen_cursor = db.get_repository_cursor
        self.get_handles = db.get_repository_handles
        self.map = db.get_raw_repository_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_email,
            self.column_search_url,            
            self.column_handle,
            self.column_tooltip
            ]
        
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_email,
            self.column_search_url,            
            self.column_handle,            
            ]
        
        BaseModel.__init__(self, db, scol, order, tooltip_column=12,
                           search=search, skip=skip)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self,data):
        return unicode(data[0])

    def column_id(self,data):
        return unicode(data[1])

    def column_type(self,data):
        return str(RelLib.RepositoryType(data[2]))

    def column_name(self,data):
        return unicode(data[3])

    def column_city(self,data):
        try:
            if data[4]:
                addr = RelLib.Address()
                addr.unserialize(data[4][0])
                return addr.get_city()
            else:
                return u''
        except:
            return u''

    def column_street(self,data):
        try:
            if data[5]:
                addr = RelLib.Address()
                addr.unserialize(data[5][0])
                return addr.get_street()
            else:
                return u''
        except:
            return u''
        
    def column_county(self,data):
        try:
            if data[5]:
                addr = RelLib.Address()
                addr.unserialize(data[5][0])
                return addr.get_county()
            else:
                return u''
        except:
            return u''
    
    def column_state(self,data):
        try:
            if data[5]:
                addr = RelLib.Address()
                addr.unserialize(data[5][0])
                return addr.get_state()
            else:
                return u''
        except:
            return u''

    def column_country(self,data):
        try:
            if data[5]:
                addr = RelLib.Address()
                addr.unserialize(data[5][0])
                return addr.get_country()
            else:
                return u''
        except:
            return u''

    def column_postal_code(self,data):
        try:
            if data[5]:
                addr = RelLib.Address()
                addr.unserialize(data[5][0])
                return addr.get_postal_code()
            else:
                return u''
        except:
            return u''

    def column_phone(self,data):
        try:
            if data[5]:
                addr = RelLib.Address()
                addr.unserialize(data[5][0])
                return addr.get_phone()
            else:
                return u''
        except:
            return u''

    def column_email(self,data):
        if data[6]:
            for i in data[6]:
                url = RelLib.Url()
                url.unserialize(i)
                if url.get_type() == RelLib.UrlType.EMAIL:
                    return unicode(url.path)
        return u''

    def column_search_url(self,data):
        if data[6]:
            for i in data[6]:
                url = RelLib.Url()
                url.unserialize(i)
                if url.get_type() == RelLib.UrlType.WEB_SEARCH:
                    return unicode(url.path)
        return u''
    
    def column_home_url(self,data):
        if data[6]:
            for i in data[6]:
                url = RelLib.Url()
                url.unserialize(i)
                if url.get_type() == RelLib.UrlType.WEB_HOME:
                    return unicode(url.path)
        return u""

    def column_tooltip(self,data):
        return ""
#         try:
#             t = ToolTips.TipFromFunction(self.db, lambda: self.db.get_repository_from_handle(data[0]))
#         except:
#             log.error("Failed to create tooltip.", exc_info=True)
#         return t
