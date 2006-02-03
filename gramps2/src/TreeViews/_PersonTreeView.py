
from gettext import gettext as _

import gtk

from Models import \
     PersonTreeModel, PersonListModel, PersonFilterModel

from NameDisplay import displayer
display_given = displayer.display_given

class PersonTreeView(gtk.TreeView):

    def __init__(self,db,apply_filter=None):
        gtk.TreeView.__init__(self)

        self._db = db

        # Add the Name column
        self._name_col = gtk.TreeViewColumn(_("Family Name"))
        self._name_col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._name_col.set_fixed_width(300)
        self._id_cell1 = gtk.CellRendererText()
        self._name_col.pack_start(self._id_cell1,True)
        self._name_col.set_cell_data_func(self._id_cell1,self._family_name)

        # Add the Name column
        self._given_col = gtk.TreeViewColumn(_("Given Name"))
        self._given_col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._given_col.set_fixed_width(300)
        self._id_cell1 = gtk.CellRendererText()
        self._given_col.pack_start(self._id_cell1,True)
        self._given_col.set_cell_data_func(self._id_cell1,self._given_name)

        # Add the ID column
        self._id_col = gtk.TreeViewColumn(_("ID"))
        self._id_col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._id_col.set_fixed_width(100)
        self._id_cell = gtk.CellRendererText()
        self._id_col.pack_start(self._id_cell,True)
        self._id_col.set_cell_data_func(self._id_cell,self._object_id)

        self.append_column(self._name_col)
        self.append_column(self._given_col)
        self.append_column(self._id_col)

        self.set_enable_search(False)
        self.set_fixed_height_mode(True)

        if apply_filter is not None:
            self.set_filter(apply_filter)
        else:
            self.clear_filter()

    def set_filter(self,apply_filter=None):
        self.set_model(PersonFilterModel(self._db,apply_filter))

    def clear_filter(self):
        self.set_model(PersonTreeModel(self._db))

                  
    # Accessor methods for the columns

    def _object_id(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', o.get_gramps_id())
        else:
            cell.set_property('text', "")

    def _family_name(self, column, cell, model, iter, user_data=None):
            (o,rowref) = model.get_value(iter, 0)
            cell.set_property('text', str(rowref) + " " + o.get_primary_name().get_surname())

    def _given_name(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', display_given(o))
        else:
            cell.set_property('text', "")

        
