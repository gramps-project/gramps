from _Constants import ObjectTypes

from _PersonSearchCriteriaWidget import PersonSearchCriteriaWidget
from _PersonPreviewFrame import PersonPreviewFrame
from _PersonTreeFrame import PersonTreeFrame

from _FamilyFilterFrame import FamilyFilterFrame
from _FamilyPreviewFrame import FamilyPreviewFrame
from _FamilyTreeFrame import FamilyTreeFrame


class FilterFactory(object):

    __frame_creators = {ObjectTypes.PERSON: PersonSearchCriteriaWidget,
                        ObjectTypes.FAMILY: FamilyFilterFrame}

    def get_frame(self,object_type,dbstate):
        return self.__class__.__frame_creators[object_type](dbstate)


class PreviewFactory(object):
    
    __frame_creators = {ObjectTypes.PERSON: PersonPreviewFrame,
                        ObjectTypes.FAMILY: FamilyPreviewFrame}

    def get_frame(self,object_type,dbstate):
        return self.__class__.__frame_creators[object_type](dbstate)

class TreeFactory(object):
    
    __frame_creators = {ObjectTypes.PERSON: PersonTreeFrame,
                        ObjectTypes.FAMILY: FamilyTreeFrame}

    def get_frame(self,object_type,dbstate):
        return self.__class__.__frame_creators[object_type](dbstate)

