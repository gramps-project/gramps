#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
import string

#-------------------------------------------------------------------------
#
# GTK/GNOME 
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gobject

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
from gettext import gettext as _

_name2list = {
    _('Personal event:')     : (const.personalEvents,const.personal_events),
    _('Family event:')       : (const.marriageEvents,const.family_events),
    _('Personal attribute:') : (const.personalAttributes,const.personal_attributes),
    _('Family attribute:')   : (const.familyAttributes,const.family_attributes),
    _('Relationship type:')  : (const.familyRelations,const.family_relations),
}


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
class MyFilters(gtk.Combo):
    
    def __init__(self,filters):
        gtk.Combo.__init__(self)
        
        flist = []
        for f in filters:
            flist.append(f.get_name())
        flist.sort()
        if len(flist) == 0:
            self.ok = 0
            self.set_sensitive(0)
        else:
            self.ok = 1
        AutoComp.AutoCombo(self,flist)
        self.show()
        
    def get_text(self):
        if self.ok:
            return unicode(self.entry.get_text())
        else:
            return ""

    def set_text(self,val):
        self.entry.set_text(val)

#-------------------------------------------------------------------------
#
# MyPlaces - AutoCombo text entry with list of places attached. Provides
#            a standard interface
#
#-------------------------------------------------------------------------
class MyPlaces(gtk.Entry):
    
    def __init__(self,places):
        gtk.Entry.__init__(self)
        
        self.comp = AutoComp.AutoEntry(self,places)
        self.show()
        
