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

from intl import gettext as _

class EvalWindow:

    def __init__(self):
        glade_file = "%s/%s" % (os.path.dirname(__file__),"eval.glade")
        self.glade = gtk.glade.XML(glade_file,"top")

        self.top = self.glade.get_widget("top")
        self.display = self.glade.get_widget("display")
        self.eval = self.glade.get_widget("eval")
        self.ebuf = self.eval.get_buffer()

        self.glade.signal_autoconnect({
            "on_apply_clicked" : self.apply_clicked,
            "on_close_clicked" : self.close_clicked,
            "on_clear_clicked" : self.clear_clicked,
            })

    def apply_clicked(self,obj):
        text = self.ebuf.get_text(self.ebuf.get_start_iter(),
                                  self.ebuf.get_end_iter(),gtk.FALSE)
        exec(text)

    def clear_clicked(self,obj):
        pass

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
    _("Python evaluation window"),
    category=_("Debug"),
    description=_("Provides a window that can evaluate python code")
    )
        
