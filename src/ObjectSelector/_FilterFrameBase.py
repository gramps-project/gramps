import gtk
import gobject

from GrampsWidgets import IntEdit
import GenericFilter

class FilterFrameBase(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        'apply-filter': (gobject.SIGNAL_RUN_LAST,
                         gobject.TYPE_NONE,
                         (gobject.TYPE_PYOBJECT,))
        }

    __default_border_width = 5

    def __init__(self,filter_spec=None,label="Filter"):
	gtk.Frame.__init__(self,label)
                
        self._filter_spec = filter_spec    

	align = gtk.Alignment()

        # table layout
        
        self._table = gtk.Table(3,6,False)
        self._table.set_row_spacings(5)
        self._table.set_col_spacings(5)

        self._label_col = 0
        self._check_col = 1
        self._control_col = 2
        

        # Apply

        apply_button = gtk.Button(stock=gtk.STOCK_APPLY)
        apply_button.connect('clicked',self.on_apply)

        # Outer box

        outer_box = gtk.VBox()
        outer_box.pack_start(self._table,True,True)
        outer_box.pack_start(apply_button,False,False)
        outer_box.set_border_width(self.__class__.__default_border_width/2)
        outer_box.set_spacing(self.__class__.__default_border_width/2)
        
	align.add(outer_box)
        align.set_padding(self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width)
                          

	self.add(align)


    def on_apply(self,button):
        """Build a GenericFilter object from the settings in the filter controls and
        emit a 'apply-filter' signal with the GenericFilter object as the parameter."""
        
        pass
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FilterFrameBase)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonFilterFrame()
    w.add(f)
    w.show_all()

    gtk.main()
