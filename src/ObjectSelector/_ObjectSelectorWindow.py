#for debug, remove later
import sys
sys.path.append("..")

import gtk
import gobject

import _Factories
from _Constants import ObjectTypes

class _ObjectTypeWidgets(object):

    def __init__(self):
        self.frame = None

    def show(self):
        self.frame.show_all()

    def hide(self):
        self.frame.hide_all()

OBJECT_LIST = [ObjectTypes.PERSON, ObjectTypes.FAMILY,
               ObjectTypes.SOURCE, ObjectTypes.EVENT,
               ObjectTypes.MEDIA,  ObjectTypes.PLACE,
               ObjectTypes.REPOSITORY, ObjectTypes.REFERENCE]

class ObjectSelectorWindow(gtk.Window):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5



    def __init__(self,
                 dbstate,
                 default_object_type = ObjectTypes.PERSON,
                 object_list = OBJECT_LIST):
        
	gtk.Window.__init__(self)

        self._dbstate = dbstate
        self._object_list = object_list
        
        self.set_title("Add Person")
        
        # Selected object label
        label = gtk.Label("Selected:")
        label.set_alignment(xalign=1,yalign=0.5)
        label.show()
        
        sel_label = gtk.Label("No Selected Object")
        sel_frame = gtk.Frame()
        sel_frame.set_shadow_type(gtk.SHADOW_IN)
        sel_frame.set_border_width(self.__class__.__default_border_width*2)
        sel_frame.add(sel_label)
        sel_frame.show()
        
        label_box = gtk.HBox()
        label_box.pack_start(label,False,False)
        label_box.pack_start(sel_frame,True,True)
        label_box.show()
        
        # Object select

        obj_label = gtk.Label("Show")
        obj_label.set_alignment(xalign=1,yalign=0.5)
        obj_label.show()
        
        person_pixbuf = gtk.gdk.pixbuf_new_from_file("../person.svg")
        flist_pixbuf = gtk.gdk.pixbuf_new_from_file("../flist.svg")

        self._tool_list = gtk.ListStore(gtk.gdk.Pixbuf, str,int)
        self._tool_list.append([person_pixbuf,'People',ObjectTypes.PERSON])
        self._tool_list.append([flist_pixbuf,'Families',ObjectTypes.FAMILY])
        self._tool_list.append([person_pixbuf,'Events',ObjectTypes.EVENT])

        
        self._tool_combo = gtk.ComboBox(self._tool_list)
        
        icon_cell = gtk.CellRendererPixbuf()
        label_cell = gtk.CellRendererText()
        
        self._tool_combo.pack_start(icon_cell, True)
        self._tool_combo.pack_start(label_cell, True)
        
        self._tool_combo.add_attribute(icon_cell, 'pixbuf', 0)
        self._tool_combo.add_attribute(label_cell, 'text', 1)

        self._tool_combo.set_active(0)
        self._tool_combo.show()

        self._tool_combo.connect('changed', lambda c: self._set_object_type(self._tool_list.get_value(c.get_active_iter(),2)))
        
        tool_box = gtk.HBox()
        tool_box.pack_start(obj_label,False,False)
        tool_box.pack_start(self._tool_combo,False,False)
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
        
        self._object_frames = {}
        
        for object_type in object_list:
            self._object_frames[object_type] = _ObjectTypeWidgets()
            
            self._object_frames[object_type].frame = \
                        _Factories.ObjectFrameFactory().get_frame(object_type,dbstate)

            frame_box.pack_start(self._object_frames[object_type].frame,True,True)

        self._set_object_type(default_object_type)
        
        # Bottom buttons
        add_button = gtk.Button(stock=gtk.STOCK_ADD)
        add_button.set_sensitive(False)
        add_button.show()
        
        cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel_button.show()
        
        cancel_button.connect_object("clicked", gtk.Widget.destroy, self)
        
        bottom_button_bar = gtk.HButtonBox()
        bottom_button_bar.set_layout(gtk.BUTTONBOX_SPREAD)
        bottom_button_bar.set_spacing(self.__class__.__default_border_width/2)
        bottom_button_bar.set_border_width(self.__class__.__default_border_width)
        bottom_button_bar.add(cancel_button)
        bottom_button_bar.add(add_button)
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


    def _set_object_type(self,selected_object_type):
        # enable default
        self._object_frames[selected_object_type].show()

        # disable all the others
        [ self._object_frames[object_type].hide() for object_type in self._object_list
          if object_type != selected_object_type]

        store = self._tool_list
        it = store.get_iter_first()
        while it:
            if store.get(it, 2)[0] == selected_object_type:
                break
            it = store.iter_next(it)

        if it != None:
            self._tool_combo.set_active_iter(it)
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonSearchCriteriaWidget)

if __name__ == "__main__":


    import GrampsDb
    import const

    def cb(d):
        pass

    db = GrampsDb.gramps_db_factory(const.app_gramps)()
    db.load("/home/rtaylor/devel/Personal/gramps/test/Untitled_1.grdb",
            cb, # callback
            "w")
    class D:
        pass

    dbstate = D()
    dbstate.db = db
    

    w = ObjectSelectorWindow(dbstate=dbstate,
                             default_object_type = ObjectTypes.PERSON,
                             object_list=[ObjectTypes.PERSON,ObjectTypes.FAMILY])
    w.show()
    w.connect("destroy", gtk.main_quit)

    gtk.main()
