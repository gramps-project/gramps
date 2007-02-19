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

#------------------------------------------------------------------------
#
# python modules 
#
#------------------------------------------------------------------------
import os
import re
import time
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules 
#
#------------------------------------------------------------------------
from PluginUtils import register_text_doc
import ImgManip
import tarfile
import const
import Errors
import BaseDoc
import QuestionDialog
import Mime
import Utils


#------------------------------------------------------------------------
#
# Constant regular expressions
#
#------------------------------------------------------------------------
t_header_line_re = re.compile(
    r"(.*)<TITLE>(.*)</TITLE>(.*)",
    re.DOTALL|re.IGNORECASE|re.MULTILINE)
t_keyword_line_re = re.compile(
    r'(.*name="keywords"\s+content=")([^\"]*)(".*)$',
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
    '  <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">\n',
    '  <META NAME="keywords" CONTENT="">\n',
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
class HtmlDoc(BaseDoc.BaseDoc):

    def __init__(self,styles,type,template,orientation):
        BaseDoc.BaseDoc.__init__(self,styles,BaseDoc.PaperSize("",0,0),template,None)
        self.year = time.localtime(time.time())[0]
        self.ext = '.html'
        self.meta = ""
        self.copyright = 'Copyright &copy; %d' % (self.year)
        self.map = None
        self.f = None
        self.filename = None
        self.top = []
        self.bottom = []
        self.base = ""
        self.load_template()
        self.build_header()
        self.style_declaration = None
        self.image_dir = "images"

    def set_extension(self,val):
        if val[0] != '.':
            val = "." + val
        self.ext = val

    def set_image_dir(self,dirname):
        self.image_dir = dirname

    def set_keywords(self,keywords):
        self.meta = ",".join(keywords)
        
    def load_tpkg(self):
        start = re.compile(r"<!--\s*START\s*-->")
        stop = re.compile(r"<!--\s*STOP\s*-->")
        top_add = 1
        bottom_add = 0
        archive = tarfile.open(self.template)
        self.map = {}
        for tarinfo in archive:
            self.map[tarinfo.name] = archive.extractfile(tarinfo)
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
        archive.close

        if top_add == 1:
            mymsg = _("The marker '<!-- START -->' was not in the template")
            QuestionDialog.ErrorDialog(_("Template Error"),mymsg)

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
            QuestionDialog.ErrorDialog(_("Template Error"),mymsg)
            
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
                QuestionDialog.WarningDialog(mymsg,str(msg))
                self.bottom = _bottom
                self.top = _top
            except:
                mymsg = _("Could not open %s\nUsing the default template") % \
                        self.template
                QuestionDialog.WarningDialog(mymsg)
                self.bottom = _bottom
                self.top = _top
        else:
            self.bottom = _bottom
            self.top = _top

    def process_line(self,line):
        l = line.replace('$VERSION',const.version)
        return l.replace('$COPYRIGHT',self.copyright)
        
    def open(self,filename):
        (r,e) = os.path.splitext(filename)
        if e == self.ext:
            self.filename = filename
        else:
            self.filename = filename + self.ext

        self.base = os.path.dirname(self.filename)

        try:
            self.f = open(self.filename,"w")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)

        if self.meta:
            match = t_keyword_line_re.match(self.file_header)
            if match:
                g = match.groups()
                line = "%s%s%s" % (g[0],self.meta,g[2])
            else:
                line = self.file_header
        else:
            line = self.file_header
        self.f.write(line)
        if not self.style_declaration:
            self.build_style_declaration()
        self.f.write(self.style_declaration)

    def build_header(self):
        self.fix_title("".join(self.top))

    def fix_title(self,msg=None):
        if msg == None:
            match = t_header_line_re.match(self.file_header)
        else:
            match = t_header_line_re.match(msg)
        if match:
            m = match.groups()
            if self.title:
                msg = self.title
            else:
                msg = m[1]
            self.file_header = '%s<TITLE>%s</TITLE>%s\n' % (m[0],msg,m[2])
        else:
            self.file_header = self.top
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
            top_margin = "%.2f" % style.get_top_margin()
            bottom_margin = "%.2f" % style.get_bottom_margin()

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
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                family = '"Helvetica","Arial","sans-serif"'
            else:
                family = '"Times New Roman","Times","serif"'

            text.append('.%s {\n'
                        '\tfont-size: %dpt; color: %s;\n' 
                        '\ttext-align: %s; text-indent: %scm;\n' 
                        '\tmargin-right: %scm; margin-left: %scm;\n' 
                        '\tmargin-top: %scm; margin-bottom: %scm;\n' 
                        '\tborder-top:%s; border-bottom:%s;\n' 
                        '\tborder-left:%s; border-right:%s;\n' 
                        '\t%s%sfont-family:%s;\n}' 
                        % (key, font_size, font_color,
                           align, text_indent,
                           right_margin, left_margin,
                           top_margin, bottom_margin,
                           top, bottom, left, right,
                           italic, bold, family))

        text.append('-->\n</style>')
        self.style_declaration = '\n'.join(text)

    def close(self):
        for line in self.bottom:
            self.f.write(self.process_line(line))
        self.f.close()
        self.write_support_files()

        if self.print_req:
            apptype = 'text/html'
            app = Mime.get_application(apptype)
            Utils.launch(app[0],self.filename)

    def write_support_files(self):
        if self.map:
            for name in self.map.keys():
                if name == 'template.html':
                    continue
                fname = '%s%s%s' % (self.base,os.path.sep,name)
                try:
                    f = open(fname, 'wb')
                    f.write(self.map[name].read())
                    f.close()
                except IOError,msg:
                    errmsg = "%s\n%s" % (_("Could not create %s") % fname, msg)
                    raise Errors.ReportError(errmsg)
                except:
                    raise Errors.ReportError(_("Could not create %s") % fname)
            
    def add_media_object(self,name,pos,x,y,alt=''):
        self.empty = 0
        size = int(max(x,y) * float(150.0/2.54))
        refname = "is%s" % os.path.basename(name)

        if self.image_dir:
            imdir = '%s%s%s' % (self.base,os.path.sep,self.image_dir)
        else:
            imdir = self.base

        if not os.path.isdir(imdir):
            try:
                os.mkdir(imdir)
            except:
                return

        try:
            img = ImgManip.ImgManip(name)
            img.jpg_thumbnail("%s%s%s" % (imdir,os.path.sep,refname),size,size)
        except:
            return

        if pos == "right":
            xtra = ' align="right"'
        elif pos == "left" :
            xtra = ' align="left"'
        else:
            xtra = ''
            
        imgsize = img.size()
        if imgsize[0] > imgsize[1]:
            size_str = "width"
        else:
            size_str = "height"

        if self.image_dir:
            self.f.write('<img src="%s/%s" border="0" %s="%d" alt="%s"%s>\n' % \
                         (self.image_dir,refname,size_str,size,alt,xtra))
        else:
            self.f.write('<img src="%s" border="0" %s="%d" alt="%s"%s>\n' 
                        % (refname,size_str,size,alt,xtra))

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

    def start_bold(self):
        self.f.write('<b>')

    def end_bold(self):
        self.f.write('</b>')
        
    def start_superscript(self):
        self.f.write('<sup>')

    def end_superscript(self):
        self.f.write('</sup>')

    def write_note(self,text,format,style_name):
        if format == 1:
            self.f.write('<pre class=%s style="font-family: courier, monospace">' % style_name)
            self.write_text(text)
            self.f.write('</pre>')
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                self.write_text(line.strip().replace('\n',' '))
                self.end_paragraph()

    def write_text(self,text,mark=None):
        text = text.replace('&','&amp;');       # Must be first
        text = text.replace('<','&lt;');
        text = text.replace('>','&gt;');
        text = text.replace('\n','<br>')
        text = text.replace('&lt;super&gt;','<sup>')
        text = text.replace('&lt;/super&gt;','</sup>')
        if text != "":
            self.empty = 0
	self.f.write(text)

#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------
print_label = None
try:
    prog = Mime.get_application("text/html")
    mtype = Mime.get_description("text/html")
    
    if Utils.search_for(prog[0]):
        print_label=_("Open in %s") % prog[1]
    else:
        print_label=None
        
    if mtype == _("unknown"):
        mtype = _('HTML')
        
    register_text_doc(mtype,HtmlDoc,1,0,1,".html", print_label)
except:
    register_text_doc(_('HTML'),HtmlDoc,1,0,1,".html", None)
