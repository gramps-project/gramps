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
import tempfile
import string
import re
import intl

_ = intl.gettext

from TextDoc import *
import const

_top = [
    '<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\" \"http://www.w3.org/TR/REC-html40/loose.dtd\">\n',
    '<HTML>\n',
    '<HEAD>\n',
    '<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=iso-8859-1\">\n',
    '<TITLE>\n',
    '</TITLE>\n',
    '<STYLE type="text/css">\n',
    '<!--\n',
    'BODY { background-color: #ffffff }\n',
    '.parent_name { font-family: Arial; font-style: bold }\n',
    '.child_name { font-family: Arial; font-style: bold }\n',
    '-->\n',
    '</STYLE>\n',
    '</HEAD>\n',
    '<BODY>\n',
    '<!-- START -->\n'
    ]

_bottom = [
    '<!-- STOP -->\n',
    '</BODY>\n',
    '</HTML>\n'
    ]

class HtmlDoc(TextDoc):

    def __init__(self,styles,template):
        TextDoc.__init__(self,styles,PaperStyle("",0,0),None)
        self.f = None
        self.filename = None
        self.template = template
        self.top = []
        self.bottom = []

    def open(self,filename):
        
        start = re.compile(r"<!--\s*START\s*-->")
        stop = re.compile(r"<!--\s*STOP\s*-->")

        top_add = 1
        bottom_add = 0

        if self.template and self.template != "":
            try:
                templateFile = open(self.template,"r")
                for line in templateFile.readlines():
                    if top_add == 1:
                        self.top.append(line)
                        match = start.search(line)
                        if match != None:
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
            except IOError,msg:
                import gnome.ui

                mymsg = _("Could not open %s\nUsing the default template") % \
                        self.template
                mymsg = "%s\n%s" % (mymsg,msg)
                gnome.ui.GnomeWarningDialog(mymsg)
                self.bottom = _bottom
                self.top = _top
            except:
                import gnome.ui

                mymsg = _("Could not open %s\nUsing the default template") % \
                        self.template
                gnome.ui.GnomeWarningDialog(mymsg)
                self.bottom = _bottom
                self.top = _top
        else:
            self.bottom = _bottom
            self.top = _top

        if filename[-5:] == ".html" or filename[-4:0] == ".htm":
            self.filename = filename
        else:
            self.filename = filename + ".html"

        self.f = open(self.filename,"w")
        for line in self.top:
            self.f.write(line)

        self.f.write('<style type="text/css">\n<!--\n')
        for key in self.cell_styles.keys():
            style = self.cell_styles[key]

            self.f.write('.')
            self.f.write(key)
            pad = "%.3fcm " % style.get_padding()
            self.f.write(' { padding:' + pad + pad + pad + pad +'; ')
            if style.get_top_border():
	       self.f.write('border-top:thin solid #000000; ')
            else:
	       self.f.write('border-top:none; ')
            if style.get_bottom_border():
	       self.f.write('border-bottom:thin solid #000000; ')
            else: 
	       self.f.write('border-bottom:none; ')
            if style.get_right_border():
	       self.f.write('border-right:thin solid #000000; ')
            else:
	       self.f.write('border-right:none; ')
            if style.get_left_border():
	       self.f.write('border-left:thin solid #000000 }\n')
            else:
	       self.f.write('border-left:none }\n')

        for key in self.style_list.keys():
            style = self.style_list[key]
            font = style.get_font()
            self.f.write('.')
            self.f.write(key)
            self.f.write(' { font-size:' + str(font.get_size()) + 'pt; ')

            self.f.write('color:#%02x%02x%02x; ' % font.get_color())

            align = style.get_alignment()
            if align == PARA_ALIGN_LEFT:
                self.f.write('text-align:left; ')
            elif align == PARA_ALIGN_CENTER:
                self.f.write('text-align:center; ')
            elif align == PARA_ALIGN_RIGHT:
                self.f.write('text-align:right; ')
            elif align == PARA_ALIGN_JUSTIFY:
                self.f.write('text-align:justify; ')
            self.f.write('text-indent:%.2fcm; ' % style.get_first_indent())
            self.f.write('margin-right:%.2fcm; ' % style.get_right_margin())
            self.f.write('margin-left:%.2fcm; ' % style.get_left_margin())
            if font.get_italic():
                self.f.write('font-style:italic; ')
            if font.get_bold():
                self.f.write('font-weight:bold; ')
            if font.get_type_face() == FONT_SANS_SERIF:
                self.f.write('font-family:"Helvetica","Arial","sans-serif"}\n')
            else:
                self.f.write('font-family:"Times New Roman","Times","serif"}\n')
                
            
        self.f.write('-->\n</style>\n')

    def close(self):
        for line in self.bottom:
            self.f.write(line)
        self.f.close()

    def start_table(self,name,style):
        self.tbl = self.table_styles[style]
        self.f.write('<table width="%d%%" cellspacing="0">\n' % self.tbl.get_width())

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

    def start_paragraph(self,style_name):
        self.f.write('<p class="' + style_name + '">')

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

