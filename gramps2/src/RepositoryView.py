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
import EditRepository
import DisplayModels
import const
import Utils
from QuestionDialog import QuestionDialog, ErrorDialog

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('Name'),
    _('ID'),
    _('Type'),
    _('Home URL'),
    _('ZIP/Postal Code'),
    _('City'),
    _('County'),
    _('State'),
    _('Country'),
    _('Email'),
    _('Search URL'),
    ]

#-------------------------------------------------------------------------
#
# RepositoryView
#
#-------------------------------------------------------------------------
class RepositoryView(PageView.ListView):
    def __init__(self,dbstate,uistate):

        signal_map = {
            'repository-add'     : self.row_add,
            'repository-update'  : self.row_update,
            'repository-delete'  : self.row_delete,
            'repository-rebuild' : self.build_tree,
            }

        PageView.ListView.__init__(self,'Repository View',dbstate,uistate,
                                   column_names,len(column_names),
                                   DisplayModels.RepositoryModel,
                                   signal_map)

    def column_order(self):
        return self.dbstate.db.get_repository_column_order()

    def get_stock(self):
        return 'gramps-repository'

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
        handle = self.first_selected()
        place = self.dbstate.db.get_place_from_handle(handle)
        EditRepository.EditRepository(place,self.dbstate, self.uistate)

    def add(self,obj):
        EditRepository.EditRepository(RelLib.Repository(),self.dbstate, self.uistate)

    def remove(self,obj):
        for event_handle in self.selected_handles():
            db = self.dbstate.db
            person_list = [ handle for handle in
                            db.get_person_handles(False)
                            if db.get_person_from_handle(handle).has_handle_reference('Repository',event_handle) ]
            family_list = [ handle for handle in
                            db.get_family_handles()
                            if db.get_family_from_handle(handle).has_handle_reference('Repository',event_handle) ]
            
            event = db.get_event_from_handle(event_handle)

            ans = EditRepository.DelRepositoryQuery(event,db,
                                          person_list,family_list)

            if len(person_list) + len(family_list) > 0:
                msg = _('This place is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'people and families that reference it.')
            else:
                msg = _('Deleting place will remove it from the database.')
            
            msg = "%s %s" % (msg,Utils.data_recover_msg)
            descr = event.get_description()
            if descr == "":
                descr = event.get_gramps_id()
                
            QuestionDialog(_('Delete %s?') % descr, msg,
                           _('_Delete Repository'),ans.query_response)

    def edit(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            place = self.dbstate.db.get_place_from_handle(handle)
            EditRepository.EditRepository(place, self.dbstate, self.uistate)

