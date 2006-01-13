import gtk
import gobject

from _PersonSearchCriteriaWidget import PersonSearchCriteriaWidget
from _PersonPreviewFrame import PersonPreviewFrame

class ObjectSelectorWindow(gtk.Window):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self):
	gtk.Window.__init__(self)

        self.set_title("Add Person")
        
        # Selected object label
        label = gtk.Label("Selected:")
        label.set_alignment(xalign=1,yalign=0.5)

        sel_label = gtk.Label("No Selected Object")
        sel_frame = gtk.Frame()
        sel_frame.set_shadow_type(gtk.SHADOW_IN)
        sel_frame.set_border_width(self.__class__.__default_border_width*2)
        sel_frame.add(sel_label)

        label_box = gtk.HBox()
        label_box.pack_start(label,False,False)
        label_box.pack_start(sel_frame,True,True)
        
        # Object select

        obj_label = gtk.Label("Show")
        obj_label.set_alignment(xalign=1,yalign=0.5)
                
        person_pixbuf = gtk.gdk.pixbuf_new_from_file("../person.svg")
        flist_pixbuf = gtk.gdk.pixbuf_new_from_file("../flist.svg")

        tool_list = gtk.ListStore(gtk.gdk.Pixbuf, str,int)
        tool_list.append([person_pixbuf,'People',0])
        tool_list.append([flist_pixbuf,'Families',1])
        tool_list.append([person_pixbuf,'Events',2])

        
        tool_combo = gtk.ComboBox(tool_list)
        
        icon_cell = gtk.CellRendererPixbuf()
        label_cell = gtk.CellRendererText()
        
        tool_combo.pack_start(icon_cell, True)
        tool_combo.pack_start(label_cell, True)
        
        tool_combo.add_attribute(icon_cell, 'pixbuf', 0)
        tool_combo.add_attribute(label_cell, 'text', 1)

        tool_combo.set_active(0)

        tool_box = gtk.HBox()
        tool_box.pack_start(obj_label,False,False)
        tool_box.pack_start(tool_combo,False,False)
        
        # Top box

        top_box = gtk.HBox()
        top_box.pack_start(tool_box,False,False)
        top_box.pack_start(label_box,True,True)

        # Filters

        person_filter = PersonSearchCriteriaWidget()

        # Preview

        person_preview_frame = PersonPreviewFrame("Preview")

        # Trees

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
        
        p_tree_frame = gtk.Frame()
        p_tree_frame.add(self.person_tree)
        p_tree_frame.set_shadow_type(gtk.SHADOW_IN)

        # paned

        vbox = gtk.VBox()
        vbox.pack_start(person_preview_frame,True,True)
        vbox.pack_start(person_filter,True,True)

        pane = gtk.HPaned()
        pane.pack1(p_tree_frame,True,False)
        pane.pack2(vbox,False,True)

        pane_align = gtk.Alignment()
        pane_align.add(pane)
        pane_align.set_padding(self.__class__.__default_border_width,
                               self.__class__.__default_border_width,
                               self.__class__.__default_border_width,
                               self.__class__.__default_border_width)
        pane_align.set(0.5,0.5,1,1)




        # Bottom buttons
        add_button = gtk.Button(stock=gtk.STOCK_ADD)
        add_button.set_sensitive(False)
        
        cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)

        cancel_button.connect_object("clicked", gtk.Widget.destroy, self)
        
        bottom_button_bar = gtk.HButtonBox()
        bottom_button_bar.set_layout(gtk.BUTTONBOX_SPREAD)
        bottom_button_bar.set_spacing(self.__class__.__default_border_width/2)
        bottom_button_bar.set_border_width(self.__class__.__default_border_width)
        bottom_button_bar.add(cancel_button)
        bottom_button_bar.add(add_button)
        
        
        box = gtk.VBox()
        box.pack_start(top_box,False,False)
        box.pack_start(pane_align,True,True)
        box.pack_start(bottom_button_bar,False,False)

        align = gtk.Alignment()
        align.set_padding(self.__class__.__default_border_width,
                           self.__class__.__default_border_width,
                           self.__class__.__default_border_width,
                           self.__class__.__default_border_width)
        align.set(0.5,0.5,1,1)
        align.add(box)
        
	self.add(align)

	
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonSearchCriteriaWidget)

if __name__ == "__main__":

    w = ObjectSelectorWindow()
    w.show_all()
    w.connect("destroy", gtk.main_quit)

    gtk.main()
