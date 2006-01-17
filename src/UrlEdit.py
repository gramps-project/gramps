#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
from gettext import gettext as _
import gc
from cgi import escape

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import GrampsDisplay
import DisplayState

from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# UrlEditor class
#
#-------------------------------------------------------------------------
class UrlEditor(DisplayState.ManagedWindow):

    def __init__(self, dbstate, uistate, track, name, url, callback):

        self.db = dbstate.db
        self.uistate = uistate
        self.state = dbstate
        self.callback = callback
        self.name = name
        
        DisplayState.ManagedWindow.__init__(self, uistate, track, url)
        if self.already_exist:
            return

        self.url = url
        self.callback = callback
        self.top = gtk.glade.XML(const.gladeFile, "url_edit","gramps")
        self.gladeif = GladeIf(self.top)
        
        self.window = self.top.get_widget("url_edit")
        self.des  = self.top.get_widget("url_des")
        self.addr = self.top.get_widget("url_addr")
        self.priv = self.top.get_widget("priv")
        title_label = self.top.get_widget("title")

        if not name or name == ", ":
            etitle =_('Internet Address Editor')
        else:
            etitle =_('Internet Address Editor for %s') % escape(name)
            

        Utils.set_titles(self.window,title_label, etitle,
                         _('Internet Address Editor'))
        if url != None:
            self.des.set_text(url.get_description())
            self.addr.set_text(url.get_path())
            self.priv.set_active(url.get_privacy())

        self.gladeif.connect('url_edit','delete_event', self.on_delete_event)
        self.gladeif.connect('button125','clicked', self.close)
        self.gladeif.connect('button124','clicked', self.on_url_edit_ok_clicked)
        self.gladeif.connect('button130','clicked', self.on_help_clicked)

        self.window.set_transient_for(self.parent_window)
        self.window.show()

    def build_menu_names(self,obj):
        if not self.name or self.name == ", ":
            etitle =_('Internet Address Editor')
        else:
            etitle =_('Internet Address Editor for %s') % escape(self.name)
        return (etitle, _('Internet Address Editor'))

    def on_delete_event(self,*obj):
        self.gladeif.close()
        gc.collect()

    def close(self,*obj):
        self.gladeif.close()
        self.window.destroy()
        gc.collect()

    def on_help_clicked(self,*obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-complete')

    def on_url_edit_ok_clicked(self,obj):
        des = unicode(self.des.get_text())
        addr = unicode(self.addr.get_text())
        priv = self.priv.get_active()
        
        self.update_url(des,addr,priv)
        self.callback(self.url)
        self.close(obj)

    def update_url(self,des,addr,priv):
        if self.url.get_path() != addr:
            self.url.set_path(addr)
        
        if self.url.get_description() != des:
            self.url.set_description(des)

        if self.url.get_privacy() != priv:
            self.url.set_privacy(priv)