#-------------------------------------------------------------------------
#
# MyID - Person/GRAMPS ID selection box with a standard interface
#
#-------------------------------------------------------------------------
class MyID(gtk.HBox):
    
    def __init__(self,db):
        gtk.HBox.__init__(self,gtk.FALSE,6)
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
            self.set_text(val.get_id())
        
    def get_text(self):
        return unicode(self.entry.get_text())

    def set_text(self,val):
        try:
            p = self.db.get_person(val)
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
class MySelect(gtk.Combo):
    
    def __init__(self,list,transtable):
        gtk.Combo.__init__(self)
        list.sort()
        self.set_popdown_strings(list)
        self.set_value_in_list(1,0)
        self.entry.set_editable(0)
        self.transtable = transtable
        self.show()
        
    def get_text(self):
        return self.transtable.find_key(unicode(self.entry.get_text()))

    def set_text(self,val):
        self.entry.set_text(_(val))

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
    def __init__(self,filterdb,db):
        self.db = db
        self.filterdb = GenericFilter.GenericFilterList(filterdb)
        self.filterdb.load()

        self.editor = gtk.glade.XML(const.filterFile,'filter_list',"gramps")
        self.editor_top = self.editor.get_widget('filter_list')
        self.filter_list = self.editor.get_widget('filters')
        self.edit = self.editor.get_widget('edit')
        self.delete = self.editor.get_widget('delete')
        self.test = self.editor.get_widget('test')

        Utils.set_titles(self.editor_top,self.editor.get_widget('title'),
                         _('User defined filters'))

        self.editor.signal_autoconnect({
            'on_add_clicked' : self.add_new_filter,
            'on_edit_clicked' : self.edit_filter,
            'on_test_clicked' : self.test_clicked,
            'on_close_clicked' : self.close_filter_editor,
            'on_delete_clicked' : self.delete_filter,
            })

        self.clist = ListModel.ListModel(self.filter_list,
                                         [(_('Filter'),0,150),(_('Comment'),1,150)],
                                         self.filter_select_row,
                                         self.edit_filter)
        self.draw_filters()

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
        self.editor_top.destroy()
        GenericFilter.reload_custom_filters()
        GenericFilter.reload_system_filters()
        
    def draw_filters(self):
        self.clist.clear()
        for f in self.filterdb.get_filters():
            self.clist.add([f.get_name(),f.get_comment()],f)

    def add_new_filter(self,obj):
        filter = GenericFilter.GenericFilter()
        self.filter_editor(filter)

    def edit_filter(self,obj):
        store,iter = self.clist.get_selected()
        if iter:
            filter = self.clist.get_object(iter)
            self.filter_editor(filter)

    def test_clicked(self,obj):
        store,iter = self.clist.get_selected()
        if iter:
            filt = self.clist.get_object(iter)
            id_list = filt.apply(self.db,self.db.get_person_keys())
            ShowResults(self.db,id_list)

    def delete_filter(self,obj):
        store,iter = self.clist.get_selected()
        if iter:
            filter = self.clist.get_object(iter)
            self.filterdb.get_filters().remove(filter)
            self.draw_filters()

    def filter_editor(self,filter):
        self.filter = filter
        self.glade = gtk.glade.XML(const.filterFile,'define_filter',"gramps")
        self.top = self.glade.get_widget('define_filter')
        self.define_title = self.glade.get_widget('title')

        Utils.set_titles(self.top,self.define_title,_('Define filter'))
        
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
            'on_cancel_clicked' : self.on_cancel_clicked,
            'on_filter_name_changed' : self.filter_name_changed,
            'on_delete_clicked' : self.on_delete_clicked,
            'on_add_clicked' : self.on_add_clicked,
            'on_edit_clicked' : self.on_edit_clicked,
            'on_cancel_clicked' : self.on_cancel_clicked,
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
            self.rlist.add([r.trans_name(),r.display_values()],r)
            
    def on_cancel_clicked(self,obj):
        self.top.destroy()

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
        self.draw_filters()
        self.top.destroy()
        
    def on_add_clicked(self,obj):
        self.edit_rule(None,_('Add Rule'))

    def on_edit_clicked(self,obj):
        store,iter = self.rlist.get_selected()
        if iter:
            d = self.rlist.get_object(iter)
            self.edit_rule(d,_('Edit Rule'))

    def edit_rule(self,val,label):
        self.pmap = {}
        self.add_places = []

        for p_id in self.db.get_place_ids():
            p = self.db.find_place_from_id(p_id)
            self.pmap[p.get_title()] = p_id

        self.active_rule = val
        self.rule = gtk.glade.XML(const.filterFile,'rule_editor',"gramps")
        self.rule_top = self.rule.get_widget('rule_editor')
        self.valuebox = self.rule.get_widget('valuebox')
        self.rname = self.rule.get_widget('ruletree')
        self.rule_name = self.rule.get_widget('rulename')

        Utils.set_titles(self.rule_top, self.rule.get_widget('title'),label)

        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(0)
        self.notebook.set_show_border(0)
        self.notebook.show()
        self.valuebox.add(self.notebook)
        self.page_num = 0
        self.page = []
        self.name2page = {}
        map = {}
        list = []
        keylist = GenericFilter.tasks.keys()
        keylist.sort()
        for name in keylist:
            cname = GenericFilter.tasks[name]
            arglist = cname.labels
            vallist = []
            tlist = []
            self.page.append((name,cname,vallist,tlist))
            table = gtk.Table(3,len(arglist))
            table.set_border_width(6)
            table.set_col_spacings(6)
            table.set_row_spacings(6)
            table.show()
            pos = 0
            l2 = gtk.Label(name)
            l2.set_alignment(0,0.5)
            l2.show()
            c = gtk.ListItem()
            c.add(l2)
            c.set_data('d',pos)
            c.show()
            list.append(c)
            map[name] = c
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
                elif v == _('Filter name:'):
                    t = MyFilters(self.filterdb.get_filters())
                elif _name2list.has_key(v1):
                    data =_name2list[v1]
                    t = MySelect(data[0],data[1])
                elif v == _('Inclusive:'):
                    t = MyBoolean(_('Include original person'))
                else:
                    t = MyEntry()
                tlist.append(t)
                table.attach(l,1,2,pos,pos+1,gtk.FILL,0,5,5)
                table.attach(t,2,3,pos,pos+1,gtk.EXPAND|gtk.FILL,0,5,5)
                pos = pos + 1
            self.notebook.append_page(table,gtk.Label(name))
            self.name2page[name] = self.page_num
            self.page_num = self.page_num + 1
        self.page_num = 0
        self.store = gtk.TreeStore(gobject.TYPE_STRING)
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
            sel_name = unicode(_(self.active_rule.name()))
        else:
            sel_name = ""
            
        for v in map.keys():
            filter = GenericFilter.tasks[v]([None])
            category = filter.category()
            if top_level.has_key(category):
                top_level[category].append(v)
            else:
                top_level[category] = [v]
                top_node[category] = self.store.insert_after(None,last_top)
                last_top = top_node[category]
                self.store.set(last_top,0,category)

            node = self.store.insert_after(top_node[category],prev)
            self.store.set(node,0,v)

            #
            # if this is an edit rule, save the node
            if v == sel_name:
                sel_node = node

        if sel_node:
            self.selection.select_iter(sel_node)
            page = self.name2page[sel_name]
            self.notebook.set_current_page(page)
            self.display_values(sel_name)
            (n,c,v,t) = self.page[page]
            r = self.active_rule.values()
            for i in range(0,len(t)):
                t[i].set_text(r[i])
            
        self.selection.connect('changed', self.on_node_selected)
        self.rule.get_widget('ok').connect('clicked',self.rule_ok)
        self.rule.get_widget('cancel').connect('clicked',self.rule_cancel)

    def on_node_selected(self,obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store,iter = self.selection.get_selected()
        if iter:
            try:
                key = unicode(store.get_value(iter,0))
                self.display_values(key)
            except:
                self.valuebox.set_sensitive(0)
                self.rule_name.set_text(_('No rule selected'))

    def display_values(self,key):
        page = self.name2page[key]
        self.notebook.set_current_page(page)
        self.valuebox.set_sensitive(1)
        self.rule_name.set_text(key)
        filter = GenericFilter.tasks[key]([None])
        self.rule.get_widget('description').set_text(filter.description())

    def on_delete_clicked(self,obj):
        store,iter = self.rlist.get_selected()
        if iter:
            filter = self.rlist.get_object(iter)
            self.filter.delete_rule(filter)
            self.draw_rules()

    def rule_ok(self,obj):
        name = unicode(self.rule_name.get_text())
        class_def = GenericFilter.tasks[name]
        obj = class_def(None)
        try:
            page = self.name2page[name]
            (n,c,v,t) = self.page[page]
            value_list = []
            for x in t:
                value_list.append(unicode(x.get_text()))
            store,iter = self.rlist.get_selected()
            new_rule = c(value_list)
            if self.active_rule:
                rule = self.rlist.get_object(iter)
                self.filter.delete_rule(rule)
            self.filter.add_rule(new_rule)
            self.draw_rules()
            self.rule_top.destroy()
        except KeyError:
            pass
        except:
            import DisplayTrace
            self.rule_top.destroy()
            DisplayTrace.DisplayTrace()
                               
    def rule_cancel(self,obj):
        self.rule_top.destroy()

class ShowResults:
    def __init__(self,db,id_list):
        self.glade = gtk.glade.XML(const.filterFile,'test',"gramps")
        self.top = self.glade.get_widget('test')
        text = self.glade.get_widget('text')

        Utils.set_titles(self.top, self.glade.get_widget('title'),
                         _('Filter Test'))
        
        self.glade.signal_autoconnect({'on_close_clicked' : self.close})

        n = []
        for p_id in id_list:
            p = db.find_person_from_id(p_id)
            n.append ("%s [%s]\n" % (p.get_primary_name().get_name(),p.get_id()))

        n.sort ()
        text.get_buffer().set_text(string.join (n, ''))
            
    def close(self,obj):
        self.top.destroy()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def CustomFilterEditor(database,person,callback):
    FilterEditor(const.custom_filters,database)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def SystemFilterEditor(database,person,callback):
    FilterEditor(const.system_filters,database)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    CustomFilterEditor,
    _("Custom Filter Editor"),
    category=_("Utilities"),
    description=_("The Custom Filter Editor builds custom "
                  "filters that can be used to select people "
                  "included in reports, exports, and other utilities.")
    )

if ((os.path.exists(const.system_filters) and
     os.access(const.system_filters, os.W_OK)) or
    (os.path.exists(os.path.dirname(const.system_filters)) and
     os.access(os.path.dirname(const.system_filters), os.W_OK))):
    register_tool(
        SystemFilterEditor,
        _("System Filter Editor"),
        category=_("Utilities"),
        description=_("The System Filter Editor builds custom "
                      "filters that can be used by anyone on the system "
                      "to select people included in reports, exports, "
                      "and other utilities.")
        )
