#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# UrlEditor class
#
#-------------------------------------------------------------------------
class UrlEditor:

    def __init__(self,parent,name,url,callback,parent_window=None):
        self.parent = parent
        self.url = url
        self.callback = callback
        self.top = gtk.glade.XML(const.dialogFile, "url_edit","gramps")
        self.window = self.top.get_widget("url_edit")
        self.des  = self.top.get_widget("url_des")
        self.addr = self.top.get_widget("url_addr")
        self.priv = self.top.get_widget("priv")
        title_label = self.top.get_widget("title")

        if name == ", ":
            etitle =_('Internet Address Editor')
        else:
            etitle =_('Internet Address Editor for %s') % name,
            

        Utils.set_titles(self.window,title_label, etitle,
                         _('Internet Address Editor'))
        if url != None:
            self.des.set_text(url.get_description())
            self.addr.set_text(url.get_path())
            self.priv.set_active(url.get_privacy())

        self.top.signal_autoconnect({
            "on_help_url_clicked" : self.on_help_clicked,
            "on_ok_url_clicked" : self.on_url_edit_ok_clicked,
            "on_cancel_url_clicked" : self.close,
            "on_url_edit_delete_event" : self.on_delete_event,
            })

        if parent_window:
            self.window.set_transient_for(parent_window)
        self.parent.child_windows.append(self)
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()
        self.parent.child_windows.remove(self)

    def close(self,obj):
        self.remove_itself_from_menu()
        self.parent.child_windows.remove(self)
        self.window.destroy()

    def add_itself_to_menu(self):
        label = _('Internet Address Editor')
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.menu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')

    def on_url_edit_ok_clicked(self,obj):
        des = unicode(self.des.get_text())
        addr = unicode(self.addr.get_text())
        priv = self.priv.get_active()
        
        if self.url == None:
            self.url = RelLib.Url()
            self.parent.ulist.append(self.url)
        
        self.update_url(des,addr,priv)
        self.callback(self.url)
        self.close(obj)

    def update_url(self,des,addr,priv):
        if self.url.get_path() != addr:
            self.url.set_path(addr)
            self.parent.lists_changed = 1
        
        if self.url.get_description() != des:
            self.url.set_description(des)
            self.parent.lists_changed = 1

        if self.url.get_privacy() != priv:
            self.url.set_privacy(priv)
            self.parent.lists_changed = 1
