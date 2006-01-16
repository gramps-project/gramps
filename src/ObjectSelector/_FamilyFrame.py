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

    __gsignals__ = {}

    __default_border_width = 5

    def __init__(self,
                 dbstate):
        
        ObjectFrameBase.__init__(self,
                                 dbstate=dbstate,
                                 filter_frame = FamilyFilterFrame(dbstate),
                                 preview_frame = FamilyPreviewFrame(dbstate),
                                 tree_frame = FamilyTreeFrame(dbstate))


    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FamilyFrame)

if __name__ == "__main__":
    pass
