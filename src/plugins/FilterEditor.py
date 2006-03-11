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

"""Generic Filtering Routines"""

__author__ = "Don Allingham"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".FilterEdit")

#-------------------------------------------------------------------------
#
# GTK/GNOME 
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gobject
import GrampsDisplay

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import GenericFilter
import AutoComp
import ListModel
import Utils
import SelectPerson
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_name2list = {
    _('Personal event:')     : const.personal_events,
    _('Family event:')       : const.family_events,
    _('Personal attribute:') : const.personal_attributes,
    _('Family attribute:')   : const.family_attributes,
}

_menulist = {
    _('Relationship type:')  : const.family_relations,
    }

#-------------------------------------------------------------------------
#
# Sorting function for the filter rules
#
#-------------------------------------------------------------------------
def by_rule_name(f,s):
    return cmp(f.name,s.name)

#-------------------------------------------------------------------------
#
# MyBoolean - check button with standard interface
#
#-------------------------------------------------------------------------
class MyBoolean(gtk.CheckButton):

    def __init__(self,label=None):
        gtk.CheckButton.__init__(self,label)
        self.show()

    def get_text(self):
        return str(int(self.get_active()))

    def set_text(self,val):
        is_active = not not int(val)
        self.set_active(is_active)

#-------------------------------------------------------------------------
#
# MyInteger - spin button with standard interface
#
#-------------------------------------------------------------------------
class MyInteger(gtk.SpinButton):

    def __init__(self,min,max):
        gtk.SpinButton.__init__(self)
        self.set_adjustment(gtk.Adjustment(min,min,max,1))
        self.show()

    def get_text(self):
        return str(self.get_value_as_int())

    def set_text(self,val):
        self.set_value(int(val))

