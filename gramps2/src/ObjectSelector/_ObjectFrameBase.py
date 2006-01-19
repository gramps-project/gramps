#for debug, remove later
import sys
sys.path.append("..")

import gtk
import gobject

class ObjectFrameBase(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {}

    __default_border_width = 5

    def __init__(self,
                 dbstate,
                 uistate,
                 filter_frame,
                 preview_frame,
                 tree_frame):
        
        gtk.Frame.__init__(self)

        self._dbstate = dbstate
        self._uistate = uistate
        self._filter_frame = filter_frame
        self._preview_frame = preview_frame
        self._tree_frame = tree_frame

        self._preview_frame.set_sensitive(False)
        
        # Create the widgets for each of the object types

        vbox = gtk.VBox()
        vbox.show()

        vbox2 = gtk.VBox()
        vbox2.show()
        
        pane = gtk.HPaned()
        pane.show()
        
        vbox.pack_start(self._preview_frame,True,True)
        vbox.pack_start(self._filter_frame,True,True)
        vbox2.pack_start(self._tree_frame,True,True)

        pane.pack1(vbox2,True,False)
        pane.pack2(vbox,False,True)

        pane_align = gtk.Alignment()
        pane_align.add(pane)
        pane_align.set_padding(self.__class__.__default_border_width,
                               self.__class__.__default_border_width,
                               self.__class__.__default_border_width,
                               self.__class__.__default_border_width)
        pane_align.set(0.5,0.5,1,1)
        pane_align.show()
        
        self.add(pane_align)

        
    def set_preview(self,treeselection,id_field):
        (model, iter) = treeselection.get_selected()
        if iter and model.get_value(iter,id_field):
            self._preview_frame.set_sensitive(True)
            self._preview_frame.set_object_from_id(model.get_value(iter,id_field))
        else:
            self._preview_frame.set_sensitive(False)
            self._preview_frame.clear_object()


    def get_selection(self):
        return self._tree_frame.get_selection()
    
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(ObjectFrameBase)

if __name__ == "__main__":
    pass
