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
import cStringIO
import sys

import gtk
import gtk.glade

import Utils


class EvalWindow:

    def __init__(self):
        glade_file = "%s/%s" % (os.path.dirname(__file__),"eval.glade")
        self.glade = gtk.glade.XML(glade_file,"top")

        self.top = self.glade.get_widget("top")
        self.dbuf = self.glade.get_widget("display").get_buffer()
        self.ebuf = self.glade.get_widget("eval").get_buffer()
        self.error = self.glade.get_widget("error").get_buffer()

        self.glade.signal_autoconnect({
            "on_apply_clicked" : self.apply_clicked,
            "on_close_clicked" : self.close_clicked,
            "on_clear_clicked" : self.clear_clicked,
            })

        Utils.set_titles(self.top,self.glade.get_widget('title'),
                         "Python Evaluation Window")

    def apply_clicked(self,obj):
        text = self.ebuf.get_text(self.ebuf.get_start_iter(),
                                  self.ebuf.get_end_iter(),gtk.FALSE)

        outtext = cStringIO.StringIO()
        errtext = cStringIO.StringIO()
        sys.stdout = outtext
        sys.stderr = errtext
        exec(text)
        self.dbuf.set_text(outtext.getvalue())
        self.error.set_text(errtext.getvalue())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def clear_clicked(self,obj):
        self.dbuf.set_text("")
        self.ebuf.set_text("")
        self.error.set_text("")

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
    "Python evaluation window",
    category="Debug",
    description="Provides a window that can evaluate python code"
    )
        
