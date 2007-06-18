#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

import gtk
import gobject

from GrampsWidgets import IntEdit

class FilterFrameBase(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        'apply-filter': (gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         (gobject.TYPE_PYOBJECT,)),
        'clear-filter': (gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         ())
        }

    __default_border_width = 5

    def __init__(self,filter_spec=None,label="Filter"):
	gtk.Frame.__init__(self,label)


        self._checkboxes = []
	self._active_widgets = []

	self._current_row = 0
                
        self._filter_spec = filter_spec    

        box = gtk.EventBox()
	align = gtk.Alignment()

        # table layout
        
        self._table = gtk.Table(3,6,False)
        self._table.set_row_spacings(5)
        self._table.set_col_spacings(5)

        self._label_col = 0
        self._check_col = 1
        self._control_col = 2
        

        # Apply / Clear

        apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        apply_button.connect('clicked',self.on_apply)
        clear_button = gtk.Button(stock=gtk.STOCK_CLEAR)
        clear_button.connect('clicked',self.on_clear)

        button_box = gtk.HButtonBox()
        button_box.set_layout(gtk.BUTTONBOX_SPREAD)
        button_box.pack_start(apply_button,False,False)
        button_box.pack_start(clear_button,False,False)
        

        # Outer box

        outer_box = gtk.VBox()
        outer_box.pack_start(self._table,True,True)
        outer_box.pack_start(button_box,False,False)
        outer_box.set_border_width(self.__class__.__default_border_width/2)
        outer_box.set_spacing(self.__class__.__default_border_width/2)
        
	align.add(outer_box)
        align.set_padding(self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width)
                          

        box.add(align)
	self.add(box)


    def _reset_widgets(self):
	for widget in self._active_widgets:
	    widget.set_sensitive(False)
        for check in self._checkboxes:
            check.set_active(False)

    def on_clear(self,button=None):
        self._reset_widgets()
        self.emit('clear-filter')

    def make_text_widget(self,widget_label):
	"""create a text edit widget with a label and check box."""

	check_col=self._check_col
	label_col=self._label_col
	control_col=self._control_col

	check = gtk.CheckButton()
	self._checkboxes.append(check)

	label = gtk.Label(widget_label)
	label.set_alignment(xalign=0,yalign=0.5)

	edit = gtk.Entry()
	self._active_widgets.append(edit)

	check.connect('toggled',lambda b: edit.set_sensitive(check.get_active()))

	self._table.attach(check,check_col,check_col+1,
			   self._current_row,self._current_row+1,xoptions=False,yoptions=False)
	self._table.attach(label,label_col,label_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.FILL,yoptions=False)
	self._table.attach(edit,control_col,control_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
	self._current_row += 1

	return(check,label,edit)

    def make_combo_widget(self,widget_label,list_model):
	"""create a combo widget with a label and check box."""
	check_col=self._check_col
	label_col=self._label_col
	control_col=self._control_col

	check = gtk.CheckButton()
	self._checkboxes.append(check)

	label = gtk.Label(widget_label)
	label.set_alignment(xalign=0,yalign=0.5)

	combo = gtk.ComboBox(list_model)
	self._active_widgets.append(combo)

	label_cell = gtk.CellRendererText()

	combo.pack_start(label_cell, True)
	combo.add_attribute(label_cell, 'text', 0)
	combo.set_active(2)

	check.connect('toggled',lambda b: combo.set_sensitive(check.get_active()))


	self._table.attach(check,check_col,check_col+1,
			   self._current_row,self._current_row+1,xoptions=False,yoptions=False)
	self._table.attach(label,label_col,label_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.FILL,yoptions=False)
	self._table.attach(combo,control_col,control_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
	self._current_row += 1

	return (check,label,combo)

    def make_year_widget(self,widget_label):
	"""Create a widget with a year edit entry, a before and after check box.
	Including a check box to enable and disable all the widgets."""
	check_col=self._check_col
	label_col=self._label_col
	control_col=self._control_col

	check = gtk.CheckButton()
	check.set_alignment(xalign=0,yalign=0)
	self._checkboxes.append(check)

	label = gtk.Label(widget_label)
	label.set_alignment(xalign=0,yalign=0)

	edit = IntEdit()
	self._active_widgets.append(edit)

	before = gtk.RadioButton(group=None,label="Before")
	self._active_widgets.append(before)

	after = gtk.RadioButton(before,"After")
	self._active_widgets.append(after)
	before.set_active(True)

	unknown = gtk.CheckButton("Include Unknown")
	self._active_widgets.append(unknown)
	unknown.set_active(False)

	check.connect('toggled',lambda b: edit.set_sensitive(check.get_active()))
	check.connect('toggled',lambda b: before.set_sensitive(check.get_active()))
	check.connect('toggled',lambda b: after.set_sensitive(check.get_active()))
	#check.connect('toggled',lambda b: unknown.set_sensitive(check.get_active()))

	inner_box = gtk.HBox()
	inner_box.pack_start(before)
	inner_box.pack_start(after)


	self._table.attach(check,check_col,check_col+1,
			   self._current_row,self._current_row+1,xoptions=False,yoptions=False)
	self._table.attach(label,label_col,label_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.FILL,yoptions=False)
	self._table.attach(edit,control_col,control_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

	self._current_row +=1
	self._table.attach(inner_box,control_col,control_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)

	self._current_row +=1
	self._table.attach(unknown,control_col,control_col+1,
			   self._current_row,self._current_row+1,xoptions=gtk.EXPAND|gtk.FILL,yoptions=False)
	self._current_row +=1

	return (check, edit, before, after, unknown)


    def on_apply(self,button):
        """Build a GenericFilter object from the settings in the filter controls and
        emit a 'apply-filter' signal with the GenericFilter object as the parameter."""
        
        raise NotImplementedError("subclass of FilterFrameBase must implement on_apply")
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FilterFrameBase)

