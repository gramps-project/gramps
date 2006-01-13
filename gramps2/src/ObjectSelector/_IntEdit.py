import gtk
import gobject

class IntEdit(gtk.Entry):
    """An gtk.Edit widget that only allows integers."""
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    def __init__(self):
	gtk.Entry.__init__(self)

        self._signal = self.connect("insert_text", self.insert_cb)

    def insert_cb(self, widget, text, length, *args):        
        # if you don't do this, garbage comes in with text
        text = text[:length]
        pos = widget.get_position()
        # stop default emission
        widget.emit_stop_by_name("insert_text")
        gobject.idle_add(self.insert, widget, text, pos)

    def insert(self, widget, text, pos):
        if len(text) > 0 and text.isdigit():            
            # the next three lines set up the text. this is done because we
            # can't use insert_text(): it always inserts at position zero.
            orig_text = widget.get_text()            
            new_text = orig_text[:pos] + text + orig_text[pos:]
            # avoid recursive calls triggered by set_text
            widget.handler_block(self._signal)
            # replace the text with some new text
            widget.set_text(new_text)
            widget.handler_unblock(self._signal)
            # set the correct position in the widget
            widget.set_position(pos + len(text))
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(IntEdit)

if __name__ == "__main__":

    w = gtk.Window()
    f = IntEdit()
    w.add(f)
    w.show_all()

    gtk.main()