#-------------------------------------------------------------------------
#
# MyFilters - Combo box with list of filters with a standard interface
#
#-------------------------------------------------------------------------
class MyFilters(gtk.ComboBox):
    
    def __init__(self,filters):
        gtk.ComboBox.__init__(self)
        store = gtk.ListStore(str)
        self.set_model(store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.flist = [ f.get_name() for f in filters ]
        self.flist.sort()

        for fname in self.flist:
            store.append(row=[fname])
        self.set_active(0)
        self.show()
        
    def get_text(self):
        active = self.get_active()
        if active < 0:
            return ""
        return self.flist[active]

    def set_text(self,val):
        if val in self.flist:
            self.set_active(self.flist.index(val))

#-------------------------------------------------------------------------
#
# MySource - Combo box with list of sources with a standard interface
#
#-------------------------------------------------------------------------
class MySource(gtk.ComboBox):
    
    def __init__(self,db):
        gtk.ComboBox.__init__(self)
        self.db = db
        store = gtk.ListStore(str)
        self.set_model(store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)

        self.slist = []
        for src_handle in self.db.get_source_handles(sort_handles=True):
            src = self.db.get_source_from_handle(src_handle)
            self.slist.append(src.get_gramps_id())
            store.append(row=["%s [%s]" % (src.get_title(),src.get_gramps_id())])

        self.set_active(0)
        self.show()
        
    def get_text(self):
        active = self.get_active()
        if active < 0:
            return ""
        return self.slist[active]

    def set_text(self,val):
        if val in self.slist:
            self.set_active(self.slist.index(val))

#-------------------------------------------------------------------------
#
# MyPlaces - AutoCombo text entry with list of places attached. Provides
#            a standard interface
#
#-------------------------------------------------------------------------
class MyPlaces(gtk.Entry):
    
    def __init__(self,places):
        gtk.Entry.__init__(self)
        
        AutoComp.fill_entry(self,places)
        self.show()
        
#-------------------------------------------------------------------------
#
# MyID - Person/GRAMPS ID selection box with a standard interface
#
#-------------------------------------------------------------------------
class MyID(gtk.HBox):
    
    def __init__(self,db):
        gtk.HBox.__init__(self,False,6)
        self.db = db

        self.entry = gtk.Entry()
        self.entry.show()
        self.button = gtk.Button()
        self.button.set_label(_('Select...'))
        self.button.connect('clicked',self.button_press)
        self.button.show()
        self.pack_start(self.entry)
        self.add(self.button)
        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.button,_('Select person from a list'))
        self.tooltips.enable()
        self.show()
        self.set_text('')

    def button_press(self,obj):
        inst = SelectPerson.SelectPerson(self.db,_('Select Person'))
        val = inst.run()
        if val == None:
            self.set_text('')
        else:
            self.set_text(val.get_gramps_id())
        
    def get_text(self):
        return unicode(self.entry.get_text())

    def set_text(self,val):
        try:
            p = self.db.get_person_from_handle(val)
            n = p.get_primary_name().get_name()
            self.tooltips.set_tip(self.entry,n)
        except:
            self.tooltips.set_tip(self.entry,_('Not a valid person'))
        self.entry.set_text(val)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class MySelect(gtk.ComboBoxEntry):
    
    def __init__(self,transtable):
        gtk.ComboBoxEntry.__init__(self)
        self.transtable = transtable
        AutoComp.fill_combo(self,transtable.get_values())
        self.show()
        
    def get_text(self):
        return self.transtable.find_key(unicode(self.child.get_text()))

    def set_text(self,val):
        self.child.set_text(_(val))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class MyListSelect(gtk.ComboBox):
    
    def __init__(self,data_list):
        gtk.ComboBox.__init__(self)
        store = gtk.ListStore(str)
        self.set_model(store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.data_list = data_list

        for item in data_list:
            store.append(row=[item[0]])
        self.set_active(0)
        self.show()
        
    def get_text(self):
        active = self.get_active()
        if active < 0:
            return str(-1)
        return str(active)
    
    def set_text(self,val):
        active = int(val)
        if active >=0:
            self.set_active(active)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class MyEntry(gtk.Entry):
    
    def __init__(self):
        gtk.Entry.__init__(self)
        self.show()
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class FilterEditor:
    def __init__(self,filterdb,db,parent):
        self.parent = parent
        if self.parent.child_windows.has_key(self.__class__):
            self.parent.child_windows[self.__class__].present(None)
            return
        self.win_key = self.__class__
        self.child_windows = {}

        self.db = db
        self.filterdb = GenericFilter.GenericFilterList(filterdb)
        self.filterdb.load()

        self.editor = gtk.glade.XML(const.rule_glade,'filter_list',"gramps")
        self.window = self.editor.get_widget('filter_list')
        self.filter_list = self.editor.get_widget('filters')
        self.edit = self.editor.get_widget('edit')
        self.delete = self.editor.get_widget('delete')
        self.test = self.editor.get_widget('test')

        Utils.set_titles(self.window,self.editor.get_widget('title'),
                         _('User defined filters'))

        self.editor.signal_autoconnect({
            'on_add_clicked' : self.add_new_filter,
            'on_edit_clicked' : self.edit_filter,
            'on_test_clicked' : self.test_clicked,
            'on_close_clicked' : self.close_filter_editor,
            "on_help_filters_clicked"  : self.on_help_clicked,
            'on_delete_clicked' : self.delete_filter,
            'on_filter_list_delete_event' : self.on_delete_event,
            })

        self.clist = ListModel.ListModel(self.filter_list,
                                         [(_('Filter'),0,150),(_('Comment'),1,150)],
                                         self.filter_select_row,
                                         self.edit_filter)
        self.draw_filters()
        self.add_itself_to_menu()
        self.window.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-cfe')

    def on_delete_event(self,obj,b):
        self.filterdb.save()
        self.close_child_windows()
        self.remove_itself_from_menu()
        GenericFilter.reload_custom_filters()
        GenericFilter.reload_system_filters()
        self.parent.init_filters()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_("Filter Editor tool"))
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Filter List'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def filter_select_row(self,obj):
        store,iter = self.clist.get_selected()
        if iter:
            self.edit.set_sensitive(1)
            self.delete.set_sensitive(1)
            self.test.set_sensitive(1)
        else:
            self.edit.set_sensitive(0)
            self.delete.set_sensitive(0)
            self.test.set_sensitive(0)
    
    def close_filter_editor(self,obj):
        self.filterdb.save()
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()
        GenericFilter.reload_custom_filters()
        GenericFilter.reload_system_filters()
        self.parent.init_filters()
        
    def draw_filters(self):
        self.clist.clear()
        for f in self.filterdb.get_filters():
            self.clist.add([f.get_name(),f.get_comment()],f)

    def add_new_filter(self,obj):
        filter = GenericFilter.GenericFilter()
        EditFilter(self,filter)

    def edit_filter(self,obj):
        store,iter = self.clist.get_selected()
        if iter:
            filter = self.clist.get_object(iter)
            EditFilter(self,filter)

    def test_clicked(self,obj):
        store,iter = self.clist.get_selected()
        if iter:
            filt = self.clist.get_object(iter)
            handle_list = filt.apply(self.db,self.db.get_person_handles(sort_handles=False))
            ShowResults(self,self.db,handle_list,filt.get_name())

    def delete_filter(self,obj):
        store,iter = self.clist.get_selected()
        if iter:
            filter = self.clist.get_object(iter)
            self.filterdb.get_filters().remove(filter)
            self.draw_filters()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class EditFilter:
    def __init__(self,parent,filter):
        self.filter = filter
        self.filterdb = parent.filterdb
        
        self.parent = parent
        if self.parent.child_windows.has_key(self.filter):
            self.parent.child_windows[self.filter].present(None)
            return
        else:
            self.win_key = self.filter
        self.child_windows = {}

        self.glade = gtk.glade.XML(const.rule_glade,'define_filter',"gramps")
        self.window = self.glade.get_widget('define_filter')
        self.define_title = self.glade.get_widget('title')

        Utils.set_titles(self.window,self.define_title,_('Define filter'))
        
        self.rule_list = self.glade.get_widget('rule_list')
        self.rlist = ListModel.ListModel(self.rule_list,
                                         [(_('Name'),-1,150),(_('Value'),-1,150)],
                                         self.select_row,
                                         self.on_edit_clicked)
                                         
        self.fname = self.glade.get_widget('filter_name')
        self.log_not = self.glade.get_widget('logical_not')
        self.log_and = self.glade.get_widget('logical_and')
        self.log_or = self.glade.get_widget('logical_or')
        self.log_one = self.glade.get_widget('logical_one')
        self.comment = self.glade.get_widget('comment')
        self.ok = self.glade.get_widget('ok')
        self.edit_btn = self.glade.get_widget('edit')
        self.del_btn = self.glade.get_widget('delete')
        self.glade.signal_autoconnect({
            'on_ok_clicked' : self.on_ok_clicked,
            'on_cancel_clicked' : self.close,
            'on_filter_name_changed' : self.filter_name_changed,
            'on_delete_clicked' : self.on_delete_clicked,
            'on_add_clicked' : self.on_add_clicked,
            "on_help_filtdef_clicked"  : self.on_help_clicked,
            'on_edit_clicked' : self.on_edit_clicked,
            "on_edit_filter_delete_event" : self.on_delete_event,
            })
        if self.filter.get_invert():
            self.log_not.set_active(1)
        if self.filter.get_logical_op() == 'or':
            self.log_or.set_active(1)
        elif self.filter.get_logical_op() == 'one':
            self.log_one.set_active(1)
        else:
            self.log_and.set_active(1)
        if self.filter.get_name():
            self.fname.set_text(self.filter.get_name())
        self.comment.set_text(self.filter.get_comment())
        self.draw_rules()

        self.window.set_transient_for(self.parent.window)
        self.add_itself_to_menu()
        self.window.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        help_display('gramps-manual','tools-util-cfe')

    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        if not self.filter.get_name():
            label = _("New Filter")
        else:
            label = self.filter.get_name()
        if not label.strip():
            label = _("New Filter")
        label = "%s: %s" % (_('Filter'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Define Filter'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)
        
    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def filter_name_changed(self,obj):
        name = unicode(self.fname.get_text())
        self.ok.set_sensitive(len(name) != 0)
    
    def select_row(self,obj):
        store,iter = self.rlist.get_selected()
        if iter:
            self.edit_btn.set_sensitive(1)
            self.del_btn.set_sensitive(1)
        else:
            self.edit_btn.set_sensitive(0)
            self.del_btn.set_sensitive(0)

    def draw_rules(self):
        self.rlist.clear()
        for r in self.filter.get_rules():
            self.rlist.add([r.name,r.display_values()],r)
            
    def on_ok_clicked(self,obj):
        n = unicode(self.fname.get_text()).strip()
        if n == '':
            return
        self.filter.set_name(n)
        self.filter.set_comment(unicode(self.comment.get_text()).strip())
        for f in self.filterdb.get_filters()[:]:
            if n == f.get_name():
                self.filterdb.get_filters().remove(f)
                break
        self.filter.set_invert(self.log_not.get_active())
        if self.log_or.get_active():
            op = 'or'
        elif self.log_one.get_active():
            op = 'one'
        else:
            op = 'and'
        self.filter.set_logical_op(op)
        self.filterdb.add(self.filter)
        self.parent.draw_filters()
        self.close(obj)
        
    def on_add_clicked(self,obj):
        EditRule(self,None,_('Add Rule'))

    def on_edit_clicked(self,obj):
        store,iter = self.rlist.get_selected()
        if iter:
            d = self.rlist.get_object(iter)
            EditRule(self,d,_('Edit Rule'))

    def on_delete_clicked(self,obj):
        store,iter = self.rlist.get_selected()
        if iter:
            filter = self.rlist.get_object(iter)
            self.filter.delete_rule(filter)
            self.draw_rules()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class EditRule:
    def __init__(self,parent,val,label):
        
        self.parent = parent
        self.win_key = self
        if val:
            if self.parent.child_windows.has_key(val):
                self.parent.child_windows[val].present(None)
                return
            else:
                self.win_key = val
        else:
            self.win_key = self

        self.db = parent.parent.db
        self.filterdb = parent.filterdb

        self.pmap = {}
        self.add_places = []

        for p_id in self.db.get_place_handles():
            p = self.db.get_place_from_handle(p_id)
            self.pmap[p.get_title()] = p_id

        self.active_rule = val
        self.rule = gtk.glade.XML(const.rule_glade,'rule_editor',"gramps")
        self.window = self.rule.get_widget('rule_editor')
        self.window.hide()
        self.valuebox = self.rule.get_widget('valuebox')
        self.rname = self.rule.get_widget('ruletree')
        self.rule_name = self.rule.get_widget('rulename')

        Utils.set_titles(self.window, self.rule.get_widget('title'),label)

        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(0)
        self.notebook.set_show_border(0)
        self.notebook.show()
        self.valuebox.add(self.notebook)
        self.page_num = 0
        self.page = []
        self.class2page = {}
        the_map = {}
        for class_obj in GenericFilter.editor_rule_list:
            arglist = class_obj.labels
            vallist = []
            tlist = []
            self.page.append((class_obj,vallist,tlist))
            pos = 0
            l2 = gtk.Label(class_obj.name)
            l2.set_alignment(0,0.5)
            l2.show()
            c = gtk.TreeView()
            c.set_data('d',pos)
            c.show()
            the_map[class_obj] = c
            # Only add a table with parameters if there are any parameters
            if arglist:
                table = gtk.Table(3,len(arglist))
            else:
                table = gtk.Table(1,1)
            table.set_border_width(6)
            table.set_col_spacings(6)
            table.set_row_spacings(6)
            table.show()
            for v in arglist:
                v1 = _(v)
                l = gtk.Label(v1)
                l.set_alignment(1,0.5)
                l.show()
                if v == _('Place:'):
                    t = MyPlaces(self.pmap.keys())
                elif v == _('Number of generations:'):
                    t = MyInteger(1,32)
                elif v == _('ID:'):
                    t = MyID(self.db)
                elif v == _('Source ID:'):
                    t = MySource(self.db)
                elif v == _('Filter name:'):
                    t = MyFilters(self.filterdb.get_filters())
                elif _name2list.has_key(v1):
                    data =_name2list[v1]
                    t = MySelect(data)
                elif _menulist.has_key(v1):
                    data =_menulist[v1]
                    t = MyListSelect(data)
                elif v == _('Inclusive:'):
                    t = MyBoolean(_('Include original person'))
                elif v == _('Case sensitive:'):
                    t = MyBoolean(_('Use exact case of letters'))
                elif v == _('Regular-Expression matching:'):
                    t = MyBoolean(_('Use regular expression'))
                else:                    
                    t = MyEntry()
                tlist.append(t)
                table.attach(l,1,2,pos,pos+1,gtk.FILL,0,5,5)
                table.attach(t,2,3,pos,pos+1,gtk.EXPAND|gtk.FILL,0,5,5)
                pos = pos + 1
            self.notebook.append_page(table,gtk.Label(class_obj.name))
            self.class2page[class_obj] = self.page_num
            self.page_num = self.page_num + 1
        self.page_num = 0
        self.store = gtk.TreeStore(gobject.TYPE_STRING,gobject.TYPE_PYOBJECT)
        self.selection = self.rname.get_selection()
        col = gtk.TreeViewColumn(_('Rule Name'),gtk.CellRendererText(),text=0)
        self.rname.append_column(col)
        self.rname.set_model(self.store)

        prev = None
        last_top = None

        top_level = {}
        top_node = {}

        #
        # If editing a rule, get the name so that we can select it later
        #
        sel_node = None
        if self.active_rule:
            self.sel_class = self.active_rule.__class__
        else:
            self.sel_class = None

        keys = the_map.keys()
        keys.sort(by_rule_name)
        keys.reverse()
        catlist = []
        for class_obj in keys:
            category = class_obj.category
            if category not in catlist:
                catlist.append(category)
        catlist.sort()

        for category in catlist:
            top_node[category] = self.store.insert_after(None,last_top)
            top_level[category] = []
            last_top = top_node[category]
            self.store.set(last_top,0,category,1,None)

        for class_obj in keys:
            category = class_obj.category
            top_level[category].append(class_obj.name)
            node = self.store.insert_after(top_node[category],prev)
            self.store.set(node,0,class_obj.name,1,class_obj)

            #
            # if this is an edit rule, save the node
            if class_obj == self.sel_class:
                sel_node = node

        if sel_node:
            self.selection.select_iter(sel_node)
            page = self.class2page[self.active_rule.__class__]
            self.notebook.set_current_page(page)
            self.display_values(self.active_rule.__class__)
            (class_obj,vallist,tlist) = self.page[page]
            r = self.active_rule.values()
            for i in range(0,len(tlist)):
                tlist[i].set_text(r[i])
            
        self.selection.connect('changed', self.on_node_selected)
        self.rule.signal_autoconnect({
            'rule_ok_clicked' : self.rule_ok,
            "on_rule_edit_delete_event" : self.on_delete_event,
            "on_help_rule_clicked"  : self.on_help_clicked,
            'rule_cancel_clicked' : self.close,
            })

        self.window.set_transient_for(self.parent.window)
        self.add_itself_to_menu()
        self.window.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        help_display('gramps-manual','append-filtref')

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        if self.sel_class:
            label = self.sel_class.name
        else:
            label = ''
        if not label.strip():
            label = _("New Rule")
        label = "%s: %s" % (_('Rule'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_node_selected(self,obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store,iter = self.selection.get_selected()
        if iter:
            try:
                class_obj = store.get_value(iter,1)
                self.display_values(class_obj)
            except:
                self.valuebox.set_sensitive(0)
                self.rule_name.set_text(_('No rule selected'))
                self.rule.get_widget('description').set_text('')

    def display_values(self,class_obj):
        page = self.class2page[class_obj]
        self.notebook.set_current_page(page)
        self.valuebox.set_sensitive(1)
        self.rule_name.set_text(class_obj.name)
        self.rule.get_widget('description').set_text(class_obj.description)

    def rule_ok(self,obj):
        if self.rule_name.get_text() == _('No rule selected'):
            return

        try:
            page = self.notebook.get_current_page()
            (class_obj,vallist,tlist) = self.page[page]
            value_list = []
            for x in tlist:
                value_list.append(unicode(x.get_text()))
            store,iter = self.parent.rlist.get_selected()
            new_rule = class_obj(value_list)
            if self.active_rule:
                rule = self.parent.rlist.get_object(iter)
                self.parent.filter.delete_rule(rule)
            self.parent.filter.add_rule(new_rule)
            self.parent.draw_rules()
            self.window.destroy()
        except KeyError:
            pass
                               
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class ShowResults:
    def __init__(self,parent,db,handle_list,filtname):
        self.parent = parent
        self.win_key = self
        self.filtname = filtname
        self.glade = gtk.glade.XML(const.rule_glade,'test',"gramps")
        self.window = self.glade.get_widget('test')
        text = self.glade.get_widget('text')

        Utils.set_titles(self.window, self.glade.get_widget('title'),
                         _('Filter Test'))
        
        self.glade.signal_autoconnect({
            'on_close_clicked' : self.close,
            "on_test_delete_event" : self.on_delete_event,
            })

        n = []
        for p_handle in handle_list:
            p = db.get_person_from_handle(p_handle)
            n.append ("%s [%s]\n" % 
                        (p.get_primary_name().get_name(),p.get_gramps_id()))

        n.sort ()
        text.get_buffer().set_text(''.join(n))

        self.window.set_transient_for(self.parent.window)
        self.add_itself_to_menu()
        self.window.show()
            
    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        label = self.filtname
        label = "%s: %s" % (_('Test'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class CustomFilterEditor(Tool.Tool):
    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        FilterEditor(const.custom_filters,db,parent)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class SystemFilterEditor(Tool.Tool):
    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        FilterEditor(const.system_filters,db,parent)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FilterEditorOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_tool(
    name = 'cfilted',
    category = Tool.TOOL_UTILS,
    tool_class = CustomFilterEditor,
    options_class = FilterEditorOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Custom Filter Editor"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("The Custom Filter Editor builds custom "
                  "filters that can be used to select people "
                  "included in reports, exports, and other utilities.")
    )

if ((os.path.exists(const.system_filters) and
     os.access(const.system_filters, os.W_OK)) or
    (os.path.exists(os.path.dirname(const.system_filters)) and
     os.access(os.path.dirname(const.system_filters), os.W_OK))):
    register_tool(
        name = 'sfilted',
        category = Tool.TOOL_UTILS,
        tool_class = SystemFilterEditor,
        options_class = FilterEditorOptions,
        modes = Tool.MODE_GUI,
        translated_name = _("System Filter Editor"),
        status = _("Stable"),
        author_name = "Donald N. Allingham",
        author_email = "don@gramps-project.org",
        description=_("The System Filter Editor builds custom "
                      "filters that can be used by anyone on the system "
                      "to select people included in reports, exports, "
                      "and other utilities.")
        )
