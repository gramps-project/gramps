import gtk
import gobject

from GrampsWidgets import IntEdit
from _FilterFrameBase import FilterFrameBase
import GenericFilter

class PersonFilterFrame(FilterFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,dbstate,label="Filter"):
	FilterFrameBase.__init__(self,label)

        # Gramps ID
        self._id_check = gtk.CheckButton()
        id_label = gtk.Label("Gramps ID")
        id_label.set_alignment(xalign=0,yalign=0.5)

        self._id_edit = gtk.Entry()
        self._id_edit.set_sensitive(False)

        self._id_check.connect('toggled',lambda b: self._id_edit.set_sensitive(self._id_check.get_active()))

        # Name
	self._name_check = gtk.CheckButton()
        name_label = gtk.Label("Name")
        name_label.set_alignment(xalign=0,yalign=0.5)

        self._name_edit = gtk.Entry()
        self._name_edit.set_sensitive(False)
        
        self._name_check.connect('toggled',lambda b: self._name_edit.set_sensitive(self._name_check.get_active()))

        # Gender
	self._gender_check = gtk.CheckButton()
        gender_label = gtk.Label("Gender")
        gender_label.set_alignment(xalign=0,yalign=0.5)

        self._gender_combo = gtk.combo_box_new_text()
        self._gender_combo.append_text("Male")
        self._gender_combo.append_text("Female")
        self._gender_combo.append_text("Unknown")
        self._gender_combo.set_active(2)
        self._gender_combo.set_sensitive(False)

        self._gender_check.connect('toggled',lambda b: self._gender_combo.set_sensitive(self._gender_check.get_active()))

        # Birth
        self._birth_check = gtk.CheckButton()
        self._birth_check.set_alignment(xalign=0,yalign=0)

        b_label = gtk.Label("Birth Year")
        b_label.set_alignment(xalign=0,yalign=0)
        
        self._b_edit = IntEdit()
        self._b_edit.set_sensitive(False)

        self._b_before = gtk.RadioButton(group=None,label="Before")
        self._b_before.set_sensitive(False)

        self._b_after = gtk.RadioButton(self._b_before,"After")
        self._b_after.set_sensitive(False)
        self._b_before.set_active(True)
        
        self._b_unknown = gtk.CheckButton("Include Unknown")
        self._b_unknown.set_sensitive(False)
        self._b_unknown.set_active(True)

        self._birth_check.connect('toggled',lambda b: self._b_edit.set_sensitive(self._birth_check.get_active()))
        self._birth_check.connect('toggled',lambda b: self._b_before.set_sensitive(self._birth_check.get_active()))
        self._birth_check.connect('toggled',lambda b: self._b_after.set_sensitive(self._birth_check.get_active()))
        self._birth_check.connect('toggled',lambda b: self._b_unknown.set_sensitive(self._birth_check.get_active()))

        self._b_inner_box = gtk.HBox()
        self._b_inner_box.pack_start(self._b_before)
        self._b_inner_box.pack_start(self._b_after)
        
        # Death

        self._death_check = gtk.CheckButton()

        d_label = gtk.Label("Death Year")
        d_label.set_alignment(xalign=0,yalign=0)

        self._d_edit = IntEdit()
        self._d_edit.set_sensitive(False)

        self._d_before = gtk.RadioButton(group=None,label="Before")
        self._d_before.set_sensitive(False)

        self._d_after = gtk.RadioButton(self._d_before,"After")
        self._d_after.set_sensitive(False)

        self._d_before.set_active(True)
        self._d_before.set_sensitive(False)

        self._d_unknown = gtk.CheckButton("Include Unknown")
        self._d_unknown.set_sensitive(False)
        self._d_unknown.set_active(True)

        self._death_check.connect('toggled',lambda b: self._d_edit.set_sensitive(self._death_check.get_active()))
        self._death_check.connect('toggled',lambda b: self._d_before.set_sensitive(self._death_check.get_active()))
        self._death_check.connect('toggled',lambda b: self._d_after.set_sensitive(self._death_check.get_active()))
        self._death_check.connect('toggled',lambda b: self._d_unknown.set_sensitive(self._death_check.get_active()))

        d_inner_box = gtk.HBox()
        d_inner_box.pack_start(self._d_before)
        d_inner_box.pack_start(self._d_after)

        # Filter
	self._filter_check = gtk.CheckButton()
        filter_label = gtk.Label("Filter")
        filter_label.set_alignment(xalign=0,yalign=0.5)

        self._filter_combo = gtk.combo_box_new_text()
        self._filter_combo.append_text("Male")
        self._filter_combo.append_text("Female")
        self._filter_combo.append_text("Unknown")
        self._filter_combo.set_active(2)
        self._filter_combo.set_sensitive(False)
        
        
        self._filter_check.connect('toggled',lambda b: self._filter_combo.set_sensitive(self._filter_check.get_active()))
        
        # table layout
        
        current_row = 0
        
        self._table.attach(self._id_check,self._check_col,self._check_col+1,
                           current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(id_label,self._label_col,self._label_col+1,
                           current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(self._id_edit,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1
        
        self._table.attach(self._name_check,self._check_col,self._check_col+1,
                           current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(name_label,self._label_col,self._label_col+1,
                           current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(self._name_edit,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1

        self._table.attach(self._gender_check,self._check_col,self._check_col+1,
                           current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(gender_label,self._label_col,self._label_col+1,
                           current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(self._gender_combo,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)


        current_row +=1

        self._table.attach(self._birth_check,self._check_col,self._check_col+1,
                           current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(b_label,self._label_col,self._label_col+1,
                           current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(self._b_edit,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        
        current_row +=1
        self._table.attach(self._b_inner_box,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        
        current_row +=1
        self._table.attach(self._b_unknown,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1

        self._table.attach(self._death_check,self._check_col,self._check_col+1,
                           current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(d_label,self._label_col,self._label_col+1,current_row,
                           current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(self._d_edit,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        
        current_row +=1
        self._table.attach(d_inner_box,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        
        current_row +=1
        self._table.attach(self._d_unknown,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1

        self._table.attach(self._filter_check,self._check_col,self._check_col+1,
                           current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(filter_label,self._label_col,self._label_col+1,
                           current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(self._filter_combo,self._control_col,self._control_col+1,
                           current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

    def on_apply(self,button):
        filter = GenericFilter.GenericFilter()
        
        if self._id_check.get_active():
            filter.add_rule(GenericFilter.HasIdOf([self._id_edit.get_text()]))

	self.emit('apply-filter',filter)
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonFilterFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonFilterFrame()
    w.add(f)
    
    w.show_all()

    gtk.main()
