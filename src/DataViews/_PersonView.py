#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
PersonView interface
"""

__author__ = "Don Allingham"
__revision__ = "$Revision$"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------

from gettext import gettext as _
import cPickle as pickle

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import gtk
import pango
from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
from DisplayModels import PeopleModel
import PageView
import NameDisplay
import Utils
import QuestionDialog
import TreeTips
import Errors
import Config
import const
import GrampsDb

from Editors import EditPerson
from Filters import SearchBar
from Filters.SideBar import PersonSidebarFilter
from DdTargets import DdTargets

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    _('Spouse'),
    _('Last Change'),
    ]
        
class PersonView(PageView.PersonNavView):
    """
    PersonView interface
    """

    def __init__(self, dbstate, uistate):
        """
        Creates the new PersonView interface, with the current dbstate and uistate
        """
        PageView.PersonNavView.__init__(self, _('People'), dbstate, uistate)
        
        self.inactive = False
        dbstate.connect('database-changed', self.change_db)
        self.handle_col = PeopleModel.COLUMN_INT_ID
        self.model = None
        self.generic_filter = None

        self.func_list = {
            'F2' : self.key_goto_home_person,
            'F3' : self.key_edit_selected_person,
            '<CONTROL>BackSpace' : self.key_delete_selected_person,
            '<CONTROL>J' : self.jump,
            }
        self.dirty = True

        Config.client.notify_add("/apps/gramps/interface/filter",
                                 self.filter_toggle)
        
    def change_page(self):
        PageView.PersonNavView.change_page(self)
        self.edit_action.set_visible(True)
        self.edit_action.set_sensitive(not self.dbstate.db.readonly)

    def set_active(self):
        PageView.PersonNavView.set_active(self)
        self.key_active_changed = self.dbstate.connect('active-changed',
                                                       self.goto_active_person)
        self.goto_active_person()
    
    def set_inactive(self):
        if self.active:
            PageView.PersonNavView.set_inactive(self)
            self.dbstate.disconnect(self.key_active_changed)
            
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

        PageView.PersonNavView.define_actions(self)

        self.all_action = gtk.ActionGroup(self.title + "/PersonAll")
        self.edit_action = gtk.ActionGroup(self.title + "/PersonEdit")

        self.all_action.add_actions([
                ('OpenAllNodes', None, _("Expand all nodes"), None, None, 
                 self.open_all_nodes),
                ('Edit', gtk.STOCK_EDIT, _("_Edit"), "<control>Return", 
                 _("Edit the selected person"), self.edit),
                ('CloseAllNodes', None, _("Collapse all nodes"), None, None, 
                 self.close_all_nodes),
                ])

        self.edit_action.add_actions(
            [
                ('Add', gtk.STOCK_ADD, _("_Add"), "<control>Insert", 
		 _("Add a new person"), self.add),
                ('Remove', gtk.STOCK_REMOVE, _("_Remove"), "<control>Delete", 
                 _("Remove the selected person"), self.remove),
                ('ColumnEdit', gtk.STOCK_PROPERTIES, _('_Column Editor'), None, 
                 None, self.column_editor),
                ('CmpMerge', None, _('_Compare and merge'), None, None, 
                 self.cmp_merge),
                ('FastMerge', None, _('_Fast merge'), None, None, 
                 self.fast_merge),
                ('ExportTab', None, _('Export view'), None, None, self.export),
                ])

        self.add_action_group(self.edit_action)
        self.add_action_group(self.all_action)

    def enable_action_group(self, obj):
        PageView.PersonNavView.enable_action_group(self, obj)
        self.all_action.set_visible(True)
        self.edit_action.set_visible(False)
        self.edit_action.set_sensitive(not self.dbstate.db.readonly)
        
    def disable_action_group(self):
        PageView.PersonNavView.disable_action_group(self)

        self.all_action.set_visible(False)
        self.edit_action.set_visible(False)

    def cmp_merge(self, obj):
        mlist = self.get_selected_objects()

        if len(mlist) != 2:
            QuestionDialog.ErrorDialog(
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
                QuestionDialog.ErrorDialog(
                    _("Cannot merge people"),
                    _("Exactly two people must be selected to perform a "
                      "merge. A second person can be selected by holding "
                      "down the control key while clicking on the desired "
                      "person."))

    def fast_merge(self, obj):
        mlist = self.get_selected_objects()

        if len(mlist) != 2:
            QuestionDialog.ErrorDialog(
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
                QuestionDialog.ErrorDialog(
		    _("Cannot merge people"),
		    _("Exactly two people must be selected to perform a merge. "
		      "A second person can be selected by holding down the "
		      "control key while clicking on the desired person."))
                
    def column_editor(self, obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Person Columns'),
            self.uistate,
            self.dbstate.db.get_person_column_order(),
            column_names,
            self.set_column_order)

    def set_column_order(self, column_list):
        self.dbstate.db.set_person_column_order(column_list)
        self.build_columns()
        self.setup_filter()

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-person'

    def start_expand(self, *obj):
        self.uistate.set_busy_cursor(True)

    def expanded(self, *obj):
        self.uistate.set_busy_cursor(False)

    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        hpaned = gtk.HBox()
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(4)
        self.vbox.set_spacing(4)
        
        self.search_bar = SearchBar(self.dbstate, self.uistate,
                                    self.build_tree, self.goto_active_person)
        filter_box = self.search_bar.build()
        
        self.tree = gtk.TreeView()
        self.tree.set_rules_hint(True)
        self.tree.set_headers_visible(True)
        self.tree.set_fixed_height_mode(True)
        self.tree.connect('key-press-event', self.key_press)
        self.tree.connect('start-interactive-search',self.open_all_nodes)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrollwindow.add(self.tree)
        scrollwindow.show_all()

        self.vbox.pack_start(filter_box, False)
        self.vbox.pack_start(scrollwindow, True)

        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize', pango.ELLIPSIZE_END)
        self.inactive = False

        self.columns = []

        self.setup_filter()
        self.build_columns()
        self.tree.connect('button-press-event', self.button_press)
        self.tree.connect('drag_data_get', self.drag_data_get)
        self.tree.connect('drag_begin', self.drag_begin)

        self.selection = self.tree.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.selection.connect('changed', self.row_changed)

        self.filter_sidebar = PersonSidebarFilter(self.uistate,
                                                  self.filter_clicked)
        self.filter_pane = self.filter_sidebar.get_widget()

        hpaned.pack_start(self.vbox, True, True)
        hpaned.pack_end(self.filter_pane, False, False)
        self.filter_toggle(None, None, None, None)
        return hpaned

    def post(self):
        if Config.get(Config.FILTER):
            self.search_bar.hide()
            self.filter_pane.show()
        else:
            self.search_bar.show()
            self.filter_pane.hide()
        
    def filter_clicked(self):
        self.generic_filter = self.filter_sidebar.get_filter()
        self.build_tree()

    def filter_toggle(self, client, cnxn_id, entry, data):
        if Config.get(Config.FILTER):
            self.search_bar.hide()
            self.filter_pane.show()
            active = True
        else:
            self.search_bar.show()
            self.filter_pane.hide()
            active = False
        self.build_tree()
        
    def drag_begin(self, widget, *data):
        widget.drag_source_set_icon_stock(self.get_stock())
        
    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
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
          </popup>
        </ui>'''

    def change_db(self, db):
        """
        Callback associated with DbState. Whenenver the database
        changes, this task is called. In this case, we rebuild the
        columns, and connect signals to the connected database. Tere
        is no need to store the database, since we will get the value
        from self.state.db
        """
        self.build_columns()
        self.setup_filter()
        self.db = db
        db.connect('person-add', self.person_added)
        db.connect('person-update', self.person_updated)
        db.connect('person-delete', self.person_removed)
        db.connect('person-rebuild', self.build_tree)

        if self.active:
            self.build_tree()
        else:
            self.dirty = True

        self.bookmarks.update_bookmarks(db.get_bookmarks())
        if self.active:
            self.bookmarks.redraw()

    def goto_active_person(self, obj=None):
        """
        Callback (and usable function) that selects the active person
        in the display tree.

        We have a bit of a problem due to the nature of how GTK works.
        We have unselect the previous path and select the new path. However,
        these cause a row change, which calls the row_change callback, which
        can end up calling change_active_person, which can call
        goto_active_person, causing a bit of recusion. Confusing, huh?

        Unforunately, we row_change has to be able to call change_active_person,
        because the can occur from the interface in addition to programatically.

        TO handle this, we set the self.inactive variable that we can check
        in row_change to look for this particular condition.
        """

        # if there is no active person, or if we have been marked inactive,
        # simply return

        if not self.dbstate.active or self.inactive:
            return

        # mark inactive to prevent recusion
        self.inactive = True

        self._goto()

        # disable the inactive flag
        self.inactive = False

        # update history
        self.handle_history(self.dbstate.active.handle)

    def _goto(self):
        """
        select the active person in the person view
        """

        person = self.dbstate.active
        try:
            if self.model and person:
                path = self.model.on_get_path(person.get_handle())
                
                group_name = person.get_primary_name().get_group_name()
                top_name = self.dbstate.db.get_name_group_mapping(group_name)
                top_path = self.model.on_get_path(top_name)
                self.tree.expand_row(top_path, 0)

                current = self.model.on_get_iter(path)
                selected = self.selection.path_is_selected(path)
                if current != person.get_handle() or not selected:
                    self.selection.unselect_all()
                    self.selection.select_path(path)
                    self.tree.scroll_to_cell(path, None, 1, 0.5, 0)
        except KeyError:
            self.selection.unselect_all()
            self.uistate.push_message(self.dbstate,
                                      _("Active person not visible"))
            self.dbstate.active = person
        
    def setup_filter(self):
        """
        Builds the default filters and add them to the filter menu.
        """

        cols = []
        cols.append((_("Name"), 0))
        for pair in self.dbstate.db.get_person_column_order():
            if not pair[0]:
                continue
            cols.append((column_names[pair[1]], pair[1]))

        self.search_bar.setup_filter(cols)

    def build_tree(self, skip=[]):
        """
        Creates a new PeopleModel instance. Essentially creates a complete
        rebuild of the data. We need to temporarily store the active person,
        since it can change when rows are unselected when the model is set.
        """
        if self.active:
            if Config.get(Config.FILTER):
                filter_info = (PeopleModel.GENERIC, self.generic_filter)
            else:
                filter_info = (PeopleModel.SEARCH, self.search_bar.get_value())

            self.model = PeopleModel(self.dbstate.db, filter_info, skip)
            active = self.dbstate.active
            self.tree.set_model(self.model)

            if const.use_tips and self.model.tooltip_column != None:
                self.tooltips = TreeTips.TreeTips(self.tree,
                                                  self.model.tooltip_column,
                                                  True)

            self.build_columns()
            self.setup_filter()
            self.dbstate.change_active_person(active)
            self._goto()
            self.dirty = False
        else:
            self.dirty = True

    def add(self, obj):
        person = RelLib.Person()
        
        # attempt to get the current surname

        (mode, paths) = self.selection.get_selected_rows()

        name = u""
        
        if len(paths) == 1:
            path = paths[0]
            if len(path) == 1:
                name = self.model.on_get_iter(path)
            else:
                node = self.model.on_get_iter(path)
                handle = self.model.on_get_value(node, 
                                                 PeopleModel.COLUMN_INT_ID)
                newp = self.dbstate.db.get_person_from_handle(handle)
                name = newp.get_primary_name().get_surname()
        try:
            person.get_primary_name().set_surname(name)
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError:
            pass

    def edit(self, obj):
        if self.dbstate.active:
            try:
                handle = self.dbstate.active.handle
                person = self.dbstate.db.get_person_from_handle(handle)
                EditPerson(self.dbstate, self.uistate, [], person)
            except Errors.WindowActiveError:
                pass

    def open_all_nodes(self, obj):
        self.uistate.status_text(_("Updating display..."))
        self.uistate.set_busy_cursor(True)

        self.tree.expand_all()

        self.uistate.set_busy_cursor(False)
        self.uistate.modify_statusbar(self.dbstate)

    def close_all_nodes(self, obj):
        self.tree.collapse_all()

    def remove(self, obj):
        mlist = self.get_selected_objects()
        if len(mlist) == 0:
            return
        
        for sel in mlist:
            person = self.dbstate.db.get_person_from_handle(sel)
            self.active_person = person
            name = NameDisplay.displayer.display(person) 

            msg = _('Deleting the person will remove the person '
                             'from the database.')
            msg = "%s %s" % (msg, Utils.data_recover_msg)
            QuestionDialog.QuestionDialog(_('Delete %s?') % name, 
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
        active_name = _("Delete Person (%s)") % NameDisplay.displayer.display(person)

        # delete the person from the database
        GrampsDb.delete_person_from_database(self.dbstate.db, person, trans)

        # remove the person from the list
        self.remove_from_person_list(person)

        # commit the transaction
        self.dbstate.db.transaction_commit(trans, active_name)

        # select the previously active person, turn off the busy cursor
        self.uistate.phistory.back()
        self.uistate.set_busy_cursor(False)

    def build_columns(self):
        for column in self.columns:
            self.tree.remove_column(column)
        try:
            column = gtk.TreeViewColumn(
                _('Name'),
                self.renderer,
                text=0,
                foreground=self.model.marker_color_column)
            
        except AttributeError:
            column = gtk.TreeViewColumn(_('Name'), self.renderer, text=0)
            
        column.set_resizable(True)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(225)
        self.tree.append_column(column)
        self.columns = [column]

        for pair in self.dbstate.db.get_person_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            try:
                column = gtk.TreeViewColumn(
                    name, self.renderer, markup=pair[1],
                    foreground=self.model.marker_color_column)
            except AttributeError:
                column = gtk.TreeViewColumn(
                    name, self.renderer, markup=pair[1])
                
            column.set_resizable(True)
            column.set_fixed_width(pair[2])
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            self.columns.append(column)
            self.tree.append_column(column)

    def row_changed(self, obj):
        """Called with a row is changed. Check the selected objects from
        the person_tree to get the IDs of the selected objects. Set the
        active person to the first person in the list. If no one is
        selected, set the active person to None"""

        selected_ids = self.get_selected_objects()
        if not self.inactive:
            try:
                if len(selected_ids) == 0:
                    self.dbstate.change_active_person(None)
                else:
                    handle = selected_ids[0]
                    person = self.dbstate.db.get_person_from_handle(handle)
                    self.dbstate.change_active_person(person)
            except:
                pass

        if len(selected_ids) == 1:
            self.tree.drag_source_set(BUTTON1_MASK,
                                      [DdTargets.PERSON_LINK.target()],
                                      ACTION_COPY)
        elif len(selected_ids) > 1:
            self.tree.drag_source_set(BUTTON1_MASK,
                                      [DdTargets.PERSON_LINK_LIST.target()],
                                      ACTION_COPY)
        self.uistate.modify_statusbar(self.dbstate)
        
    def drag_data_get(self, widget, context, sel_data, info, time):
        selected_ids = self.get_selected_objects()
        nonempty_ids = [h for h in selected_ids if h]
        if nonempty_ids:
            data = (DdTargets.PERSON_LINK.drag_type, 
                    id(self), nonempty_ids[0], 0)
            sel_data.set(sel_data.target, 8, pickle.dumps(data))

    def person_added(self, handle_list):
        if not self.model:
            return
        if self.active:
            self.dirty = False
            for node in handle_list:
                person = self.dbstate.db.get_person_from_handle(node)
                pname = person.get_primary_name()
                top = NameDisplay.displayer.name_grouping_name(self.db, pname)

                self.model.rebuild_data(self.model.current_filter)

                if not self.model.is_visable(node):
                    continue

                if (not self.model.mapper.has_top_node(top) or 
                    self.model.mapper.number_of_children(top) == 1):
                    path = self.model.on_get_path(top)
                    pnode = self.model.get_iter(path)
                    self.model.row_inserted(path, pnode)
                path = self.model.on_get_path(node)
                pnode = self.model.get_iter(path)
                self.model.row_inserted(path, pnode)
        else:
            self.dirty = True

    def func(self, tree, path, ex_list):
        ex_list.append(self.model.mapper.top_path2iter[path[0]])

    def person_removed(self, handle_list):
        if not self.model:
            return

        expand = []
        self.tree.map_expanded_rows(self.func, expand)

        self.build_tree(handle_list)
        for i in expand:
            path = self.model.mapper.top_iter2path.get(i)
            if path:
                self.tree.expand_row(path, False)
            
    def person_updated(self, handle_list):
        if not self.model:
            return
        
        self.model.clear_cache()
        for node in handle_list:
            person = self.dbstate.db.get_person_from_handle(node)
            try:
                oldpath = self.model.mapper.iter2path[node]
            except:
                return
            pathval = self.model.on_get_path(node)
            pnode = self.model.get_iter(pathval)

            # calculate the new data

            if person.primary_name.group_as:
                surname = person.primary_name.group_as
            else:
                base = person.primary_name.surname
                surname = self.dbstate.db.get_name_group_mapping(base)

            if oldpath[0] == surname:
                try:
                    self.model.build_sub_entry(surname)
                except:
                    self.model.calculate_data()
            else:
                self.model.calculate_data()
            
            # find the path of the person in the new data build
            newpath = self.model.mapper.temp_iter2path[node]
            
            # if paths same, just issue row changed signal

            if oldpath == newpath:
                self.model.row_changed(pathval, pnode)
            else:
                self.build_tree()
                break
            
        self.goto_active_person()

    def get_selected_objects(self):
        (mode, paths) = self.selection.get_selected_rows()
        mlist = []
        for path in paths:
            node = self.model.on_get_iter(path)
            handle = self.model.on_get_value(node, PeopleModel.COLUMN_INT_ID)
            if handle:
                mlist.append(handle)
        return mlist

    def remove_from_person_list(self, person):
        """Remove the selected person from the list. A person object is
        expected, not an ID"""
        path = self.model.on_get_path(person.get_handle())
        (col, row) = path
        if row > 0:
            self.selection.select_path((col, row-1))
        elif row == 0 and self.model.on_get_iter(path):
            self.selection.select_path(path)

    def button_press(self, obj, event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            handle = self.first_selected()
            person = self.dbstate.db.get_person_from_handle(handle)
            if person:
                try:
                    EditPerson(self.dbstate, self.uistate, [], person)
                except Errors.WindowActiveError:
                    pass
                return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = self.uistate.uimanager.get_widget('/Popup')
            if menu:
                menu.popup(None, None, None, event.button, event.time)
                return True
        return False

    def key_press(self,obj,event):
        if not event.state or event.state  in (gtk.gdk.MOD2_MASK,):
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                if self.dbstate.active:
                    self.edit(obj)
                    return True
                else:
                    store, paths = self.selection.get_selected_rows()
                    if paths and len(paths[0]) == 1 :
                        if self.tree.row_expanded(paths[0]):
                            self.tree.collapse_row(paths[0])
                        else:
                            self.tree.expand_row(paths[0], 0)
                        return True
        return False

    def key_goto_home_person(self):
        self.home(None)
        self.uistate.push_message(self.dbstate,
                                  _("Go to default person"))

    def key_edit_selected_person(self):
        self.edit(None)
        self.uistate.push_message(self.dbstate,
                                  _("Edit selected person"))


    def key_delete_selected_person(self):
        self.remove(None)
        self.uistate.push_message(self.dbstate,
                                  _("Delete selected person"))

    def export(self, obj):
        chooser = gtk.FileChooserDialog(
            _("Export view as spreadsheet"),
            self.uistate.window, 
            gtk.FILE_CHOOSER_ACTION_SAVE,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_do_overwrite_confirmation(True)

        combobox = gtk.combo_box_new_text()
        label = gtk.Label(_("Format:"))
        label.set_alignment(1.0, 0.5)
        box = gtk.HBox()
        box.pack_start(label, True, True, padding=12)
        box.pack_start(combobox, False, False)
        combobox.append_text(_('CSV'))
        combobox.append_text(_('Open Document Spreadsheet'))
        combobox.set_active(0)
        box.show_all()
        chooser.set_extra_widget(box)

        while True:
            value = chooser.run()
            fn = chooser.get_filename()
            fl = combobox.get_active()
            if value == gtk.RESPONSE_OK:
                if fn:
                    chooser.destroy()
                    break
            else:
                chooser.destroy()
                return
        self.write_tabbed_file(fn, fl)

    def write_tabbed_file(self, name, type):
        """
        Writes a tabbed file to the specified name. The output file type is determined
        by the type variable.
        """
        
        # Select the correct output format
        if type == 0:
            from CSVTab import CSVTab as tabgen
        else:
            from ODSTab import ODSTab as tabgen

        # build the active data columns, prepending 0 for the name column, then
        # derive the column names fromt the active data columns

        data_cols = [0] + [pair[1] \
                               for pair in self.dbstate.db.get_person_column_order() \
                               if pair[0]]

        cnames = [column_names[i] for i in data_cols]

        # create the output tabbed document, and open it

        ofile = tabgen(len(cnames))
        ofile.open(name)

        # start the current page
        ofile.start_page()

        # open the header row, write the column names, and close the row
        ofile.start_row()
        for name in cnames:
            ofile.write_cell(name)
        ofile.end_row()

        # The tree model works different from the rest of the list-based models,
        # since the iterator method only works on top level nodes. So we must 
        # loop through based off of paths

        path = (0,)
        node = self.model.on_get_iter(path)
        while node:
            real_iter = self.model.get_iter(path)
            for subindex in range(0, self.model.iter_n_children(real_iter)):
                subpath = ((path[0],subindex))
                row = self.model[subpath]
                ofile.start_row()
                for index in data_cols:
                    ofile.write_cell(row[index])
                ofile.end_row()
            node = self.model.on_iter_next(node)
            path = (path[0]+1,)
        ofile.end_page()
        ofile.close()
            
