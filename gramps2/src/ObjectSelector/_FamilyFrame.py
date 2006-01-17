#for debug, remove later
import sys
sys.path.append("..")

import gtk
import gobject

from _ObjectFrameBase import ObjectFrameBase
from _FamilyFilterFrame import FamilyFilterFrame
from _FamilyPreviewFrame import FamilyPreviewFrame
from _FamilyTreeFrame import FamilyTreeFrame

class FamilyFrame(ObjectFrameBase):
    
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

    __person_id_field = 0

    def __init__(self,
                 dbstate):
        
        ObjectFrameBase.__init__(self,
                                 dbstate=dbstate,
                                 filter_frame = FamilyFilterFrame(dbstate),
                                 preview_frame = FamilyPreviewFrame(dbstate),
                                 tree_frame = FamilyTreeFrame(dbstate))


        self._tree_frame.get_selection().connect('changed',self._handle_selection)
        self._tree_frame.get_selection().connect('changed',self.set_preview,self.__class__.__person_id_field)
        self._tree_frame.get_tree().connect('row-activated',self._on_row_activated)


    def _handle_selection(self,treeselection):
        (model, iter) = treeselection.get_selected()
        if iter and model.get_value(iter,self.__class__.__person_id_field):
            self.emit('selection-changed', "%s / %s [%s]" % (                
                str(model.get_value(iter,1)),
                str(model.get_value(iter,2)),
                str(model.get_value(iter,0))),
                      model.get_value(iter,self.__class__.__person_id_field))
        else:
            self.emit('selection-changed',"No Selection","")

    def _on_row_activated(self,widget,path,col):
        (model, iter) = widget.get_selection().get_selected()
        if iter and model.get_value(iter,self.__class__.__person_id_field):
            self.emit('add-object')
        

            


    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FamilyFrame)

if __name__ == "__main__":
    pass
