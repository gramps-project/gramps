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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import string

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import Plugins
from intl import gettext as _
import TextDoc
import DrawDoc

#-------------------------------------------------------------------------
#
# SvgDrawDoc
#
#-------------------------------------------------------------------------
class SvgDrawDoc(DrawDoc.DrawDoc):

    def __init__(self,styles,type,orientation):
        DrawDoc.DrawDoc.__init__(self,styles,type,orientation)
        self.f = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"
	self.page = 0

    def open(self,filename):
        if filename[-4:] != ".svg":
            self.root = filename
        else:
            self.root = filename[:-4]

    def close(self):
        pass
        
    def start_paragraph(self,style_name):
	pass

    def end_paragraph(self):
        pass

    def write_text(self,text):
        pass

    def start_page(self,orientation=None):
	self.page = self.page + 1
        if self.page != 1:
            name = "%s-%d.svg" % (self.root,self.page)
        else:
            name = "%s.svg" % self.root
        self.f = open(name,"w")
            
        self.f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        self.f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" ')
        self.f.write('"http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">\n')
        self.f.write('<svg width="%5.2fcm" height="%5.2fcm" ' % (self.width,self.height))
        self.f.write('xmlns="http://www.w3.org/2000/svg">\n')
        if self.orientation != TextDoc.PAPER_PORTRAIT:
            self.f.write('<g transform="rotate(-90); ')
            self.f.write(' translate(-%5.2fcm,0)">\n' % self.height)
            
    def end_page(self):
        if self.orientation != TextDoc.PAPER_PORTRAIT:
            self.f.write('</g>\n')
        self.f.write('</svg>\n')
        self.f.close()
    
    def draw_line(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin

        self.f.write('<line x1="%4.2fcm" y1="%4.2fcm" ' % (x1*28.35,y1*28.35))
        self.f.write('x2="%4.2fcm" y2="%4.2fcm" ' % (x2*28.35,y2*28.35))
        self.f.write(' style="stroke:#000000;stroke-width=1"/>\n')

    def draw_bar(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin

	s = self.draw_styles[style]
        self.f.write('<rect ')
        self.f.write('x="%4.2fcm" ' % x1)
        self.f.write('y="%4.2fcm" ' % y1)
        self.f.write('width="%4.2fcm" ' % (x2-x1))
        self.f.write('height="%4.2fcm" ' % (y2-y1))
        self.f.write('style="fill:#ffffff;stroke:#000000;')
        self.f.write('stroke-width:%.2f"/>\n' % s.get_line_width())
    
    def draw_box(self,style,text,x,y):
        x = x + self.lmargin
        y = y + self.tmargin

	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()
	p = self.style_list[para_name]
        
        bh = box_style.get_height()
        bw = box_style.get_width()
        self.f.write('<rect ')
        self.f.write('x="%4.2fcm" ' % (x+0.15))
        self.f.write('y="%4.2fcm" ' % (y+0.15))
        self.f.write('width="%4.2fcm" ' % bw)
        self.f.write('height="%4.2fcm" ' % bh)
        self.f.write('style="fill:#808080;stroke:#808080;stroke-width:1"/>\n')
        self.f.write('<rect ')
        self.f.write('x="%4.2fcm" ' % x)
        self.f.write('y="%4.2fcm" ' % y)
        self.f.write('width="%4.2fcm" ' % bw)
        self.f.write('height="%4.2fcm" ' % bh)
        self.f.write('style="fill:#%02x%02x%02x;stroke:#000000;stroke-width:1"/>\n' % box_style.get_color())
        if text != "":
            font = p.get_font()
            font_size = font.get_size()
            lines = string.split(text,'\n')
            nlines = len(lines)
            mar = 10/28.35
            fs = (font_size/28.35) * 1.2
            center = y + (bh + fs)/2.0 + (fs*0.2)
            ystart = center - (fs/2.0) * nlines
            for i in range(nlines):
                ypos = ystart + (i * fs)
                self.f.write('<text ')
                self.f.write('x="%4.2fcm" ' % (x+mar))
                self.f.write('y="%4.2fcm" ' % ypos)
                self.f.write('style="fill:#%02x%02x%02x; '% font.get_color())
                if font.get_bold():
                    self.f.write('font-weight="bold";')
                if font.get_italic():
                    self.f.write('font-style="italic";')
                self.f.write('font-size:%d;' % font_size)
                if font.get_type_face() == TextDoc.FONT_SANS_SERIF:
                    self.f.write('font-family=sans-serif;')
                else:
                    self.f.write('font-family=serif;')
                self.f.write('">')
                self.f.write(lines[i])
                self.f.write('</text>\n')

    def draw_text(self,style,text,x,y):
        x = x + self.lmargin
        y = y + self.tmargin
        
	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()
	p = self.style_list[para_name]
        
        font = p.get_font()
        font_size = font.get_size()
        fs = (font_size/28.35) * 1.2
        self.f.write('<text ')
        self.f.write('x="%4.2fcm" ' % x)
        self.f.write('y="%4.2fcm" ' % (y+fs))
        self.f.write('style="fill:#%02x%02x%02x; '% font.get_color())
        if font.get_bold():
            self.f.write('font-weight="bold";')
        if font.get_italic():
            self.f.write('font-style="italic";')
        self.f.write('font-size:%d;' % font_size)
        if font.get_type_face() == TextDoc.FONT_SANS_SERIF:
            self.f.write('font-family=sans-serif;')
        else:
            self.f.write('font-family=serif;')
        self.f.write('">')
        self.f.write(text)
        self.f.write('</text>\n')
        
#-------------------------------------------------------------------------
#
# Register document generator
#
#-------------------------------------------------------------------------
Plugins.register_draw_doc(_("SVG (Scalable Vector Graphics)"),SvgDrawDoc);
