import gtk
import gobject
from logging import getLogger
log = getLogger(".ObjectSelector")

import ImgManip

class PersonPreviewFrame(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,dbstate,label="Preview"):
	gtk.Frame.__init__(self,label)

        self._dbstate = dbstate
        
	align = gtk.Alignment()

        # Image
        self._image = gtk.Image()

        # test image
        self._image.set_from_file("../person.svg")
        image_frame = gtk.Frame()
        image_frame.add(self._image)
        
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

    def set_object_from_id(self,id):
        try:
            person = self._dbstate.db.get_person_from_gramps_id(id)
            if not person:
                return

            image_list = person.get_media_list()
            if image_list:
                mobj = self._dbstate.db.get_object_from_handle(image_list[0].ref)
                if mobj.get_mime_type()[0:5] == "image":
                    pixbuf = ImgManip.get_thumbnail_image(mobj.get_path())
                    self._image.set_from_pixbuf(pixbuf)
            else:
                self._image.set_from_file("../person.svg")

        except:
            log.warn("Failed to generate preview for person", exc_info=True)
            self._clear_object()

    def clear_object(self):
        self._image.set_from_file("../person.svg")
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonPreviewFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonPreviewFrame()
    w.add(f)
    w.show_all()

    gtk.main()
