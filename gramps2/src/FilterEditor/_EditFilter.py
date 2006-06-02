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
import GrampsDisplay

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import RelLib
from Filters import GenericFilter, FilterList, Rules, \
     reload_custom_filters, reload_system_filters
import ListModel
import ManagedWindow

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class EditFilter(ManagedWindow.ManagedWindow):
    
    def __init__(self, space, dbstate, uistate, track, gfilter, filterdb, update):

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.space = space
        self.update = update
        self.dbstate = dbstate
        self.db = dbstate.db
        self.filter = gfilter
        self.filterdb = filterdb
        
        self.glade = gtk.glade.XML(const.rule_glade,'define_filter',"gramps")
        self.define_title = self.glade.get_widget('title')

        self.set_window(
            self.glade.get_widget('define_filter'),
            self.define_title,
            _('Define filter'))
        
        self.rule_list = self.glade.get_widget('rule_list')
        self.rlist = ListModel.ListModel(
            self.rule_list,
            [(_('Name'),-1,150),(_('Value'),-1,150)],
            self.select_row,
            self.on_edit_clicked)
                                         
        self.fname = self.glade.get_widget('filter_name')
        self.logical = self.glade.get_widget('rule_apply')
        self.comment = self.glade.get_widget('comment')
        self.ok = self.glade.get_widget('ok')
        self.edit_btn = self.glade.get_widget('edit')
        self.del_btn = self.glade.get_widget('delete')
        self.add_btn = self.glade.get_widget('add')

        self.ok.connect('clicked', self.on_ok_clicked)
        self.edit_btn.connect('clicked', self.on_edit_clicked)
        self.del_btn.connect('clicked', self.on_delete_clicked)
        self.add_btn.connect('clicked', self.on_add_clicked)
        
        self.glade.get_widget('help').('clicked', self.on_help_clicked)
        self.glade.get_widget('cancel').('clicked', self.close_window)
        self.fname.connect('changed', self.filter_name_changed)

        if self.filter.get_logical_op() == 'or':
            self.logical.set_active(1)
        elif self.filter.get_logical_op() == 'one':
            self.logical.set_active(2)
        else:
            self.logical.set_active(0)
        if self.filter.get_name():
            self.fname.set_text(self.filter.get_name())
        self.comment.set_text(self.filter.get_comment())
        self.draw_rules()

        self.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-cfe')

    def close_window(self,obj):
        self.close()

    def filter_name_changed(self,obj):
        name = unicode(self.fname.get_text())
        self.ok.set_sensitive(len(name) != 0)
    
    def select_row(self,obj):
        store,node = self.rlist.get_selected()
        if node:
            self.edit_btn.set_sensitive(True)
            self.del_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)
            self.del_btn.set_sensitive(False)

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
        for f in self.filterdb.get_filters(self.space)[:]:
            if n == f.get_name():
                self.filterdb.get_filters(self.space).remove(f)
                break
        val = self.logical.get_active() 
        if val == 1:
            op = 'or'
        elif val == 2:
            op = 'one'
        else:
            op = 'and'
        self.filter.set_logical_op(op)
        self.filterdb.add(self.space,self.filter)
        self.update()
        self.close()
        
    def on_add_clicked(self,obj):
        from _EditRule import EditRule
        
        EditRule(self.space, self.dbstate, self.uistate, self.track,
                 self.filterdb, None, _('Add Rule'), self.update_rule)

    def on_edit_clicked(self,obj):
        print "ON EDIT"
        store, node = self.rlist.get_selected()
        if node:
            from _EditRule import EditRule
            
            d = self.rlist.get_object(node)

            EditRule(self.space, self.dbstate, self.uistate, self.track,
                     self.filterdb, d, _('Edit Rule'), self.update_rule)

    def update_rule(self, old_rule, new_rule):
        if old_rule:
            self.filter.delete_rule(old_rule)
        self.filter.add_rule(new_rule)
        self.draw_rules()

    def on_delete_clicked(self,obj):
        store,node = self.rlist.get_selected()
        if node:
            gfilter = self.rlist.get_object(node)
            self.filter.delete_rule(gfilter)
            self.draw_rules()

