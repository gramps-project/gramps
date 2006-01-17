import gtk
import gobject
from logging import getLogger
log = getLogger(".ObjectSelector")

import ImgManip

class FamilyPreviewFrame(gtk.Frame):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,dbstate,label="Preview"):
	gtk.Frame.__init__(self,label)

        self._dbstate = dbstate
        
	align = gtk.Alignment()

        # Image
        self._image_l = gtk.Image()
        self._image_r = gtk.Image()

        image_box = gtk.HBox()
        image_box.pack_start(self._image_l)
        image_box.pack_start(self._image_r)
                             
        # test image
        image_frame = gtk.Frame()
        image_frame.add(image_box)
        
        # Text
        label = gtk.Label()
        label.set_use_markup(True)
        label.set_line_wrap(True)
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_alignment(xalign=0.1,yalign=0.1)
        label.set_markup("<b>Father:</b> Joe Blogs\n"
                         "<b>Mother:</b> Joe Blogs\n"
                         "<b>m:</b> 1906\n")
        
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

        self.clear_object()

    def set_object_from_id(self,id):
        try:
            family = self._dbstate.db.get_family_from_gramps_id(id)

            image = [self._image_l, self._image_r]
            image_no = 0
            for person_handle in (family.get_father_handle(),family.get_mother_handle()):
                person = self._dbstate.db.get_person_from_handle(person_handle)
                if not person:
                    return

                image_list = person.get_media_list()
                if image_list:
                    mobj = self._dbstate.db.get_object_from_handle(image_list[0].ref)
                    if mobj.get_mime_type()[0:5] == "image":
                        pixbuf = ImgManip.get_thumbnail_image(mobj.get_path())
                        image[image_no].set_from_pixbuf(pixbuf)
                        image_no += 1
                else:
                    self._image_l.set_from_file("../person.svg")
                    self._image_r.set_from_file("../person.svg")

        except:
            log.warn("Failed to generate preview for family", exc_info=True)
            self.clear_object()

    def clear_object(self):
        self._image_l.set_from_file("../person.svg")
        self._image_r.set_from_file("../person.svg")

    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FamilyPreviewFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonPreviewFrame()
    w.add(f)
    w.show_all()

    gtk.main()
