from gettext import gettext as _

from _ObjectSelectorWindow import ObjectSelectorWindow
from _Constants import ObjectTypes
from _PersonFilterSpec import PersonFilterSpec

class PersonSelector(ObjectSelectorWindow):
    """Provides an ObjectSelectorWindow configured for selecting a person object."""

    def __init__(self,dbstate,uistate,track,filter_spec=None,title=_("Select Person")):
        ObjectSelectorWindow.__init__(self,dbstate,uistate,track,
                                      title=title,
                                      filter_spec=filter_spec,
                                      default_object_type = ObjectTypes.PERSON,
                                      object_list = [ObjectTypes.PERSON])
