#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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

#----------------------------------------------------------------
#
# python
#
#----------------------------------------------------------------
from gettext import gettext as _
import cPickle as pickle

#----------------------------------------------------------------
#
# gtk
#
#----------------------------------------------------------------
import gtk
import pango
from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#----------------------------------------------------------------
#
# GRAMPS 
#
#----------------------------------------------------------------
import Config
import TreeTips
import Bookmarks
import Errors
from Filters import SearchBar
import const

NAVIGATION_NONE   = -1
NAVIGATION_PERSON = 0

EMPTY_SEARCH = (0, '', False)

#----------------------------------------------------------------
#
# PageView
#
#----------------------------------------------------------------
class PageView:
    
    def __init__(self,title,dbstate,uistate):
        self.title = title
        self.dbstate = dbstate
        self.uistate = uistate
        self.action_list = []
        self.action_toggle_list = []
        self.action_group = None
        self.additional_action_groups = []
        self.additional_uis = []
        self.widget = None
        self.ui = '<ui></ui>'
        self.dbstate.connect('no-database',self.disable_action_group)
        self.dbstate.connect('database-changed',self.enable_action_group)
        self.dirty = True
        self.active = False
        self.handle_col = 0
        self.selection = None
        self.func_list = {}

    def call_function(self, key):
        self.func_list.get(key)()

    def post(self):
        pass
    
    def set_active(self):
        self.active = True
        if self.dirty:
            self.uistate.set_busy_cursor(True)
            self.build_tree()
            self.uistate.set_busy_cursor(False)
            
    def set_inactive(self):
        self.active = False

    def build_tree(self):
        pass

    def navigation_type(self):
        return NAVIGATION_NONE
    
    def ui_definition(self):
        return self.ui

    def additional_ui_definitions(self):
        return self.additional_uis

    def disable_action_group(self):
        if self.action_group:
            self.action_group.set_visible(False)

    def enable_action_group(self,obj):
        if self.action_group:
            self.action_group.set_visible(True)

    def get_stock(self):
        try:
            return gtk.STOCK_MEDIA_MISSING
        except AttributeError:
            return gtk.STOCK_MISSING_IMAGE
        
    def get_title(self):
        return self.title

    def get_display(self):
        if not self.widget:
            self.widget = self.build_widget()
        return self.widget

    def build_widget(self):
        assert False

    def define_actions(self):
        assert False

    def _build_action_group(self):
        self.action_group = gtk.ActionGroup(self.title)
        if len(self.action_list) > 0:
            self.action_group.add_actions(self.action_list)
        if len(self.action_toggle_list) > 0:
            self.action_group.add_toggle_actions(self.action_toggle_list)

    def add_action(self, name, stock_icon, label, accel=None, tip=None,
                   callback=None):
        self.action_list.append((name,stock_icon,label,accel,tip,callback))

    def add_toggle_action(self, name, stock_icon, label, accel=None,
                          tip=None, callback=None, value=False):
        self.action_toggle_list.append((name,stock_icon,label,accel,
                                        tip,callback,value))

    def get_actions(self):
        if not self.action_group:
            self.define_actions()
            self._build_action_group()
        return [self.action_group] + self.additional_action_groups

    def add_action_group(self,group):
        self.additional_action_groups.append(group)

    def change_page(self):
        pass

    def edit(self,obj):
        pass

    def remove(self,obj):
        pass

    def add(self,obj):
        pass
    
    def key_press(self,obj,event):
        ret_key = gtk.gdk.keyval_from_name("Return")
        if event.keyval == ret_key and not event.state:
            self.edit(obj)
            return True
        return False

    def blist(self,store,path,iter,sel_list):
        handle = store.get_value(iter,self.handle_col)
        sel_list.append(handle)

    def selected_handles(self):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        return mlist

    def first_selected(self):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        if mlist:
            return mlist[0]
        else:
            return None


