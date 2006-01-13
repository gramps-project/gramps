import gtk
import gobject

class PersonPreviewFrame(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,label="Filter"):
	gtk.Frame.__init__(self,label)

	align = gtk.Alignment()

        # Image
        image = gtk.Image()

        # test image
        image.set_from_file("../person.svg")
        image_frame = gtk.Frame()
        image_frame.add(image)
        
        # Text
        label = gtk.Label()
        label.set_use_markup(True)
        label.set_line_wrap(True)
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_alignment(xalign=0.1,yalign=0.1)
        label.set_markup("<b>Name:</b> Joe Blogs\n"
                         "<b>b:</b> 1906\n"
                         "<b>d:</b> 1937\n")
        
        # box
        box = gtk.VBox()
        box.pack_start(image_frame)
        box.pack_start(label)
        

        # align
        
	align.add(box)
        align.set_padding(self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width,
                          self.__class__.__default_border_width)
        align.set(0.5,0.5,
                  1.0,1.0)
                          

	self.add(align)

	
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonPreviewFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonPreviewFrame()
    w.add(f)
    w.show_all()

    gtk.main()
