#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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
import os
from gettext import gettext as _
from bsddb.db import DBError

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk
import gtk.glade
import gc

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
from PluginUtils import Tool, register_tool
import ManagedWindow

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

        glade_file = "%s/%s" % (os.path.dirname(__file__),"leak.glade")
        self.glade = gtk.glade.XML(glade_file,"top","gramps")

        window = self.glade.get_widget("top")
        self.eval = self.glade.get_widget("eval")
        self.ebuf = self.eval.get_buffer()
        gc.set_debug(gc.DEBUG_UNCOLLECTABLE|gc.DEBUG_OBJECTS|gc.DEBUG_SAVEALL)

        self.set_window(window,self.glade.get_widget('title'),self.title)

        self.glade.signal_autoconnect({
            "on_apply_clicked" : self.apply_clicked,
            "on_close_clicked" : self.close,
            })
        self.display()
        self.show()

    def build_menu_names(self,obj):
        return (self.title,None)

    def display(self):
        gc.collect()
        mylist = []
        if len(gc.garbage):
            for each in gc.garbage:
                try:
                    mylist.append(str(each))
                except DBError:
                    mylist.append('db.DB instance at %s' % id(each))
            self.ebuf.set_text(_("Uncollected objects:\n\n")
                               + '\n\n'.join(mylist))
        else:
            self.ebuf.set_text(_("No uncollected objects\n")
                               + str(gc.get_debug()))

    def apply_clicked(self,obj):
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

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------

if __debug__:
    register_tool(
        name = 'eval',
        category = Tool.TOOL_DEBUG,
        tool_class = Leak,
        options_class = LeakOptions,
        modes = Tool.MODE_GUI,
        translated_name = _("Show uncollected objects"),
        status = _("Stable"),
        author_name = "Donald N. Allingham",
        author_email = "don@gramps-project.org",
        description=_("Provide a window listing all uncollected objects"),
        )
