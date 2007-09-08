#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

import os.path

from xml.sax.saxutils import escape
from gettext import gettext as _

import gtk
import gobject
from logging import getLogger
log = getLogger(".ObjectSelector")

import ImgManip
import const
from ToolTips import PersonTip
import DateHandler

from _PreviewFrameBase import PreviewFrameBase

def short(val,size=60):
    if len(val) > size:
        return "%s..." % val[0:size]
    else:
        return val

class PersonPreviewFrame(PreviewFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,dbstate,label="Preview"):
	PreviewFrameBase.__init__(self,label)

        self._dbstate = dbstate
        
	align = gtk.Alignment()

        # Image
        self._image = gtk.Image()

        # test image
        self._image.set_from_file(os.path.join(const.IMAGE_DIR,"person.svg"))
        
        # Text
        label = gtk.Label()
        label.set_use_markup(True)
        label.set_line_wrap(True)
        label.set_justify(gtk.JUSTIFY_LEFT)
        label.set_alignment(xalign=0.5,yalign=0.1)
        
        # box
        box = gtk.VBox()
        box.pack_start(self._image,False,False)
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

        self._label = label

    def _get_text_preview(self,person):
        global escape

        birth_str = ""
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self._dbstate.db.get_event_from_handle(birth_ref.ref)
            date_str = DateHandler.get_date(birth)
            if date_str != "":
                birth_str = escape(date_str)

        death_str = ""
        death_ref = person.get_death_ref()
        if death_ref:
            death = self._dbstate.db.get_event_from_handle(death_ref.ref)
            date_str = DateHandler.get_date(death)
            if date_str != "":
                death_str = escape(date_str)

        s = "<span weight=\"bold\">%s</span>\n"\
            "   <span weight=\"normal\">%s:</span> %s\n"\
            "   <span weight=\"normal\">%s:</span> %s\n"\
            "   <span weight=\"normal\">%s:</span> %s\n"% (
            _("Person"),
            _("Name"),escape(person.get_primary_name().get_name()),
            _("Birth"),birth_str,
            _("Death"),death_str)

        if len(person.get_source_references()) > 0:
            psrc_ref = person.get_source_references()[0]
            psrc_id = psrc_ref.get_reference_handle()
            psrc = self._dbstate.db.get_source_from_handle(psrc_id)

            s += "\n<span weight=\"bold\">%s</span>\n"\
                 "   <span weight=\"normal\">%s:</span> %s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

    def set_object(self,person):
        try:
            image_list = person.get_media_list()
            if image_list:
                mobj = self._dbstate.db.get_object_from_handle(image_list[0].ref)
                if mobj.get_mime_type()[0:5] == "image":
                    pixbuf = ImgManip.get_thumbnail_image(mobj.get_path())
                    self._image.set_from_pixbuf(pixbuf)
            else:
                self._image.set_from_file(os.path.join(const.IMAGE_DIR,"person.svg"))

            self._label.set_markup(self._get_text_preview(person))

        except:
            log.warn("Failed to generate preview for person", exc_info=True)
            self.clear_object()

    def set_object_from_id(self,id):
        person = self._dbstate.db.get_person_from_gramps_id(id)
        if person:
            self.set_object(person)


    def clear_object(self):
        self._image.set_from_file(os.path.join(const.IMAGE_DIR,"person.svg"))
        self._label.set_markup("")

    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(PersonPreviewFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = PersonPreviewFrame()
    w.add(f)
    w.show_all()

    gtk.main()
