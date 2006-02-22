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
import AutoComp
from GrampsWidgets import *

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
        
        self.window = self.top.get_widget("url_edit")

        title_label = self.top.get_widget("title")
        if not name or name == ", ":
            etitle =_('Internet Address Editor')
        else:
            etitle =_('Internet Address Editor for %s') % escape(name)
            

        Utils.set_titles(self.window,title_label, etitle,
                         _('Internet Address Editor'))

        self._setup_fields()
        self._connect_signals()
        self.show()

    def _connect_signals(self):
        self.window.connect('delete_event', self.on_delete_event)
        self.top.get_widget('button125').connect('clicked', self.close_window)
        self.top.get_widget('button124').connect('clicked', self.ok_clicked)
        self.top.get_widget('button130').connect('clicked', self.help_clicked)
        
    def _setup_fields(self):
        self.des  = MonitoredEntry(
            self.top.get_widget("url_des"), self.url.set_description,
            self.url.get_description, self.db.readonly)

        self.addr  = MonitoredEntry(
            self.top.get_widget("url_addr"), self.url.set_path,
            self.url.get_path, self.db.readonly)
        
        self.priv = PrivacyButton(self.top.get_widget("priv"),
                                  self.url, self.db.readonly)

        self.type_sel = MonitoredType(
            self.top.get_widget("type"), self.url.set_type,
            self.url.get_type, dict(Utils.web_types), RelLib.Url.CUSTOM)
            

    def build_menu_names(self,obj):
        if not self.name or self.name == ", ":
            etitle =_('Internet Address Editor')
        else:
            etitle =_('Internet Address Editor for %s') % escape(self.name)
        return (etitle, _('Internet Address Editor'))

    def on_delete_event(self,*obj):
        self.close()

    def close_window(self,*obj):
        self.close()

    def help_clicked(self,*obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-complete')

    def ok_clicked(self,obj):
        self.callback(self.url)
        self.close_window(obj)

