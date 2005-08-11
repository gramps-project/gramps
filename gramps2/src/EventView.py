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
import EventEdit
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
    _('Description'),
    _('ID'),
    _('Type'),
    _('Date'),
    _('Place'),
    _('Cause'),
    _('Last Changed'),
    ]

#-------------------------------------------------------------------------
#
# EventView
#
#-------------------------------------------------------------------------
class EventView(PageView.ListView):
    def __init__(self,dbstate,uistate):

        signal_map = {
            'event-add'     : self.row_add,
            'event-update'  : self.row_update,
            'event-delete'  : self.row_delete,
            'event-rebuild' : self.build_tree,
            }

        PageView.ListView.__init__(self,'Event View',dbstate,uistate,
                                   column_names,len(column_names),
                                   DisplayModels.EventModel,
                                   signal_map)

    def get_stock(self):
        return 'gramps-event'

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
        </ui>'''

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            handle = mlist[0]
            the_event = self.dbstate.db.get_event_from_handle(handle)
            EventEdit.EventEditor(the_event,self.dbstate, self.uistate)
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_context_menu(event)
            return True
        return False

    def build_context_menu(self,event):
        """Builds the menu with editing operations on the repository's list"""
        
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        if mlist:
            sel_sensitivity = 1
        else:
            sel_sensitivity = 0

        entries = [
            (gtk.STOCK_ADD, self.on_add_clicked,1),
            (gtk.STOCK_REMOVE, self.on_deletze_clicked,sel_sensitivity),
            (_("Edit"), self.on_edit_clicked,sel_sensitivity),
        ]

        menu = gtk.Menu()
        menu.set_title(_('Event Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def add(self,obj):
        EventEdit.EventEditor(RelLib.Event(),self.dbstate, self.uistate)

    def remove(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for event_handle in mlist:
            db = self.dbstate.db
            person_list = [ handle for handle in
                            db.get_person_handles(False)
                            if db.get_person_from_handle(handle).has_handle_reference('Event',event_handle) ]
            family_list = [ handle for handle in
                            db.get_family_handles()
                            if db.get_family_from_handle(handle).has_handle_reference('Event',event_handle) ]
            
            event = db.get_event_from_handle(event_handle)

            ans = EventEdit.DelEventQuery(event,db,
                                          person_list,family_list)

            if len(person_list) + len(family_list) > 0:
                msg = _('This event is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'people and families that reference it.')
            else:
                msg = _('Deleting event will remove it from the database.')
            
            msg = "%s %s" % (msg,Utils.data_recover_msg)
            QuestionDialog(_('Delete %s?') % event.get_gramps_id(), msg,
                           _('_Delete Event'),ans.query_response,
                           self.topWindow)

    def edit(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for handle in mlist:
            event = self.dbstate.db.get_event_from_handle(handle)
            EventEdit.EventEditor(event, self.dbstate, self.uistate)

