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
Provide a python evaluation window
"""
#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import cStringIO
import sys
from gen.ggettext import gettext as _
import traceback

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import Tool
import ManagedWindow
from glade import Glade

#-------------------------------------------------------------------------
#
# Actual tool
#
#-------------------------------------------------------------------------
class Eval(Tool.Tool,ManagedWindow.ManagedWindow):
    def __init__(self,dbstate, uistate, options_class, name, callback=None):
        self.title =  _("Python evaluation window")

        Tool.Tool.__init__(self,dbstate, options_class, name)
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)

        self.glade = Glade()

        window = self.glade.toplevel
        self.dbuf = self.glade.get_object("display").get_buffer()
        self.ebuf = self.glade.get_object("ebuf").get_buffer()
        self.error = self.glade.get_object("error").get_buffer()
        self.dbstate = dbstate

        self.glade.connect_signals({
            "on_apply_clicked" : self.apply_clicked,
            "on_close_clicked" : self.close,
            "on_clear_clicked" : self.clear_clicked,
            "on_delete_event"  : self.close,
            })

        self.set_window(window,self.glade.get_object('title'),self.title)
        self.show()

    def build_menu_names(self, obj):
        return (self.title,None)

    def apply_clicked(self, obj):
        text = unicode(self.ebuf.get_text(self.ebuf.get_start_iter(),
                                          self.ebuf.get_end_iter(),False))

        outtext = cStringIO.StringIO()
        errtext = cStringIO.StringIO()
        sys.stdout = outtext
        sys.stderr = errtext
        try:
            exec(text)
        except:
            traceback.print_exc()
        self.dbuf.set_text(outtext.getvalue())
        self.error.set_text(errtext.getvalue())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def clear_clicked(self, obj):
        self.dbuf.set_text("")
        self.ebuf.set_text("")
        self.error.set_text("")

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class EvalOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        Tool.ToolOptions.__init__(self, name,person_id)
