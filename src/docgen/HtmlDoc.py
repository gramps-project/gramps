#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# Modified August 2002 by Gary Shao
#
#   Removed Gramps dependencies.
#
#   Removed dependencies on Gnome UI.
#
#   Moved call to build_style_declaration() out of __init__ method and
#   into open method to allow cell table styles to get emitted in HTML.
#
#   Added style entry for underlined text in HTML output
#
#   Changed statements which constructed paths using "%s/%s" string
#   formatting into ones using the os.path.join function to give better
#   cross-platform compatibility.
#
#   Allowed table width to default to 0, which causes output table
#   to have column widths that are automatically sized to the length
#   of their contents.
#
#   Added support for start_bold() and end_bold() methods of TextDoc
#   class for inline bolding of text.
#
#   Modified open() and close() methods to allow the filename parameter
#   passed to open() to be either a string containing a file name, or
#   a Python file object. This allows the document generator to be more
#   easily used with its output directed to stdout, as may be called for
#   in a CGI script.
#
# Modified September 2002 by Gary Shao
#
#   Changed implicit conversion of '\n' character to <br> command in
#   write_text() to instead require an explicit call to line_break()
#   for insertion of <br> into text. This makes the paragraph behavior
#   a better match for that of other document generators.
#
#   Added start_listing() and end_listing() methods to allow displaying
#   text blocks without automatic filling and justification. Intended
#   for printing things like source code and plain text graphics.
#
#   Added support for start_italic() and end_italic() methods of TextDoc
#   class for inline italicizing of text.
#
#   Added method show_link() to display a link as an anchor.
#   This method really only has an active role in the HTML generator.
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
import time

import ImgManip
import TarFile

from TextDoc import *

try:
    import gnome.ui
    import Plugins
    import const
    from intl import gettext
    _ = gettext
except:
    withGramps = 0
    Version = "1.0"
