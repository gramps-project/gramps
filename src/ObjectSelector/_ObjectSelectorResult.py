
from _Constants import ObjectTypes

class ObjectSelectorResult(object):

    def __init__(self):
        self._gramps_id = None
        self._object_type = None

    def __str__(self):
        return "Object Type = %s\n"\
               "Gramps ID = %s" % (str(self._object_type),
                                   str(self._gramps_id))    
        
    def set_gramps_id(self,id):
        self._gramps_id = id

    def get_gramps_id(self):
        return self._gramps_id

    def set_object_type(self,object_type):
        self._object_type = object_type

    def get_object_type(self,object_type):
        return self._object_type

    def is_person(self):
        return self._object_type == ObjectTypes.PERSON

    def is_family(self):
        return self._object_type == ObjectTypes.FAMILY
    
    def is_event(self):
        return self._object_type == ObjectTypes.EVENT
    
    def is_source(self):
        return self._object_type == ObjectTypes.SOURCE
    
    def is_repository(self):
        return self._object_type == ObjectTypes.REPOSITORY
    
    def is_media(self):
        return self._object_type == ObjectTypes.MEDIA

    def is_place(self):
        return self._object_type == ObjectTypes.PLACE
