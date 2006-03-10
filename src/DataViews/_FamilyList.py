# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import PageView
import DisplayModels
import const
import Utils
import Errors
from QuestionDialog import QuestionDialog, ErrorDialog

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('ID'),
    _('Father'),
    _('Mother'),
    _('Relationship'),
    _('Last Changed'),
    ]

#-------------------------------------------------------------------------
#
# FamilyListView
#
#-------------------------------------------------------------------------
class FamilyListView(PageView.ListView):
    def __init__(self,dbstate,uistate):

        signal_map = {
            'family-add'     : self.family_add,
            'family-update'  : self.row_update,
            'family-delete'  : self.row_delete,
            'family-rebuild' : self.build_tree,
            }

        PageView.ListView.__init__(self,'Family List View',dbstate,uistate,
                                   column_names,len(column_names),
                                   DisplayModels.FamilyModel,
                                   signal_map)
        self.updating = False

    def column_order(self):
        return self.dbstate.db.get_family_list_column_order()

    def get_stock(self):
        return 'gramps-family-list'

    def ui_definition(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
            </menu>
            <menu action="ViewMenu">
              <menuitem action="Filter"/>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
          </popup>
        </ui>'''

    def on_double_click(self,obj,event):
        return

    def add(self,obj):
        from Editors import EditFamily
        family = RelLib.Family()
        try:
            EditFamily(self.dbstate,self.uistate,[],family)
        except Errors.WindowActiveError:
            pass

    def family_add(self,handle_list):
        while not self.redraw(handle_list):
            pass

    def redraw(self,handle_list):
        if self.updating:
            return False
        self.updating = True
        self.row_add(handle_list)
        self.updating = False
        return True

    def remove(self,obj):
        return
    
    def edit(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            from Editors import EditFamily
            family = self.dbstate.db.get_family_from_handle(handle)
            try:
                EditFamily(self.dbstate,self.uistate,[],family)
            except Errors.WindowActiveError:
                pass
