#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
from math import pi, cos, sin
from gettext import gettext as _
        
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import PluginMgr
import Errors
import BaseDoc
from Report import run_print_dialog
from ReportUtils import pt2cm

#-------------------------------------------------------------------------
#
# PSDrawDoc
#
#-------------------------------------------------------------------------
class PSDrawDoc(BaseDoc.BaseDoc):

    def __init__(self,styles,type,template,orientation):
        BaseDoc.BaseDoc.__init__(self,styles,type,template,orientation)
        self.f = None
        self.filename = None
        self.level = 0
        self.page = 0

    def fontdef(self,para):
        font = para.get_font()
        if font.get_type_face() == BaseDoc.FONT_SERIF:
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
        
        return "%s find-latin-font %d scalefont setfont\n" % (font_name,font.get_size())

    def translate(self,x,y):
        return (x,self.height-y)

    def open(self,filename):
        if filename[-3:] != ".ps":
            self.filename = filename + ".ps"
        else:
            self.filename = filename

        try:
            self.f = open(self.filename,"w")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)
        
        self.f.write('%!PS-Adobe-3.0\n')
        self.f.write('%%LanguageLevel: 2\n')
        self.f.write('%%Pages: (atend)\n')
        self.f.write('%%PageOrder: Ascend\n')
        if self.orientation != BaseDoc.PAPER_PORTRAIT:
            self.f.write('%%Orientation: Landscape\n')
        else:
            self.f.write('%%Orientation: Portrait\n')
        self.f.write('%%EndComments\n')
        self.f.write('/cm { 28.34 mul } def\n')
        self.f.write('% build iso-latin-1 version of a font\n')
        self.f.write('/font-to-iso-latin-1 {	% <font> font-to-iso-latin-1 <font>\n')
        self.f.write('%% reencode for iso latin1; from the 2nd edition red book, sec 5.6.1\n')
        self.f.write('dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall\n')
        self.f.write('/Encoding ISOLatin1Encoding def currentdict end\n')
        self.f.write('dup /FontName get 80 string cvs (-ISOLatin1) concatstrings cvn \n')
        self.f.write('exch definefont\n')
        self.f.write('} def\n')
        self.f.write('\n')
        self.f.write('/find-latin-font {	% <name> find-latin-font <font>\n')
        self.f.write('findfont font-to-iso-latin-1\n')
        self.f.write('} def\n')
        
        self.filename = filename

    def close(self):
        self.f.write('%%Trailer\n')
        self.f.write('%%Pages: ')
        self.f.write('%d\n' % self.page)
        self.f.write('%%EOF\n')
        self.f.close()
        if self.print_req:
            run_print_dialog (self.filename)
        
    def write_text(self,text):
        pass

    def start_page(self):
        self.page = self.page + 1
        self.f.write("%%Page:")
        self.f.write("%d %d\n" % (self.page,self.page))
        if self.orientation != BaseDoc.PAPER_PORTRAIT:
            self.f.write('90 rotate %5.2f cm %5.2f cm translate\n' % (0,-1*self.height))

    def end_page(self):
        self.f.write('showpage\n')
        self.f.write('%%PageTrailer\n')

    def encode_text(self,p,text):
        fdef = self.fontdef(p)
        try:
            orig = unicode(text)
            new_text = orig.encode('iso-8859-1')
        except:
            new_text = "?"
        return (new_text,fdef)

    def center_text(self,style,text,x,y):
        x += self.lmargin
        y += self.tmargin

        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]

        (text,fdef) = self.encode_text(p,text)

        self.f.write('gsave\n')
        self.f.write('%.4f %.4f %.4f setrgbcolor\n' % rgb_color(stype.get_color()))
        self.f.write(fdef)
        self.f.write('(%s) dup stringwidth pop -2 div ' % text)
        self.f.write('%.4f cm add %.4f cm moveto ' % self.translate(x,y))
        self.f.write('show\n')
        self.f.write('grestore\n')

    def draw_text(self,style,text,x1,y1):
        stype = self.draw_styles[style]
        para_name = stype.get_paragraph_style()
        p = self.style_list[para_name]

        x1 = x1 + self.lmargin
        y1 = y1 + self.tmargin + pt2cm(p.get_font().get_size())

        (text,fdef) = self.encode_text(p,text)

        self.f.write('gsave\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x1,y1))
        self.f.write(fdef)
        self.f.write('(%s) show grestore\n' % text)

    def draw_wedge(self, style, centerx, centery, radius, start_angle,
                   end_angle, short_radius=0):

        while end_angle < start_angle:
            end_angle += 360

        p = []
        
        degreestoradians = pi/180.0
        radiansdelta = degreestoradians/2
        sangle = start_angle*degreestoradians
        eangle = end_angle*degreestoradians
        while eangle<sangle:
            eangle = eangle+2*pi
        angle = sangle

        if short_radius == 0:
            p.append((centerx,centery))
        else:
            origx = (centerx + cos(angle)*short_radius)
            origy = (centery + sin(angle)*short_radius)
            p.append((origx, origy))
            
        while angle<eangle:
            x = centerx + cos(angle)*radius
            y = centery + sin(angle)*radius
            p.append((x,y))
            angle = angle+radiansdelta
        x = centerx + cos(eangle)*radius
        y = centery + sin(eangle)*radius
        p.append((x,y))

        if short_radius:
            x = centerx + cos(eangle)*short_radius
            y = centery + sin(eangle)*short_radius
            p.append((x,y))

            angle = eangle
            while angle>=sangle:
                x = centerx + cos(angle)*short_radius
                y = centery + sin(angle)*short_radius
                p.append((x,y))
                angle = angle-radiansdelta
        self.draw_path(style,p)

        delta = (eangle - sangle)/2.0
        rad = short_radius + (radius-short_radius)/2.0

        return ( (centerx + cos(sangle+delta) * rad),
                 (centery + sin(sangle+delta) * rad))

    def rotate_text(self,style,text,x,y,angle):

        x += self.lmargin
        y += self.tmargin

        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]
        font = p.get_font()

        size = font.get_size()

        (new_text,fdef) = self.encode_text(p,text[0])

        self.f.write('gsave\n')
        self.f.write(fdef)
        self.f.write('%4.2f cm %4.2f cm translate\n' % self.translate(x,y))
        self.f.write('%4.2f rotate\n' % -angle)

        self.f.write('%.4f %.4f %.4f setrgbcolor\n' % rgb_color(stype.get_color()))

        val = len(text)
        y = ((size * val)/2.0) - size

        for line in text:
            self.f.write('(%s) dup stringwidth pop -2 div  '% line.encode('iso-8859-1'))
            self.f.write("%.4f moveto show\n" % y)
            y -= size
 
        self.f.write('grestore\n')

    def draw_path(self,style,path):
        stype = self.draw_styles[style]
        self.f.write('gsave\n')
        self.f.write('newpath\n')
        self.f.write('%.4f setlinewidth\n' % stype.get_line_width())
        if stype.get_line_style() == BaseDoc.SOLID:
            self.f.write('[] 0 setdash\n')
        else:
            self.f.write('[2 4] 0 setdash\n')

        point = path[0]
        x1 = point[0]+self.lmargin
        y1 = point[1]+self.tmargin
        self.f.write('%f cm %f cm moveto\n' % self.translate(x1,y1))

        for point in path[1:]:
            x1 = point[0]+self.lmargin
            y1 = point[1]+self.tmargin
            self.f.write('%f cm %f cm lineto\n' % self.translate(x1,y1))
        self.f.write('closepath\n')

        color = stype.get_fill_color()
        self.f.write('gsave %.4f %.4f %.4f setrgbcolor fill grestore\n' % rgb_color(color))
        self.f.write('%.4f %.4f %.4f setrgbcolor stroke\n' % rgb_color(stype.get_color()))
        self.f.write('grestore\n')

    def draw_line(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin
        stype = self.draw_styles[style]
        self.f.write('gsave newpath\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x1,y1))
        self.f.write('%f cm %f cm lineto\n' % self.translate(x2,y2))
        self.f.write('%.4f setlinewidth\n' % stype.get_line_width())
        if stype.get_line_style() == BaseDoc.SOLID:
            self.f.write('[] 0 setdash\n')
        else:
            self.f.write('[2 4] 0 setdash\n')
            
        self.f.write('2 setlinecap\n')
        self.f.write('%.4f %.4f %.4f setrgbcolor stroke\n' % rgb_color(stype.get_color()))
        self.f.write('grestore\n')

    def patch_text(self,text):
        return text.encode('iso-8859-1')

    def write_at(self,style,text,x,y):
        para_style = self.style_list[style]

        x = x + self.lmargin
        y = y + self.tmargin

        (text,fdef) = self.encode_text(para_style,text)

        self.f.write('gsave\n')
        self.f.write('%f cm %f cm moveto\n' % self.translate(x,y))
        self.f.write(fdef)
        self.f.write('(%s) show grestore\n' % text)

    def draw_bar(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin

        box_type = self.draw_styles[style]
        fill_color = rgb_color(box_type.get_fill_color())
        color = rgb_color(box_type.get_color())

        self.f.write('gsave\n')
        self.f.write("%f cm %f cm moveto\n" % self.translate(x1,y1))
        self.f.write("0 %f cm rlineto\n" % (y2-y1)) 
        self.f.write("%f cm 0 rlineto\n" % (x2-x1)) 
        self.f.write("0  %f cm rlineto\n" % (y1-y2))
        self.f.write('closepath\n')
        self.f.write("%.4f setlinewidth\n" % box_type.get_line_width())
        self.f.write('gsave %.4f %.4f %.4f setrgbcolor fill grestore\n' % fill_color)
        self.f.write('%.4f %.4f %.4f setrgbcolor stroke\n' % color)
        self.f.write('grestore\n')
    
    def draw_box(self,style,text,x,y):
        x = x + self.lmargin
        y = y + self.tmargin

        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()
        p = self.style_list[para_name]
        
        bh = box_style.get_height()
        bw = box_style.get_width()
        self.f.write('gsave\n')

        shadsize = box_style.get_shadow_space()
        if box_style.get_shadow():
            self.f.write('newpath\n')
            self.f.write('%f cm %f cm moveto\n' % self.translate(x+shadsize,y+shadsize))
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
        if box_style.get_line_width():
            self.f.write('%f cm %f cm moveto\n' % self.translate(x,y))
            self.f.write('0 -%f cm rlineto\n' % bh)
            self.f.write('%f cm 0 rlineto\n' % bw)
            self.f.write('0 %f cm rlineto\n' % bh)
            self.f.write('closepath\n')
            self.f.write('%.4f setlinewidth\n' % box_style.get_line_width())
            self.f.write('%.4f %.4f %.4f setrgbcolor stroke\n' % rgb_color(box_style.get_color()))
        if text != "":
            (text,fdef) = self.encode_text(p,text)
            self.f.write(fdef)
            lines = '\n'.split(text)
            nlines = len(lines)
            mar = 10/28.35
            f_in_cm = p.get_font().get_size()/28.35
            fs = f_in_cm * 1.2
            center = y + (bh + fs)/2.0 + (fs*shadsize)
            ystart = center - (fs/2.0) * nlines
            for i in range(nlines):
                ypos = ystart + (i * fs)
                self.f.write('%f cm %f cm moveto\n' % self.translate(x+mar,ypos))
                self.f.write("(%s) show\n" % lines[i])
        self.f.write('grestore\n')

def rgb_color(color):
    r = float(color[0])/255.0
    g = float(color[1])/255.0
    b = float(color[2])/255.0
    return (r,g,b)
        
PluginMgr.register_draw_doc(_("PostScript"),PSDrawDoc,1,1,".ps",
                          _("Print a copy"));
