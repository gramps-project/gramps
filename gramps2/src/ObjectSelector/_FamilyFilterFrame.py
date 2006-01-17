import gtk
import gobject

from GrampsWidgets import IntEdit

class FamilyFilterFrame(gtk.Frame):
    
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


        # Mar
        mar_check = gtk.CheckButton()
        mar_check.set_alignment(xalign=0,yalign=0)

        m_label = gtk.Label("Marriage Year")
        m_label.set_alignment(xalign=0,yalign=0)
        
        m_edit = IntEdit()
        m_edit.set_sensitive(False)

        m_before = gtk.RadioButton(group=None,label="Before")
        m_before.set_sensitive(False)

        m_after = gtk.RadioButton(m_before,"After")
        m_after.set_sensitive(False)
        m_before.set_active(True)
        
        m_unknown = gtk.CheckButton("Include Unknown")
        m_unknown.set_sensitive(False)
        m_unknown.set_active(True)

        mar_check.connect('toggled',lambda b: m_edit.set_sensitive(mar_check.get_active()))
        mar_check.connect('toggled',lambda b: m_before.set_sensitive(mar_check.get_active()))
        mar_check.connect('toggled',lambda b: m_after.set_sensitive(mar_check.get_active()))
        mar_check.connect('toggled',lambda b: m_unknown.set_sensitive(mar_check.get_active()))

        m_inner_box = gtk.HBox()
        m_inner_box.pack_start(m_before)
        m_inner_box.pack_start(m_after)
        

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

        table.attach(mar_check,check_col,check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        table.attach(m_label,label_col,label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        table.attach(m_edit,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        table.attach(m_inner_box,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        table.attach(m_unknown,control_col,control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

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
    gobject.type_register(FamilyFilterFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = FamilyFilterFrame()
    w.add(f)
    w.show_all()

    gtk.main()
