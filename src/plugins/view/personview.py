# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2009       Nick Hall
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
Provide the person view.
"""

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".gui.personview")

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
from gui.views.pageview import NAVIGATION_PERSON
from gui.views.listview import ListView
from gui.views.treemodels import PeopleModel
import Utils
from BasicUtils import name_displayer
from QuestionDialog import ErrorDialog, QuestionDialog
import Errors
import Bookmarks
import config
from DdTargets import DdTargets
from gui.editors import EditPerson
from Filters.SideBar import PersonSidebarFilter
from gen.plug import CATEGORY_QR_PERSON

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# PersonView
#
#-------------------------------------------------------------------------
class PersonView(ListView):
    """
    PersonView class, derived from the ListView
    """
    COLUMN_NAMES = [
        _('Name'),
        _('ID'),
        _('Gender'),
        _('Birth Date'),
        _('Birth Place'),
        _('Death Date'),
        _('Death Place'),
        _('Spouse'),
        _('Last Changed'),
        ]
    
    ADD_MSG     = _("Add a new person")
    EDIT_MSG    = _("Edit the selected person")
    DEL_MSG     = _("Delete the selected person")
    FILTER_TYPE = "Person"
    QR_CATEGORY = CATEGORY_QR_PERSON

    def __init__(self, dbstate, uistate):
        """
        Create the Person View
        """
        signal_map = {
            'person-add'     : self.row_add,
            'person-update'  : self.row_update,
            'person-delete'  : self.row_delete,
            'person-rebuild' : self.object_build,
            }

        ListView.__init__(
            self, _('People'), dbstate, uistate,
            PersonView.COLUMN_NAMES, len(PersonView.COLUMN_NAMES), 
            PeopleModel,
            signal_map, dbstate.db.get_bookmarks(),
            Bookmarks.Bookmarks,
            multiple=True,
            filter_class=PersonSidebarFilter,
            markup=True)
            
        self.func_list = {
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            }

        config.connect("interface.filter", self.filter_toggle)
        
    def column_ord_setfunc(self, clist):
        self.dbstate.db.set_person_column_order(clist)

    def navigation_type(self):
        return NAVIGATION_PERSON

    def get_bookmarks(self):
        """
        Return the bookmark object
        """
        return self.dbstate.db.get_bookmarks()

    def drag_info(self):
        """
        Specify the drag type for a single selection
        """
        return DdTargets.PERSON_LINK
        
    def drag_list_info(self):
        """
        Specify the drag type for a multiple selected rows
        """
        return DdTargets.PERSON_LINK_LIST

    def column_order(self):
        """
        returns a tuple indicating the column order
        """
        return self.dbstate.db.get_person_column_order()

    def exact_search(self):
        """
        Returns a tuple indicating columns requiring an exact search
        """
        return (2,) # Gender ('female' contains the string 'male')

    def get_stock(self):
        """
        Use the gramps-person stock icon
        """
        return 'gramps-person'
    
    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'gramps-tree-group'

    def ui_definition(self):
        """
        Defines the UI string for UIManager
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
                <menuitem action="HomePerson"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="SetActive"/>
              <menuitem action="ColumnEdit"/>
              <menuitem action="FilterEdit"/>
              <placeholder name="Merge">
                <menuitem action="CmpMerge"/>
                <menuitem action="FastMerge"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="HomePerson"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <menuitem action="HomePerson"/>
            <separator/>
            <menuitem action="OpenAllNodes"/>
            <menuitem action="CloseAllNodes"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <separator/>
            <menu name="QuickReport" action="QuickReport">
              <menuitem action="Dummy"/>
            </menu>
          </popup>
        </ui>'''

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_person_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def _column_editor(self, obj):
        """
        returns a tuple indicating the column order
        """
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Person Columns'),
            self.uistate,
            self.dbstate.db.get_person_column_order(),
            PersonView.COLUMN_NAMES,
            self.set_column_order)

    def add(self, obj):
        person = gen.lib.Person()
        
        # attempt to get the current surname
        (model, pathlist) = self.selection.get_selected_rows()
        name = u""
        if len(pathlist) == 1:
            path = pathlist[0]
            if len(path) == 1:
                name = model.on_get_iter(path)
            else:
                node = model.on_get_iter(path)
                name = model.on_iter_parent(node)

        try:
            person.get_primary_name().set_surname(name)
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError:
            pass

    def edit(self, obj):
        for handle in self.selected_handles():
            person = self.dbstate.db.get_person_from_handle(handle)
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except Errors.WindowActiveError:
                pass

    def remove(self, obj):
        for sel in self.selected_handles():
            person = self.dbstate.db.get_person_from_handle(sel)
            self.active_person = person
            name = name_displayer.display(person) 

            msg = _('Deleting the person will remove the person '
                             'from the database.')
            msg = "%s %s" % (msg, Utils.data_recover_msg)
            QuestionDialog(_('Delete %s?') % name, 
                                          msg, 
                                          _('_Delete Person'), 
                                          self.delete_person_response)

    def delete_person_response(self):
        """
        Deletes the person from the database.
        """
        # set the busy cursor, so the user knows that we are working
        self.uistate.set_busy_cursor(True)

        # create the transaction
        trans = self.dbstate.db.transaction_begin()
        
        # create name to save
        person = self.active_person
        active_name = _("Delete Person (%s)") % name_displayer.display(person)

        # delete the person from the database
        gen.utils.delete_person_from_database(self.dbstate.db, person, trans)

        # remove the person from the list
        self.remove_from_person_list(person)

        # commit the transaction
        self.dbstate.db.transaction_commit(trans, active_name)

        # select the previously active person, turn off the busy cursor
        self.uistate.phistory.back()
        self.uistate.set_busy_cursor(False)

    def remove_from_person_list(self, person):
        """Remove the selected person from the list. A person object is
        expected, not an ID"""
        path = self.model.on_get_path(person.get_handle())
        (col, row) = path
        if row > 0:
            self.selection.select_path((col, row-1))
        elif row == 0 and self.model.on_get_iter(path):
            self.selection.select_path(path)

    def dummy_report(self, obj):
        """ For the xml UI definition of popup to work, the submenu 
            Quick Report must have an entry in the xml
            As this submenu will be dynamically built, we offer a dummy action
        """
        pass

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here, 
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.

        Special action groups for Forward and Back are created to allow the
        handling of navigation buttons. Forward and Back allow the user to
        advance or retreat throughout the history, and we want to have these
        be able to toggle these when you are at the end of the history or
        at the beginning of the history.
        """

        ListView.define_actions(self)

        self.all_action = gtk.ActionGroup(self.title + "/PersonAll")
        self.edit_action = gtk.ActionGroup(self.title + "/PersonEdit")

        self.all_action.add_actions([
                ('FilterEdit', None, _('Person Filter Editor'), None, None,
                self.filter_editor),
                ('OpenAllNodes', None, _("Expand all Nodes"), None, None, 
                 self.open_all_nodes), 
                ('Edit', gtk.STOCK_EDIT, _("action|_Edit..."), "<control>Return", 
                 _("Edit the selected person"), self.edit), 
                ('CloseAllNodes', None, _("Collapse all Nodes"), None, None, 
                 self.close_all_nodes), 
                ('QuickReport', None, _("Quick View"), None, None, None), 
                ('Dummy', None, '  ', None, None, self.dummy_report), 
                ])

        self.edit_action.add_actions(
            [
                ('Add', gtk.STOCK_ADD, _("_Add..."), "<control>Insert", 
                _("Add a new person"), self.add), 
                ('Remove', gtk.STOCK_REMOVE, _("_Remove"), "<control>Delete", 
                 _("Remove the Selected Person"), self.remove), 
                ('ColumnEdit', gtk.STOCK_PROPERTIES, _('_Column Editor...'), None, 
                 None, self._column_editor),  
                ('CmpMerge', None, _('Compare and _Merge...'), None, None, 
                 self.cmp_merge), 
                ('FastMerge', None, _('_Fast Merge...'), None, None, 
                 self.fast_merge), 
                ('ExportTab', None, _('Export View...'), None, None, self.export), 
                ])

        self._add_action_group(self.edit_action)
        self._add_action_group(self.all_action)

    def enable_action_group(self, obj):
        ListView.enable_action_group(self, obj)
        self.all_action.set_visible(True)
        self.edit_action.set_visible(False)
        self.edit_action.set_sensitive(not self.dbstate.db.readonly)
        
    def disable_action_group(self):
        ListView.disable_action_group(self)

        self.all_action.set_visible(False)
        self.edit_action.set_visible(False)

    def open_all_nodes(self, obj):
        self.uistate.status_text(_("Updating display..."))
        self.uistate.set_busy_cursor(True)

        self.list.expand_all()

        self.uistate.set_busy_cursor(False)
        self.uistate.modify_statusbar(self.dbstate)

    def close_all_nodes(self, obj):
        self.list.collapse_all()
        
    def cmp_merge(self, obj):
        mlist = self.get_selected_objects()

        if len(mlist) != 2:
            ErrorDialog(
        _("Cannot merge people"), 
        _("Exactly two people must be selected to perform a merge. "
          "A second person can be selected by holding down the "
          "control key while clicking on the desired person."))
        else:
            import Merge 
            person1 = self.db.get_person_from_handle(mlist[0])
            person2 = self.db.get_person_from_handle(mlist[1])
            if person1 and person2:
                Merge.PersonCompare(self.dbstate, self.uistate, person1, 
                                    person2, self.build_tree)
            else:
                ErrorDialog(
                    _("Cannot merge people"), 
                    _("Exactly two people must be selected to perform a "
                      "merge. A second person can be selected by holding "
                      "down the control key while clicking on the desired "
                      "person."))

    def fast_merge(self, obj):
        mlist = self.get_selected_objects()

        if len(mlist) != 2:
            ErrorDialog(
        _("Cannot merge people"), 
        _("Exactly two people must be selected to perform a merge. "
          "A second person can be selected by holding down the "
          "control key while clicking on the desired person."))
        else:
            import Merge
            
            person1 = self.db.get_person_from_handle(mlist[0])
            person2 = self.db.get_person_from_handle(mlist[1])
            if person1 and person2:
                Merge.MergePeopleUI(self.dbstate, self.uistate, person1, 
                                    person2, self.build_tree)
            else:
                ErrorDialog(
            _("Cannot merge people"), 
            _("Exactly two people must be selected to perform a merge. "
              "A second person can be selected by holding down the "
              "control key while clicking on the desired person."))
