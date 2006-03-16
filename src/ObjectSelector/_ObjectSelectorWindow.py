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

#for debug, remove later
import sys
sys.path.append("..")
sys.path.append(".")
sys.path.append("ObjectSelector")

import os.path
import gtk
import gobject
from TransUtils import sgettext as _

import _Factories
from _Constants import ObjectTypes

from DisplayState import ManagedWindow
import const

class _ObjectTypeWidgets(object):

    def __init__(self):
        self.frame = None
        self.sel_label = None
        self.selected_obj = None
        self.new_button = None

    def show(self):
        self.frame.show_all()
        self.sel_label.show_all()
        self.new_button.show()

    def hide(self):
        self.frame.hide_all()
        self.sel_label.hide_all()
        self.new_button.hide()

    def set_selected_obj(self,obj):
        self.selected_obj = obj

OBJECT_LIST = [ObjectTypes.PERSON, ObjectTypes.FAMILY,
               ObjectTypes.SOURCE, ObjectTypes.EVENT,
               ObjectTypes.MEDIA,  ObjectTypes.PLACE,
               ObjectTypes.REPOSITORY]

class ObjectSelectorWindow(gtk.Window,ManagedWindow):
    
    __gproperties__ = {}

    __gsignals__ = {
        'add-object'  : (gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         (gobject.TYPE_PYOBJECT,)),
        }

    __default_border_width = 5



    def __init__(self,
                 dbstate,
                 uistate,
                 track,
                 title = _("Select Object"),
                 filter_spec = None,
                 default_object_type = ObjectTypes.PERSON,
                 object_list = OBJECT_LIST):

        # Init the display manager
        ManagedWindow.__init__(self,uistate,track,self)

        # Init the Window
	gtk.Window.__init__(self)

        self._dbstate = dbstate
        self._uistate = dbstate
        self._track = track
        self._object_list = object_list
        self._current_object_type = None

        # Create objects to hold the information about
        # each object type
        self._object_frames = {}        
        for object_type in object_list:
            self._object_frames[object_type] = _ObjectTypeWidgets()

        self.set_title(title)
        
        # Selected object label

        new_button_box = gtk.VBox()
        new_button_box.show()
        
        for object_type in object_list:
            new_button = gtk.Button(stock=gtk.STOCK_NEW)

            self._object_frames[object_type].new_button = new_button
            new_button_box.pack_start(new_button)

        label = gtk.Label("<b>Selected:</b>")
        label.set_use_markup(True)
        label.set_alignment(xalign=0.9,yalign=0.5)
        label.set_padding(self.__class__.__default_border_width,
                          self.__class__.__default_border_width)

        label.show()

        sel_frame = gtk.Frame()
        sel_frame.set_shadow_type(gtk.SHADOW_IN)
        sel_frame.set_border_width(self.__class__.__default_border_width*2)

        sel_label_box = gtk.HBox()
        sel_label_box.show()
                
        for object_type in object_list:
            sel_label = gtk.Label("No Selected Object")
            sel_label.set_alignment(xalign=0,yalign=0.5)
            sel_label_box.pack_start(sel_label)

            self._object_frames[object_type].sel_label = sel_label

        sel_frame.add(sel_label_box)
        sel_frame.show()
        
        label_box = gtk.HBox()
        label_box.pack_start(new_button_box,False,False)
        label_box.pack_start(label,False,False)
        label_box.pack_start(sel_frame,True,True)
        label_box.show()
        
        # Object select
        obj_label = gtk.Label("<b>Show</b>")
        obj_label.set_use_markup(True)
        obj_label.set_alignment(xalign=0.9,yalign=0.5)
        obj_label.set_padding(self.__class__.__default_border_width,
                              self.__class__.__default_border_width)

        
        person_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"person.svg"))
        flist_pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(const.image_dir,"flist.svg"))

        self._tool_list = gtk.ListStore(gtk.gdk.Pixbuf, str,int)

        d={ObjectTypes.PERSON: [person_pixbuf,'People',ObjectTypes.PERSON],
           ObjectTypes.FAMILY: [flist_pixbuf,'Families',ObjectTypes.FAMILY],
           ObjectTypes.EVENT: [person_pixbuf,'Events',ObjectTypes.EVENT]}
        
        for object_type in self._object_list:        
            self._tool_list.append(d[object_type])
        
        self._tool_combo = gtk.ComboBox(self._tool_list)
        
        icon_cell = gtk.CellRendererPixbuf()
        label_cell = gtk.CellRendererText()
        
        self._tool_combo.pack_start(icon_cell, True)
        self._tool_combo.pack_start(label_cell, True)
        
        self._tool_combo.add_attribute(icon_cell, 'pixbuf', 0)
        self._tool_combo.add_attribute(label_cell, 'text', 1)

        self._tool_combo.set_active(0)

        self._tool_combo.connect('changed', lambda c: self._set_object_type(self._tool_list.get_value(c.get_active_iter(),2)))
        
        tool_box = gtk.HBox()
        tool_box.pack_start(obj_label,False,False)
        tool_box.pack_start(self._tool_combo,False,False)

        # only show the object_list if there is more than
        # one object_type requested.
        if len(self._object_list) > 1:
            self._tool_combo.show()
            obj_label.show()
            tool_box.show()

        # Top box

        top_box = gtk.HBox()
        top_box.pack_start(tool_box,False,False)
        top_box.pack_start(label_box,True,True)
        top_box.show()
        
        # Create the widgets for each of the object types

        # Object frame box

        frame_box = gtk.HBox()
        frame_box.show()


        for object_type in object_list:
            
            self._object_frames[object_type].frame = \
                        _Factories.ObjectFrameFactory().get_frame(object_type,dbstate,uistate,filter_spec)

            # connect signals                
            self._object_frames[object_type].frame.connect(
                'selection-changed',
                lambda widget,text,selected_object,label: label.set_text(text),
                self._object_frames[object_type].sel_label)

            self._object_frames[object_type].frame.connect(
                'selection-changed',
                lambda widget,text,selected_object,current_object: current_object.set_selected_obj(selected_object),
                self._object_frames[object_type])

            self._object_frames[object_type].frame.connect(
                'selection-changed',
                self.on_selection_changed)

            self._object_frames[object_type].frame.connect(
                'add-object',
                self.on_add)
            
            self._object_frames[object_type].new_button.connect(
                'clicked',
                self._object_frames[object_type].frame.new_object)
            
            frame_box.pack_start(self._object_frames[object_type].frame,True,True)

        
        # Bottom buttons
        self._add_button = gtk.Button(stock=gtk.STOCK_ADD)
        self._add_button.set_sensitive(False)
        self._add_button.show()

        self._add_button.connect("clicked", self.on_add)
        
        cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel_button.show()
        
        cancel_button.connect_object("clicked", self._close_window, self)
        
        bottom_button_bar = gtk.HButtonBox()
        bottom_button_bar.set_layout(gtk.BUTTONBOX_SPREAD)
        bottom_button_bar.set_spacing(self.__class__.__default_border_width/2)
        bottom_button_bar.set_border_width(self.__class__.__default_border_width)
        bottom_button_bar.add(cancel_button)
        bottom_button_bar.add(self._add_button)
        bottom_button_bar.show()
        
        box = gtk.VBox()
        box.pack_start(top_box,False,False)
        box.pack_start(frame_box,True,True)
        box.pack_start(bottom_button_bar,False,False)
        box.show()
        
        align = gtk.Alignment()
        align.set_padding(self.__class__.__default_border_width,
                           self.__class__.__default_border_width,
                           self.__class__.__default_border_width,
                           self.__class__.__default_border_width)
        align.set(0.5,0.5,1,1)
        align.add(box)
        align.show()
        
	self.add(align)

        self._set_object_type(default_object_type)
        self.set_default_size(700,300)

        self.show()


    def _close_window(self,obj):
        self.close()

    def _set_object_type(self,selected_object_type):
        # enable selected object type
        self._object_frames[selected_object_type].show()

        # disable all the others
        [ self._object_frames[object_type].hide() for object_type in self._object_list
          if object_type != selected_object_type]

        # Set the object selector list to the selected object type
        # this is required because we may be asked to set the object type
        # without the use selecting it explicitly from the list.
        store = self._tool_list
        it = store.get_iter_first()
        while it:
            if store.get(it, 2)[0] == selected_object_type:
                break
            it = store.iter_next(it)

        if it != None:
            self._tool_combo.set_active_iter(it)

        self._current_object_type = selected_object_type

        # Set the add button sensitivity
        if self._object_frames[selected_object_type].selected_obj:
            self._add_button.set_sensitive(True)
        else:
            self._add_button.set_sensitive(False)
            

    def on_add(self,widget=None,object=None):
        if object is None:
            self.emit('add-object',self._object_frames[self._current_object_type].selected_obj)
        else:
            self.emit('add-object',object)
        
    def on_selection_changed(self,widget,text,handle):
        if handle:
            self._add_button.set_sensitive(True)
        else:
            self._add_button.set_sensitive(False)
        
        
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(ObjectSelectorWindow)

if __name__ == "__main__":


    import GrampsDb
    import ViewManager
    import const

    import logging
    import sys,os.path
    
    form = logging.Formatter(fmt="%(relativeCreated)d: %(levelname)s: %(filename)s: line %(lineno)d: %(message)s")
    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setFormatter(form)
    stderrh.setLevel(logging.DEBUG)

    # everything.
    l = logging.getLogger()
    l.setLevel(logging.DEBUG)
    l.addHandler(stderrh)

    def cb(d):
        pass

    state = GrampsDb.DbState()
    vm = ViewManager.ViewManager(state)

    db = GrampsDb.gramps_db_factory(const.app_gramps)()
    db.load(os.path.realpath(sys.argv[1]),
            cb, # callback
            "w")
    class D:
        pass

    dbstate = D()
    dbstate.db = db


    w = ObjectSelectorWindow(dbstate=dbstate,
                             uistate=vm.uistate,
                             default_object_type = ObjectTypes.PERSON,
                             object_list=[ObjectTypes.PERSON,ObjectTypes.FAMILY])
    w.show()
    w.connect("destroy", gtk.main_quit)

    def add(w,results):
        print str(results)

    w.connect('add-object',add)
    
    gtk.main()
