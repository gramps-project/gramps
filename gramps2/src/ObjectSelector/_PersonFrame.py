#for debug, remove later
import sys
sys.path.append("..")

import gtk
import gobject

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
        }

    def __init__(self,
                 dbstate):
        
        ObjectFrameBase.__init__(self,
                                 dbstate=dbstate,
                                 filter_frame = PersonFilterFrame(dbstate),
                                 preview_frame = PersonPreviewFrame(dbstate),
                                 tree_frame = PersonTreeFrame(dbstate))

        def handle_selection(treeselection):
            (model, iter) = treeselection.get_selected()
            self.emit('selection-changed', "%s (%s)" % (                
                str(model.get_value(iter,0)),
                str(model.get_value(iter,1))),
                      model.get_value(iter,0))
            

        self._tree_frame.get_selection().connect('changed',handle_selection)

    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonFrame)

if __name__ == "__main__":
    pass
