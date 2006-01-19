import gtk
import gobject

from GrampsWidgets import IntEdit
from _FilterFrameBase import FilterFrameBase

class FamilyFilterFrame(FilterFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,dbstate,label="Filter"):
	FilterFrameBase.__init__(self,label)

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
        
        
        current_row = 0
        
        self._table.attach(id_check,self._check_col,self._check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(id_label,self._label_col,self._label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(id_edit,self._control_col,self._control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1
        
        self._table.attach(name_check,self._check_col,self._check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(name_label,self._label_col,self._label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(name_edit,self._control_col,self._control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)


        current_row +=1

        self._table.attach(mar_check,self._check_col,self._check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(m_label,self._label_col,self._label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(m_edit,self._control_col,self._control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        self._table.attach(m_inner_box,self._control_col,self._control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
        current_row +=1
        self._table.attach(m_unknown,self._control_col,self._control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

        current_row +=1

        self._table.attach(filter_check,self._check_col,self._check_col+1,current_row,current_row+1,xoptions=False,yoptions=False)
        self._table.attach(filter_label,self._label_col,self._label_col+1,current_row,current_row+1,xoptions=gtk.FILL,yoptions=False)
        self._table.attach(filter_combo,self._control_col,self._control_col+1,current_row,current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)


    def on_apply(self,button):
        pass
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FamilyFilterFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = FamilyFilterFrame()
    w.add(f)
    w.show_all()

    gtk.main()
