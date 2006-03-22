#
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

#----------------------------------------------------------------
#
# python
#
#----------------------------------------------------------------
from TransUtils import sgettext as _
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
import TreeTips
import GenericFilter
import const

NAVIGATION_NONE   = -1
NAVIGATION_PERSON = 0

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

#----------------------------------------------------------------
#
# PersonNavView
#
#----------------------------------------------------------------
class PersonNavView(PageView):

    def __init__(self,title,dbstate,uistate):
        PageView.__init__(self,title,dbstate,uistate)

    def navigation_type(self):
        return NAVIGATION_PERSON

    def define_actions(self):
        # add the Forward action group to handle the Forward button

        self.fwd_action = gtk.ActionGroup(self.title + '/Forward')
        self.fwd_action.add_actions([
            ('Forward',gtk.STOCK_GO_FORWARD,"_Forward", None, None, self.fwd_clicked)
            ])

        # add the Backward action group to handle the Forward button
        self.back_action = gtk.ActionGroup(self.title + '/Backward')
        self.back_action.add_actions([
            ('Back',gtk.STOCK_GO_BACK,"_Back", None, None, self.back_clicked)
            ])

        self.add_action('HomePerson', gtk.STOCK_HOME, "_Home",
                        callback=self.home)
        self.add_action('SetActive', gtk.STOCK_HOME, "Set _Home Person",
                        callback=self.set_default_person)

        self.add_action_group(self.back_action)
        self.add_action_group(self.fwd_action)

    def disable_action_group(self):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.disable_action_group(self)
        
        self.fwd_action.set_visible(False)
        self.back_action.set_visible(False)

    def enable_action_group(self,obj):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.enable_action_group(self,obj)
        
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
                self.uistate.push_message(_("Error: %s is not a valid GRAMPS ID") % gid)
        dialog.destroy()

    def fwd_clicked(self,obj,step=1):
        hobj = self.uistate.phistory
        hobj.lock = True
        if not hobj.at_end():
            try:
                handle = hobj.forward()
                self.dbstate.active = self.dbstate.db.get_person_from_handle(handle)
                self.uistate.modify_statusbar()
                self.dbstate.change_active_handle(handle)
                hobj.mhistory.append(hobj.history[hobj.index])
                #self.redraw_histmenu()
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
                self.uistate.modify_statusbar()
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
            #self.redraw_histmenu()
            self.fwd_action.set_sensitive(not hobj.at_end())
            self.back_action.set_sensitive(not hobj.at_front())

    def change_page(self):
        hobj = self.uistate.phistory
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

#----------------------------------------------------------------
#
# ListView
#
#----------------------------------------------------------------
class ListView(PageView):

    def __init__(self, title, dbstate, uistate, columns, handle_col,
                 make_model, signal_map):
        PageView.__init__(self, title, dbstate, uistate)
        self.renderer = gtk.CellRendererText()
        self.renderer.set_property('ellipsize',pango.ELLIPSIZE_END)
        self.sort_col = 0
        self.columns = []
        self.colinfo = columns
        self.handle_col = handle_col
        self.make_model = make_model
        self.signal_map = signal_map
        dbstate.connect('database-changed',self.change_db)

    def drag_info(self):
        return None
        
    def column_order(self):
        assert False
 
    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(0)
        self.vbox.set_spacing(4)
        
        self.generic_filter_widget = GenericFilter.FilterWidget( self.uistate, self.build_tree)
        filter_box = self.generic_filter_widget.build()

        self.list = gtk.TreeView()
        self.list.set_rules_hint(True)
        self.list.set_headers_visible(True)
        self.list.set_headers_clickable(True)
        self.list.set_fixed_height_mode(True)
        self.list.connect('button-press-event',self.button_press)
        self.list.connect('key-press-event',self.key_press)
        if self.drag_info():
            self.list.connect('drag_data_get', self.drag_data_get)

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
        self.selection.connect('changed',self.row_changed)

        self.setup_filter()

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

        data = (self.drag_info().drag_type, id(self), selected_ids[0], 0)
        
        sel_data.set(sel_data.target, 8 ,pickle.dumps(data))

    def setup_filter(self):
        """
        Builds the default filters and add them to the filter menu.
        """
        default_filters = [
            [GenericFilter.Everyone, []],
            [GenericFilter.HasTextMatchingSubstringOf, ['',0,0]],
            [GenericFilter.HasTextMatchingRegexpOf, ['',0,1]],
            [GenericFilter.PeoplePrivate, []],
            ]
        self.generic_filter_widget.setup_filter( default_filters)        

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
        self.model = self.make_model(self.dbstate.db, self.sort_col,order)
        self.list.set_model(self.model)
        colmap = self.column_order()

        if handle:
            path = self.model.on_get_path(handle)
            self.selection.select_path(path)
            self.list.scroll_to_cell(path,None,1,0.5,0)
        for i in xrange(len(self.columns)):
            self.columns[i].set_sort_indicator(i==colmap[data][1])
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
            self.model = self.make_model(self.dbstate.db,self.sort_col)
            self.list.set_model(self.model)
            self.selection = self.list.get_selection()

            if const.use_tips and self.model.tooltip_column != None:
                self.tooltips = TreeTips.TreeTips(self.list,
                                                  self.model.tooltip_column,True)
            self.dirty = False
        else:
            self.dirty = True
        
    def change_db(self,db):
        for sig in self.signal_map:
            db.connect(sig, self.signal_map[sig])
        self.model = self.make_model(self.dbstate.db,0)
        self.list.set_model(self.model)
        self.build_columns()
        if self.active:
            self.build_tree()
        else:
            self.dirty = True

    def row_add(self,handle_list):
        if self.active:
            for handle in handle_list:
                self.model.add_row_by_handle(handle)

    def row_update(self,handle_list):
        if self.active:
            for handle in handle_list:
                self.model.update_row_by_handle(handle)

    def row_delete(self,handle_list):
        if self.active:
            for handle in handle_list:
                self.model.delete_row_by_handle(handle)

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here,
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.
        """

        self.add_action('Add',   gtk.STOCK_ADD,   "_Add",   callback=self.add)
        self.add_action('Edit',  gtk.STOCK_EDIT,  "_Edit",  callback=self.edit)
        self.add_action('Remove',gtk.STOCK_REMOVE,"_Remove",callback=self.remove)
        self.add_toggle_action('Filter', None, '_Filter',
                               callback=self.filter_toggle)

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

    def filter_toggle(self,obj):
        if obj.get_active():
            self.generic_filter_widget.show()
        else:
            self.generic_filter_widget.hide()
