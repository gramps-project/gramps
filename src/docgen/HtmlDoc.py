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

import os
import string
import re
import gnome.ui
import Plugins
import ImgManip
import TarFile

from TextDoc import *

from intl import gettext
_ = gettext

t_header_line_re = re.compile(r"(.*)<TITLE>(.*)</TITLE>(.*)",
                              re.DOTALL|re.IGNORECASE|re.MULTILINE)

#------------------------------------------------------------------------
#
# Default template
#
#------------------------------------------------------------------------
_top = [
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">\n',
    '<HTML>\n',
    '<HEAD>\n',
    '  <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">\n',
    '  <TITLE>\n',
    '  </TITLE>\n',
    '  <STYLE type="text/css">\n',
    '  <!--\n',
    '    BODY { background-color: #ffffff }\n',
    '    .parent_name { font-family: Arial; font-style: bold }\n',
    '    .child_name { font-family: Arial; font-style: bold }\n',
    '    -->\n',
    '  </STYLE>\n',
    '</HEAD>\n',
    '<BODY>\n',
    '  <!-- START -->\n'
    ]

_bottom = [
    '  <!-- STOP -->\n',
    '</BODY>\n',
    '</HTML>\n'
    ]

#------------------------------------------------------------------------
#
# HtmlDoc
#
#------------------------------------------------------------------------
class HtmlDoc(TextDoc):

    def __init__(self,styles,type,template,orientation,source=None):
        TextDoc.__init__(self,styles,PaperStyle("",0,0),template,None)
        if source == None:
            self.map = None
            self.f = None
            self.filename = None
            self.top = []
            self.bottom = []
            self.base = ""
            self.load_template()
            self.build_header()
            self.build_style_declaration()
            self.image_dir = "images"
        else:
            self.map = source.map
            self.f = None
            self.filename = source.filename
            self.template = None
            self.top = source.top
            self.bottom = source.bottom
            self.base = source.base
            self.file_header = source.file_header
            self.style_declaration = source.style_declaration
            self.table_styles = source.table_styles;
            self.cell_styles = source.cell_styles;
            self.image_dir = source.image_dir
            
    def set_image_dir(self,dirname):
        self.image_dir = dirname

    def load_tpkg(self):
        start = re.compile(r"<!--\s*START\s*-->")
        stop = re.compile(r"<!--\s*STOP\s*-->")
        top_add = 1
        bottom_add = 0
        tf = TarFile.ReadTarFile(self.template,None)
        self.map = tf.extract_files()
        templateFile = self.map['template.html']
        while 1:
            line = templateFile.readline()
            if line == '':
                break
            if top_add == 1:
                self.top.append(line)
                match = start.search(line)
                if match:
                    top_add = 0
            elif bottom_add == 0:
                match = stop.search(line)
                if match != None:
                    bottom_add = 1
                    self.bottom.append(line)
            else:
                self.bottom.append(line)
        templateFile.close()

        if top_add == 1:
            mymsg = _("The marker '<!-- START -->' was not in the template")
            gnome.ui.GnomeErrorDialog(mymsg)

    def load_html(self):
        start = re.compile(r"<!--\s*START\s*-->")
        stop = re.compile(r"<!--\s*STOP\s*-->")
        top_add = 1
        bottom_add = 0
        templateFile = open(self.template,"r")
        for line in templateFile.readlines():
            if top_add == 1:
                self.top.append(line)
                match = start.search(line)
                if match:
                    top_add = 0
            elif bottom_add == 0:
                match = stop.search(line)
                if match != None:
                    bottom_add = 1
                    self.bottom.append(line)
            else:
                self.bottom.append(line)
        templateFile.close()

        if top_add == 1:
            mymsg = _("The marker '<!-- START -->' was not in the template")
            gnome.ui.GnomeErrorDialog(mymsg)
            
    def load_template(self):
        if self.template:
            try:
                if self.template[-4:] == 'tpkg':
                    self.load_tpkg()
                else:
                    self.load_html()
            except IOError,msg:
                mymsg = _("Could not open %s\nUsing the default template") % \
                        self.template
                mymsg = "%s\n%s" % (mymsg,msg)
                gnome.ui.GnomeWarningDialog(mymsg)
                self.bottom = _bottom
                self.top = _top
            except:
                mymsg = _("Could not open %s\nUsing the default template") % \
                        self.template
                gnome.ui.GnomeWarningDialog(mymsg)
                self.bottom = _bottom
                self.top = _top
        else:
            self.bottom = _bottom
            self.top = _top

    def open(self,filename):
        if filename[-5:] == ".html" or filename[-4:0] == ".htm":
            self.filename = filename
        else:
            self.filename = filename + ".html"

        self.base = os.path.dirname(self.filename)

        self.f = open(self.filename,"w")
        self.f.write(self.file_header)
        self.f.write(self.style_declaration)

    def build_header(self):
        top = string.join(self.top, "")
        match = t_header_line_re.match(top)
        if match:
            m = match.groups()
            self.file_header = '%s<TITLE>%s</TITLE>%s\n' % (m[0],m[1],m[2])
        else:
            self.file_header = top

    def build_style_declaration(self):
        text = ['<style type="text/css">\n<!--']
        for key in self.cell_styles.keys():
            style = self.cell_styles[key]
            
            pad = "%.3fcm"  % style.get_padding()
            top = bottom = left = right = 'none'
            if style.get_top_border():
                top = 'thin solid #000000'
            if style.get_bottom_border():
                bottom = 'thin solid #000000'
            if style.get_left_border():
	       left = 'thin solid #000000'
            if style.get_right_border():
                right = 'thin solid #000000'
            text.append('.%s {\n'
                        '\tpadding: %s %s %s %s;\n'
                        '\tborder-top:%s; border-bottom:%s;\n' 
                        '\tborder-left:%s; border-right:%s;\n}' 
                        % (key, pad, pad, pad, pad, top, bottom, left, right))

        for key in self.style_list.keys():
            style = self.style_list[key]
            font = style.get_font()
            font_size = font.get_size()
            font_color = '#%02x%02x%02x' % font.get_color()
            align = style.get_alignment_text()
            text_indent = "%.2f" % style.get_first_indent()
            right_margin = "%.2f" % style.get_right_margin()
            left_margin = "%.2f" % style.get_left_margin()

            top = bottom = left = right = 'none'
            if style.get_top_border():
                top = 'thin solid #000000'
            if style.get_bottom_border():
                bottom = 'thin solid #000000'
            if style.get_left_border():
	       left = 'thin solid #000000'
            if style.get_right_border():
                right = 'thin solid #000000'

            italic = bold = ''
            if font.get_italic():
                italic = 'font-style:italic; '
            if font.get_bold():
                bold = 'font-weight:bold; '
            if font.get_type_face() == FONT_SANS_SERIF:
                family = '"Helvetica","Arial","sans-serif"'
            else:
                family = '"Times New Roman","Times","serif"'

            text.append('.%s {\n'
                        '\tfont-size: %dpt; color: %s;\n' 
                        '\ttext-align: %s; text-indent: %scm;\n' 
                        '\tmargin-right: %scm; margin-left: %scm;\n' 
                        '\tborder-top:%s; border-bottom:%s;\n' 
                        '\tborder-left:%s; border-right:%s;\n' 
                        '\t%s%sfont-family:%s;\n}' 
                        % (key, font_size, font_color,
                           align, text_indent,
                           right_margin, left_margin,
                           top, bottom, left, right,
                           italic, bold, family))

        text.append('-->\n</style>')
        self.style_declaration = string.join(text,'\n')

    def close(self):
        for line in self.bottom:
            self.f.write(line)
        self.f.close()

    def write_support_files(self):
        if self.map:
            for name in self.map.keys():
                if name == 'template.html':
                    continue
                fname = '%s/%s' % (self.base,name)
                f = open(fname, 'wb')
                f.write(self.map[name].read())
                f.close()
            
    def add_photo(self,name,pos,x,y):
        self.empty = 0
        size = int(max(x,y) * float(150.0/2.54))
        refname = "is%s" % os.path.basename(name)

        if self.image_dir:
            imdir = "%s/%s" % (self.base,self.image_dir)
        else:
            imdir = self.base

        if not os.path.isdir(imdir):
            try:
                os.mkdir(imdir)
            except:
                return

        try:
            img = ImgManip.ImgManip(name)
            img.jpg_thumbnail("%s/%s" % (imdir,refname),size,size)
        except:
            return

        if pos == "right":
            xtra = ' align="right"'
        elif pos == "left" :
            xtra = ' align="left"'
        else:
            xtra = ''
            
        if self.image_dir:
            self.f.write('<img src="%s/%s" border="0""%s>\n' % \
                         (self.image_dir,refname,xtra))
        else:
            self.f.write('<img src="%s" border="0""%s>\n' % (refname,xtra))

    def start_table(self,name,style):
        self.tbl = self.table_styles[style]
        self.f.write('<table width="%d%%" ' % self.tbl.get_width())
        self.f.write('cellspacing="0">\n')

    def end_table(self):
        self.f.write('</table>\n')

    def start_row(self):
        self.col = 0
        self.f.write('<tr>\n')

    def end_row(self):
        self.f.write('</tr>\n')

    def start_cell(self,style_name,span=1):
        self.empty = 1
        self.f.write('<td valign="top"')
        if span > 1:
            self.f.write(' colspan="' + str(span) + '"')
            self.col = self.col + 1
        else:
            self.f.write(' width="')
            self.f.write(str(self.tbl.get_column_width(self.col)))
            self.f.write('%"')
        self.f.write(' class="')
        self.f.write(style_name)
        self.f.write('">')
        self.col = self.col + 1

    def end_cell(self):
        self.f.write('</td>\n')

    def start_paragraph(self,style_name,leader=None):
        self.f.write('<p class="' + style_name + '">')
        if leader != None:
            self.f.write(leader)
            self.f.write(' ')

    def end_paragraph(self):
        if self.empty == 1:
            self.f.write('&nbsp;')
        self.empty = 0
        self.f.write('</p>\n')

    def write_text(self,text):
        if text != "":
            self.empty = 0
        text = string.replace(text,'\n','<br>')
	self.f.write(text)

Plugins.register_text_doc(_("HTML"),HtmlDoc,1,0,1)
