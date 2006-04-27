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
# Python modules
#
#-------------------------------------------------------------------------
import traceback
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import ManagedWindow
import Errors
import _PluginMgr as PluginMgr

#-------------------------------------------------------------------------
#
# PluginStatus: overview of all plugins
#
#-------------------------------------------------------------------------
class PluginStatus(ManagedWindow.ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self, state, uistate, track=[]):

        self.title = _("Plugin Status")
        ManagedWindow.ManagedWindow.__init__(self,uistate,track,self.__class__)

        self.set_window(gtk.Dialog("",uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, self.title)
        self.window.set_size_request(600,400)
        self.window.connect('response', self.close)
        
        scrolled_window = gtk.ScrolledWindow()
        self.list = gtk.TreeView()
        self.model = gtk.ListStore(str, str, str, object)
        self.selection = self.list.get_selection()
        
        self.list.set_model(self.model)
        self.list.set_rules_hint(True)
        self.list.connect('button-press-event', self.button_press)
        self.list.append_column(
            gtk.TreeViewColumn(_('Status'), gtk.CellRendererText(),
                               markup=0))
        self.list.append_column(
            gtk.TreeViewColumn(_('File'), gtk.CellRendererText(),
                               text=1))
        self.list.append_column(
            gtk.TreeViewColumn(_('Message'), gtk.CellRendererText(),
                               text=2))

        scrolled_window.add(self.list)
        self.window.vbox.add(scrolled_window)
        self.window.show_all()

        for i in PluginMgr.failmsg_list:
            err = i[1][0]
            
            if err == Errors.UnavailableError:
                self.model.append(row=[
                    '<span color="blue">%s</span>' % _('Unavailable'),
                    i[0], str(i[1][1]), None])
            else:
                self.model.append(row=[
                    '<span weight="bold" color="red">%s</span>' % _('Fail'),
                    i[0], str(i[1][1]), i[1]])

        for i in PluginMgr.success_list:
            modname = i[1].__name__
            descr = PluginMgr.mod2text.get(modname,'')
            self.model.append(row=[
                '<span weight="bold" color="#267726">%s</span>' % _("OK"),
                i[0], descr, None])

    def button_press(self, obj, event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            model, node = self.selection.get_selected()
            data = model.get_value(node, 3)
            name = model.get_value(node, 1)
            if data:
                PluginTrace(self.uistate, self.track, data, name)
                
    def build_menu_names(self,obj):
        return ( _('Summary'),self.title)

#-------------------------------------------------------------------------
#
# Details for an individual plugin that failed
#
#-------------------------------------------------------------------------
class PluginTrace(ManagedWindow.ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self, uistate, track, data, name):
        self.name = name
        title = "%s: %s" % (_("Plugin Status"),name)
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.set_window(gtk.Dialog("",uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, title)
        self.window.set_size_request(600,400)
        self.window.connect('response', self.close)
        
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.text = gtk.TextView()
        scrolled_window.add(self.text)
        self.text.get_buffer().set_text(
            "".join(traceback.format_exception(data[0],data[1],data[2])))

        self.window.vbox.add(scrolled_window)
        self.window.show_all()

    def build_menu_names(self,obj):
        return (self.name, None)
