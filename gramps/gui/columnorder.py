#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2010       Nick Hall
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# gui/columnorder.py

"""
Handle the column ordering
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
import logging

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .managedwindow import ManagedWindow
from .glade import Glade


#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
__LOG = logging.getLogger(".ColumnOrder")

class ColumnOrder(Gtk.Box):
    """
    Column ordering selection widget
    """

    def __init__(self, config, column_names, widths, on_apply, tree=False):
        """
        Create the Column Ordering widget based on config

        config: a configuration file with column data
        column_names: translated names for the possible columns
        widths: the widths of the visible columns
        on_apply: function to run when apply is clicked
        tree: are the columns for a treeview, if so, the first columns is not
            changable
        """
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.treeview = tree
        self.colnames = column_names
        self.config = config
        self.on_apply = on_apply

        self.pack_start(Gtk.Label(label=' '), False, False, 0)

        self.startrow = 0
        if self.treeview:
            label = Gtk.Label(label=
                    _('Tree View: first column "%s" cannot be changed') %
                      column_names[0])
            self.startrow = 1
            self.pack_start(label, False, False, 0)
            self.pack_start(Gtk.Label(label=' '), False, False, 0)

        self.pack_start(Gtk.Label(label=_('Drag and drop the columns to change'
                                    ' the order')), False, False, 0)
        self.pack_start(Gtk.Label(label=' '), False, False,0)
        hbox = Gtk.Box()
        hbox.set_spacing(10)
        hbox.pack_start(Gtk.Label(label=' '), True, True, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(300,300)
        hbox.pack_start(scroll, True, True, 0)
        self.tree = Gtk.TreeView()
        self.tree.set_reorderable(True)
        scroll.add(self.tree)
        self.apply_button = Gtk.Button.new_with_mnemonic(_('_Apply'))
        btns = Gtk.ButtonBox()
        btns.set_layout(Gtk.ButtonBoxStyle.END)
        btns.pack_start(self.apply_button, True, True, 0)
        hbox.pack_start(btns, False, True, 0)
        self.pack_start(hbox, True, True, 0)

        #Model holds:
        # bool: column visible or not
        # str : name of the column
        # int : order of the column
        # int : size (width) of the column
        self.model = Gtk.ListStore(GObject.TYPE_BOOLEAN, GObject.TYPE_STRING,
                                   GObject.TYPE_INT, GObject.TYPE_INT)

        self.tree.set_model(self.model)

        checkbox = Gtk.CellRendererToggle()
        checkbox.connect('toggled', toggled, self.model)
        renderer = Gtk.CellRendererText()

        column_n = Gtk.TreeViewColumn(_('Display'), checkbox, active=0)
        column_n.set_min_width(50)
        self.tree.append_column(column_n)

        column_n = Gtk.TreeViewColumn(_('Column Name'),  renderer, text=1)
        column_n.set_min_width(225)
        self.tree.append_column(column_n)

        self.apply_button.connect('clicked', self.__on_apply)

        #obtain the columns from config file
        self.oldorder = self.config.get('columns.rank')
        self.oldsize = self.config.get('columns.size')
        self.oldvis = self.config.get('columns.visible')
        colord = []
        index = 0
        for val, size in zip(self.oldorder, self.oldsize):
            if val in self.oldvis:
                if val != self.oldvis[-1]:
                    # don't use last col width, its wrong
                    size = widths[index]
                    index += 1
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
        if len(newvis) > 0 and self.on_apply:
            self.config.set('columns.rank', neworder)
            self.config.set('columns.size', newsize)
            self.config.set('columns.visible', newvis)
            self.config.save()
            self.on_apply()

def toggled(cell, path, model):
    """
    Called when the cell information is changed, updating the
    data model so the that change occurs.
    """
    node = model.get_iter((int(path), ))
    value = not model.get_value(node, 0)
    model.set(node, 0, value)
