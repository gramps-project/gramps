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

    __gsignals__ = {}

    __default_border_width = 5

    def __init__(self,
                 dbstate):
        
        ObjectFrameBase.__init__(self,
                                 dbstate=dbstate,
                                 filter_frame = PersonFilterFrame(dbstate),
                                 preview_frame = PersonPreviewFrame(dbstate),
                                 tree_frame = PersonTreeFrame(dbstate))


    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonFrame)

if __name__ == "__main__":
    pass
