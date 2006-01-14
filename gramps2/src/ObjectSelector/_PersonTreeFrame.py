import gtk
import gobject


class PersonTreeFrame(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5


    def __init__(self,dbstate):
	gtk.Frame.__init__(self)

        # dummy data for testing
        self.treestore = gtk.TreeStore(str)

        # we'll add some data now - 4 rows with 3 child rows each
        for parent in range(4):
            piter = self.treestore.append(None, ['parent %i' % parent])
            for child in range(3):
                self.treestore.append(piter, ['child %i of parent %i' %
                                              (child, parent)])
   
        self.person_tree = gtk.TreeView(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn('Column 0')
        self.person_tree.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.person_tree.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.person_tree.set_reorderable(True)
        
        self.add(self.person_tree)
        self.set_shadow_type(gtk.SHADOW_IN)

    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonTreeFrame)

if __name__ == "__main__":

    w = ObjectSelectorWindow()
    w.show_all()
    w.connect("destroy", gtk.main_quit)

    gtk.main()
