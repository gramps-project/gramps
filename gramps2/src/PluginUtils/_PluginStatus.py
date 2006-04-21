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
# PluginStatus
#
#-------------------------------------------------------------------------
class PluginStatus(ManagedWindow.ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self,state,uistate,track=[]):

        self.title = _("Plugin Status")
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.set_window(
            gtk.Dialog("%s - GRAMPS" % self.title,
                       uistate.window,
                       gtk.DIALOG_DESTROY_WITH_PARENT,
                       (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
            )
        )
        self.window.set_size_request(600,400)
        self.window.connect('delete-event',self.close)

        scrolled_window = gtk.ScrolledWindow()
        self.list = gtk.TreeView()
        self.model = gtk.ListStore(str, str, str)
        self.list.set_model(self.model)

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
        self.window.connect
        self.window.show_all()

        for i in PluginMgr.failmsg_list:
            err = i[1][0]
            if err == Errors.UnavailableError:
                self.model.append(row=[
                    '<span color="blue">%s</span>' % _('Unavailable'),
                    i[0], str(i[1][1])])
            else:
                self.model.append(row=[
                    '<span weight="bold" color="red">%s</span>' % _('Fail'),
                    i[0], str(i[1][1])])

        for i in PluginMgr.success_list:
            self.model.append(row=[
                '<span weight="bold" color="#267726">%s</span>' % _("OK"),
                i[0], ''])

        self.window.run()
        self.window.destroy()

    def build_menu_names(self,obj):
        return (self.title,None)
