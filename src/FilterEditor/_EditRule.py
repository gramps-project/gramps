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

# $Id: _FilterEditor.py 6840 2006-06-01 22:37:13Z dallingham $

"""
Custom Filter Editor tool.
"""

__author__ = "Don Allingham"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
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
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GrampsDisplay
import const
import RelLib
from Filters import Rules
import AutoComp
from Selectors import selector_factory
from NameDisplay import displayer as _nd
import Utils
import ManagedWindow

#-------------------------------------------------------------------------
#
# Sorting function for the filter rules
#
#-------------------------------------------------------------------------
def by_rule_name(f,s):
    return cmp(f.name,s.name)

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_name2typeclass = {
    _('Personal event:')     : RelLib.EventType,
    _('Family event:')       : RelLib.EventType,
    _('Event type:')         : RelLib.EventType,
    _('Personal attribute:') : RelLib.AttributeType,
    _('Family attribute:')   : RelLib.AttributeType,
    _('Relationship type:')  : RelLib.FamilyRelType,
    _('Marker type:')        : RelLib.MarkerType,
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
        """
        This method returns the text to save. It should be the same
        no matter the present locale (English or numeric types).
        This class sets this to get_display_text, but when localization
        is an issue (events/attr/etc types) then it has to be overridden.
        """
        return str(int(self.get_active()))

    def set_text(self,val):
        """
        This method sets the selector state to display the passed value.
        """
        is_active = bool(int(val))
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
    
    def __init__(self,filters,filter_name):
        gtk.ComboBox.__init__(self)
        store = gtk.ListStore(str)
        self.set_model(store)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.flist = [ f.get_name() for f in filters ]
        self.flist.sort()

        for fname in self.flist:
            if fname != filter_name:
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
    
    def __init__(self, db):
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
            title = src.get_title()
            if len(title) > 44:
                title = title[:40] + "..."
            store.append(row=["%s [%s]" % (title,src.get_gramps_id())])

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

    obj_name = {
        'Person' : _('Person'),
        'Family' : _('Family'),
        'Event'  : _('Event'),
        'Place'  : _('Place'),
        'Source' : _('Source'),
        'MediaObject'  : _('Media Object'),
        'Repository' : _('Repository'),
        }
    
    def __init__(self, dbstate, uistate, track, namespace='Person'):
        gtk.HBox.__init__(self,False,6)
        self.dbstate = dbstate
        self.db = dbstate.db
        self.uistate = uistate
        self.track = track
        
        self.namespace = namespace
        self.entry = gtk.Entry()
        self.entry.show()
        self.button = gtk.Button()
        self.button.set_label(_('Select...'))
        self.button.connect('clicked',self.button_press)
        self.button.show()
        self.pack_start(self.entry)
        self.add(self.button)
        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.button,_('Select %s from a list')
                              % self.obj_name[namespace])
        self.tooltips.enable()
        self.show()
        self.set_text('')

    def button_press(self,obj):
        obj_class = self.namespace
        selector = selector_factory(obj_class)
        inst = selector(self.dbstate, self.uistate, self.track)
        val = inst.run()
        if val == None:
            self.set_text('')
        else:
            self.set_text(val.get_gramps_id())
        
    def get_text(self):
        return unicode(self.entry.get_text())

    def name_from_gramps_id(self,gramps_id):
        if self.namespace == 'Person':
            person = self.db.get_person_from_gramps_id(gramps_id)
            name = _nd.display_name(person.get_primary_name())
        elif self.namespace == 'Family':
            family = self.db.get_family_from_gramps_id(gramps_id)
            name = Utils.family_name(family, self.db)
        elif self.namespace == 'Event':
            event = self.db.get_event_from_gramps_id(gramps_id)
            name = str(event.get_type)
        elif self.namespace == 'Place':
            place = self.db.get_place_from_gramps_id(gramps_id)
            name = place.get_title()
        elif self.namespace == 'Source':
            source = self.db.get_source_from_gramps_id(gramps_id)
            name = source.get_title()
        elif self.namespace == 'MediaObject':
            obj = self.db.get_object_from_gramps_id(gramps_id)
            name = obj.get_path()
        elif self.namespace == 'Repository':
            repo = self.db.get_repository_from_gramps_id(gramps_id)
            name = repo.get_name()
        return name

    def set_text(self,val):
        try:
            name = self.name_from_gramps_id(val)
            self.tooltips.set_tip(self.entry,name)
        except AttributeError:
            self.tooltips.set_tip(self.entry,_('Not a valid ID'))
        self.entry.set_text(val)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class MySelect(gtk.ComboBoxEntry):
    
    def __init__(self, type_class):
        gtk.ComboBoxEntry.__init__(self)
        self.type_class = type_class
        self.sel = AutoComp.StandardCustomSelector(type_class._I2SMAP, self,
                                                   type_class._CUSTOM,
                                                   type_class._DEFAULT)
        self.show()
        
    def get_text(self):
        return self.type_class(self.sel.get_values()).xml_str()

    def set_text(self,val):
        tc = self.type_class()
        tc.set_from_xml_str(val)
        self.sel.set_values((tc.val,tc.string))

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
class EditRule(ManagedWindow.ManagedWindow):
    def __init__(self, space, dbstate, uistate, track, filterdb, val,
                 label, update, filter_name):

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, EditRule)

        self.space = space
        self.dbstate = dbstate
        self.db = dbstate.db
        self.filterdb = filterdb
        self.update_rule = update
        self.filter_name = filter_name

        self.active_rule = val
        self.define_glade('rule_editor', const.rule_glade)
        
        self.set_window(self.get_widget('rule_editor'),
                        self.get_widget('title'),label)
        self.window.hide()
        self.valuebox = self.get_widget('valuebox')
        self.rname = self.get_widget('ruletree')
        self.rule_name = self.get_widget('rulename')

        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(0)
        self.notebook.set_show_border(0)
        self.notebook.show()
        self.valuebox.add(self.notebook)
        self.page_num = 0
        self.page = []
        self.class2page = {}
        the_map = {}

        if self.space == "Person":
            class_list = Rules.Person.editor_rule_list
        elif self.space == "Family":
            class_list = Rules.Family.editor_rule_list
        elif self.space == "Event":
            class_list = Rules.Event.editor_rule_list
        elif self.space == 'Source':
            class_list = Rules.Source.editor_rule_list
        elif self.space == 'Place':
            class_list = Rules.Place.editor_rule_list
        elif self.space == 'MediaObject':
            class_list = Rules.MediaObject.editor_rule_list
        elif self.space == 'Repository':
            class_list = Rules.Repository.editor_rule_list
        
        for class_obj in class_list:
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
                l = gtk.Label(v)
                l.set_alignment(1,0.5)
                l.show()
                if v == _('Place:'):
                    t = MyPlaces([])
                elif v == _('Number of generations:'):
                    t = MyInteger(1,32)
                elif v == _('ID:'):
                    t = MyID(self.dbstate,self.uistate,self.track,self.space)
                elif v == _('Source ID:'):
                    t = MySource(self.db)
                elif v == _('Filter name:'):
                    t = MyFilters(self.filterdb.get_filters(self.space),
                                  self.filter_name)
                elif _name2typeclass.has_key(v):
                    t = MySelect(_name2typeclass[v])
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
        self.get_widget('ok').connect('clicked',self.rule_ok)
        self.get_widget('cancel').connect('clicked', self.close_window)
        self.get_widget('help').connect('clicked',self.on_help_clicked)

        self.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('append-filtref')

    def close_window(self,obj):
        self.close()

    def on_node_selected(self,obj):
        """Updates the informational display on the right hand side of
        the dialog box with the description of the selected report"""

        store,node = self.selection.get_selected()
        if node:
            try:
                class_obj = store.get_value(node,1)
                self.display_values(class_obj)
            except:
                self.valuebox.set_sensitive(0)
                self.rule_name.set_text(_('No rule selected'))
                self.get_widget('description').set_text('')

    def display_values(self,class_obj):
        page = self.class2page[class_obj]
        self.notebook.set_current_page(page)
        self.valuebox.set_sensitive(1)
        self.rule_name.set_text(class_obj.name)
        self.get_widget('description').set_text(class_obj.description)

    def rule_ok(self,obj):
        if self.rule_name.get_text() == _('No rule selected'):
            return

        try:
            page = self.notebook.get_current_page()
            (class_obj,vallist,tlist) = self.page[page]
            value_list = []
            for selector_class in tlist:
                value_list.append(unicode(selector_class.get_text()))
            new_rule = class_obj(value_list)

            self.update_rule(self.active_rule, new_rule)
            self.close()
        except KeyError:
            pass
