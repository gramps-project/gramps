#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import os
import string

from TextDoc import *
from DrawDoc import *
import Plugins
import intl
_ = intl.gettext

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    from reportlab.lib.colors import Color
except:
    raise Plugins.MissingLibraries, _("The ReportLab modules are not installed")

def make_color(color):
    return Color(float(color[0])/255.0, float(color[1])/255.0,
                 float(color[2])/255.0)

class PdfDrawDoc(DrawDoc):

    def __init__(self,styles,type,orientation):
        DrawDoc.__init__(self,styles,type,orientation)
        self.f = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"
	self.page = 0

    def open(self,filename):

        if filename[-4:] != ".pdf":
            self.filename = filename + ".pdf"
        else:
            self.filename = filename
        self.f = canvas.Canvas(self.filename,(self.width*cm,self.height*cm),0)
	if self.name:
	    self.f.setAuthor(self.name)

    def close(self):
	self.f.save()

    def start_paragraph(self,style_name):
	pass

    def end_paragraph(self):
        pass

    def write_text(self,text):
        pass

    def start_page(self,orientation=None):
	pass

    def end_page(self):
	self.f.showPage()

    def draw_line(self,style,x1,y1,x2,y2):
	self.f.line(x1*cm,y1*cm,x2*cm,y2*cm)

    def draw_box(self,style,text,x,y):
	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()
	p = self.style_list[para_name]

	w = box_style.get_width()*cm
        h = box_style.get_height()*cm

	if box_style.get_shadow():
            self.f.setFillColorRGB(0.5,0.5,0.5)
            self.f.rect((x+0.3)*cm,(y+0.3)*cm,w,h,fill=1,stroke=0)

	font = p.get_font()

        self.f.setStrokeColor(make_color(font.get_color()))
	self.f.setFillColor(make_color(box_style.get_color()))

 	self.f.rect(x*cm,y*cm,w,h,fill=1)

	if text != "":
            lines = string.split(text,'\n')
            self.center_print(lines,font,x*cm,y*cm,w,h)

    def write_at(self,style,text,x,y):
	p = self.style_list[style]
	font = p.get_font()

        self.f.setStrokeColor(make_color(font.get_color()))

        self.left_print(text,font,x*cm,y*cm)

    def center_print(self,lines,font,x,y,w,h):
        l = len(lines)
        size = font.get_size()
        start_y = (y + h/2.0 + l/2.0 + l) - ((l*size) + ((l-1)*0.2))/2.0
        start_x = (x + w/2.0)

        self.f.saveState()
        self.f.setFillColor(make_color(font.get_color()))
        if font.get_type_face() == FONT_SANS_SERIF:
            if font.get_bold():
                self.f.setFont("Helvetica-Bold",font.get_size())
            else:
                self.f.setFont("Helvetica",font.get_size())
        else:
            if font.get_bold():
                self.f.setFont("Times-Bold",font.get_size())
            else:
                self.f.setFont("Times-Roman",font.get_size())
       
        for text in lines:
            self.f.drawCentredString(start_x,start_y,text)
            start_y = start_y + size*1.2
        start_y = start_y + size*1.2

        self.f.restoreState()

    def left_print(self,text,font,x,y):
        size = font.get_size()
        start_y = y
        start_x = x

        self.f.saveState()
        self.f.setFillColor(make_color(font.get_color()))
        if font.get_type_face() == FONT_SANS_SERIF:
            if font.get_bold():
                self.f.setFont("Helvetica-Bold",font.get_size())
            else:
                self.f.setFont("Helvetica",font.get_size())
        else:
            if font.get_bold():
                self.f.setFont("Times-Bold",font.get_size())
            else:
                self.f.setFont("Times-Roman",font.get_size())
       
        self.f.drawString(start_x,start_y,text)
        self.f.restoreState()

Plugins.register_draw_doc(_("PDF"),PdfDrawDoc);
