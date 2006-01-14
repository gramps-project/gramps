import gtk
import gobject

from _IntEdit import IntEdit

class PersonSearchCriteriaWidget(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,dbstate,label="Filter"):
	gtk.Frame.__init__(self,label)

	align = gtk.Alignment()

        # Gramps ID
        id_check = gtk.CheckButton()
        id_label = gtk.Label("Gramps ID")
        id_label.set_alignment(xalign=0,yalign=0.5)

        id_edit = gtk.Entry()
        id_edit.set_sensitive(False)

        id_check.connect('toggled',lambda b: id_edit.set_sensitive(id_check.get_active()))

        # Name
	name_check = gtk.CheckButton()
        name_label = gtk.Label("Name")
        name_label.set_alignment(xalign=0,yalign=0.5)

        name_edit = gtk.Entry()
        name_edit.set_sensitive(False)
        
        name_check.connect('toggled',lambda b: name_edit.set_sensitive(name_check.get_active()))

        # Gender
	gender_check = gtk.CheckButton()
        gender_label = gtk.Label("Gender")
        gender_label.set_alignment(xalign=0,yalign=0.5)

        gender_combo = gtk.combo_box_new_text()
        gender_combo.append_text("Male")
        gender_combo.append_text("Female")
        gender_combo.append_text("Unknown")
        gender_combo.set_active(2)
        gender_combo.set_sensitive(False)

        gender_check.connect('toggled',lambda b: gender_combo.set_sensitive(gender_check.get_active()))

        # Birth
        birth_check = gtk.CheckButton()
        birth_check.set_alignment(xalign=0,yalign=0)

        b_label = gtk.Label("Birth Year")
        b_label.set_alignment(xalign=0,yalign=0)
        
        b_edit = IntEdit()
        b_edit.set_sensitive(False)

        b_before = gtk.RadioButton(group=None,label="Before")
        b_before.set_sensitive(False)

        b_after = gtk.RadioButton(b_before,"After")
        b_after.set_sensitive(False)
        b_before.set_active(True)
        
        b_unknown = gtk.CheckButton("Include Unknown")
        b_unknown.set_sensitive(False)
        b_unknown.set_active(True)

        birth_check.connect('toggled',lambda b: b_edit.set_sensitive(birth_check.get_active()))
        birth_check.connect('toggled',lambda b: b_before.set_sensitive(birth_check.get_active()))
        birth_check.connect('toggled',lambda b: b_after.set_sensitive(birth_check.get_active()))
        birth_check.connect('toggled',lambda b: b_unknown.set_sensitive(birth_check.get_active()))

        b_inner_box = gtk.HBox()
        b_inner_box.pack_start(b_before)
        b_inner_box.pack_start(b_after)
        
        # Death

        death_check = gtk.CheckButton()

        d_label = gtk.Label("Death Year")
        d_label.set_alignment(xalign=0,yalign=0)

        d_edit = IntEdit()
        d_edit.set_sensitive(False)

        d_before = gtk.RadioButton(group=None,label="Before")
        d_before.set_sensitive(False)

        d_after = gtk.RadioButton(d_before,"After")
        d_after.set_sensitive(False)

        d_before.set_active(True)
        d_before.set_sensitive(False)

        d_unknown = gtk.CheckButton("Include Unknown")
        d_unknown.set_sensitive(False)
        d_unknown.set_active(True)

        death_check.connect('toggled',lambda b: d_edit.set_sensitive(death_check.get_active()))
        death_check.connect('toggled',lambda b: d_before.set_sensitive(death_check.get_active()))
        death_check.connect('toggled',lambda b: d_after.set_sensitive(death_check.get_active()))
        death_check.connect('toggled',lambda b: d_unknown.set_sensitive(death_check.get_active()))

        d_inner_box = gtk.HBox()
        d_inner_box.pack_start(d_before)
        d_inner_box.pack_start(d_after)

        # Filter
	filter_check = gtk.CheckButton()
        filter_label = gtk.Label("Filter")
        filter_label.set_alignment(xalign=0,yalign=0.5)

        filter_combo = gtk.combo_box_new_text()
        filter_combo.append_text("Male")
        filter_combo.append_text("Female")
        filter_combo.append_text("Unknown")
        filter_combo.set_active(2)
        filter_combo.set_sensitive(False)
        
        
        filter_check.connect('toggled',lambda b: filter_combo.set_sensitive(filter_check.get_active()))
        
        # table layout
        
        table = gtk.Table(3,6,False)
        table.set_row_spacings(5)
        table.set_col_spacings(5)

        label_col = 0
        check_col = 1
        control_col = 2
        
        current_row = 0
        
        table.attach(id_check,check_col,check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        table.attach(id_label,label_col,label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        table.attach(id_edit,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1
        
        table.attach(name_check,check_col,check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        table.attach(name_label,label_col,label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        table.attach(name_edit,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1

        table.attach(gender_check,check_col,check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        table.attach(gender_label,label_col,label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        table.attach(gender_combo,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)


        current_row +=1

        table.attach(birth_check,check_col,check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        table.attach(b_label,label_col,label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        table.attach(b_edit,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        table.attach(b_inner_box,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        table.attach(b_unknown,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1

        table.attach(death_check,check_col,check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        table.attach(d_label,label_col,label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        table.attach(d_edit,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        table.attach(d_inner_box,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        table.attach(d_unknown,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1

        table.attach(filter_check,check_col,check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        table.attach(filter_label,label_col,label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        table.attach(filter_combo,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

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
