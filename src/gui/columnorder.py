#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

"""
Handle the column ordering
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import logging

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ManagedWindow
from glade import Glade


#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
__LOG = logging.getLogger(".ColumnOrder")

class ColumnOrder(gtk.VBox):
    """
    Column ordering selection widget
    """

    def __init__(self, config, column_names, on_apply, tree=False):
        """
        Create the Column Ordering widget based on config
        
        config: a configuration file with column data
        column_names: translated names for the possible columns
        on_apply: function to run when apply is clicked
        tree: are the columns for a treeview, if so, the first columns is not
            changable
        """
        gtk.VBox.__init__(self)

        self.treeview = tree
        self.colnames = column_names
        self.config = config
        self.on_apply = on_apply
        
        self.startrow = 0
        if self.treeview:
            label = gtk.Label(
                    _('Tree View: first column "%s" cannot be changed') % 
                      column_names[0])
            self.startrow = 1
            self.pack_start(label, expand=False, fill=False)

        hbox = gtk.HBox()
        hbox.set_spacing(10)
        scroll = gtk.ScrolledWindow()
        scroll.set_size_request(250,300)
        hbox.pack_start(scroll)
        self.tree = gtk.TreeView()
        self.tree.set_reorderable(True)
        scroll.add(self.tree)
        self.apply_button = gtk.Button(stock='gtk-apply')
        btns = gtk.HButtonBox()
        btns.set_layout(gtk.BUTTONBOX_END)
        btns.pack_start(self.apply_button)
        hbox.pack_start(btns, expand=False)
        self.pack_start(hbox)

        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, 
                                   gobject.TYPE_INT, object)
        
        self.tree.set_model(self.model)

        checkbox = gtk.CellRendererToggle()
        checkbox.connect('toggled', toggled, self.model)
        renderer = gtk.CellRendererText()
        
        column_n = gtk.TreeViewColumn(_('Display'), checkbox, active=0)
        column_n.set_min_width(50)
        self.tree.append_column(column_n)

        column_n = gtk.TreeViewColumn(_('Column Name'),  renderer, text=1)
        column_n.set_min_width(225)
        self.tree.append_column(column_n)

        self.apply_button.connect('clicked', self.__on_apply)

        #obtain the columns from config file
        self.oldorder = self.config.get('columns.order')
        self.oldsize = self.config.get('columns.sizecol')
        self.oldvis =  self.config.get('columns.visible')
        colord = []
        for val, size in zip(self.oldorder, self.oldsize):
            if val in self.oldvis:
                colord.append((1, val, size))
            else:
                colord.append((0, val, size))
        for item in colord[self.startrow:]:
            node = self.model.append()
            self.model.set(node,
                           0, item[0],
                           1, column_names[item[1]],
                           2, item[1],
                           3, item[2])

    def __on_apply(self, obj):
        """
        called with the OK button is pressed
        """
        neworder = []
        newsize = []
        newvis = []
        if self.treeview:
            #first row is fixed
            neworder.append(self.oldorder[0])
            newvis.append(self.oldvis[0])
            newsize.append(self.oldsize[0])
        for i in range(0, len(self.colnames[self.startrow:])):
            node = self.model.get_iter((int(i), ))
            enable = self.model.get_value(node, 0)
            index = self.model.get_value(node, 2)
            size = self.model.get_value(node, 3)
            if enable:
                newvis.append(index)
            neworder.append(index)
            newsize.append(size)
        self.config.set('columns.order', neworder)
        self.config.set('columns.sizecol', newsize)
        self.config.set('columns.visible', newvis)
        self.config.save()
        if self.on_apply:
            self.on_apply()

def toggled(cell, path, model):
    """
    Called when the cell information is changed, updating the
    data model so the that change occurs.
    """
    node = model.get_iter((int(path), ))
    value = not model.get_value(node, 0)
    model.set(node, 0, value)
