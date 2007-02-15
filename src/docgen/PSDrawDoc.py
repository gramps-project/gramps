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

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from math import pi, cos, sin
from gettext import gettext as _
        
#-------------------------------------------------------------------------
#Gramps modules
#-------------------------------------------------------------------------
from ReportBase import ReportUtils, run_print_dialog, get_print_dialog_app
from PluginUtils import register_draw_doc
import BaseDoc
import Errors

from Utils import gformat
import Mime
import Utils

def lrgb(grp):
    grp = ReportUtils.rgb_color(grp)
    return (gformat(grp[0]),gformat(grp[1]),gformat(grp[2]))

def coords(grp):
    return (gformat(grp[0]),gformat(grp[1]))
    
_apptype = 'application/postscript'
print_label = None

try:
    # First try to find a viewer program
    mprog = Mime.get_application(_apptype)
    if Utils.search_for(mprog[0]):
        print_label = _("Open in %(program_name)s") % {'program_name': mprog[1]}
except:
    pass

if print_label == None:
    # Second, try to print directly
    if get_print_dialog_app() != None:
        print_label = _("Print a copy")

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
            if print_label == _("Print a copy"):
            	run_print_dialog (self.filename)
            elif print_label:
                app = Mime.get_application(_apptype)
                Utils.launch(app[0],self.filename)
            else:
                # This should never happen
                print "Invalid print request"
        
    def write_text(self,text,mark=None):
        pass

    def start_page(self):
        self.page = self.page + 1
        self.f.write("%%Page:")
        self.f.write("%d %d\n" % (self.page,self.page))
        if self.orientation != BaseDoc.PAPER_PORTRAIT:
            self.f.write('90 rotate %s cm %s cm translate\n' % (
                gformat(0),gformat(-1*self.height)))

    def end_page(self):
        self.f.write('showpage\n')
        self.f.write('%%PageTrailer\n')

    def encode(self,text):
        try:
            orig = unicode(text)
            new_text = orig.encode('iso-8859-1')
        except:
            new_text = "?"*len(text)
        return new_text

    def encode_text(self,p,text):
        fdef = self.fontdef(p)
        new_text = self.encode(text)
        return (new_text,fdef)

    def center_text(self,style,text,x,y):
        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]

        x += self.lmargin
        y = y + self.tmargin + ReportUtils.pt2cm(p.get_font().get_size())

        (text,fdef) = self.encode_text(p,text)

        self.f.write('gsave\n')
        self.f.write('%s %s %s setrgbcolor\n' % lrgb(stype.get_color()))
        self.f.write(fdef)
        self.f.write('(%s) dup stringwidth pop -2 div ' % text)
        self.f.write('%s cm add %s cm moveto ' % coords(self.translate(x,y)))
        self.f.write('show\n')
        self.f.write('grestore\n')

    def draw_text(self,style,text,x1,y1):
        stype = self.draw_styles[style]
        para_name = stype.get_paragraph_style()
        p = self.style_list[para_name]

        x1 = x1 + self.lmargin
        y1 = y1 + self.tmargin + ReportUtils.pt2cm(p.get_font().get_size())

        (text,fdef) = self.encode_text(p,text)

        self.f.write('gsave\n')
        self.f.write('%s cm %s cm moveto\n' % coords(self.translate(x1,y1)))
        self.f.write(fdef)
        self.f.write('(%s) show grestore\n' % text)

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
        coords = self.translate(x,y)
        self.f.write('%s cm %s cm translate\n' % (
            gformat(coords[0]),gformat(coords[1])))
        self.f.write('%s rotate\n' % gformat(-angle))

        self.f.write('%s %s %s setrgbcolor\n' % lrgb(stype.get_color()))

        val = len(text)
        y = ((size * val)/2.0) - size

        for line in text:
            self.f.write('(%s) dup stringwidth pop -2 div  '
                         % self.encode(line))
            self.f.write("%s moveto show\n" % gformat(y))
            y -= size
 
        self.f.write('grestore\n')

    def draw_path(self,style,path):
        stype = self.draw_styles[style]
        self.f.write('gsave\n')
        self.f.write('newpath\n')
        self.f.write('%s setlinewidth\n' % gformat(stype.get_line_width()))
        if stype.get_line_style() == BaseDoc.SOLID:
            self.f.write('[] 0 setdash\n')
        else:
            self.f.write('[2 4] 0 setdash\n')

        point = path[0]
        x1 = point[0]+self.lmargin
        y1 = point[1]+self.tmargin
        self.f.write('%s cm %s cm moveto\n' % coords(self.translate(x1,y1)))

        for point in path[1:]:
            x1 = point[0]+self.lmargin
            y1 = point[1]+self.tmargin
            self.f.write('%s cm %s cm lineto\n' % coords(self.translate(x1,y1)))
        self.f.write('closepath\n')

        color = stype.get_fill_color()
        self.f.write('gsave %s %s %s setrgbcolor fill grestore\n' % lrgb(color))
        self.f.write('%s %s %s setrgbcolor stroke\n' % lrgb(stype.get_color()))
        self.f.write('grestore\n')

    def draw_line(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin
        stype = self.draw_styles[style]
        self.f.write('gsave newpath\n')
        self.f.write('%s cm %s cm moveto\n' % coords(self.translate(x1,y1)))
        self.f.write('%s cm %s cm lineto\n' % coords(self.translate(x2,y2)))
        self.f.write('%s setlinewidth\n' % gformat(stype.get_line_width()))
        if stype.get_line_style() == BaseDoc.SOLID:
            self.f.write('[] 0 setdash\n')
        else:
            self.f.write('[2 4] 0 setdash\n')
            
        self.f.write('2 setlinecap\n')
        self.f.write('%s %s %s setrgbcolor stroke\n' % lrgb(stype.get_color()))
        self.f.write('grestore\n')

    def draw_bar(self,style,x1,y1,x2,y2):
        x1 = x1 + self.lmargin
        x2 = x2 + self.lmargin
        y1 = y1 + self.tmargin
        y2 = y2 + self.tmargin

        box_type = self.draw_styles[style]
        fill_color = box_type.get_fill_color()
        color = box_type.get_color()
        
        self.f.write('gsave\n')
        self.f.write("%s cm %s cm moveto\n" % coords(self.translate(x1,y1)))
        self.f.write("%s cm %s cm lineto\n" % coords(self.translate(x1,y2))) 
        self.f.write("%s cm %s cm lineto\n" % coords(self.translate(x2,y2))) 
        self.f.write("%s cm %s cm lineto\n" % coords(self.translate(x2,y1))) 
        self.f.write("%s cm %s cm lineto\n" % coords(self.translate(x1,y1))) 
        self.f.write('closepath\n')
        self.f.write("%s setlinewidth\n" % gformat(box_type.get_line_width()))
        self.f.write('gsave %s %s %s setrgbcolor fill grestore\n' % lrgb(fill_color))
        self.f.write('%s %s %s setrgbcolor stroke\n' % lrgb(color))
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
            self.f.write('%s cm %s cm moveto\n' % coords(self.translate(x+shadsize,y+shadsize)))
            self.f.write('0 -%s cm rlineto\n' % gformat(bh))
            self.f.write('%s cm 0 rlineto\n' % gformat(bw))
            self.f.write('0 %s cm rlineto\n' % gformat(bh))
            self.f.write('closepath\n')
            self.f.write('.5 setgray\n')
            self.f.write('fill\n')
        self.f.write('newpath\n')
        self.f.write('%s cm %s cm moveto\n' % coords(self.translate(x,y)))
        self.f.write('0 -%s cm rlineto\n' % gformat(bh))
        self.f.write('%s cm 0 rlineto\n' % gformat(bw))
        self.f.write('0 %s cm rlineto\n' % gformat(bh))
        self.f.write('closepath\n')
        self.f.write('1 setgray\n')
        self.f.write('fill\n')
        self.f.write('newpath\n')
        if box_style.get_line_width():
            self.f.write('%s cm %s cm moveto\n' % coords(self.translate(x,y)))
            self.f.write('0 -%s cm rlineto\n' % gformat(bh))
            self.f.write('%s cm 0 rlineto\n' % gformat(bw))
            self.f.write('0 %s cm rlineto\n' % gformat(bh))
            self.f.write('closepath\n')
            self.f.write('%s setlinewidth\n' % gformat(box_style.get_line_width()))
            self.f.write('%s %s %s setrgbcolor stroke\n' % lrgb(box_style.get_color()))
        if text != "":
            (text,fdef) = self.encode_text(p,text)
            self.f.write(fdef)
            lines = text.split('\n')

            nlines = len(lines)
            mar = 10/28.35
            f_in_cm = p.get_font().get_size()/28.35
            fs = f_in_cm * 1.2
            center = y + (bh + fs)/2.0 + (fs*shadsize)
            ystart = center - (fs/2.0) * nlines
            for i in range(nlines):
                ypos = ystart + (i * fs)
                self.f.write('%s cm %s cm moveto\n' % coords(self.translate(x+mar,ypos)))
                self.f.write("(%s) show\n" % lines[i])
        self.f.write('grestore\n')

register_draw_doc(_("PostScript"),PSDrawDoc,1,1,".ps", print_label);
