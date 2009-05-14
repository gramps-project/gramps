#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"""
Show uncollected objects in a window.
"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
from bsddb.db import DBError

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk
import pango
import gc

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import Tool
from gen.plug import PluginManager
import ManagedWindow
from QuestionDialog import InfoDialog
from glade import Glade

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------
class Leak(Tool.Tool,ManagedWindow.ManagedWindow):
    def __init__(self,dbstate, uistate, options_class, name, callback=None):
        self.title = _('Uncollected Objects Tool')

        Tool.Tool.__init__(self,dbstate, options_class, name)
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)

        self.glade = Glade()

        self.window = self.glade.toplevel
        self.scroll = self.glade.get_object("scrolledwindow1")
        #add a listview to the scrollable
        self.list = gtk.TreeView()
        self.list.set_headers_visible(True)
        self.list.connect('button-press-event', self._button_press)
        self.scroll.add(self.list)
        #make a model
        self.modeldata = []
        self.model = gtk.ListStore(int, str)
        self.list.set_model(self.model)
        
        #set the colums
        self.renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_('Number'), self.renderer, text=0)
        column.set_resizable(True)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.list.append_column(column)
        column = gtk.TreeViewColumn(_('Uncollected object'), self.renderer,
                                    text=1)
        column.set_resizable(True)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.list.append_column(column)
        self.selection = self.list.get_selection()
        
        gc.set_debug(gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_OBJECTS|gc.DEBUG_SAVEALL)

        self.set_window(self.window, self.glade.get_object('title'),
                        self.title)

        self.glade.connect_signals({
            "on_apply_clicked" : self.apply_clicked,
            "on_close_clicked" : self.close,
            })
        self.display()
        self.show()

    def build_menu_names(self, obj):
        return (self.title,None)

    def _button_press(self, obj, event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.referenced_in()
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.refers_to()
            return True

    def referenced_in(self):
        model, iter = self.selection.get_selected()
        if iter is not None:
            count = model.get_value(iter, 0)
            referrers = gc.get_referrers(self.modeldata[count])
            text = ""
            for referrer in referrers:
                text += str(referrer) + '\n'
            InfoDialog(_('Referrers of %d') % count, text, 
                        parent=self.window)

    def refers_to(self):
        model, iter = self.selection.get_selected()
        if iter is not None:
            count = model.get_value(iter, 0)
            referents = gc.get_referents(self.modeldata[count])
            text = ""
            for referent in referents:
                text += str(referent) + '\n'
            InfoDialog(_('%d refers to') % count, text, 
                        parent=self.window)

    def display(self):
        gc.collect()
        self.model.clear()
        count = 0
        if len(gc.garbage):
            for each in gc.garbage:
                try:
                    self.modeldata.append(each)
                    self.model.append((count, str(each)))
                except DBError:
                    self.modeldata.append(each)
                    self.model.append((count, 'db.DB instance at %s' % id(each)))
                count += 1

    def apply_clicked(self, obj):
        self.display()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class LeakOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        Tool.ToolOptions.__init__(self, name,person_id)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

if __debug__:
    pmgr = PluginManager.get_instance()
    pmgr.register_tool(
        name = 'leak',
        category = Tool.TOOL_DEBUG,
        tool_class = Leak,
        options_class = LeakOptions,
        modes = PluginManager.TOOL_MODE_GUI,
        translated_name = _("Show Uncollected Objects"),
        status = _("Stable"),
        author_name = "Donald N. Allingham",
        author_email = "don@gramps-project.org",
        description=_("Provide a window listing all uncollected objects"),
        )