class BookMarkView(PageView):

    def __init__(self, title, state, uistate, bookmarks, bm_type):
        PageView.__init__(self, title, state, uistate)
        self.bm_type = bm_type
        self.setup_bookmarks(bookmarks)

    def goto_handle(self, obj):
        pass

    def setup_bookmarks(self, bookmarks):
        self.bookmarks = self.bm_type(
            self.dbstate, self.uistate, bookmarks, self.goto_handle)

    def add_bookmark(self, obj):
        import NameDisplay
        
        if self.dbstate.active:
            self.bookmarks.add(self.dbstate.active.get_handle())
            name = NameDisplay.displayer.display(self.dbstate.active)
            self.uistate.push_message(self.dbstate,
                                      _("%s has been bookmarked") % name)
        else:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "no one was selected."))

    def set_active(self):
        PageView.set_active(self)
        self.bookmarks.display()

    def set_inactive(self):
        PageView.set_inactive(self)
        self.bookmarks.undisplay()

    def edit_bookmarks(self, obj):
        self.bookmarks.edit()

    def enable_action_group(self, obj):
        PageView.enable_action_group(self, obj)

    def disable_action_group(self, obj):
        PageView.disable_action_group(self)

    def define_actions(self):
        self.book_action = gtk.ActionGroup(self.title + '/Bookmark')
        self.book_action.add_actions([
            ('AddBook','gramps-add-bookmark', _('_Add bookmark'),'<control>d',None,
             self.add_bookmark), 
            ('EditBook','gramps-edit-bookmark', _('_Edit bookmarks'),'<control>b',None,
             self.edit_bookmarks),
            ])

        self.add_action_group(self.book_action)
        

