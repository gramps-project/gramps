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

import string
import os

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser,handler
except:
    from _xmlplus.sax import make_parser,handler

FONT_SANS_SERIF = 0
FONT_SERIF = 1

PAPER_PORTRAIT  = 0
PAPER_LANDSCAPE = 1

PARA_ALIGN_CENTER = 0
PARA_ALIGN_LEFT   = 1 
PARA_ALIGN_RIGHT  = 2
PARA_ALIGN_JUSTIFY= 3

def cnv2color(text):
    c0 = string.atoi(text[1:3],16)
    c1 = string.atoi(text[3:5],16)
    c2 = string.atoi(text[5:7],16)
    return (c0,c1,c2)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PaperStyle:
    def __init__(self,name,height,width):
        self.name = name
        self.orientation = PAPER_PORTRAIT
        self.height = height
        self.width = width

    def get_name(self):
        return self.name

    def get_orientation(self):
        return self.orientation

    def set_orientation(self,val):
        self.orientation = val

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def get_height_inches(self):
        return self.height / 2.54

    def get_width_inches(self):
        return self.width / 2.54

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FontStyle:
    def __init__(self, style=None):
        if style:
            self.face   = style.face
            self.size   = style.size
            self.italic = style.italic
            self.bold   = style.bold
            self.color  = style.color
            self.under  = style.under
        else:
            self.face   = FONT_SERIF
            self.size   = 12
            self.italic = 0
            self.bold   = 0
            self.color  = (0,0,0)
            self.under  = 0
            
    def set(self,face=None,size=None,italic=None,bold=None,underline=None,color=None):
        if face != None:
            self.set_type_face(face)
        if size != None:
            self.set_size(size)
        if italic != None:
            self.set_italic(italic)
        if bold != None:
            self.set_bold(bold)
        if underline != None:
            self.set_underline(underline)
        if color != None:
            self.set_color(color)

    def set_italic(self,val):
        "0 disables italics, 1 enables italics"
        self.italic = val

    def get_italic(self):
        "1 indicates use italics"
        return self.italic

    def set_bold(self,val):
        "0 disables bold face, 1 enables bold face"
        self.bold = val

    def get_bold(self):
        "1 indicates use bold face"
        return self.bold

    def set_color(self,val):
        "sets the color using an RGB color tuple"
        self.color = val

    def get_color(self):
        "Returns an RGB color tuple"
	return self.color

    def set_size(self,val):
        "sets font size in points"
        self.size = val

    def get_size(self):
        "returns font size in points"
        return self.size

    def set_type_face(self,val):
        "sets the font face type"
        self.face = val

    def get_type_face(self):
        "returns the font face type"
        return self.face

    def set_underline(self,val):
        "1 enables underlining"
        self.under = val

    def get_underline(self):
        "1 indicates underlining"
        return self.under

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TableStyle:
    def __init__(self,obj=None):
        if obj:
            self.width = obj.width
            self.columns = obj.columns
            self.colwid  = obj.colwid[:]
        else:
            self.width = 0
            self.columns = 0
            self.colwid = [ 0 ] * 100

    def set_width(self,width):
        self.width = width

    def get_width(self):
        return self.width

    def set_columns(self,columns):
        self.columns = columns

    def get_columns(self):
        return self.columns 

    def set_column_widths(self, list):
        self.columns = len(list)
        for i in range(self.columns):
            self.colwid[i] = list[i]

    def set_column_width(self,index,width):
	self.colwid[index] = width

    def get_column_width(self,index):
	return self.colwid[index]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TableCellStyle:
    def __init__(self,obj=None):
        if obj:
            self.rborder = obj.rborder
            self.lborder = obj.lborder
            self.tborder = obj.tborder
            self.bborder = obj.bborder
            self.padding = obj.padding
	    self.longlist = obj.longlist
        else:
            self.rborder = 0
            self.lborder = 0
            self.tborder = 0
            self.bborder = 0
            self.padding = 0
	    self.longlist = 0
	    
    def set_padding(self,val):
        self.padding = val

    def set_right_border(self,val):
        self.rborder = val

    def set_left_border(self,val):
        self.lborder = val

    def set_top_border(self,val):
        self.tborder = val

    def set_bottom_border(self,val):
        self.bborder = val

    def set_longlist(self,val):
        self.longlist = val

    def get_padding(self):
        return self.padding

    def get_right_border(self):
        return self.rborder

    def get_left_border(self):
        return self.lborder

    def get_top_border(self):
        return self.tborder

    def get_bottom_border(self):
        return self.bborder

    def get_longlist(self):
        return self.longlist

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ParagraphStyle:
    def __init__(self,p=None):
        if p:
            self.font    = FontStyle(p.font)
            self.rmargin = p.rmargin
            self.lmargin = p.lmargin
            self.first_indent = p.first_indent
            self.align   = p.align
	    self.level   = p.level
	    self.top_border = p.top_border
	    self.bottom_border = p.bottom_border
	    self.right_border = p.right_border
	    self.left_border = p.left_border
            self.pad = p.pad
            self.bgcolor = p.bgcolor
        else:
            self.font    = FontStyle()
            self.rmargin = 0
            self.lmargin = 0
            self.first_indent = 0
            self.align   = PARA_ALIGN_LEFT
	    self.level   = 0
	    self.top_border = 0
	    self.bottom_border = 0
	    self.right_border = 0
	    self.left_border = 0
            self.pad = 0
            self.bgcolor = (255,255,255)

    def set(self,rmargin=None,lmargin=None,first_indent=None,align=None,\
            tborder=None,bborder=None,rborder=None,lborder=None,pad=None,
            bgcolor=None,font=None):
        if font != None:
            self.font = FontStyle(font)
        if pad != None:
            self.set_padding(pad)
        if tborder != None:
            self.set_top_border(tborder)
        if bborder != None:
            self.set_bottom_border(bborder)
        if rborder != None:
            self.set_right_border(rborder)
        if lborder != None:
            self.set_left_border(lborder)
        if bgcolor != None:
            self.set_background_color(bgcolor)
        if align != None:
            self.set_alignment(align)
        if rmargin != None:
            self.set_right_margin(rmargin)
        if lmargin != None:
            self.set_left_margin(lmargin)
        if first_indent != None:
            self.set_first_indent(first_indent)
            
    def set_header_level(self,level):
        self.level = level

    def get_header_level(self):
        return self.level

    def set_font(self,font):
        self.font = FontStyle(font)

    def get_font(self):
        return self.font

    def set_padding(self,val):
        self.pad = val

    def get_padding(self):
        return self.pad

    def set_top_border(self,val):
        self.top_border = val

    def get_top_border(self):
        return self.top_border

    def set_bottom_border(self,val):
        self.bottom_border = val

    def get_bottom_border(self):
	return self.bottom_border

    def set_left_border(self,val):
        self.left_border = val

    def get_background_color(self):
        return self.bgcolor

    def set_background_color(self,color):
        self.bgcolor = color

    def get_left_border(self):
        return self.left_border

    def set_right_border(self,val):
        self.right_border = val

    def get_right_border(self):
        return self.right_border

    def set_alignment(self,align):
        self.align = align

    def get_alignment(self):
        return self.align

    def get_alignment_text(self):
        if self.align == PARA_ALIGN_LEFT:
            return "left"
        elif self.align == PARA_ALIGN_CENTER:
            return "center"
        elif self.align == PARA_ALIGN_RIGHT:
            return "right"
        elif self.align == PARA_ALIGN_JUSTIFY:
            return "justify"
        return "unknown"

    def set_left_margin(self,value):
	"sets the left paragraph margin in centimeters"
        self.lmargin = value

    def set_right_margin(self,value):
	"sets the right paragraph margin in centimeters"
        self.rmargin = value

    def set_first_indent(self,value):
	"sets the first indent margin in centimeters"
        self.first_indent = value

    def get_left_margin(self):
	"returns the left margin in centimeters"
        return self.lmargin

    def get_right_margin(self):
	"returns the right margin in centimeters"
        return self.rmargin

    def get_first_indent(self):
	"returns the first indent margin in centimeters"
        return self.first_indent

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class StyleSheetList:
    def __init__(self,file,defstyle):
        self.map = { "default" : defstyle }
        self.file = os.path.expanduser("~/.gramps/" + file)
        self.parse()

    def delete_style_sheet(self,name):
        del self.map[name]

    def get_style_sheet_map(self):
        return self.map

    def get_style_sheet(self,name):
        return self.map[name]

    def get_style_names(self):
        return self.map.keys()

    def set_style_sheet(self,name,style):
        if name != "default":
            self.map[name] = style

    def save(self):
        f = open(self.file,"w")
        f.write("<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n")
        f.write('<stylelist>\n')
        for name in self.map.keys():
            if name == "default":
                continue
            sheet = self.map[name]
            f.write('<sheet name="%s">\n' % name)
            for p_name in sheet.get_names():
                p = sheet.get_style(p_name)
                f.write('<style name="%s">\n' % p_name)
                font = p.get_font()
                f.write('<font face="%d" ' % font.get_type_face())
                f.write('size="%d" ' % font.get_size())
                f.write('italic="%d" ' % font.get_italic())
                f.write('bold="%d" ' % font.get_bold())
                f.write('underline="%d" ' % font.get_underline())
                f.write('color="#%02x%02x%02x"/>\n' % font.get_color())
                f.write('<para ')
                rm = float(p.get_right_margin())
                lm = float(p.get_left_margin())
                fi = float(p.get_first_indent())
                f.write('rmargin="%.3f" ' % rm)
                f.write('lmargin="%.3f" ' % lm)
                f.write('first="%.3f" ' % fi)
                f.write('pad="%.3f" ' % p.get_padding())
                f.write('bgcolor="#%02x%02x%02x" ' % p.get_background_color())
                f.write('level="%d" ' % p.get_header_level())
                f.write('align="%d" ' % p.get_alignment())
                f.write('tborder="%d" ' % p.get_top_border())
                f.write('lborder="%d" ' % p.get_left_border())
                f.write('rborder="%d" ' % p.get_right_border())
                f.write('bborder="%d"/>\n' % p.get_bottom_border())
                f.write('</style>\n')
            f.write('</sheet>\n')
        f.write('</stylelist>\n')
        f.close()
            

    def parse(self):
        try:
            parser = make_parser()
            parser.setContentHandler(SheetParser(self))
            parser.parse(self.file)
        except IOError:
            pass
        except OSError:
            pass
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class StyleSheet:
    def __init__(self,obj=None):
        self.style_list = {}
        if obj != None:
            for style_name in obj.style_list.keys():
                style = obj.style_list[style_name]
                self.style_list[style_name] = ParagraphStyle(style)

    def clear(self):
        self.style_list = {}

    def add_style(self,name,style):
        self.style_list[name] = ParagraphStyle(style)

    def get_names(self):
        return self.style_list.keys()

    def get_styles(self):
        return self.style_list

    def get_style(self,name):
        return self.style_list[name]

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
class SheetParser(handler.ContentHandler):
    def __init__(self,sheetlist):
        handler.ContentHandler.__init__(self)
        self.sheetlist = sheetlist
        self.f = None
        self.p = None
        self.s = None
        self.sname = None
        self.pname = None
        
    def setDocumentLocator(self,locator):
        self.locator = locator

    def startElement(self,tag,attrs):
        if tag == "sheet":
            self.s = StyleSheet(self.sheetlist.map["default"])
            self.sname = attrs['name']
        elif tag == "font":
            self.f = FontStyle()
            self.f.set_type_face(int(attrs['face']))
            self.f.set_size(int(attrs['size']))
            self.f.set_italic(int(attrs['italic']))
            self.f.set_bold(int(attrs['bold']))
            self.f.set_underline(int(attrs['underline']))
            self.f.set_color(cnv2color(attrs['color']))
        elif tag == "para":
            self.p.set_right_margin(float(attrs['rmargin']))
            self.p.set_left_margin(float(attrs['lmargin']))
            self.p.set_first_indent(float(attrs['first']))
            self.p.set_padding(float(attrs['pad']))
            self.p.set_alignment(int(attrs['align']))
            self.p.set_right_border(int(attrs['rborder']))
            self.p.set_header_level(int(attrs['level']))
            self.p.set_left_border(int(attrs['lborder']))
            self.p.set_top_border(int(attrs['tborder']))
            self.p.set_bottom_border(int(attrs['bborder']))
            self.p.set_background_color(cnv2color(attrs['bgcolor']))
        elif tag == "style":
            self.p = ParagraphStyle()
            self.pname = attrs['name']

    def endElement(self,tag):
        if tag == "style":
            self.p.set_font(self.f)
            self.s.add_style(self.pname,self.p)
        elif tag == "sheet":
            self.sheetlist.set_style_sheet(self.sname,self.s)
            
    def characters(self, data):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class TextDoc:
    def __init__(self,styles,type,template,orientation=PAPER_PORTRAIT):
        self.orientation = orientation
        self.template = template
        if orientation == PAPER_PORTRAIT:
            self.width = type.get_width()
            self.height = type.get_height()
        else:
            self.width = type.get_height()
            self.height = type.get_width()
        self.paper = type
        self.tmargin = 2.54
        self.bmargin = 2.54
        self.lmargin = 2.54
        self.rmargin = 2.54
        self.title = ""
                
        self.font = FontStyle()
        self.style_list = styles.get_styles()
	self.table_styles = {}
        self.cell_styles = {}
        self.name = ""
        self.photo_list = []

    def add_photo(self,name,align,w_cm,h_cm):
        """adds a photo of the specified width (in centimeters)"""
        pass
    
    def get_usable_width(self):
        return self.width - (self.rmargin + self.lmargin)

    def get_usable_height(self):
        return self.height - (self.tmargin + self.bmargin)

    def creator(self,name):
        self.name = name

    def set_title(self,name):
        self.title = name

    def add_table_style(self,name,style):
        self.table_styles[name] = TableStyle(style)

    def add_cell_style(self,name,style):
        self.cell_styles[name] = TableCellStyle(style)

    def open(self,filename):
        pass

    def close(self):
        pass

    def page_break(self):
        pass

    def start_bold(self):
        pass

    def end_bold(self):
        pass

    def start_paragraph(self,style_name,leader=None):
        pass

    def end_paragraph(self):
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

    def horizontal_line(self):
        pass

    def write_text(self,text):
        pass

