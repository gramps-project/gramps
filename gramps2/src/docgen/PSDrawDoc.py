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

import string
import cStringIO
import Plugins
from intl import gettext as _

import TextDoc
import DrawDoc


class PSDrawDoc(DrawDoc.DrawDoc):

    def __init__(self,styles,type,orientation):
        DrawDoc.DrawDoc.__init__(self,styles,type,orientation)
        self.f = None
        self.filename = None
        self.level = 0
	self.page = 0

    def translate(self,x,y):
        return (x,self.height-y)

    def fontdef(self,para):
        font = para.get_font()
        if font.get_type_face() == TextDoc.FONT_SERIF:
            if font.get_bold():
                if font.get_italic():
                    font_name = "/Times-BoldItalic"
                else:
                    font_name = "/Times-Bold"
            else:
                if font.get_italic():
                    font_name = "/Times-Italic"
                else:
                    font_name = "/Times-Roman"
        else:
            if font.get_bold():
                if font.get_italic():
                    font_name = "/Helvetica-BoldOblique"
                else:
                    font_name = "/Helvetica-Bold"
            else:
                if font.get_italic():
                    font_name = "/Helvetica-Oblique"
                else:
                    font_name = "/Helvetica"
        
        return "%s findfont %d scalefont setfont\n" % (font_name,font.get_size())
    
    def open(self,filename):
        if filename[-3:] != ".ps":
            self.filename = filename + ".ps"
        else:
            self.filename = filename

        self.f = open(self.filename,"w")
        
        self.f.write('%!PS-Adobe-3.0\n')
        self.f.write('%%LanguageLevel: 2\n')
        self.f.write('%%Pages: (atend)\n')
        self.f.write('%%PageOrder: Ascend\n')
        if self.orientation != TextDoc.PAPER_PORTRAIT:
            self.f.write('%%Orientation: Landscape\n')
        self.f.write('%%EndComments\n')
        self.f.write('/cm { 28.34 mul } def\n')

    def close(self):
        self.f.write('%%Trailer\n')
        self.f.write('%%Pages: ')
        self.f.write('%d\n' % self.page)
        self.f.write('%%EOF\n')
        self.f.close()
        
    def start_paragraph(self,style_name):
	pass

    def end_paragraph(self):
        pass

    def write_text(self,text):
        pass

    def start_page(self,orientation=None):
	self.page = self.page + 1
        self.f.write("%%Page:")
        self.f.write("%d %d\n" % (self.page,self.page))
        if self.orientation != TextDoc.PAPER_PORTRAIT:
            self.f.write('90 rotate %5.2f cm %5.2f cm translate\n' % (0,-1*self.height))

    def end_page(self):
        self.f.write('showpage\n')
        self.f.write('%%PageTrailer\n')

    def draw_text(self,style,text,x1,y1):
        x1 = x1 + self.lmargin
        y1 = y1 + self.tmargin

        stype = self.draw_styles[style]
	para_name = stype.get_paragraph_style()
	p = self.style_list[para_name]
        self.f.write('gsave\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x1,y1))
        self.f.write(self.fontdef(p))
        self.f.write('(%s) show\n' % text)
        self.f.write('grestore\n')

    def draw_line(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin
        stype = self.draw_styles[style]
        self.f.write('gsave\n')
        self.f.write('newpath\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x1,y1))
        self.f.write('%f cm %f cm lineto\n' % self.translate(x2,y2))
        self.f.write('%d setlinewidth\n' % stype.get_line_width())
        self.f.write('2 setlinecap\n')
        self.f.write('stroke\n')
        self.f.write('grestore\n')

    def patch_text(self,text):
        return text.encode('iso-8859-1')

    def draw_bar(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin

        box_type = self.draw_styles[style]
        self.f.write('gsave\n')
        self.f.write("%f cm %f cm moveto\n" % self.translate(x1,y1))
        self.f.write("0 %f cm rlineto\n" % (y2-y1)) 
        self.f.write("%f cm 0 rlineto\n" % (x2-x1)) 
        self.f.write("0  %f cm rlineto\n" % (y1-y2))
        self.f.write('closepath\n')
        self.f.write("%d setlinewidth\n" % box_type.get_line_width())
        self.f.write("stroke\n")
        self.f.write('grestore\n')
    
    def draw_box(self,style,text,x,y):
        x = x + self.lmargin
        y = y + self.tmargin

	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()
	p = self.style_list[para_name]
        text = self.patch_text(text)
        
        bh = box_style.get_height()
        bw = box_style.get_width()
        self.f.write('gsave\n')
#        if box_style.get_shadow():
        self.f.write('newpath\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x+0.15,y+0.15))
        self.f.write('0 -%f cm rlineto\n' % bh)
        self.f.write('%f cm 0 rlineto\n' % bw)
        self.f.write('0 %f cm rlineto\n' % bh)
        self.f.write('closepath\n')
        self.f.write('.5 setgray\n')
        self.f.write('fill\n')
        self.f.write('newpath\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x,y))
        self.f.write('0 -%f cm rlineto\n' % bh)
        self.f.write('%f cm 0 rlineto\n' % bw)
        self.f.write('0 %f cm rlineto\n' % bh)
        self.f.write('closepath\n')
        self.f.write('1 setgray\n')
        self.f.write('fill\n')
        self.f.write('newpath\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x,y))
        self.f.write('0 -%f cm rlineto\n' % bh)
        self.f.write('%f cm 0 rlineto\n' % bw)
        self.f.write('0 %f cm rlineto\n' % bh)
        self.f.write('closepath\n')
        self.f.write('0 setgray\n')
        self.f.write('1 setlinewidth\n')
        self.f.write('stroke\n')
	if text != "":
            self.f.write(self.fontdef(p))
            lines = string.split(text,'\n')
            nlines = len(lines)
            mar = 10/28.35
            f_in_cm = p.get_font().get_size()/28.35
            fs = f_in_cm * 1.2
            center = y + (bh + fs)/2.0 + (fs*0.2)
            ystart = center - (fs/2.0) * nlines
            for i in range(nlines):
                ypos = ystart + (i * fs)
                self.f.write('%f cm %f cm moveto\n' % self.translate(x+mar,ypos))
                self.f.write("(%s) show\n" % lines[i])
        self.f.write('grestore\n')
        
Plugins.register_draw_doc(_("PostScript"),PSDrawDoc);
