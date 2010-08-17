import gtk

class ValidatableMaskedEntry(gtk.Entry):
    __gtype_name__ = 'ValidatableMaskedEntry'

class StyledTextEditor(gtk.TextView):
    __gtype_name__ = 'StyledTextEditor'

class UndoableBuffer(gtk.TextBuffer):
    __gtype_name__ = 'UndoableBuffer'
