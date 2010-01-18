#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
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

"""
PostScript document generator.
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
        
#-------------------------------------------------------------------------
#Gramps modules
#-------------------------------------------------------------------------
from gui.utils import open_file_with_default_application
from ReportBase import ReportUtils
from gen.plug.docgen import BaseDoc, DrawDoc, FONT_SERIF, PAPER_PORTRAIT, SOLID
from gen.plug.utils import gformat
import Errors

def lrgb(grp):
    grp = ReportUtils.rgb_color(grp)
    return (gformat(grp[0]), gformat(grp[1]), gformat(grp[2]))

def coords(grp):
    return (gformat(grp[0]), gformat(grp[1]))

#-------------------------------------------------------------------------
#
# PSDrawDoc
#
#-------------------------------------------------------------------------
class PSDrawDoc(BaseDoc, DrawDoc):

    def __init__(self, styles, type):
        BaseDoc.__init__(self, styles, type)
        self.file = None
        self.filename = None
        self.level = 0
        self.page = 0

    def fontdef(self, para):
        font = para.get_font()
        if font.get_type_face() == FONT_SERIF:
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
        
        return "%s find-latin-font %d scalefont setfont\n" % (font_name, font.get_size())

    def translate(self, x, y):
        return (x, self.paper.get_size().get_height()-y)

    def open(self, filename):
        """
        Opens the file so that it can be generated.

        @param filename: path name of the file to create
        """
        if filename[-3:] != ".ps":
            self.filename = filename + ".ps"
        else:
            self.filename = filename

        try:
            self.file = open(self.filename,"w")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)
        
        self.file.write('%!PS-Adobe-3.0\n')
        self.file.write('%%LanguageLevel: 2\n')
        self.file.write('%%Pages: (atend)\n')
        self.file.write('%%PageOrder: Ascend\n')
        if self.paper.get_orientation() != PAPER_PORTRAIT:
            self.file.write('%%Orientation: Landscape\n')
        else:
            self.file.write('%%Orientation: Portrait\n')
        self.file.write('%%EndComments\n')
        self.file.write('/cm { 28.34 mul } def\n')
        self.file.write('% build iso-latin-1 version of a font\n')
        self.file.write('/font-to-iso-latin-1 {	% <font> font-to-iso-latin-1 <font>\n')
        self.file.write('%% reencode for iso latin1; from the 2nd edition red book, sec 5.6.1\n')
        self.file.write('dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall\n')
        self.file.write('/Encoding ISOLatin1Encoding def currentdict end\n')
        self.file.write('dup /FontName get 80 string cvs (-ISOLatin1) concatstrings cvn \n')
        self.file.write('exch definefont\n')
        self.file.write('} def\n')
        self.file.write('\n')
        self.file.write('/find-latin-font {	% <name> find-latin-font <font>\n')
        self.file.write('findfont font-to-iso-latin-1\n')
        self.file.write('} def\n')
        
        self.filename = filename

    def close(self):
        self.file.write('%%Trailer\n')
        self.file.write('%%Pages: ')
        self.file.write('%d\n' % self.page)
        self.file.write('%%EOF\n')
        self.file.close()
        if self.open_req:
            open_file_with_default_application(self.filename)
        
    def write_text(self, text, mark=None):
        pass

    def start_page(self):
        self.page = self.page + 1
        self.file.write("%%Page:")
        self.file.write("%d %d\n" % (self.page, self.page))
        if self.paper.get_orientation() != PAPER_PORTRAIT:
            self.file.write('90 rotate %s cm %s cm translate\n' % (
                gformat(0),gformat(-1*self.paper.get_size().get_height())))

    def end_page(self):
        self.file.write('showpage\n')
        self.file.write('%%PageTrailer\n')

    def encode(self, text):
        try:
            orig = unicode(text)
            new_text = orig.encode('iso-8859-1')
        except:
            new_text = "?"*len(text)
        return new_text

    def encode_text(self, p, text):
        fdef = self.fontdef(p)
        new_text = self.encode(text)
        return (new_text, fdef)

    def center_text(self, style, text, x, y):
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)

        x += self.paper.get_left_margin()
        y = y + self.paper.get_top_margin() + ReportUtils.pt2cm(p.get_font().get_size())

        (text, fdef) = self.encode_text(p, text)

        self.file.write('gsave\n')
        self.file.write('%s %s %s setrgbcolor\n' % lrgb(stype.get_color()))
        self.file.write(fdef)
        self.file.write('(%s) dup stringwidth pop -2 div ' % text)
        self.file.write('%s cm add %s cm moveto ' % coords(self.translate(x, y)))
        self.file.write('show\n')
        self.file.write('grestore\n')

    def draw_text(self, style, text, x1, y1):
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)

        x1 = x1 + self.paper.get_left_margin()
        y1 = y1 + self.paper.get_top_margin() + ReportUtils.pt2cm(p.get_font().get_size())

        (text, fdef) = self.encode_text(p, text)

        self.file.write('gsave\n')
        self.file.write('%s cm %s cm moveto\n' % coords(self.translate(x1, y1)))
        self.file.write(fdef)
        self.file.write('(%s) show grestore\n' % text)

    def rotate_text(self, style, text, x, y, angle):

        x += self.paper.get_left_margin()
        y += self.paper.get_top_margin()

        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)
        font = p.get_font()

        size = font.get_size()

        (new_text, fdef) = self.encode_text(p, text[0])

        self.file.write('gsave\n')
        self.file.write(fdef)
        coords = self.translate(x, y)
        self.file.write('%s cm %s cm translate\n' % (
            gformat(coords[0]),gformat(coords[1])))
        self.file.write('%s rotate\n' % gformat(-angle))

        self.file.write('%s %s %s setrgbcolor\n' % lrgb(stype.get_color()))

        val = len(text)
        y = ((size * val)/2.0) - size

        for line in text:
            self.file.write('(%s) dup stringwidth pop -2 div  '
                         % self.encode(line))
            self.file.write("%s moveto show\n" % gformat(y))
            y -= size
 
        self.file.write('grestore\n')

    def draw_path(self, style, path):
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        self.file.write('gsave\n')
        self.file.write('newpath\n')
        self.file.write('%s setlinewidth\n' % gformat(stype.get_line_width()))
        if stype.get_line_style() == SOLID:
            self.file.write('[] 0 setdash\n')
        else:
            self.file.write('[2 4] 0 setdash\n')

        point = path[0]
        x1 = point[0]+self.paper.get_left_margin()
        y1 = point[1]+self.paper.get_top_margin()
        self.file.write('%s cm %s cm moveto\n' % coords(self.translate(x1, y1)))

        for point in path[1:]:
            x1 = point[0]+self.paper.get_left_margin()
            y1 = point[1]+self.paper.get_top_margin()
            self.file.write('%s cm %s cm lineto\n' % coords(self.translate(x1, y1)))
        self.file.write('closepath\n')

        color = stype.get_fill_color()
        self.file.write('gsave %s %s %s setrgbcolor fill grestore\n' % lrgb(color))
        self.file.write('%s %s %s setrgbcolor stroke\n' % lrgb(stype.get_color()))
        self.file.write('grestore\n')

    def draw_line(self, style, x1, y1, x2, y2):
        x1 = x1 + self.paper.get_left_margin()
        x2 = x2 + self.paper.get_left_margin()
        y1 = y1 + self.paper.get_top_margin()
        y2 = y2 + self.paper.get_top_margin()
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        self.file.write('gsave newpath\n')
        self.file.write('%s cm %s cm moveto\n' % coords(self.translate(x1, y1)))
        self.file.write('%s cm %s cm lineto\n' % coords(self.translate(x2, y2)))
        self.file.write('%s setlinewidth\n' % gformat(stype.get_line_width()))
        if stype.get_line_style() == SOLID:
            self.file.write('[] 0 setdash\n')
        else:
            self.file.write('[2 4] 0 setdash\n')
            
        self.file.write('2 setlinecap\n')
        self.file.write('%s %s %s setrgbcolor stroke\n' % lrgb(stype.get_color()))
        self.file.write('grestore\n')

    def draw_box(self, style, text, x, y, w, h):
        x = x + self.paper.get_left_margin()
        y = y + self.paper.get_top_margin()
        
        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)

        self.file.write('gsave\n')

        shadsize = box_style.get_shadow_space()
        if box_style.get_shadow():
            self.file.write('newpath\n')
            self.file.write('%s cm %s cm moveto\n' % coords(self.translate(x+shadsize, y+shadsize)))
            self.file.write('0 -%s cm rlineto\n' % gformat(h))
            self.file.write('%s cm 0 rlineto\n' % gformat(w))
            self.file.write('0 %s cm rlineto\n' % gformat(h))
            self.file.write('closepath\n')
            self.file.write('.5 setgray\n')
            self.file.write('fill\n')
        self.file.write('newpath\n')
        self.file.write('%s cm %s cm moveto\n' % coords(self.translate(x, y)))
        self.file.write('0 -%s cm rlineto\n' % gformat(h))
        self.file.write('%s cm 0 rlineto\n' % gformat(w))
        self.file.write('0 %s cm rlineto\n' % gformat(h))
        self.file.write('closepath\n')
        
        fill_color = box_style.get_fill_color()
        color = box_style.get_color()
        self.file.write('gsave %s %s %s setrgbcolor fill grestore\n' % lrgb(fill_color))
        self.file.write('%s %s %s setrgbcolor stroke\n' % lrgb(color))

        self.file.write('newpath\n')
        if box_style.get_line_width():
            self.file.write('%s cm %s cm moveto\n' % coords(self.translate(x, y)))
            self.file.write('0 -%s cm rlineto\n' % gformat(h))
            self.file.write('%s cm 0 rlineto\n' % gformat(w))
            self.file.write('0 %s cm rlineto\n' % gformat(h))
            self.file.write('closepath\n')
            self.file.write('%s setlinewidth\n' % gformat(box_style.get_line_width()))
            self.file.write('%s %s %s setrgbcolor stroke\n' % lrgb(box_style.get_color()))
        if text != "":
            para_name = box_style.get_paragraph_style()
            assert( para_name != '' )
            p = style_sheet.get_paragraph_style(para_name)
            (text, fdef) = self.encode_text(p, text)
            self.file.write(fdef)
            lines = text.split('\n')

            nlines = len(lines)
            mar = 10/28.35
            f_in_cm = p.get_font().get_size()/28.35
            fs = f_in_cm * 1.2
            center = y + (h + fs)/2.0 + (fs*shadsize)
            ystart = center - (fs/2.0) * nlines
            for i in range(nlines):
                ypos = ystart + (i * fs)
                self.file.write('%s cm %s cm moveto\n' % coords(self.translate(x+mar, ypos)))
                self.file.write("(%s) show\n" % lines[i])
        self.file.write('grestore\n')
