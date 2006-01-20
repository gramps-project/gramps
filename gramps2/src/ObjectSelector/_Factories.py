from _Constants import ObjectTypes

from _PersonFrame import PersonFrame
from _FamilyFrame import FamilyFrame


class ObjectFrameFactory(object):
    __frame_creators = {ObjectTypes.PERSON: PersonFrame,
                        ObjectTypes.FAMILY: FamilyFrame}

    def get_frame(self,object_type,dbstate,uistate,filter_spec=None):
        return self.__class__.__frame_creators[object_type](dbstate,uistate,filter_spec)
    

