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
        sel_label = gtk.Label("No Selected Object")
        sel_frame = gtk.Frame()
        sel_frame.set_shadow_type(gtk.SHADOW_IN)
        sel_frame.set_border_width(self.__class__.__default_border_width*2)
        sel_frame.add(sel_label)

        label_box = gtk.HBox()
        label_box.pack_start(label,False,False)
        label_box.pack_start(sel_frame,True,True)
        
        # Toolbar

        # FIXME: This should be done somewhere central
        factory = gtk.IconFactory()
        
        pixbuf = gtk.gdk.pixbuf_new_from_file("person.svg")
        iconset = gtk.IconSet(pixbuf)
        factory.add('gramps-person', iconset)

        pixbuf = gtk.gdk.pixbuf_new_from_file("flist.svg")
        iconset = gtk.IconSet(pixbuf)
        factory.add('gramps-family', iconset)
        
        factory.add_default()
  
        tips = gtk.Tooltips()
        
        person_tool = gtk.ToolButton("gramps-person")
        person_tool.set_tooltip(tips,"Show People")
        
        family_tool = gtk.ToolButton("gramps-family")
        family_tool.set_tooltip(tips,"Show Families")
        
        event_tool = gtk.ToolButton("gramps-person")
        event_tool.set_tooltip(tips,"Show Events")

        toolbar = gtk.Toolbar()
        toolbar.insert(person_tool,0)
        toolbar.insert(family_tool,1)
        toolbar.insert(event_tool,2)

        # Top box

        top_box = gtk.HBox()
        top_box.pack_start(toolbar,True,True)
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

    gtk.main()
