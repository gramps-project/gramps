import gobject
import gtk

class ValidatableMaskedEntry(gtk.Entry):
       __gtype_name__ = 'ValidatableMaskedEntry'

       def __init__(self):
               gtk.Entry.__init__(self)
               
class StyledTextEditor(gtk.TextView):
       __gtype_name__ = 'StyledTextEditor'

       def __init__(self):
               gtk.Entry.__init__(self)
