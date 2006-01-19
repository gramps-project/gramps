from gettext import gettext as _

import gtk
import gobject

from PeopleModel import PeopleModel
import NameDisplay

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    _('Spouse'),
    _('Last Change'),
    _('Cause of Death'),
    ]


class PersonTreeFrame(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5


    def __init__(self,dbstate):
	gtk.Frame.__init__(self)

        self._dbstate = dbstate
        self._selection = None
        self._model = None
        self._data_filter = None

        self._tree = gtk.TreeView()
        self._tree.set_rules_hint(True)
        self._tree.set_headers_visible(True)
        #self._tree.connect('key-press-event',self.key_press)

        self._tree.connect('row-activated',self._on_row_activated)


        renderer = gtk.CellRendererText()

        column = gtk.TreeViewColumn(_('Name'), renderer,text=0)
        column.set_resizable(True)
        column.set_min_width(225)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self._tree.append_column(column)
       
        for pair in self._dbstate.db.get_person_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            column = gtk.TreeViewColumn(name, renderer, markup=pair[1])
            column.set_resizable(True)
            column.set_min_width(60)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            self._tree.append_column(column)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        scrollwindow.add(self._tree)

        self.add(scrollwindow)

        self.change_db(self._dbstate.db)

    def _on_row_activated(self,widget,path,col):
        """Expand / colapse row"""

        if self._tree.row_expanded(path):
            self._tree.collapse_row(path)
        else:
            self._tree.expand_row(path,False)

    def change_db(self,db):
        self.set_model()
        db.connect('person-add', self.person_added)
        db.connect('person-update', self.person_updated)
        db.connect('person-delete', self.person_removed)

    def set_model(self,data_filter=None):

        self._model = PeopleModel(self._dbstate.db,data_filter=data_filter)

        self._tree.set_model(self._model)

        self._selection = self._tree.get_selection()

        # expand the first row so that the tree is a sensible size.
        self._tree.expand_row((0,),False)

    def person_added(self,handle_list):
        for node in handle_list:
            person = self._dbstate.db.get_person_from_handle(node)
            top = NameDisplay.displayer.name_grouping(self._dbstate.db,person)
            self._model.rebuild_data(self._data_filter)
            if not self._model.is_visable(node):
                continue
            if (not self._model.sname_sub.has_key(top) or 
                len(self._model.sname_sub[top]) == 1):
                path = self._model.on_get_path(top)
                pnode = self._model.get_iter(path)
                self._model.row_inserted(path,pnode)
            path = self._model.on_get_path(node)
            pnode = self._model.get_iter(path)
            self._model.row_inserted(path,pnode)
            self._tree.expand_to_path(path)
            self._tree.set_cursor(path)

    def person_removed(self,handle_list):
        for node in handle_list:
            person = self._dbstate.db.get_person_from_handle(node)
            if not self._model.is_visable(node):
                continue
            top = NameDisplay.displayer.name_grouping(self._dbstate.db,person)
            mylist = self._model.sname_sub.get(top,[])
            if mylist:
                try:
                    path = self._model.on_get_path(node)
                    self._model.row_deleted(path)
                    if len(mylist) == 1:
                        path = self._model.on_get_path(top)
                        self._model.row_deleted(path)
                except KeyError:
                    pass
        self._model.rebuild_data(self.DataFilter,skip=node)

    def person_updated(self,handle_list):
        for node in handle_list:
            person = self._dbstate.db.get_person_from_handle(node)
            try:
                oldpath = self._model.iter2path[node]
            except:
                return
            pathval = self._model.on_get_path(node)
            pnode = self._model.get_iter(pathval)

            # calculate the new data

            surname = NameDisplay.displayer.name_grouping(self._dbstate.db,person)

            if oldpath[0] == surname:
                self._model.build_sub_entry(surname)
            else:
                self._model.calculate_data(self.DataFilter)
            
            # find the path of the person in the new data build
            newpath = self._model.temp_iter2path[node]
            
            # if paths same, just issue row changed signal

            if oldpath == newpath:
                self._model.row_changed(pathval,pnode)
            else:
                # paths different, get the new surname list
                
                mylist = self._model.temp_sname_sub.get(oldpath[0],[])
                path = self._model.on_get_path(node)
                
                # delete original
                self._model.row_deleted(pathval)
                
                # delete top node of original if necessar
                if len(mylist)==0:
                    self._model.row_deleted(pathval[0])
                    
                # determine if we need to insert a new top node',
                insert = not self._model.sname_sub.has_key(newpath[0])

                # assign new data
                self._model.assign_data()
                
                # insert new row if needed
                if insert:
                    path = self._model.on_get_path(newpath[0])
                    pnode = self._model.get_iter(path)
                    self._model.row_inserted(path,pnode)

                # insert new person
                path = self._model.on_get_path(node)
                pnode = self._model.get_iter(path)
                self._model.row_inserted(path,pnode)

    def get_selection(self):
        return self._selection
    
    def get_tree(self):
        return self._tree

if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonTreeFrame)

if __name__ == "__main__":

    w = ObjectSelectorWindow()
    w.show_all()
    w.connect("destroy", gtk.main_quit)

    gtk.main()
