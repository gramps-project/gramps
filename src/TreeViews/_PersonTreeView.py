
from gettext import gettext as _
import cgi

import gtk

from Models import \
     PersonTreeModel, PersonListModel, PersonFilterModel

from BasicUtils.NameDisplay import displayer
from RelLib import Event
import DateHandler
import Utils

display_given = displayer.display_given


class PersonTreeView(gtk.TreeView):

    def __init__(self,db,apply_filter=None):
        gtk.TreeView.__init__(self)

        self._db = db

        # Add the Name column
        cols = (\
            (_("Name"),300,self._family_name),\
            (_("ID"),100,self._object_id),\
            (_("Gender"),100,self._gender),\
            (_("Birth Date"),200,self._birth_date),\
            (_("Birth Place"),200,self._birth_place),\
            (_("Death Date"),200,self._death_date),\
            (_("Death Place"),200,self._death_place),\
            (_("Spouse"),200,self._spouce),\
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
        if ( len(rowref) > 1 or model.is_list() )and o is not None:
            cell.set_property('text', o.get_gramps_id())
        else:
            cell.set_property('text', "")

    def _family_name(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', "%s, %s"% (o.get_primary_name().surname,
                                                 display_given(o)))
        elif o is not None:
            cell.set_property('text',o.get_primary_name().surname)
        else:
            cell.set_property('text','')
        
    def _gender(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', Utils.gender[o.gender])
        else:
            cell.set_property('text', "")

    def _birth_date(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        cell_value = ''
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            b = o.get_birth_ref()
            if b:
                birth = self._db.get_event_from_handle(b.ref)
                date_str = DateHandler.get_date(birth)
                if date_str != "":
                    cell_value = cgi.escape(date_str)
            else:
                for er in o.get_event_ref_list():
                    event = self._db.get_event_from_handle(er.ref)
                    etype = event.get_type()[0]
                    date_str = DateHandler.get_date(event)
                    if (etype in [Event.BAPTISM, Event.CHRISTEN]
                        and date_str != ""):
                        return 
                    cell_value = "<i>" + cgi.escape(date_str) + "</i>"
        cell.set_property('markup', cell_value)

    def _birth_place(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _death_date(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _death_place(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _last_change(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _death_cause(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

    def _spouce(self, column, cell, model, iter, user_data=None):
        (o,rowref) = model.get_value(iter, 0)
        if (len(rowref) > 1 or model.is_list()) and o is not None:
            cell.set_property('text', "")
        else:
            cell.set_property('text', "")

