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
        self.f.write('<PAPER format="1" ')
        self.f.write('ptWidth="595" ')
        self.f.write('ptHeight="841" ')
        self.f.write('mmWidth ="210" ')
        self.f.write('mmHeight="297" ')
        self.f.write('inchWidth ="8.26772" ')
        self.f.write('inchHeight="11.6929" ')
        self.f.write('orientation="0" ')
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
        self.f.write('<PAPERBORDERS mmLeft="10" ')
        self.f.write('mmTop="15" mmRight="10" ')
        self.f.write('mmBottom="15" ')
        self.f.write('ptLeft="28" ')
        self.f.write('ptTop="42" ')
        self.f.write('ptRight="28" ')
        self.f.write('ptBottom="42" ')
        self.f.write('inchLeft="0.393701" ')
        self.f.write('inchTop="0.590551" ')
        self.f.write('inchRight="0.393701" ')
        self.f.write('inchBottom="0.590551"/>\n')
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
                self.f.write('<FLOW value="2">\n')
            elif p.get_alignment() == PARA_ALIGN_JUSTIFY:
                self.f.write('<FLOW value="3">\n')
            elif p.get_alignment() == PARA_ALIGN_RIGHT:
                self.f.write('<FLOW value="1">\n')

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
            if font.get_bold():
                self.f.write('<WEIGHT value="75"/>\n')
            if font.get_italic():
                self.f.write('<ITALIC value="1"/>\n')
            self.f.write('</FORMAT>\n')
            if left != 0:
                self.f.write('<TABULATOR ptpos="%d" mmpos="%s" inchpos="%s"/>\n' % sizes(left))
            self.f.write('</STYLE>\n')

        self.f.write('</STYLES>\n')
        self.f.write('<PIXMAPS>\n')
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
        tar.close()

        self.f.close()
        self.m.close()
        
    def start_page(self,orientation=None):
        pass

    def end_page(self):
        pass

    def start_paragraph(self,style_name):
        self.text = ""
        self.style_name = style_name
        pass

    def end_paragraph(self):
        self.f.write('<PARAGRAPH>\n')
        self.f.write('<TEXT>')
        self.f.write(latin_to_utf8(self.text))
        self.f.write('</TEXT>\n')
        self.f.write('<LAYOUT>\n')
        self.f.write('<NAME value="%s"/>\n' % self.style_name)

        p = self.style_list[self.style_name]

        padding = p.get_padding()
        self.f.write('<OFOOT pt="%d" mm="%s" inch="%s"/>\n' % sizes(padding))
        
        if p.get_alignment() == PARA_ALIGN_CENTER:
            self.f.write('<FLOW value="2">\n')
        elif p.get_alignment() == PARA_ALIGN_JUSTIFY:
            self.f.write('<FLOW value="3">\n')
        elif p.get_alignment() == PARA_ALIGN_RIGHT:
            self.f.write('<FLOW value="1">\n')

        first = p.get_first_indent()
        right = p.get_right_margin()
        left = p.get_left_margin()
        
        first = left+first
        if first != 0:
            self.f.write('<IFIRST pt="%d" mm="%s" inch="%s"/>\n' % sizes(first))
        if left != 0:
            self.f.write('<ILEFT pt="%d" mm="%s" inch="%s"/>\n' % sizes(left))

        font = self.style_list[self.style_name].get_font()
        self.f.write('<FORMAT>\n')
        if font.get_type_face==FONT_SANS_SERIF:
            self.f.write('<FONT name="helvetica"/>\n')
        else:
            self.f.write('<FONT name="times"/>\n')
        self.f.write('<SIZE value="%d"/>\n' % font.get_size())
        if font.get_bold():
            self.f.write('<WEIGHT value="75"/>\n')
        if font.get_italic():
            self.f.write('<ITALIC value="1"/>\n')
        self.f.write('</FORMAT>\n')
        if left != 0:
            self.f.write('<TABULATOR ptpos="%d" mmpos="%s" inchpos="%s"/>\n' % sizes(left))
        self.f.write('</LAYOUT>\n')
        self.f.write('</PARAGRAPH>\n')

    def start_bold(self):
        pass

    def end_bold(self):
        pass

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
	self.text = self.text + text

