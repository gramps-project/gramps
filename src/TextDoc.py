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

FONT_SANS_SERIF = 0
FONT_SERIF = 1

PAPER_PORTRAIT  = 0
PAPER_LANDSCAPE = 1

PARA_ALIGN_CENTER = 0
PARA_ALIGN_LEFT   = 1 
PARA_ALIGN_RIGHT  = 2
PARA_ALIGN_JUSTIFY= 3

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
            self.colwid = [ 0 ] * 10

    def set_width(self,width):
        self.width = width

    def get_width(self):
        return self.width

    def set_columns(self,columns):
        self.columns = columns

    def get_columns(self):
        return self.columns 

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
        else:
            self.rborder = 0
            self.lborder = 0
            self.tborder = 0
            self.bborder = 0
            self.padding = 0

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

    def set_header_level(self,level):
        self.level = level

    def get_header_level(self):
        return self.level

    def set_font(self,font):
        self.font = FontStyle(font)

    def get_font(self):
        return FontStyle(self.font)

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
class TextDoc:
    def __init__(self,type,orientation=PAPER_PORTRAIT):
        self.orientation = orientation
        if orientation == PAPER_PORTRAIT:
            self.width = type.get_width()
            self.height = type.get_height()
        else:
            self.width = type.get_height()
            self.height = type.get_width()
        self.tmargin = 2.54
        self.bmargin = 2.54
        self.lmargin = 2.54
        self.rmargin = 2.54
                
        self.font = FontStyle()
        self.style_list = {}
	self.table_styles = {}
        self.cell_styles = {}
        self.name = ""
        self.photo_list = []

    def add_photo(self,name,x,y):
        pass
    
    def get_usable_width(self):
        return self.width - (self.rmargin + self.lmargin)

    def get_usable_height(self):
        return self.height - (self.tmargin + self.bmargin)

    def creator(self,name):
        self.name = name

    def add_style(self,name,style):
        self.style_list[name] = ParagraphStyle(style)

    def add_table_style(self,name,style):
        self.table_styles[name] = TableStyle(style)

    def add_cell_style(self,name,style):
        self.cell_styles[name] = TableCellStyle(style)

    def open(self,filename):
        pass

    def close(self):
        pass

    def start_page(self,orientation=None):
        pass

    def end_page(self):
        pass

    def start_paragraph(self,style_name):
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