#----------------------------------------------------------------
#
# PersonNavView
#
#----------------------------------------------------------------
class PersonNavView(BookMarkView):

    def __init__(self,title,dbstate,uistate, callback=None):
        BookMarkView.__init__(self, title, dbstate, uistate,
                              dbstate.db.get_bookmarks(),
                              Bookmarks.Bookmarks)

    def navigation_type(self):
        return NAVIGATION_PERSON

    def define_actions(self):
        # add the Forward action group to handle the Forward button

        BookMarkView.define_actions(self)

        self.fwd_action = gtk.ActionGroup(self.title + '/Forward')
        self.fwd_action.add_actions([
            ('Forward',gtk.STOCK_GO_FORWARD,_("_Forward"),
             None, _("Go to the next person in the history"),
             self.fwd_clicked)
            ])

        # add the Backward action group to handle the Forward button
        self.back_action = gtk.ActionGroup(self.title + '/Backward')
        self.back_action.add_actions([
            ('Back',gtk.STOCK_GO_BACK,_("_Back"),
             None, _("Go to the previous person in the history"),
             self.back_clicked)
            ])

        self.add_action('HomePerson', gtk.STOCK_HOME, _("_Home"),
                        tip=_("Go to the default person"), callback=self.home)
        self.add_action('FilterEdit',  None, _('Person Filter Editor'), 
                        callback=self.filter_editor)

        self.other_action = gtk.ActionGroup(self.title + '/PersonOther')
        self.other_action.add_actions([
                ('SetActive', gtk.STOCK_HOME, _("Set _Home Person"), None, None, self.set_default_person),
                ])

        self.add_action_group(self.back_action)
        self.add_action_group(self.fwd_action)
        self.add_action_group(self.other_action)

    def disable_action_group(self):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        BookMarkView.disable_action_group(self)
        
        self.fwd_action.set_visible(False)
        self.back_action.set_visible(False)

    def enable_action_group(self,obj):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        BookMarkView.enable_action_group(self,obj)
        
        self.fwd_action.set_visible(True)
        self.back_action.set_visible(True)
        hobj = self.uistate.phistory
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

    def set_default_person(self,obj):
        active = self.dbstate.active
        if active:
            self.dbstate.db.set_default_person_handle(active.get_handle())

    def home(self,obj):
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.dbstate.change_active_person(defperson)

    def jumpto(self,obj):
        dialog = gtk.Dialog(_('Jump to by GRAMPS ID'),None,
                            gtk.DIALOG_NO_SEPARATOR)
        dialog.set_border_width(12)
        label = gtk.Label('<span weight="bold" size="larger">%s</span>' % _('Jump to by GRAMPS ID'))
        label.set_use_markup(True)
        dialog.vbox.add(label)
        dialog.vbox.set_spacing(10)
        dialog.vbox.set_border_width(12)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("%s: " % _('ID')),False)
        text = gtk.Entry()
        text.set_activates_default(True)
        hbox.pack_start(text,False)
        dialog.vbox.pack_start(hbox,False)
        dialog.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                           gtk.STOCK_JUMP_TO, gtk.RESPONSE_OK)
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.vbox.show_all()
        
        if dialog.run() == gtk.RESPONSE_OK:
            gid = text.get_text()
            person = self.dbstate.db.get_person_from_gramps_id(gid)
            if person:
                self.dbstate.change_active_person(person)
            else:
                self.uistate.push_message(
                    self.dbstate,
                    _("Error: %s is not a valid GRAMPS ID") % gid)
        dialog.destroy()

    def filter_editor(self,obj):
        from FilterEditor import FilterEditor

        try:
            FilterEditor('Person',const.custom_filters,
                         self.dbstate,self.uistate)
        except Errors.WindowActiveError:
            pass

    def fwd_clicked(self,obj,step=1):
        hobj = self.uistate.phistory
        hobj.lock = True
        if not hobj.at_end():
            try:
                handle = hobj.forward()
                self.dbstate.change_active_handle(handle)
                self.uistate.modify_statusbar(self.dbstate)
                hobj.mhistory.append(hobj.history[hobj.index])
                self.fwd_action.set_sensitive(not hobj.at_end())
                self.back_action.set_sensitive(True)
            except:
                hobj.clear()
                self.fwd_action.set_sensitive(False)
                self.back_action.set_sensitive(False)
        else:
            self.fwd_action.set_sensitive(False)
            self.back_action.set_sensitive(True)
        hobj.lock = False

    def back_clicked(self,obj,step=1):
        hobj = self.uistate.phistory
        hobj.lock = True
        if not hobj.at_front():
            try:
                handle = hobj.back()
                self.active = self.dbstate.db.get_person_from_handle(handle)
                self.uistate.modify_statusbar(self.dbstate)
                self.dbstate.change_active_handle(handle)
                hobj.mhistory.append(hobj.history[hobj.index])
                self.back_action.set_sensitive(not hobj.at_front())
                self.fwd_action.set_sensitive(True)
            except:
                hobj.clear()
                self.fwd_action.set_sensitive(False)
                self.back_action.set_sensitive(False)
        else:
            self.back_action.set_sensitive(False)
            self.fwd_action.set_sensitive(True)
        hobj.lock = False
        
    def handle_history(self, handle):
        """
        Updates the person history information
        """
        hobj = self.uistate.phistory
        if handle and not hobj.lock:
            hobj.push(handle)
            self.fwd_action.set_sensitive(not hobj.at_end())
            self.back_action.set_sensitive(not hobj.at_front())

    def change_page(self):
        hobj = self.uistate.phistory
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())
        self.other_action.set_sensitive(not self.dbstate.db.readonly)

