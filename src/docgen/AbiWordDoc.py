#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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
"""
Provides a BaseDoc based interface to the AbiWord document format.
"""

#-------------------------------------------------------------------------
#
# Imported Modules
#
#-------------------------------------------------------------------------
import os
import base64
import string

import BaseDoc
from latin_utf8 import latin_to_utf8
import string
import Plugins
import ImgManip
import Errors
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Class Definitions
#
#-------------------------------------------------------------------------
class AbiWordDoc(BaseDoc.BaseDoc):
    """AbiWord document generator. Inherits from the BaseDoc generic
    document interface class."""

    def __init__(self,styles,type,template,orientation):
        """Initializes the AbiWordDoc class, calling the __init__ routine
        of the parent BaseDoc class"""
        BaseDoc.BaseDoc.__init__(self,styles,type,template,orientation)
        self.f = None
        self.level = 0
        self.new_page = 0
        self.in_table = 0

    def open(self,filename):
        """Opens the document, writing the necessary header information.
        AbiWord uses an XML format, so the document format is pretty easy
        to understand"""
        if filename[-4:] != ".abw":
            self.filename = "%s.abw" % filename
        else:
            self.filename = filename

        try:
            self.f = open(self.filename,"w")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)
            
        self.f.write('<?xml version="1.0"?>\n')
        self.f.write('<!DOCTYPE abiword PUBLIC "-//ABISOURCE//DTD AWML')
        self.f.write('1.0 Strict//EN" "http://www.abisource.com/awml.dtd">\n')
        self.f.write('<abiword xmlns:awml="http://www.abisource.com/awml.dtd" ')
        self.f.write('version="0.9.6.1" fileformat="1.0">\n')
        self.f.write('<pagesize ')
        self.f.write('pagetype="%s" ' % self.paper.get_name())
        if self.orientation == BaseDoc.PAPER_PORTRAIT:
            self.f.write('orientation="portrait" ')
        else:
            self.f.write('orientation="landscape" ')
        self.f.write('width="%.4f" ' % (self.width/2.54))
        self.f.write('height="%.4f" ' % (self.height/2.54))
        self.f.write('units="inch" page-scale="1.000000"/>\n')
        self.f.write('<section ')
        rmargin = float(self.rmargin)/2.54
        lmargin = float(self.lmargin)/2.54
        self.f.write('props="page-margin-right:%.4fin; ' % rmargin)
        self.f.write('page-margin-left:%.4fin"' % lmargin)
        self.f.write('>\n')

    def close(self):
        """Write the trailing information and closes the file"""
        self.f.write('</section>\n')
        if len(self.photo_list) > 0:
            self.f.write('<data>\n')
            for file_tuple in self.photo_list:
                file = file_tuple[0]
                base = "%s/%s_png" % (os.path.dirname(file),
                                      os.path.basename(file))
                tag = string.replace(base,'.','_')

                img = ImgManip.ImgManip(file)
                buf = img.png_data()

                self.f.write('<d name="')
                self.f.write(tag)
                self.f.write('" mime-type="image/png" base64="yes">\n')
                self.f.write(base64.encodestring(buf))
                self.f.write('</d>\n')
            self.f.write('</data>\n')

        self.f.write('</abiword>\n')
        self.f.close()

    def add_photo(self,name,pos,x_cm,y_cm):

        try:
            image = ImgManip.ImgManip(name)
        except:
            return
        (x,y) = image.size()
        aspect_ratio = float(x)/float(y)

        if aspect_ratio > x_cm/y_cm:
            act_width = x_cm
            act_height = y_cm/aspect_ratio
        else:
            act_height = y_cm
            act_width = x_cm*aspect_ratio

        self.photo_list.append((name,act_width,act_height))

	base = "/tmp/%s.png" % os.path.basename(name)
        tag = string.replace(base,'.','_')

        self.f.write('<image dataid="')
        self.f.write(tag)
        self.f.write('" props="width:%.3fin; ' % act_width)
        self.f.write('height:%.3fin"/>'  % act_height)

    def start_superscript(self):
        self.text = self.text + '<c props="text-position:superscript">'

    def end_superscript(self):
        self.text = self.text + '</c>'

    def start_paragraph(self,style_name,leader=None):
        if self.in_table:
            self.start_paragraph_intable(style_name,leader)
        else:
            self.start_paragraph_notable(style_name,leader)
            
    def start_paragraph_notable(self,style_name,leader=None):
        style = self.style_list[style_name]
        self.current_style = style
        self.f.write('<p props="')
        self.f.write('margin-top:%.4fin; ' % (float(style.get_padding())/2.54))
        self.f.write('margin-bottom:%.4fin; ' % (float(style.get_padding())/2.54))
        if style.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
            self.f.write('text-align:right;')
        elif style.get_alignment() == BaseDoc.PARA_ALIGN_LEFT:
            self.f.write('text-align:left;')
        elif style.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
            self.f.write('text-align:center;')
        else:
            self.f.write('text-align:justify;')
        rmargin = float(style.get_right_margin())/2.54
        lmargin = float(style.get_left_margin())/2.54
        indent = float(style.get_first_indent())/2.54
        self.f.write(' margin-right:%.4fin;' % rmargin)
        self.f.write(' margin-left:%.4fin;' % lmargin)
        self.f.write(' tabstops:%.4fin/L;' % lmargin)
        self.f.write(' text-indent:%.4fin' % indent)
        self.f.write('">')
        font = style.get_font()
        self.f.write('<c props="font-family:')
        if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            self.f.write('Arial;')
        else:
            self.f.write('Times New Roman;')
        self.f.write('font-size:%dpt' % font.get_size())
        if font.get_bold():
            self.f.write('; font-weight:bold')
        if font.get_italic():
            self.f.write('; font-style:italic')
        color = font.get_color()
        if color != (0,0,0):
            self.f.write('; color:%2x%2x%2x' % color)
        if font.get_underline():
            self.f.write('; text-decoration:underline')
        self.f.write('">')
        if self.new_page == 1:
            self.new_page = 0
            self.f.write('<pbr/>')
        if leader != None:
            self.f.write(leader)
            self.f.write('\t')

    def start_paragraph_intable(self,style_name,leader=None):
        style = self.style_list[style_name]
        self.current_style = style
        font = style.get_font()
        self.cdata = '<c props="font-family:'
        if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            self.cdata = self.cdata + 'Arial;'
        else:
            self.cdata = self.cdata + 'Times New Roman;'
        self.cdata = self.cdata + 'font-size:%dpt' % font.get_size()
        if font.get_bold():
            self.cdata = self.cdata + '; font-weight:bold'
        if font.get_italic():
            self.cdata = self.cdata + '; font-style:italic'
        color = font.get_color()
        if color != (0,0,0):
            self.cdata = self.cdata + '; color:%2x%2x%2x' % color
        if font.get_underline():
            self.cdata = self.cdata + '; text-decoration:underline'
        self.cdata = self.cdata + '; lang:en-US">'
        if self.new_page == 1:
            self.new_page = 0
            self.f.write('<pbr/>')
                     
    def page_break(self):
        self.new_page = 1

    def end_paragraph(self):
        if self.in_table:
            self.cdata = self.cdata + '\t'
        else:
            self.f.write('</c></p>\n')

    def write_note(self,text,format,style_name):
        if format == 1:
            for line in text.split('\n'):
                self.start_paragraph(style_name)
                self.write_text(line)
                self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = string.join(string.split(line))
                self.write_text(line)
                self.end_paragraph()

    def write_text(self,text):
        text = text.replace('&','&amp;');       # Must be first
        text = text.replace('<','&lt;');
        text = text.replace('>','&gt;');
        text = text.replace('&lt;super&gt;','<c props="text-position:superscript">')
        text = text.replace('&lt;/super&gt;','</c>')
        if self.in_table:
            self.cdata = self.cdata + text
        else:
            self.f.write(text)

    def start_bold(self):
        font = self.current_style.get_font()
        self.f.write('</c><c props="font-family:')
        if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            self.f.write('Arial;')
        else:
            self.f.write('Times New Roman;')
        self.f.write('font-size:%dpt' % font.get_size())
        self.f.write('; font-weight:bold')
        if font.get_italic():
            self.f.write('; font-style:italic')
        color = font.get_color()
        if color != (0,0,0):
            self.f.write('; color:%02x%02x%02x' % color)
        if font.get_underline():
            self.f.write('; text-decoration:underline')
        self.f.write('">')

    def end_bold(self):
        font = self.current_style.get_font()
        self.f.write('</c><c props="font-family:')
        if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
            self.f.write('Arial;')
        else:
            self.f.write('Times New Roman;')
        self.f.write('font-size:%dpt' % font.get_size())
        if font.get_bold():
            self.f.write('; font-weight:bold')
        if font.get_italic():
            self.f.write('; font-style:italic')
        color = font.get_color()
        if color != (0,0,0):
            self.f.write('; color:%02x%02x%02x' % color)
        if font.get_underline():
            self.f.write('; text-decoration:underline')
        self.f.write('">')

    def start_table(self,name,style_name):
        self.in_table = 1
        self.tblstyle = self.table_styles[style_name]
        
    def end_table(self):
        self.in_table = 0

    def start_row(self):
        self.tabs = []
        self.ledge = 0.0
        self.col = 0
        self.cdatalist = []

    def end_row(self):
        first = 0
        self.f.write('<p')
        self.tabs.sort()
        oldv = -1.0
        useb = 0
        if len(self.tabs) > 0:
            self.f.write(' props="tabstops:')
            for val,t in self.tabs:
                if val == oldv:
                    if t == 'B0':
                        useb = 1
                    continue
                oldv = val
                if not first:
                    first = 1
                else:
                    self.f.write(',')
                edge = (val * self.get_usable_width())

                if val == 1.0:
                    edge = edge-0.1
                elif val == 0.0:
                    edge = edge+0.1
                if useb:
                    t = 'B0'
                self.f.write("%6.4fin/%s" % (edge/2.54,t))
            self.f.write('"')
        self.f.write('>')
        for data in self.cdatalist:
            self.f.write(data)
        self.f.write('</p>\n')
        
    def start_cell(self,style_name,span=1):
        self.cstyle = self.cell_styles[style_name]
        for i in range(self.col,self.col+span):
            self.col = self.col + 1
            self.ledge = self.ledge + self.tblstyle.get_column_width(i)
        self.tabs.append((self.ledge/100.0,"L"))

    def end_cell(self):
        self.cdata = self.cdata + "</c>"
        self.cdatalist.append(self.cdata)

Plugins.register_text_doc(_("AbiWord (version 1.0.x)"),AbiWordDoc,1,1,1,".abw")
