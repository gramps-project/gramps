#for debug, remove later
import sys
sys.path.append("..")

import gtk
import gobject

from RelLib import Person
from EditPerson import EditPerson

from _ObjectFrameBase import ObjectFrameBase
from _PersonFilterFrame import PersonFilterFrame
from _PersonPreviewFrame import PersonPreviewFrame
from _PersonTreeFrame import PersonTreeFrame

class PersonFrame(ObjectFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        'selection-changed'  : (gobject.SIGNAL_RUN_LAST,
                                gobject.TYPE_NONE,
                                (gobject.TYPE_STRING,
                                 gobject.TYPE_STRING)),
        
        'add-object': (gobject.SIGNAL_RUN_LAST,
                       gobject.TYPE_NONE,
                       ())

        }

    __person_id_field = 1
    
    def __init__(self,
                 dbstate,
                 uistate):
        
        ObjectFrameBase.__init__(self,
                                 dbstate=dbstate,
                                 uistate=uistate,
                                 filter_frame = PersonFilterFrame(dbstate),
                                 preview_frame = PersonPreviewFrame(dbstate),
                                 tree_frame = PersonTreeFrame(dbstate))

        def handle_selection(treeselection):
            (model, iter) = treeselection.get_selected()
            if iter and model.get_value(iter,1):                            
                self.emit('selection-changed', "%s [%s]" % (                
                    str(model.get_value(iter,0)),
                    str(model.get_value(iter,1))),
                          model.get_value(iter,1))
            else:
                self.emit('selection-changed',"No Selection","")
            

        self._tree_frame.get_selection().connect('changed',handle_selection)                
        self._tree_frame.get_selection().connect('changed',self.set_preview,self.__class__.__person_id_field)
        self._tree_frame.get_tree().connect('row-activated',self._on_row_activated)

        self._filter_frame.connect('apply-filter',lambda w,m: self._tree_frame.set_model(m))

    def _on_row_activated(self,widget,path,col):
        (model, iter) = widget.get_selection().get_selected()
        if iter and model.get_value(iter,self.__class__.__person_id_field):
            self.emit('add-object')

    def new_object(self,button):
        person = Person()
        EditPerson(self._dbstate,self._uistate,[],person)
        
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonFrame)

if __name__ == "__main__":
    pass
