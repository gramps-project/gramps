#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

"""
Provides a python evaluation window
"""
import os
import gtk
import gtk.glade
import gc
import string

from intl import gettext as _

class EvalWindow:

    def __init__(self):
        glade_file = "%s/%s" % (os.path.dirname(__file__),"leak.glade")
        self.glade = gtk.glade.XML(glade_file,"top")

        self.top = self.glade.get_widget("top")
        self.eval = self.glade.get_widget("eval")
        self.ebuf = self.eval.get_buffer()
        gc.set_debug(gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_OBJECTS | gc.DEBUG_SAVEALL)

        self.glade.signal_autoconnect({
            "on_apply_clicked" : self.apply_clicked,
            "on_close_clicked" : self.close_clicked,
            })
        self.display()

    def display(self):
        gc.collect()
        mylist = []
        if len(gc.garbage):
            for each in gc.garbage:
                mylist.append(str(each))
            self.ebuf.set_text("Uncollected objects:\n\n" + string.join(mylist,'\n\n'))
        else:
            self.ebuf.set_text("No uncollected objects\n" + str(gc.get_debug()))

    def apply_clicked(self,obj):
        self.display()
        
    def close_clicked(self,obj):
        self.top.destroy()
        
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_tool

def runtool(database,person,callback):
    EvalWindow()

register_tool(
    runtool,
    _("Show uncollected objects"),
    category=_("Debug"),
    description=_(""),
    )
        
