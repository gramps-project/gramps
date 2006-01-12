import gtk
import gobject

class PersonSearchCriteriaWidget(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,label="Filter"):
	gtk.Frame.__init__(self,label)

	align = gtk.Alignment()

        # Gramps ID
        id_check = gtk.CheckButton()
        id_label = gtk.Label("Gramps ID:")
        id_label.set_sensitive(False)
        id_label.set_alignment(xalign=0,yalign=0.5)

        id_edit = gtk.Entry()
        id_edit.set_sensitive(False)
        
        id_box = gtk.HBox()
        id_box.pack_start(id_label,False,False)
        id_box.pack_start(id_edit,True,True)

        id_check.connect('toggled',lambda b: id_edit.set_sensitive(id_check.get_active()))
        id_check.connect('toggled',lambda b: id_label.set_sensitive(id_check.get_active()))

        # Name
	name_check = gtk.CheckButton()
        name_label = gtk.Label("Name:")
        name_label.set_sensitive(False)
        name_label.set_alignment(xalign=0,yalign=0.5)

        name_edit = gtk.Entry()
        name_edit.set_sensitive(False)
        
        name_box = gtk.HBox()
        name_box.pack_start(name_label,False,False)
        name_box.pack_start(name_edit,True,True)

        name_check.connect('toggled',lambda b: name_edit.set_sensitive(name_check.get_active()))
        name_check.connect('toggled',lambda b: name_label.set_sensitive(name_check.get_active()))

        # Gender
	gender_check = gtk.CheckButton()
        gender_label = gtk.Label("Gender:")
        gender_label.set_sensitive(False)
        gender_label.set_alignment(xalign=0,yalign=0.5)

        gender_combo = gtk.combo_box_new_text()
        gender_combo.append_text("Male")
        gender_combo.append_text("Female")
        gender_combo.append_text("Unknown")
        gender_combo.set_active(2)
        gender_combo.set_sensitive(False)
        
        
        gender_box = gtk.HBox()
        gender_box.pack_start(gender_label,False,False)
        gender_box.pack_start(gender_combo,True,True)

        gender_check.connect('toggled',lambda b: gender_combo.set_sensitive(gender_check.get_active()))
        gender_check.connect('toggled',lambda b: gender_label.set_sensitive(gender_check.get_active()))

        # Birth
        birth_check = gtk.CheckButton()
        birth_check.set_alignment(xalign=0,yalign=0)
        
        #birth_frame = gtk.Frame("Birth")
        #birth_frame.set_sensitive(False)

        #birth_check.connect('toggled',lambda b: birth_frame.set_sensitive(birth_check.get_active()))

        birth_box = gtk.HBox()
        birth_box.set_sensitive(False)
        birth_check.connect('toggled',lambda b: birth_box.set_sensitive(birth_check.get_active()))

        b_label = gtk.Label("Birth:")
        b_label.set_alignment(xalign=0,yalign=0)
        
        b_edit = gtk.Entry()        
        b_before = gtk.RadioButton(group=None,label="Before")        
        b_after = gtk.RadioButton(b_before,"After")
        b_before.set_active(True)
        b_unknown = gtk.CheckButton("Include Unknown")
        b_unknown.set_active(True)

        b_inner_box = gtk.HBox()
        b_inner_box.pack_start(b_before)
        b_inner_box.pack_start(b_after)
        
        b_box = gtk.VBox()
        b_box.pack_start(b_edit,True,True)
        b_box.pack_start(b_inner_box,False)
        b_box.pack_start(b_unknown,False)

        b_align = gtk.Alignment()
        b_align.set(0.5,0.5,1,1)
        b_align.add(b_box)
        
        #birth_frame.add(b_align)
        birth_box.pack_start(b_label,False,False)
        birth_box.pack_start(b_align,True,True)
        
        # Death

        death_check = gtk.CheckButton()
        #death_frame = gtk.Frame("Death")
        #death_frame.set_sensitive(False)

        #death_check.connect('toggled',lambda b: death_frame.set_sensitive(death_check.get_active()))

        death_box = gtk.HBox()
        death_box.set_sensitive(False)
        death_check.connect('toggled',lambda b: death_box.set_sensitive(death_check.get_active()))

        d_label = gtk.Label("Death:")
        d_label.set_alignment(xalign=0,yalign=0)

        d_edit = gtk.Entry()        
        d_before = gtk.RadioButton(group=None,label="Before")        
        d_after = gtk.RadioButton(d_before,"After")
        d_before.set_active(True)
        d_unknown = gtk.CheckButton("Include Unknown")
        d_unknown.set_active(True)

        d_inner_box = gtk.HBox()
        d_inner_box.pack_start(d_before)
        d_inner_box.pack_start(d_after)
        
        d_box = gtk.VBox()
        d_box.pack_start(d_edit,True,True)
        d_box.pack_start(d_inner_box,False)
        d_box.pack_start(d_unknown,False)

        d_align = gtk.Alignment()
        b_align.set(0.5,0.5,1,1)

        d_align.add(d_box)
        
        #death_frame.add(d_align)
        death_box.pack_start(d_label,False,False)
        death_box.pack_start(d_align,True,True)

        # Filter
	filter_check = gtk.CheckButton()
        filter_label = gtk.Label("Filter:")
        filter_label.set_sensitive(False)
        filter_label.set_alignment(xalign=0,yalign=0.5)

        filter_combo = gtk.combo_box_new_text()
        filter_combo.append_text("Male")
        filter_combo.append_text("Female")
        filter_combo.append_text("Unknown")
        filter_combo.set_active(2)
        filter_combo.set_sensitive(False)
        
        
        filter_box = gtk.HBox()
        filter_box.pack_start(filter_label,False,False)
        filter_box.pack_start(filter_combo,True,True)

        filter_check.connect('toggled',lambda b: filter_combo.set_sensitive(filter_check.get_active()))
        filter_check.connect('toggled',lambda b: filter_label.set_sensitive(filter_check.get_active()))
        
        # table layout
        
        table = gtk.Table(2,6,False)
        table.set_row_spacings(5)
        table.set_col_spacings(5)
        table.attach(id_check,0,1,0,1,xoptions=False,yoptions=False)
        table.attach(id_box,1,2,0,1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        table.attach(name_check,0,1,1,2,xoptions=False,yoptions=False)
        table.attach(name_box,1,2,1,2,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        table.attach(gender_check,0,1,2,3,xoptions=False,yoptions=False)
        table.attach(gender_box,1,2,2,3,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        table.attach(birth_check,0,1,3,4,xoptions=False,yoptions=False)
        table.attach(birth_box,1,2,3,4,xoptions=gtk.EXPAND|gtk.FILL,yoptions=gtk.EXPAND|gtk.FILL)

        table.attach(death_check,0,1,4,5,xoptions=False,yoptions=False)
        table.attach(death_box,1,2,4,5,xoptions=gtk.EXPAND|gtk.FILL,yoptions=gtk.EXPAND|gtk.FILL)

        table.attach(filter_check,0,1,5,6,xoptions=False,yoptions=False)
        table.attach(filter_box,1,2,5,6,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        # Apply

        apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        
        
        # Outer box

        outer_box = gtk.VBox()
        outer_box.pack_start(table,True,True)
        outer_box.pack_start(apply_button,False,False)
        outer_box.set_border_width(self.__class__.__default_border_width/2)
        outer_box.set_spacing(self.__class__.__default_border_width/2)
        
	align.add(outer_box)
        align.set_padding(self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width)
                          

	self.add(align)

	
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonSearchCriteriaWidget)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonSearchCriteriaWidget()
    w.add(f)
    w.show_all()

    gtk.main()
