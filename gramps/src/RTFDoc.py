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

from TextDoc import *
from latin_utf8 import latin_to_utf8

try:
    import PIL.Image
    no_pil = 0
except:
    no_pil = 1


def twips(cm):
    return int(((cm/2.54)*72)+0.5)*20

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class RTFDoc(TextDoc):

    def open(self,filename):
        if filename[-4:] != ".rtf":
            self.filename = filename + ".rtf"
        else:
            self.filename = filename

        self.f = open(self.filename,"w")
        self.f.write('{\\rtf1\\ansi\\ansicpg1252\\deff0\n')
        self.f.write('{\\fonttbl\n')
        self.f.write('{\\f0\\froman\\fcharset0\\fprq0 Times New Roman;}\n')
        self.f.write('{\\f1\\fswiss\\fcharset0\\fprq0 Arial;}}\n')
        self.f.write('{\colortbl\n')
        self.color_map = {}
        index = 1
        self.color_map[(0,0,0)] = 0
        self.f.write('\\red0\\green0\\blue0;')
        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            fgcolor = style.get_font().get_color()
            bgcolor = style.get_background_color()
            if not self.color_map.has_key(fgcolor):
                self.color_map[fgcolor] = index
                self.f.write('\\red%d\\green%d\\blue%d;' % fgcolor)
                index = index + 1
            if not self.color_map.has_key(bgcolor):
                self.f.write('\\red%d\\green%d\\blue%d;' % bgcolor)
                self.color_map[bgcolor] = index
                index = index + 1
        self.f.write('}\n')
        self.f.write('\\kerning0\\cf0\\viewkind1')
        self.f.write('\\paperw%d' % twips(self.width))
        self.f.write('\\paperh%d' % twips(self.height))
        self.f.write('\\margl%d' % twips(self.lmargin))
        self.f.write('\\margr%d' % twips(self.rmargin))
        self.f.write('\\margt%d' % twips(self.tmargin))
        self.f.write('\\margb%d' % twips(self.bmargin))
        self.f.write('\\widowctl\n')

    def close(self):
        self.f.write('}\n')
        self.f.close()

    def start_page(self,orientation=None):
        pass

    def end_page(self):
        pass

    def start_paragraph(self,style_name,leader=None):
        self.open = 0
        p = self.style_list[style_name]
        f = p.get_font()
        size = f.get_size()*2
        bgindex = self.color_map[p.get_background_color()]
        fgindex = self.color_map[f.get_color()]
        if f.get_type_face() == FONT_SERIF:
            self.font_type = '\\f0\\fs%d\\cf%d\\cb%d' % (size,fgindex,bgindex)
        else:
            self.font_type = '\\f1\\fs%d\\cf%d\\cb%d' % (size,fgindex,bgindex)
        if f.get_bold():
            self.font_type = self.font_type + "\\b"
        if f.get_underline():
            self.font_type = self.font_type + "\\ul"
        if f.get_italic():
            self.font_type = self.font_type + "\\i"

        self.f.write('\\pard')
        if p.get_alignment() == PARA_ALIGN_RIGHT:
            self.f.write('\\qr')
        elif p.get_alignment() == PARA_ALIGN_CENTER:
            self.f.write('\\qc')
        if p.get_alignment() == PARA_ALIGN_JUSTIFY:
            self.f.write('\\qj')
        if p.get_padding():
            self.f.write('\\sa%d' % twips(p.get_padding()/2.0))
        if p.get_top_border():
            self.f.write('\\brdrt\\brdrs')
        if p.get_bottom_border():
            self.f.write('\\brdrb\\brdrs')
        if p.get_left_border():
            self.f.write('\\brdrl\\brdrs')
        if p.get_right_border():
            self.f.write('\\brdrr\\brdrs')
        if p.get_first_indent():
            self.f.write('\\fi%d' % twips(p.get_first_indent()))
        if p.get_left_margin():
            self.f.write('\\li%d' % twips(p.get_left_margin()))
        if p.get_right_margin():
            self.f.write('\\ri%d' % twips(p.get_right_margin()))

        if leader:
            self.open = 1
            self.f.write('\\tx%d' % twips(p.get_left_margin()))
            self.f.write('{%s ' % self.font_type)
            self.write_text(leader)
            self.f.write('\\tab}')
            self.open = 0
    
    def end_paragraph(self):
        if self.open:
            self.f.write('}')
            self.open  = 0
        self.f.write('\n\\par')
        pass

    def start_bold(self):
        if self.open:
            self.f.write('}')
        self.f.write('{%s\\b ' % self.font_type)
        self.open = 1
        pass

    def end_bold(self):
        self.open = 0
        self.f.write('}')

    def start_table(self,name,style_name):
        pass

    def end_table(self):
        pass

    def start_row(self):
        pass

    def end_row(self):
        pass

    def start_cell(self,style_name,span=1):
        pass

    def end_cell(self):
        pass

    def add_photo(self,name,x,y):
        pass
    
    def horizontal_line(self):
        pass

    def write_text(self,text):
        if self.open == 0:
            self.open = 1
            self.f.write('{%s ' % self.font_type)
        for i in text:
            if ord(i) > 127:
                self.f.write('\\\'%2x' % ord(i))
            else:
                self.f.write(i)


if __name__ == "__main__":

    paper = PaperStyle("Letter",27.94,21.59)

    styles = StyleSheet()
    foo = FontStyle()
    foo.set_type_face(FONT_SANS_SERIF)
    foo.set_color((255,0,0))
    foo.set_size(24)
    foo.set_underline(1)
    foo.set_bold(1)
    foo.set_italic(1)

    para = ParagraphStyle()
    para.set_alignment(PARA_ALIGN_RIGHT)
    para.set_font(foo)
    styles.add_style("Title",para)

    foo = FontStyle()
    foo.set_type_face(FONT_SERIF)
    foo.set_size(12)

    para = ParagraphStyle()
    para.set_font(foo)
    styles.add_style("Normal",para)

    foo = FontStyle()
    foo.set_type_face(FONT_SERIF)
    foo.set_size(12)

    para = ParagraphStyle()
    para.set_font(foo)
    para.set_top_border(1)
    para.set_left_border(1)
    para.set_right_border(1)
    para.set_bottom_border(1)
    styles.add_style("Box",para)

    doc = RTFDoc(styles,paper,PAPER_PORTRAIT)
    doc.open("/home/dona/test")

    doc.start_paragraph("Title")
    doc.write_text("My Title")
    doc.end_paragraph()

    doc.start_paragraph("Normal")
    doc.write_text("Hello there. This is fun")
    doc.end_paragraph()

    doc.start_paragraph("Box")
    doc.write_text("This is my box")
    doc.end_paragraph()

    doc.start_paragraph("Normal")
    doc.add_photo("/home/dona/dad.jpg",200,200)
    doc.end_paragraph()

    doc.close()
