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
from gramps.gen.lib import Address, RepositoryType, Url, UrlType
from gramps.gen.datehandler import format_time
from gramps.gen.constfunc import cuni
from .flatbasemodel import FlatBaseModel
from gramps.gen.const import GRAMPS_LOCALE as glocale
#-------------------------------------------------------------------------
#
# RepositoryModel
#
#-------------------------------------------------------------------------
class RepositoryModel(FlatBaseModel):

    def __init__(self, db, scol=0, order=Gtk.SortType.ASCENDING, search=None,
                 skip=set(), sort_map=None):
        self.gen_cursor = db.get_repository_cursor
        self.get_handles = db.get_repository_handles
        self.map = db.get_raw_repository_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_locality,
            self.column_city,
            self.column_state,
            self.column_country,
            self.column_postal_code,
            self.column_email,
            self.column_search_url,
            self.column_private,
            self.column_change,
            ]
        
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_type,
            self.column_home_url,
            self.column_street,
            self.column_locality,
            self.column_city,
            self.column_state,
            self.column_country,
            self.column_postal_code,
            self.column_email,
            self.column_search_url,
            self.column_private,
            self.sort_change,           
            ]
        
        FlatBaseModel.__init__(self, db, scol, order, search=search, skip=skip,
                               sort_map=sort_map)

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.get_handles = None
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_id(self,data):
        return cuni(data[1])

    def column_type(self,data):
        return cuni(RepositoryType(data[2]))

    def column_name(self,data):
        return cuni(data[3])

    def column_city(self,data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_city()
        except:
            pass
        return cuni('')

    def column_street(self,data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_street()
        except:
            pass
        return cuni('')
        
    def column_locality(self,data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_locality()
        except:
            pass
        return cuni('')
    
    def column_state(self,data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_state()
        except:
            pass
        return cuni('')

    def column_country(self,data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_country()
        except:
            pass
        return cuni('')

    def column_postal_code(self,data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_postal_code()
        except:
            pass
        return cuni('')

    def column_phone(self,data):
        try:
            if data[5]:
                addr = Address()
                addr.unserialize(data[5][0])
                return addr.get_phone()
        except:
            pass
        return cuni('')

    def column_email(self,data):
        if data[6]:
            for i in data[6]:
                url = Url()
                url.unserialize(i)
                if url.get_type() == UrlType.EMAIL:
                    return cuni(url.path)
        return cuni('')

    def column_search_url(self,data):
        if data[6]:
            for i in data[6]:
                url = Url()
                url.unserialize(i)
                if url.get_type() == UrlType.WEB_SEARCH:
                    return cuni(url.path)
        return ''
    
    def column_home_url(self,data):
        if data[6]:
            for i in data[6]:
                url = Url()
                url.unserialize(i)
                if url.get_type() == UrlType.WEB_HOME:
                    return cuni(url.path)
        return ""

    def column_private(self, data):
        if data[8]:
            return 'gramps-lock'
        else:
            # There is a problem returning None here.
            return ''

    def sort_change(self,data):
        return "%012x" % data[7]

    def column_change(self,data):
        return format_time(data[7])