#----------------------------------------------------------------
#
# ListView
#
#----------------------------------------------------------------
class ListView(BookMarkView):

    ADD_MSG = ""
    EDIT_MSG = ""
    DEL_MSG = ""

    def __init__(self, title, dbstate, uistate, columns, handle_col,
                 make_model, signal_map, get_bookmarks, bm_type,
                 multiple=False, filter_class=None):

        BookMarkView.__init__(self, title, dbstate, uistate,
                              get_bookmarks, bm_type)

        self.filter_class = filter_class
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
        self.sort_col = 0
        self.columns = []
        self.colinfo = columns
        self.handle_col = handle_col
        self.make_model = make_model
        self.signal_map = signal_map
        self.multiple_selection = multiple
        self.generic_filter = None
        dbstate.connect('database-changed',self.change_db)

    def build_filter_container(self, box, filter_class):
        self.filter_sidebar = filter_class(self.uistate,self.filter_clicked)
        self.filter_pane = self.filter_sidebar.get_widget()

        hpaned = gtk.HBox()
        hpaned.pack_start(self.vbox, True, True)
        hpaned.pack_end(self.filter_pane, False, False)
        self.filter_toggle(None, None, None, None)
        return hpaned

    def post(self):
        if self.filter_class:
            if Config.get(Config.FILTER):
                self.search_bar.hide()
                self.filter_pane.show()
            else:
                self.search_bar.show()
                self.filter_pane.hide()

    def filter_clicked(self):
        self.generic_filter = self.filter_sidebar.get_filter()
        self.build_tree()

    def add_bookmark(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        if mlist:
            self.bookmarks.add(mlist[0])
        else:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "nothing was selected."))

    def drag_info(self):
        return None

    def drag_begin(self, widget, *data):
        widget.drag_source_set_icon_stock(self.get_stock())
        
    def column_order(self):
        assert False
 
    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(4)
        self.vbox.set_spacing(4)
        
        self.search_bar = SearchBar(self.dbstate,self.uistate, self.build_tree)
        filter_box = self.search_bar.build()

        self.list = gtk.TreeView()
        self.list.set_rules_hint(True)
        self.list.set_headers_visible(True)
        self.list.set_headers_clickable(True)
        self.list.set_fixed_height_mode(True)
        self.list.connect('button-press-event',self.button_press)
        self.list.connect('key-press-event',self.key_press)
        if self.drag_info():
            self.list.connect('drag_data_get', self.drag_data_get)
            self.list.connect('drag_begin', self.drag_begin)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrollwindow.add(self.list)

        self.vbox.pack_start(filter_box,False)
        self.vbox.pack_start(scrollwindow,True)

        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
        self.inactive = False

        self.columns = []
        self.build_columns()
        self.selection = self.list.get_selection()
        if self.multiple_selection:
            self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.selection.connect('changed',self.row_changed)

        self.setup_filter()

        if self.filter_class:
            return self.build_filter_container(self.vbox, self.filter_class)
        else:
            return self.vbox
    
    def row_changed(self,obj):
        """Called with a row is changed. Check the selected objects from
        the person_tree to get the IDs of the selected objects. Set the
        active person to the first person in the list. If no one is
        selected, set the active person to None"""

        if self.drag_info():
            selected_ids = self.selected_handles()

            if len(selected_ids) == 1:
                self.list.drag_source_set(BUTTON1_MASK,
                                          [self.drag_info().target()],
                                          ACTION_COPY)
        
    def drag_data_get(self, widget, context, sel_data, info, time):
        selected_ids = self.selected_handles()

        if selected_ids:
            data = (self.drag_info().drag_type, id(self), selected_ids[0], 0)
            sel_data.set(sel_data.target, 8 ,pickle.dumps(data))

    def setup_filter(self):
        """
        Builds the default filters and add them to the filter menu.
        """
        cols = []
        for pair in [pair for pair in self.column_order() if pair[0]]:
            cols.append((self.colinfo[pair[1]],pair[1]))
        self.search_bar.setup_filter(cols)

    def goto_handle(self, handle):
        if not self.dbstate.active or self.inactive:
            return

        # mark inactive to prevent recusion
        self.inactive = True

        # select the active person in the person view

        try:
            path = self.model.on_get_path(handle)
            self.selection.unselect_all()
            self.selection.select_path(path)
            self.list.scroll_to_cell(path,None,1,0.5,0)
        except KeyError:
            self.selection.unselect_all()

        # disable the inactive flag
        self.inactive = False

    def column_clicked(self,obj,data):
        if self.sort_col != data:
            order = gtk.SORT_ASCENDING
        else:
            if (self.columns[data].get_sort_order() == gtk.SORT_DESCENDING
                or not self.columns[data].get_sort_indicator()):
                order = gtk.SORT_ASCENDING
            else:
                order = gtk.SORT_DESCENDING

        self.sort_col = data
        handle = self.first_selected()

        if Config.get(Config.FILTER):
            search = EMPTY_SEARCH
        else:
            search = (False,self.search_bar.get_value())

        self.model = self.make_model(self.dbstate.db, self.sort_col, order,
                                     search=search,
                                     sort_map=self.column_order())
        
        self.list.set_model(self.model)
        colmap = self.column_order()

        if handle:
            path = self.model.on_get_path(handle)
            self.selection.select_path(path)
            self.list.scroll_to_cell(path,None,1,0.5,0)
        for i in xrange(len(self.columns)):
            enable_sort_flag = (i==self.sort_col)
            self.columns[i].set_sort_indicator(enable_sort_flag)
        self.columns[self.sort_col].set_sort_order(order)
        
    def build_columns(self):
        for column in self.columns:
            self.list.remove_column(column)
            
        self.columns = []

        index = 0
        for pair in [pair for pair in self.column_order() if pair[0]]:
            name = self.colinfo[pair[1]]
            column = gtk.TreeViewColumn(name, self.renderer, text=pair[1])
            column.connect('clicked',self.column_clicked,index)
            column.set_resizable(True)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(pair[2])
            column.set_clickable(True)
            self.columns.append(column)
            self.list.append_column(column)
            index += 1

    def build_tree(self):
        if self.active:

            if Config.get(Config.FILTER):
                filter_info = (True, self.generic_filter)
            else:
                filter_info = (False, self.search_bar.get_value())

            self.model = self.make_model(self.dbstate.db,self.sort_col,
                                         search=filter_info)
            self.list.set_model(self.model)
            self.selection = self.list.get_selection()

            if const.use_tips and self.model.tooltip_column != None:
                self.tooltips = TreeTips.TreeTips(
                    self.list, self.model.tooltip_column, True)
            self.dirty = False
        else:
            self.dirty = True
        
    def filter_toggle(self,obj):
        if obj.get_active():
            self.search_bar.hide()
            self.filter_pane.show()
            active = True
        else:
            self.search_bar.show()
            self.filter_pane.hide()
            active = False
        Config.set(Config.FILTER, active)
        self.build_tree()

    def change_db(self,db):
        for sig in self.signal_map:
            db.connect(sig, self.signal_map[sig])

        if Config.get(Config.FILTER):
            search = EMPTY_SEARCH
        else:
            search = self.search_bar.get_value()
            
        self.model = self.make_model(self.dbstate.db, 0, search=search)
        
        self.list.set_model(self.model)
        self.build_columns()
        self.bookmarks.update_bookmarks(self.get_bookmarks())
        if self.active:
            self.build_tree()
            self.bookmarks.redraw()
        else:
            self.dirty = True

    def row_add(self,handle_list):
        if self.active:
            for handle in handle_list:
                self.model.add_row_by_handle(handle)
        else:
            self.dirty = True

    def row_update(self,handle_list):
        self.model.prev_handle = None
        if self.active:
            for handle in handle_list:
                self.model.update_row_by_handle(handle)
        else:
            self.dirty = True

    def row_delete(self,handle_list):
        if self.active:
            for handle in handle_list:
                self.model.delete_row_by_handle(handle)
        else:
            self.dirty = True

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here,
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.
        """
        
        BookMarkView.define_actions(self)

        self.edit_action = gtk.ActionGroup(self.title + '/ChangeOrder')
        self.edit_action.add_actions([
                ('Add', gtk.STOCK_ADD, _("_Add"), None, self.ADD_MSG, self.add),
                ('Remove', gtk.STOCK_REMOVE, _("_Remove"), None, self.DEL_MSG, self.remove),
                ('ColumnEdit', gtk.STOCK_PROPERTIES, _('_Column Editor'), None, None, self.column_editor),
                ])

        self.add_action_group(self.edit_action)

        self.add_action('Edit', gtk.STOCK_EDIT,_("_Edit"), tip=self.EDIT_MSG,
                        callback=self.edit)
        
        self.add_toggle_action('Filter', None, _('_Filter'),
                               callback=self.filter_toggle)

    def column_editor(self,obj):
        pass

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.edit(obj)
            return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = self.uistate.uimanager.get_widget('/Popup')
            if menu:
                menu.popup(None,None,None,event.button,event.time)
                return True
        return False
    
    def key_press(self,obj,event):
        ret_key = gtk.gdk.keyval_from_name("Return")
        if event.keyval == ret_key and not event.state:
            self.edit(obj)
            return True
        return False

    def double_click(self,obj,event):
        return False

    def change_page(self):
        self.edit_action.set_sensitive(not self.dbstate.db.readonly)

