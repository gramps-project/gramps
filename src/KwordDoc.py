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
import utils
import time
import StringIO
import os
import gzip

_BLKSIZE=512


nul = '\0'

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TarFile:
    def __init__(self,name):
        self.name = name
        self.f = gzip.open(name,"wb")
        self.pos = 0
        
    def add_file(self,filename,mtime,iobuf):
        iobuf.seek(0,2)
        length = iobuf.tell()
        iobuf.seek(0)

        buf = filename
        buf = buf + '\0'*(100-len(filename))
        buf = buf + "0100664" + nul
        buf = buf + "0000764" + nul
        buf = buf + "0000764" + nul
        buf = buf + "%011o" % length + nul
        buf = buf + "%011o" % mtime + nul
        buf = buf + "%s"
        buf = buf + "0" + '\0'*100 + 'ustar  \0'
        buf = buf + '\0'*32
        buf = buf + '\0'*32
        buf = buf + '\0'*183

        chksum = 0
        blank = "        "
        temp = buf % (blank)
        for c in temp:
            chksum = chksum + ord(c)
        sum = "%06o " % chksum
        sum = sum + nul
        buf = buf % sum

        self.pos = self.pos + len(buf)
        self.f.write(buf)

        buf = iobuf.read(length)
        self.f.write(buf)
        self.pos = self.pos + length
        rem = _BLKSIZE - (self.pos % _BLKSIZE)
        if rem != 0:
            self.f.write('\0' * rem)
        self.pos = self.pos + rem


    def close(self):
        rem = (_BLKSIZE*20) - (self.pos % (_BLKSIZE*20))
        if rem != 0:
            self.f.write('\0' * rem)
        self.f.close()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def sizes(val):
    mm = val*10
    inch = val/2.54
    points = int(inch*72)
    return (points,utils.fl2txt("%.6f",mm),utils.fl2txt("%.6f",inch))
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class KwordDoc(TextDoc):

    def open(self,filename):
        self.photolist = []
        
        if filename[-4:] != ".kwd":
            self.filename = filename + ".kwd"
        else:
            self.filename = filename

        self.f = StringIO.StringIO()
        self.m = StringIO.StringIO()

        self.m.write('<?xml version="1.0" encoding="UTF-8"?>')
        self.m.write('<!DOCTYPE document-info ><document-info>\n')
        self.m.write('<log>\n')
        self.m.write('<text></text>\n')
        self.m.write('</log>\n')
        self.m.write('<author>\n')
        self.m.write('<full-name></full-name>\n')
        self.m.write('<title></title>\n')
        self.m.write('<company></company>\n')
        self.m.write('<email></email>\n')
        self.m.write('<telephone></telephone>\n')
        self.m.write('<fax></fax>\n')
        self.m.write('<country></country>\n')
        self.m.write('<postal-code></postal-code>\n')
        self.m.write('<city></city>\n')
        self.m.write('<street></street>\n')
        self.m.write('</author>\n')
        self.m.write('<about>\n')
        self.m.write('<abstract><![CDATA[]]></abstract>\n')
        self.m.write('<title></title>\n')
        self.m.write('</about>\n')
        self.m.write('</document-info>\n')

        self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.f.write('<DOC editor="KWord" mime="application/x-kword" ')
        self.f.write('syntaxVersion="1">\n')

        if self.paper.name == "A3":
            self.f.write('<PAPER format="0" ')
        elif self.paper.name == "A4":
            self.f.write('<PAPER format="1" ')
        elif self.paper.name == "A5":
            self.f.write('<PAPER format="2" ')
        elif self.paper.name == "Letter":
            self.f.write('<PAPER format="3" ')
        elif self.paper.name == "Legal":
            self.f.write('<PAPER format="4" ')
        elif self.paper.name == "B5":
            self.f.write('<PAPER format="7" ')
        else:
            self.f.write('<PAPER format="6" ')

        self.f.write('ptWidth="%d" mmWidth ="%s" inchWidth ="%s" ' % sizes(self.width))
        self.f.write('ptHeight="%d" mmHeight="%s" inchHeight="%s" ' % sizes(self.height))
        if self.orientation == PAPER_PORTRAIT:
            self.f.write('orientation="0" ')
        else:
            self.f.write('orientation="1" ')
        self.f.write('columns="1" ')
        self.f.write('ptColumnspc="2" ')
        self.f.write('mmColumnspc="1" ')
        self.f.write('inchColumnspc="0.0393701" ')
        self.f.write('hType="0" ')
        self.f.write('fType="0" ')
        self.f.write('ptHeadBody="9" ')
        self.f.write('ptFootBody="9" ')
        self.f.write('mmHeadBody="3.5" ')
        self.f.write('mmFootBody="3.5" ')
        self.f.write('inchHeadBody="0.137795" ')
        self.f.write('inchFootBody="0.137795">\n')
        self.f.write('<PAPERBORDERS ')
        self.f.write('ptTop="%d" mmTop="%s" inchTop="%s" ' % sizes(self.tmargin))
        self.f.write('ptRight="%d" mmRight="%s" inchRight="%s" ' % sizes(self.rmargin))
        self.f.write('ptBottom="%d" mmBottom="%s" inchBottom="%s"\n' % sizes(self.bmargin))
        self.f.write('ptLeft="%d" mmLeft="%s" inchLeft="%s"/>' % sizes(self.lmargin))
        self.f.write('</PAPER>\n')
        self.f.write('<ATTRIBUTES processing="0" ')
        self.f.write('standardpage="1" ')
        self.f.write('hasHeader="0" ')
        self.f.write('hasFooter="0" ')
        self.f.write('unit="mm"/>\n')
        self.f.write('<FRAMESETS>\n')
        self.f.write('<FRAMESET frameType="1" ')
        self.f.write('frameInfo="0" ')
        self.f.write('removable="0" ')
        self.f.write('visible="1" ')
        self.f.write('name="Frameset 1">\n')
        self.f.write('<FRAME left="28" ')
        self.f.write('top="42" ')
        self.f.write('right="566" ')
        self.f.write('bottom="798" ')
        self.f.write('runaround="1" />\n')

    def close(self):
        self.f.write('</FRAMESET>\n')
        self.f.write('</FRAMESETS>\n')
        self.f.write('<STYLES>\n')
        for name in self.style_list.keys():
            self.f.write('<STYLE>\n')
            self.f.write('<NAME value="%s"/>\n' % name)

            p = self.style_list[name]

            padding = p.get_padding()
            self.f.write('<OFOOT pt="%d" mm="%s" inch="%s"/>\n' % sizes(padding))
            if p.get_alignment() == PARA_ALIGN_CENTER:
                self.f.write('<FLOW value="2"/>\n')
            elif p.get_alignment() == PARA_ALIGN_JUSTIFY:
                self.f.write('<FLOW value="3"/>\n')
            elif p.get_alignment() == PARA_ALIGN_RIGHT:
                self.f.write('<FLOW value="1"/>\n')

            first = p.get_first_indent()
            right = p.get_right_margin() 
            left = p.get_left_margin()

            first = left+first
            if first != 0:
                self.f.write('<IFIRST pt="%d" mm="%s" inch="%s"/>\n' % sizes(first))
            if left != 0:
                self.f.write('<ILEFT pt="%d" mm="%s" inch="%s"/>\n' % sizes(left))

            font = p.get_font()
            self.f.write('<FORMAT>\n')
            if font.get_type_face==FONT_SANS_SERIF:
                self.f.write('<FONT name="helvetica"/>\n')
            else:
                self.f.write('<FONT name="times"/>\n')
            self.f.write('<SIZE value="%d"/>\n' % font.get_size())
            self.f.write('<COLOR red="%d" green="%d" blue="%d"/>\n' % font.get_color())
            if font.get_bold():
                self.f.write('<WEIGHT value="75"/>\n')
            if font.get_italic():
                self.f.write('<ITALIC value="1"/>\n')
            if font.get_underline():
                self.f.write('<UNDERLINE value="1"/>\n')
            if p.get_top_border():
                self.f.write('<TOPBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
            if p.get_bottom_border():
                self.f.write('<BOTTOMBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
            if p.get_right_border():
                self.f.write('<RIGHTBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
            if p.get_left_border():
                self.f.write('<LEFTBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
            self.f.write('</FORMAT>\n')
            if left != 0:
                self.f.write('<TABULATOR ptpos="%d" mmpos="%s" inchpos="%s"/>\n' % sizes(left))
            self.f.write('</STYLE>\n')

        self.f.write('</STYLES>\n')
        self.f.write('<PIXMAPS>\n')
        for file in self.photo_list:
            self.f.write('<KEY key="%s" name="%s"/>\n' % file)
        self.f.write('</PIXMAPS>\n')
        self.f.write('<SERIALL>\n')
        self.f.write('<SAMPLE>\n')
        self.f.write('</SAMPLE>\n')
        self.f.write('<DB>\n')
        self.f.write('</DB>\n')
        self.f.write('</SERIALL>\n')
        self.f.write('</DOC>\n')

        mtime = time.time()
        tar = TarFile(self.filename)
        tar.add_file("documentinfo.xml",mtime,self.m)
        tar.add_file("maindoc.xml",mtime,self.f)
        for file in self.photo_list:
            f = open(file[0],"r")
            tar.add_file(file[1],mtime,f)
            f.close()
        tar.close()

        self.f.close()
        self.m.close()
        
    def start_page(self,orientation=None):
        pass

    def end_page(self):
        pass

    def start_paragraph(self,style_name,leader=None):
        self.format_list = []
        self.bold_start = 0
        self.text = ""
        self.style_name = style_name
        self.p = self.style_list[self.style_name]
        self.font = self.p.get_font()
        if self.font.get_type_face() == FONT_SERIF:
            self.font_face = "times"
        else:
            self.font_face = "helvetica"

        if leader != None:
            self.text = leader + chr(1)
            txt = '<FORMAT id="1" pos="0" len="%d">\n' % len(leader)
            txt = txt + '<FONT name="%s"/>\n</FORMAT>\n' % self.font_face
            txt = txt + '<FORMAT id="3" pos="%d">\n' % len(leader)
            txt = txt + '<FONT name="%s"/>\n</FORMAT>\n' % self.font_face
            self.format_list.append(txt)

        self.bold_stop = len(self.text)

    def end_paragraph(self):
        if self.bold_start != 0 and self.bold_stop != len(self.text):
            txt = '<FORMAT>\n<FONT name="%s"/>\n</FORMAT>\n' % self.font_face
            self.format_list.append(txt)

        self.f.write('<PARAGRAPH>\n')
        self.f.write('<TEXT>')
        self.f.write(latin_to_utf8(self.text))
        self.f.write('</TEXT>\n')
        old_pos = 0
        self.f.write('<FORMATS>\n')
        for format in self.format_list:
            self.f.write(format)
        self.f.write('</FORMATS>\n')
        self.f.write('<LAYOUT>\n')
        self.f.write('<NAME value="%s"/>\n' % self.style_name)

        padding = self.p.get_padding()
        self.f.write('<OFOOT pt="%d" mm="%s" inch="%s"/>\n' % sizes(padding))
        
        if self.p.get_alignment() == PARA_ALIGN_CENTER:
            self.f.write('<FLOW value="2"/>\n')
        elif self.p.get_alignment() == PARA_ALIGN_JUSTIFY:
            self.f.write('<FLOW value="3"/>\n')
        elif self.p.get_alignment() == PARA_ALIGN_RIGHT:
            self.f.write('<FLOW value="1"/>\n')

        first = self.p.get_first_indent()
        right = self.p.get_right_margin()
        left = self.p.get_left_margin()
        
        first = left+first
        if first != 0:
            self.f.write('<IFIRST pt="%d" mm="%s" inch="%s"/>\n' % sizes(first))
        if left != 0:
            self.f.write('<ILEFT pt="%d" mm="%s" inch="%s"/>\n' % sizes(left))

        self.f.write('<FORMAT>\n')
        self.f.write('<FONT name="%s"/>\n' % self.font_face)
        self.f.write('<SIZE value="%d"/>\n' % self.font.get_size())
        self.f.write('<COLOR red="%d" green="%d" blue="%d"/>\n' % self.font.get_color())
        if self.font.get_bold():
            self.f.write('<WEIGHT value="75"/>\n')
        if self.font.get_italic():
            self.f.write('<ITALIC value="1"/>\n')
        if self.font.get_underline():
            self.f.write('<UNDERLINE value="1"/>\n')
        if self.p.get_top_border():
            self.f.write('<TOPBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
        if self.p.get_bottom_border():
            self.f.write('<BOTTOMBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
        if self.p.get_right_border():
            self.f.write('<RIGHTBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
        if self.p.get_left_border():
            self.f.write('<LEFTBORDER red="0" green="0" blue="0" style="0" width="1"/>\n')
        self.f.write('</FORMAT>\n')
        if left != 0:
            self.f.write('<TABULATOR ptpos="%d" mmpos="%s" inchpos="%s"/>\n' % sizes(left))
        self.f.write('</LAYOUT>\n')
        self.f.write('</PARAGRAPH>\n')

    def start_bold(self):
        self.bold_start = len(self.text)
        if self.bold_stop != self.bold_start:
            length = self.bold_stop - self.bold_start
            txt = '<FORMAT id="1" pos="0" len="%d">\n' % length
            txt = txt + '<FONT name="%s"/>\n</FORMAT>\n' % self.font_face
            self.format_list.append(txt)

    def end_bold(self):
        self.bold_stop = len(self.text)
        length = self.bold_stop - self.bold_start
        txt = '<FORMAT id="1" pos="%d" len="%d">\n' % (self.bold_start,length)
        txt = txt + '<FONT name="%s"/>\n<WEIGHT value="75"/>\n</FORMAT>\n' % self.font_face
        self.format_list.append(txt)

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
#        index = len(self.photo_list)+1
#        self.photo_list.append((name,'pictures/picture%d.jpeg' % index))
#        txt = '<FORMAT id="2" pos="%d">\n' % len(self.text)
#        txt = txt + '<FILENAME value="%s"/>\n</FORMAT>\n' % name
#        
#        self.bold_stop = len(self.text)
#        self.format_list.append(txt)
#
#        self.text = self.text + chr(1)
    
    def horizontal_line(self):
        pass

    def write_text(self,text):
	self.text = self.text + text


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

    doc = KwordDoc(styles,paper,PAPER_PORTRAIT)
    doc.open("/home/dona/test")

    doc.start_paragraph("Title")
    doc.write_text("My Title")
    doc.end_paragraph()

    doc.start_paragraph("Normal")
    doc.write_text("Hello there. This is fun")
    doc.end_paragraph()

    doc.start_paragraph("Normal")
    doc.add_photo("/home/dona/dad.jpg",200,200)
    doc.end_paragraph()

    doc.close()
