
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
        cols = (\
            (_("Family Name"),300,self._family_name),\
            (_("ID"),100,self._object_id),\
            (_("Given Name"),300,self._given_name),\
            (_("Gender"),100,self._gender),\
            (_("Birth Date"),200,self._birth_date),\
            (_("Birth Place"),200,self._birth_place),\
            (_("Death Date"),200,self._death_date),\
            (_("Death Place"),200,self._death_place),\
            (_("Spouce"),200,self._spouce),\
            (_("Last Change"),200,self._last_change),\
            (_("Cause of Death"),300,self._death_cause))

        for col in cols:
            self.append_column(
                self._new_column(
                    col[0],col[1],col[2]))
            
        self.set_enable_search(False)
        self.set_fixed_height_mode(True)

        if apply_filter is not None:
            self.set_filter(apply_filter)
        else:
            self.clear_filter()

    def _new_column(self,name,size,func):
        col = gtk.TreeViewColumn(name)
        col.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        col.set_fixed_width(size)
        cell = gtk.CellRendererText()
        col.pack_start(cell,True)
        col.set_cell_data_func(cell,func)
        return col

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
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

        
    def _gender(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _birth_date(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _birth_place(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _death_date(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _death_place(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _last_change(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _death_cause(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _spouce(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if len(rowref) > 1:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

