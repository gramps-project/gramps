#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import StringIO

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from PluginUtils import register_draw_doc
import BaseDoc
import Errors

#-------------------------------------------------------------------------
#
# SvgDrawDoc
#
#-------------------------------------------------------------------------
class SvgDrawDoc(BaseDoc.BaseDoc,BaseDoc.DrawDoc):

    def __init__(self,styles,type,template):
        BaseDoc.BaseDoc.__init__(self,styles,type,template)
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

    def start_page(self):
        self.page = self.page + 1
        if self.page != 1:
            name = "%s-%d.svg" % (self.root,self.page)
        else:
            name = "%s.svg" % self.root

        try:
            self.f = open(name,"w")
        except IOError,msg:
            raise Errors.ReportError(_("Could not create %s") % name, msg)
        except:
            raise Errors.ReportError(_("Could not create %s") % name)
        
        self.t = StringIO.StringIO()
            
        self.f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        self.f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" ')
        self.f.write('"http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">\n')
        self.f.write('<svg width="%5.2fcm" height="%5.2fcm" ' % (self.paper.get_size().get_width(),self.paper.get_size().get_height()))
        self.f.write('xmlns="http://www.w3.org/2000/svg">\n')

    def rotate_text(self,style,text,x,y,angle):
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)
        font = p.get_font()
        size = font.get_size()

        width = 0
        height = 0
        for line in text:
            width = max(width,self.string_width(font,line))
            height += size

        centerx,centery = units(( x+self.paper.get_left_margin(),
                                  y+self.paper.get_top_margin() ))
        xpos = (centerx - (width/2.0)) 
        ypos = (centery - (height/2.0)) 

        self.t.write('<text ')
        self.t.write('x="%4.2f" y="%4.2f" ' % (xpos,ypos))
        self.t.write('transform="rotate(%d %4.2f %4.2f)" ' % (angle,centerx,centery))
        self.t.write('style="fill:#%02x%02x%02x; '% font.get_color())
        if font.get_bold():
            self.t.write('font-weight:"bold";')
        if font.get_italic():
            self.t.write('font-style:"italic";')
        self.t.write('font-size:%d; ' % size)
        if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            self.t.write('font-family:sans-serif;')
        else:
            self.t.write('font-family:serif;')
        self.t.write('">')
    
        for line in text:
            # Center this line relative to the rest of the text
            linex = xpos + (width - self.string_width(font,line) ) / 2
            self.t.write('<tspan x="%4.2f" dy="%d">' % (linex,size))
            self.t.write(line)
            self.t.write('</tspan>')
        self.t.write('</text>\n')
                           
    def end_page(self):
        # Print the text last for each page so that it is rendered on top of 
        # other graphic elements.
        self.f.write(self.t.getvalue())
        self.t.close()
        self.f.write('</svg>\n')
        self.f.close()
    
    def draw_line(self,style,x1,y1,x2,y2):
        x1 = x1 + self.paper.get_left_margin()
        x2 = x2 + self.paper.get_left_margin()
        y1 = y1 + self.paper.get_top_margin()
        y2 = y2 + self.paper.get_top_margin()

        style_sheet = self.get_style_sheet()
        s = style_sheet.get_draw_style(style)

        self.f.write('<line x1="%4.2fcm" y1="%4.2fcm" ' % (x1,y1))
        self.f.write('x2="%4.2fcm" y2="%4.2fcm" ' % (x2,y2))
        self.f.write('style="stroke:#%02x%02x%02x; ' % s.get_color())
        self.f.write('stroke-width:%.2fpt;"/>\n' % s.get_line_width())

    def draw_path(self,style,path):
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)

        point = path[0]
        self.f.write('<polygon fill="#%02x%02x%02x"' % stype.get_fill_color())
        self.f.write(' style="stroke:#%02x%02x%02x; ' % stype.get_color())
        self.f.write(' stroke-width:%.2fpt;"' % stype.get_line_width())
        self.f.write(' points="%.2f,%.2f' % units((point[0]+self.paper.get_left_margin(),point[1]+self.paper.get_top_margin())))
        for point in path[1:]:
            self.f.write(' %.2f,%.2f' % units((point[0]+self.paper.get_left_margin(),point[1]+self.paper.get_top_margin())))
        self.f.write('"/>\n')

    def draw_box(self,style,text,x,y, w, h):
        x = x + self.paper.get_left_margin()
        y = y + self.paper.get_top_margin()

        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)

        if box_style.get_shadow():
            self.f.write('<rect ')
            self.f.write('x="%4.2fcm" ' % (x+0.15))
            self.f.write('y="%4.2fcm" ' % (y+0.15))
            self.f.write('width="%4.2fcm" ' % w)
            self.f.write('height="%4.2fcm" ' % h)
            self.f.write('style="fill:#808080; stroke:#808080; stroke-width:1;"/>\n')
        self.f.write('<rect ')
        self.f.write('x="%4.2fcm" ' % x)
        self.f.write('y="%4.2fcm" ' % y)
        self.f.write('width="%4.2fcm" ' % w)
        self.f.write('height="%4.2fcm" ' % h)
        self.f.write('style="fill:#%02x%02x%02x; ' % box_style.get_fill_color())
        self.f.write('stroke:#%02x%02x%02x; ' % box_style.get_color())
        self.f.write('stroke-width:%f;"/>\n' % box_style.get_line_width())
        if text != "":
            para_name = box_style.get_paragraph_style()
            assert( para_name != '' )
            p = style_sheet.get_paragraph_style(para_name)
            font = p.get_font()
            font_size = font.get_size()
            lines = text.split('\n')
            nlines = len(lines)
            mar = 10/28.35
            fs = (font_size/28.35) * 1.2
            center = y + (h + fs)/2.0 + (fs*0.2)
            ystart = center - (fs/2.0) * nlines
            for i in range(nlines):
                ypos = ystart + (i * fs)
                self.t.write('<text ')
                self.t.write('x="%4.2fcm" ' % (x+mar))
                self.t.write('y="%4.2fcm" ' % ypos)
                self.t.write('style="fill:#%02x%02x%02x; '% font.get_color())
                if font.get_bold():
                    self.t.write(' font-weight:"bold";')
                if font.get_italic():
                    self.t.write(' font-style:"italic";')
                self.t.write(' font-size:%d;' % font_size)
                if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                    self.t.write(' font-family:sans-serif;')
                else:
                    self.t.write(' font-family:serif;')
                self.t.write('">')
                self.f.write(lines[i])
                self.t.write('</text>\n')

    def draw_text(self,style,text,x,y):
        x = x + self.paper.get_left_margin()
        y = y + self.paper.get_top_margin()
        
        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)
        para_name = box_style.get_paragraph_style()
        p = style_sheet.get_paragraph_style(para_name)
        
        font = p.get_font()
        font_size = font.get_size()
        fs = (font_size/28.35) * 1.2
        self.t.write('<text ')
        self.t.write('x="%4.2fcm" ' % x)
        self.t.write('y="%4.2fcm" ' % (y+fs))
        self.t.write('style="fill:#%02x%02x%02x;'% font.get_color())
        if font.get_bold():
            self.t.write('font-weight:bold;')
        if font.get_italic():
            self.t.write('font-style:italic;')
        self.t.write('font-size:%d; ' % font_size)
        if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            self.t.write('font-family:sans-serif;')
        else:
            self.t.write('font-family:serif;')
        self.t.write('">')
        self.t.write(text)
        self.t.write('</text>\n')

    def center_text(self, style, text, x, y):
        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)
        para_name = box_style.get_paragraph_style()
        p = style_sheet.get_paragraph_style(para_name)
        font = p.get_font()
        font_size = font.get_size()
        width = self.string_width(font,text) / 72
        x = x - width
        self.draw_text(style,text,x,y)

def units(val):
    return (val[0]*35.433, val[1]*35.433)

#-------------------------------------------------------------------------
#
# Register document generator
#
#-------------------------------------------------------------------------
register_draw_doc(_("SVG (Scalable Vector Graphics)"),SvgDrawDoc,1,1,".svg");
