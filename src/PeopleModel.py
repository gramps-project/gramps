import gobject
import gtk
import gtk.glade
import gnome
import gnome.ui

from RelLib import *

def unique(mylist):
    a = {}
    for val in mylist:
        a[val] = 1
    return a.keys()

def callback(foo):
    pass

class JunkIter(gtk.TreeIter):
    def __init__(self):
        pass

class PeopleModel(gtk.GenericTreeModel):

    def __init__(self,db):

        gtk.GenericTreeModel.__init__(self)
        self.db = db
        self.rebuild_data()
        
        self.connect('row-inserted',self.on_row_inserted)
        self.connect('row-deleted',self.on_row_deleted)

    def rebuild_data(self):
        self.top_iter2path = {}
        self.top_path2iter = {}
        self.iter2path = {}
        self.path2iter = {}
        self.sname_sub = {}

        if not self.db.is_open():
            return
        
        val = 0
        name_list = self.db.get_surnames()
        for name in name_list:
            self.top_iter2path[unicode(name)] = (val,)
            self.top_path2iter[val] = unicode(name)
            val += 1

        for person_id in self.db.get_person_keys():
            
            person = self.db.find_person_from_id(person_id)
            surname = unicode(person.get_primary_name().get_surname())

            if self.sname_sub.has_key(surname):
                val = len(self.sname_sub[surname])
                self.sname_sub[surname].append(person_id)
            else:
                self.sname_sub[surname] = [person_id]
                val = 0

            tpl = (surname,val)
            self.iter2path[person_id] = tpl
            self.path2iter[tpl] = person_id
        
    def on_row_inserted(self,obj,path,iter):
        self.rebuild_data()

    def on_row_deleted(self,obj,path):
        self.rebuild_data()
            
    def find_path(self,iter):
        if self.top_iter2path.has_key(iter):
            return self.top_iter2path[iter]
        else:
            path = self.iter2path.get(iter)
            if path:
                return (self.top_iter2path[path[0]][0],path[1]);
            else:
                return None

    def on_get_flags(self):
	'''returns the GtkTreeModelFlags for this particular type of model'''
	return 0

    def on_get_n_columns(self):
        return 5

    def on_get_path(self, node):
	'''returns the tree path (a tuple of indices at the various
	levels) for a particular node.'''
        if self.top_iter2path.has_key(node):
            return self.top_iter2path[node]
        else:
            (surname,index) = self.iter2path[node]
            return (self.top_iter2path[surname][0],index)

    def on_get_column_type(self,index):
        return gobject.TYPE_STRING

    def on_get_iter(self, path):
        try:
            if len(path)==1:
                return self.top_path2iter[path[0]]
            else:
                surname = self.top_path2iter[path[0]]
                return self.path2iter[(surname,path[1])]
        except:
            return None

    def on_get_value(self,iter,col):
        if self.top_iter2path.has_key(iter):
            if col == 0:
                return iter
            else:
                return ''
        else:
            data = self.db.person_map[str(iter)]
            if col==0:
                return str(data[2].get_name())
            elif col == 1:
                return str(data[0])
            elif col == 2:
                if data[1]:
                    return "male"
                else:
                    return "female"
            elif col == 3:
                if data[5]:
                    return self.db.find_event_from_id(data[5]).get_date()
                else:
                    return u""
            elif col == 4:
                if data[6]:
                    return self.db.find_event_from_id(data[6]).get_date()
                else:
                    return u""

    def on_iter_next(self, node):
	'''returns the next node at this level of the tree'''
        if self.top_iter2path.has_key(node):
            path = self.top_iter2path[node]
            return self.top_path2iter.get(path[0]+1)
        else:
            (surname,val) = self.iter2path[node]
            return self.path2iter.get((surname,val+1))

    def on_iter_children(self,node):
        if node == None:
            return self.top_path2iter[0]
        if self.top_iter2path.has_key(node):
            return self.path2iter.get((node,0))
        return None

    def on_iter_has_child(self, node):
	'''returns true if this node has children'''
        if node == None:
            return 1
        if self.top_iter2path.has_key(node):
            return 1
        return 0

    def on_iter_n_children(self,node):
        if node == NONE:
            return len(self.sname_sub)
        if self.iter2path.has_key(node):
            return len(self.sname_sub[node])
        return 0

    def on_iter_nth_child(self,node,n):
        path = self.top_iter2path.get(node)
        if path:
            return self.path2iter.get((node,n))
        else:
            return None

    def on_iter_parent(self, node):
	'''returns the parent of this node'''
        path = self.iter2path[node]
        if path:
            return path[0]
        return None
