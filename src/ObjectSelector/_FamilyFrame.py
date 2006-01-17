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
        }

    __default_border_width = 5

    def __init__(self,
                 dbstate):
        
        ObjectFrameBase.__init__(self,
                                 dbstate=dbstate,
                                 filter_frame = FamilyFilterFrame(dbstate),
                                 preview_frame = FamilyPreviewFrame(dbstate),
                                 tree_frame = FamilyTreeFrame(dbstate))

        def handle_selection(treeselection):
            (model, iter) = treeselection.get_selected()
            if iter:
                self.emit('selection-changed', "%s / %s (%s)" % (                
                    str(model.get_value(iter,1)),
                    str(model.get_value(iter,2)),
                    str(model.get_value(iter,0))),
                          model.get_value(iter,0))
            else:
                self.emit('selection-changed',"No Selection","")
            

        self._tree_frame.get_selection().connect('changed',handle_selection)

        def set_preview_frame_sensitivity(treeselection):
            (model, iter) = treeselection.get_selected()
            if iter:
                self._preview_frame.set_sensitive(True)
            else:
                self._preview_frame.set_sensitive(False)

        self._tree_frame.get_selection().connect('changed',set_preview_frame_sensitivity)
        
            


    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FamilyFrame)

if __name__ == "__main__":
    pass
