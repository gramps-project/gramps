
class FilterSpecBase(object):

    def __init__(self):
        self._gramps_id = None

    def set_gramps_id(self,gramps_id):
        self._gramps_id = gramps_id

    def get_gramps_id(self):
        return self._gramps_id

    def include_gramps_id(self):
        return self._gramps_id is not None
