#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
from RelLib import *

#-------------------------------------------------------------------------
#
# UrlEditor class
#
#-------------------------------------------------------------------------
class UrlEditor:

    def __init__(self,parent,name,url):
        self.parent = parent
        self.url = url
        self.top = libglade.GladeXML(const.dialogFile, "url_edit")
        self.window = self.top.get_widget("url_edit")
        self.des  = self.top.get_widget("url_des")
        self.addr = self.top.get_widget("url_addr")
        self.priv = self.top.get_widget("priv")

        self.top.get_widget("urlTitle").set_text(name) 

        if url != None:
            self.des.set_text(url.get_description())
            self.addr.set_text(url.get_path())
            self.priv.set_active(url.getPrivacy())

        self.top.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_url_edit_ok_clicked" : self.on_url_edit_ok_clicked
            })

    def on_url_edit_ok_clicked(self,obj):
        des = self.des.get_text()
        addr = self.addr.get_text()
        priv = self.priv.get_active()
        
        if self.url == None:
            self.url = Url()
            self.parent.ulist.append(self.url)
        
        self.update_url(des,addr,priv)
        self.parent.redraw_url_list()
        Utils.destroy_passed_object(obj)

    def update_url(self,des,addr,priv):
        if self.url.get_path() != addr:
            self.url.set_path(addr)
            self.parent.lists_changed = 1
        
        if self.url.get_description() != des:
            self.url.set_description(des)
            self.parent.lists_changed = 1

        if self.url.getPrivacy() != priv:
            self.url.setPrivacy(priv)
            self.parent.lists_changed = 1