else:
    withGramps = 1

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
        self.year = time.localtime(time.time())[0]
        self.ext = '.html'
        if source == None:
            self.copyright = 'Copyright &copy; %d' % (self.year)
            self.map = None
            self.f = None
            self.filename = None
            self.top = []
            self.bottom = []
            self.base = "."
            self.load_template()
            self.build_header()
            self.image_dir = "images"
        else:
            self.owner = source.owner
            self.copyright = 'Copyright &copy; %d %s' % (self.year,self.owner)
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

    def set_extension(self,val):
        if val[0] != '.':
            val = "." + val
        self.ext = val
        
    def set_owner(self,owner):
        HtmlDoc.set_owner(self,owner)
        self.copyright = 'Copyright &copy; %d %s' % (self.year,self.owner)
        
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
	    if withGramps:
	        gnome.ui.GnomeErrorDialog(mymsg)
	    else:
	        print mymsg
		raise "TemplateError: No START marker"

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
	    if withGramps:
	        gnome.ui.GnomeErrorDialog(mymsg)
	    else:
	        print mymsg
		raise "TemplateError: No START marker"
            
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
		if withGramps:
		    gnome.ui.GnomeWarningDialog(mymsg)
		else:
	            print mymsg
                self.bottom = _bottom
                self.top = _top
            except:
                mymsg = _("Could not open %s\nUsing the default template") % \
                        self.template
		if withGramps:
		    gnome.ui.GnomeWarningDialog(mymsg)
		else:
	            print mymsg
                self.bottom = _bottom
                self.top = _top
        else:
            self.bottom = _bottom
            self.top = _top

    def process_line(self,line):
        if withGramps:
	    l = string.replace(line,'$VERSION',const.version)
	else:
            l = string.replace(line,'$VERSION',Version)
        return string.replace(l,'$COPYRIGHT',self.copyright)
        
    def open(self,filename):
        if type(filename) == type(""):
            (r,e) = os.path.splitext(filename)
            if e == self.ext:
                self.filename = filename
            else:
                self.filename = filename + self.ext

            self.base = os.path.dirname(self.filename)

            self.f = open(self.filename,"w")
	    self.alreadyOpen = 0
	elif hasattr(filename, "write"):
	    self.f = filename
	    self.alreadyOpen = 1
        self.f.write(self.file_header)
        self.build_style_declaration()
        self.f.write(self.style_declaration)

    def build_header(self):
        top = string.join(self.top, "")
        match = t_header_line_re.match(top)
        if match:
            m = match.groups()
            self.file_header = '%s<TITLE>%s</TITLE>%s\n' % (m[0],m[1],m[2])
        else:
            self.file_header = top
        self.file_header = self.process_line(self.file_header)

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

            italic = bold = underline = ''
            if font.get_italic():
                italic = 'font-style:italic; '
            if font.get_bold():
                bold = 'font-weight:bold; '
	    if font.get_underline():
	        underline = 'text-decoration:underline; '
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
                        '\t%s%s%sfont-family:%s;\n}' 
                        % (key, font_size, font_color,
                           align, text_indent,
                           right_margin, left_margin,
                           top, bottom, left, right,
                           italic, bold, underline, family))

        text.append('-->\n</style>')
        self.style_declaration = string.join(text,'\n')

    def close(self):
        for line in self.bottom:
            self.f.write(self.process_line(line))
	if not self.alreadyOpen:
            self.f.close()

    def write_support_files(self):
        if self.map:
            for name in self.map.keys():
                if name == 'template.html':
                    continue
                fname = '%s' % (os.path.join(self.base,name))
                f = open(fname, 'wb')
                f.write(self.map[name].read())
                f.close()
            
    def add_photo(self,name,pos,x,y):
        self.empty = 0
        size = int(max(x,y) * float(150.0/2.54))
        refname = "is%s" % os.path.basename(name)

        if self.image_dir:
	    if self.base:
                imdir = "%s" % (os.path.join(self.base,self.image_dir))
	    else:
                imdir = "%s" % (self.image_dir)
        else:
            imdir = self.base

        if not os.path.isdir(imdir):
            try:
                os.mkdir(imdir)
            except:
                return

        try:
            img = ImgManip.ImgManip(name)
            img.jpg_thumbnail("%s" % (os.path.join(imdir,refname)),size,size)
        except:
            return

        if pos == "right":
            xtra = ' align="right"'
        elif pos == "left" :
            xtra = ' align="left"'
        else:
            xtra = ''
            
	if pos == "center":
	    self.f.write('<center>')
        if self.image_dir:
            self.f.write('<img src="%s" border="0"%s>' % \
                         (os.path.join(self.image_dir,refname),xtra))
        else:
            self.f.write('<img src="%s" border="0"%s>' % (refname,xtra))
	if pos == "center":
	    self.f.write('</center>')
	self.f.write('\n')

    def start_table(self,name,style):
        self.tbl = self.table_styles[style]
	if self.tbl.get_width() == 0:
            self.f.write('<table ')
	else:
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
        elif self.tbl.get_column_width(self.col) > 0:
            self.f.write(' width="')
            self.f.write(str(self.tbl.get_column_width(self.col)))
            self.f.write('%"')
        self.f.write(' class="')
        self.f.write(style_name)
        self.f.write('">')
        self.col = self.col + 1

    def end_cell(self):
        self.f.write('</td>\n')

    def start_listing(self,style_name):
        style = self.style_list[style_name]
        font = style.get_font()
        font_size = font.get_size()
        font_color = '#%02x%02x%02x' % font.get_color()
        right_margin = "%.2f" % style.get_right_margin()
        left_margin = "%.2f" % style.get_left_margin()
        top = bottom = left = right = 'none'
        pad = "%.3fcm"  % style.get_padding()
        if style.get_top_border():
            top = 'thin solid #000000'
        if style.get_bottom_border():
            bottom = 'thin solid #000000'
        if style.get_left_border():
	    left = 'thin solid #000000'
        if style.get_right_border():
            right = 'thin solid #000000'

        italic = bold = underline = ''
        if font.get_italic():
            italic = 'font-style:italic; '
        if font.get_bold():
            bold = 'font-weight:bold; '
	if font.get_underline():
	    underline = 'text-decoration:underline; '
	if font.get_type_face() == FONT_MONOSPACE:
	    family = 'Courier,monospace'
        elif font.get_type_face() == FONT_SANS_SERIF:
            family = 'Helvetica,Arial,sans-serif'
        else:
            family = 'Times New Roman,Times,serif'

        styleStr = '<pre style="font-size: %dpt; color: %s;\n' % \
                     (font_size, font_color)
	styleStr = styleStr + '\tpadding: %s %s %s %s;\n' % \
		     (pad, pad, pad, pad)
	styleStr = styleStr + '\tmargin-right: %scm; margin-left: %scm;\n' % \
                     (right_margin, left_margin)
	styleStr = styleStr + '\tborder-top:%s; border-bottom:%s;\n' % \
                     (top, bottom)
	styleStr = styleStr + '\tborder-left:%s; border-right:%s;\n' % \
                     (left, right)
	styleStr = styleStr + '\t%s%s%sfont-family:%s">\n' % \
                     (italic, bold, underline, family)
        self.f.write(styleStr)

    def end_listing(self):
        self.f.write('</pre>\n')

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
        text = string.replace(text,'&','&amp;');       # Must be first
        text = string.replace(text,'<','&lt;');
        text = string.replace(text,'>','&gt;');
        text = string.replace(text,'\n','<br>')
        if text != "":
            self.empty = 0
	self.f.write(text)

    def start_bold(self):
        self.f.write('<b>')

    def end_bold(self):
        self.f.write('</b>')

    def start_italic(self):
        self.f.write('<i>')

    def end_italic(self):
        self.f.write('</i>')

    def line_break(self):
        self.f.write('<br>\n')

    def show_link(self, text, href):
        self.f.write(' <a href="%s">%s</a> ' % (href, text))

#------------------------------------------------------------------------
#
# Register the document generator with the system if in Gramps
#
#------------------------------------------------------------------------
if withGramps:
    Plugins.register_text_doc(
        name=_("HTML"),
        classref=HtmlDoc,
        table=1,
        paper=0,
        style=1
        )
