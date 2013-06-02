#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013  Benny Malengier
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
A class to select source templates
"""

#-------------------------------------------------------------------------
#
# GTK classes
#
#-------------------------------------------------------------------------

from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------

from gramps.gen.lib import SrcAttributeType

#-------------------------------------------------------------------------
#
# SrcTemplateTreeView class
#
#-------------------------------------------------------------------------

class SrcTemplateTreeView(Gtk.TreeView):
    '''
    TreeView for SrcAttribute templates, to allow fast selection
    '''
    def __init__(self, default_key, sel_callback):
        """
        Set up the treeview to select template. 
        TreeView is initialized to default_key
        On setting a selection, sel_callback is called
        """
        Gtk.TreeView.__init__(self)
        self.sel_callback = sel_callback
        self.default_key = default_key
        self.build_model()
        self.make_columns()
        self.selection = self.get_selection()
        self.set_model(self.model)
        self.goto(default_key)
        # set up selection and fields on click
        self.connect('button-release-event', self._on_button_release)
        self.connect('key_press_event', self._on_key_press_event)

    def build_model(self):
        """
        Obtains all templates and stores them in a TreeStore
        """
        srcattrt = SrcAttributeType()
        self.I2Str = srcattrt.I2S_SRCTEMPLATEMAP
        self.I2Key = srcattrt.I2K_SRCTEMPLATEMAP
        self.Str2I = srcattrt.S2I_SRCTEMPLATEMAP
        self.Key2I = srcattrt.K2I_SRCTEMPLATEMAP
        self.Key2Path = {}
        # store (index, key, cat, cat_type, src_type)
        self.model = Gtk.TreeStore(int, str, str)
        alltexts = sorted(self.Str2I.keys())
        parentiter = None
        parentiterlev1 = None
        prevstrval = ['', '']
        for alltext in alltexts:
            vals = alltext.split('-')
            if len(vals) > 3:
                vals = [vals[0], vals[1], ' - '.join(vals[2:])]
            vals = [x.strip() for x in vals]
            #lastval is last non '' value
            lastval = vals[-1]
            if not lastval:
                lastval = vals[-2]
            if not lastval:
                lastval = vals[-3]
            truevals = ['','','']
            if len(vals) < 3 :
                truevals[:len(vals)] = vals[:]
                vals = truevals
            index = self.Str2I[alltext]
            row = [index, self.I2Key[index], lastval]
            iter = None
            if prevstrval[0] == vals[0] and prevstrval[1] == vals[1]:
                #same parentiter
                iter = self.model.append(parentiter, row)
            elif prevstrval[0] == vals[0]:
                #up one parentiter, make new sublevel2 if needed
                parentiter = parentiterlev1
                if vals[2]:
                    parentiter = self.model.append(parentiter, [-10, '', vals[1]])
                iter = self.model.append(parentiter, row)
            else:
                #new value
                parentiterlev1 = None
                if vals[2] and vals[1]:
                    #new sublevel1  and 2 needed
                    parentiterlev1 = self.model.append(None, [-10, '', vals[0]])
                    #make sublevel2
                    parentiter= self.model.append(parentiterlev1, [-10, '', vals[1]])
                    iter = self.model.append(parentiter, row)
                elif vals[1]:
                    #only new sublevel1 needed
                    parentiterlev1 = self.model.append(None, [-10, '', vals[0]])
                    parentiter = parentiterlev1
                    iter = self.model.append(parentiter, row)
                else:
                    #only a top level
                    iter = self.model.append(None, row)
            #store key to path
            self.Key2Path[row[1]] = self.model.get_path(iter)
            prevstrval = [vals[0], vals[1]]

    def make_columns(self):
        #make the column in the treeview
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Template", renderer, text=2)
        self.append_column(column)
        #no headers needed:
        self.set_headers_visible (False)

    def goto(self, key):
        """
        highlight key in the view
        """
        #we determine the path of key
        
        path = self.Key2Path[key]
        iter_ = self.model.get_iter(path)
        if iter_:
            # Expand tree
            parent_iter = self.model.iter_parent(iter_)
            if parent_iter:
                parent_path = self.model.get_path(parent_iter)
                parent_path_list = parent_path.get_indices()
                for i in range(len(parent_path_list)):
                    expand_path = Gtk.TreePath(
                            tuple([x for x in parent_path_list[:i+1]]))
                    self.expand_row(expand_path, False)

            # Select active object
            self.selection.unselect_all()
            self.selection.select_path(path)
            self.scroll_to_cell(path, None, 1, 0.5, 0)
            self.sel_callback(self.Key2I[key], key)

    def get_selected(self):
        """
        Return the (index, key) associated with selected row in the model,
        """
        (model, node) = self.selection.get_selected()
        if node:
            return (model.get_value(node, 0), model.get_value(node,1), node)
        return None

    def _on_button_release(self, obj, event):
        """
        Handle button press
        """
        if event.type == Gdk.EventType.BUTTON_RELEASE and event.button == 1:
            ref = self.get_selected()
            if ref and ref[0] != -10:
                self.sel_callback(ref[0], ref[1])
        return False
    
    def _on_key_press_event(self, widget, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                ref = self.get_selected()
                if ref:
                    if ref[0] != -10:
                        self.sel_callback(ref[0], ref[1])
                    else:
                        path = self.model.get_path(ref[2])
                        if self.row_expanded(path):
                            self.collapse_row(path)
                        else:
                            self.expand_row(path, False)
        return False
