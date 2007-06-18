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

"""
Provides a BaseDoc based interface to the AbiWord document format.
"""

#-------------------------------------------------------------------------
#
# Python Modules
#
#-------------------------------------------------------------------------
import base64
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import BaseDoc
import Errors
from PluginUtils import register_text_doc
import ImgManip
import Mime
import Utils

mime_type = ""
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
        self.in_paragraph = 0

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

        # doctype
        self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.f.write('<!DOCTYPE abiword PUBLIC "-//ABISOURCE//DTD AWML 1.0 Strict//EN" ')
        self.f.write('"http://www.abisource.com/awml.dtd">\n')
        self.f.write('<abiword template="false" styles="unlocked" xmlns:fo="http://www.w3.org/1999/XSL/Format" ')
        self.f.write('xmlns:svg="http://www.w3.org/2000/svg" xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.f.write('fileformat="1.1" xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.f.write('xmlns:awml="http://www.abisource.com/awml.dtd" xmlns="http://www.abisource.com/awml.dtd" ')
        self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" version="1.9.1" xml:space="preserve" ')
        self.f.write('props="lang:%s; dom-dir:ltr">\n' % Utils.xml_lang())

        # metadata section
        self.f.write('<metadata>\n')
        self.f.write('<m key="dc.format">application/x-abiword</m>\n')
        self.f.write('<m key="abiword.generator">AbiWord</m>\n')
        self.f.write('<m key="abiword.date_last_changed">Mon May 19 14:16:24 2003</m>\n')
        self.f.write('</metadata>\n')

        self.write_styles()

        # page size section
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

    def write_styles(self):
        self.f.write('<styles>\n')
        for style_name in self.style_list.keys():
            style = self.style_list[style_name]
            self.current_style = style
            self.f.write('<s type="P" name="%s" basedon="" followedby="" props="' % style_name)
            self.f.write('margin-top:%.4fin; ' % (float(style.get_top_margin())/2.54))
            self.f.write('margin-bottom:%.4fin; ' % (float(style.get_bottom_margin())/2.54))
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
            self.f.write(' text-indent:%.4fin;' % indent)
            font = style.get_font()
            self.f.write(' font-family:')
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                self.f.write('Arial; ')
            else:
                self.f.write('Times New Roman; ')
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
            self.f.write('"/>\n')
        self.f.write('</styles>\n')

    def close(self):
        """Write the trailing information and closes the file"""
        self.f.write('</section>\n')
        if self.media_list:
            self.f.write('<data>\n')
            for tag_number in range(len(self.media_list)):
                name = self.media_list[tag_number]
                img = ImgManip.ImgManip(name)
                buf = img.png_data()

                self.f.write(
                    '<d name="image%d" mime-type="image/png" base64="yes">\n'
                    % tag_number)
                self.f.write(base64.encodestring(buf))
                self.f.write('</d>\n')
            self.f.write('</data>\n')

        self.f.write('</abiword>\n')
        self.f.close()

        if self.print_req:
            try:
                app = Mime.get_application(mime_type)[0]
                Utils.launch(app,self.filename)
            except:
                pass

    def add_media_object(self,name,pos,x_cm,y_cm):

        try:
            image = ImgManip.ImgManip(name)
            (x,y) = image.size()
        except:
            return

        if y:
            aspect_ratio = float(x)/float(y)
        else:
            aspect_ratio = 1

        if aspect_ratio > x_cm/y_cm:
            act_width = x_cm
            act_height = y_cm/aspect_ratio
        else:
            act_height = y_cm
            act_width = x_cm*aspect_ratio

        if name in self.media_list:
            tag_number = self.media_list.index(name)
        else:
            tag_number = len(self.media_list)
            self.media_list.append(name)

        if self.in_paragraph:        # We cannot insert photo 
            start_p = end_p = ''     # outside text paragraph.
        else:                        # So if not in paragraph, insert one.
            start_p = '<p>'
            end_p = '</p>'

        self.f.write('%s<image dataid="image%d" '
                     'props="height:%.3fcm; width:%.3fcm"/>%s '
                     % (start_p,tag_number,act_height,act_width,end_p))

    def start_superscript(self):
        self.f.write('<c props="text-position:superscript">')

    def end_superscript(self):
        self.f.write('</c>')

    def start_paragraph(self,style_name,leader=None):
        self.in_paragraph = 1
        style = self.style_list[style_name]
        self.current_style = style
        self.f.write('<p style="%s">' % style_name)
        if self.new_page == 1:
            self.new_page = 0
            self.f.write('<pbr/>')
        if leader != None:
            self.f.write(leader)
            self.f.write('\t')
                     
    def page_break(self):
        self.new_page = 1

    def end_paragraph(self):
        self.in_paragraph = 0
        self.f.write('</p>\n')

    def write_note(self,text,format,style_name):
        if format == 1:
            self.start_paragraph(style_name)
            self.f.write('<c props="font-family:Courier">')
            self.write_text(text)
            self.f.write('</c>')
            self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = ' '.join(line.split())
                self.write_text(line)
                self.end_paragraph()

    def write_text(self,text,mark=None):
        text = text.replace('&','&amp;');       # Must be first
        text = text.replace('<','&lt;');
        text = text.replace('>','&gt;');
        text = text.replace('&lt;super&gt;','<c props="text-position:superscript">')
        text = text.replace('&lt;/super&gt;','</c>')
        self.f.write(text)

    def start_bold(self):
        self.f.write('<c props="font-weight:bold">')

    def end_bold(self):
        self.f.write('</c>')

    def start_table(self,name,style_name):
        self.in_table = 1
        self.tblstyle = self.table_styles[style_name]
        self.f.write('<table props="table-column-props:')
        width = float(self.get_usable_width())
        for col in range(0,self.tblstyle.get_columns()):
            self.f.write("%.2fcm/" % ((self.tblstyle.get_column_width(col)/100.0) * width))
        self.f.write('">\n')
        self.current_row = -1
        
    def end_table(self):
        self.in_table = 0
        self.f.write('</table>\n')

    def start_row(self):
        self.ledge = 0.0
        self.col = 0
        self.current_row += 1

    def end_row(self):
        pass
    
    def start_cell(self,style_name,span=1):
        self.cstyle = self.cell_styles[style_name]
        self.f.write('<cell props="')
        if not self.cstyle.get_top_border():
            self.f.write('top-style:0; top-style:0;')
        if not self.cstyle.get_bottom_border():
            self.f.write('bot-style:0; bot-style:0;')
        if not self.cstyle.get_right_border():
            self.f.write('right-style:0; right-style:0;')
        if not self.cstyle.get_left_border():
            self.f.write('left-style:0; left-style:0;')
            
        self.f.write('bot-attach:%d; ' % (self.current_row+1))
        self.f.write('top-attach:%d; ' % self.current_row)
        self.f.write('left-attach:%d; ' % self.col)
        self.f.write('right-attach:%d"' % (self.col+span))
        self.f.write('>\n')
        self.col += span

    def end_cell(self):
        self.f.write('</cell>\n')

#--------------------------------------------------------------------------
#
# Register plugins
#
#--------------------------------------------------------------------------

try:
    if Mime.mime_type_is_defined("application/x-abiword"):
        mime_type = "application/x-abiword"
    elif Mime.mime_type_is_defined("application/abiword"):
        mime_type = "application/abiword"
    
    prog = Mime.get_application(mime_type)
    mtype = Mime.get_description(mime_type)
    
    if Utils.search_for(prog[0]):
        print_label=_("Open in %s") % prog[1]
    else:
        print_label=None
    register_text_doc(mtype,AbiWordDoc,1,1,1,".abw", print_label)
except:
    register_text_doc(_('AbiWord document'),AbiWordDoc,1,1,1,".abw", None)
