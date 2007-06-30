#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
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
Provides base interface to text based documents. Specific document
interfaces should be derived from the core classes.
"""

__author__ = "Donald N. Allingham"
__revision__ = "Revision:$Id$"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
from xml.sax.saxutils import escape

def escxml(string):
    """
    Escapes XML special characters.
    """
    return escape(string, { '"' : '&quot;' } )

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Utils
import FontScale
import const

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".BaseDoc")

#-------------------------------------------------------------------------
#
# SAX interface
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser, handler, SAXParseException
except ImportError:
    from _xmlplus.sax import make_parser, handler, SAXParseException

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
FONT_SANS_SERIF = 0
FONT_SERIF      = 1
FONT_MONOSPACE  = 2

#-------------------------------------------------------------------------
#
# Page orientation
#
#-------------------------------------------------------------------------
PAPER_PORTRAIT  = 0
PAPER_LANDSCAPE = 1

#-------------------------------------------------------------------------
#
# Paragraph alignment
#
#-------------------------------------------------------------------------
PARA_ALIGN_CENTER  = 0
PARA_ALIGN_LEFT    = 1 
PARA_ALIGN_RIGHT   = 2
PARA_ALIGN_JUSTIFY = 3

#-------------------------------------------------------------------------
#
# Text vs. Graphics mode
#
#-------------------------------------------------------------------------
TEXT_MODE     = 0
GRAPHICS_MODE = 1

#-------------------------------------------------------------------------
#
# Line style
#
#-------------------------------------------------------------------------
SOLID  = 0
DASHED = 1

#-------------------------------------------------------------------------
#
# IndexMark types
#
#-------------------------------------------------------------------------
INDEX_TYPE_ALP = 0
INDEX_TYPE_TOC = 1

#------------------------------------------------------------------------
#
# cnv2color
#
#------------------------------------------------------------------------
def cnv2color(text):
    """
    converts a hex value in the form of #XXXXXX into a tuple of integers
    representing the RGB values
    """
    return (int(text[1:3], 16), int(text[3:5], 16), int(text[5:7], 16))

#------------------------------------------------------------------------
#
# PaperSize
#
#------------------------------------------------------------------------
class PaperSize:
    """
    Defines the dimensions of a sheet of paper. All dimensions are in
    centimeters.
    """
    def __init__(self, name, height, width):
        """
        Creates a new paper style with.

        @param name: name of the new style
        @param height: page height in centimeters
        @param width: page width in centimeters
        """
        self.name = name
        self.height = height
        self.width = width

    def get_name(self):
        "Returns the name of the paper style"
        return self.name

    def get_height(self):
        "Returns the page height in cm"
        return self.height

    def set_height(self, height):
        "Sets the page height in cm"
        self.height = height

    def get_width(self):
        "Returns the page width in cm"
        return self.width

    def set_width(self, width):
        "Sets the page width in cm"
        self.width = width

    def get_height_inches(self):
        "Returns the page height in inches"
        return self.height / 2.54

    def get_width_inches(self):
        "Returns the page width in inches"
        return self.width / 2.54

#------------------------------------------------------------------------
#
# PaperStyle
#
#------------------------------------------------------------------------
class PaperStyle:
    """
    Defines the various options for a sheet of paper.
    """
    def __init__(self, size, orientation):
        """
        Creates a new paper style.

        @param size: size of the new style
        @type size: PaperSize
        @param orientation: page orientation
        @type orientation: PAPER_PORTRAIT or PAPER_LANDSCAPE
        """

        self.__orientation = orientation
        if orientation == PAPER_PORTRAIT:
            self.__size = PaperSize( size.get_name(),
                                     size.get_height(),
                                     size.get_width()  )
        else:
            self.__size = PaperSize( size.get_name(),
                                     size.get_width(),
                                     size.get_height() )

        self.__tmargin = 2.54
        self.__bmargin = 2.54
        self.__lmargin = 2.54
        self.__rmargin = 2.54
        
    def get_size(self):
        """
        returns the size of the paper.

        @returns: object indicating the paper size
        @rtype: PaperSize
        """
        return self.__size
        
    def get_orientation(self):
        """
        returns the orientation of the page.

        @returns: PAPER_PORTRIAT or PAPER_LANDSCAPE
        @rtype: int
        """
        return self.__orientation
        
    def get_usable_width(self):
        """
        Returns the width of the page area in centimeters. The value is
        the page width less the margins.
        """
        return self.__size.get_width() - (self.__rmargin + self.__lmargin)

    def get_usable_height(self):
        """
        Returns the height of the page area in centimeters. The value is
        the page height less the margins.
        """
        return self.__size.get_height() - (self.__tmargin + self.__bmargin)

    def get_right_margin(self):
        """
        Returns the right margin.

        @returns: Right margin in centimeters
        @rtype: float
        """
        return self.__rmargin

    def get_left_margin(self):
        """
        Returns the left margin.

        @returns: Left margin in centimeters
        @rtype: float
        """
        return self.__lmargin

    def get_top_margin(self):
        """
        Returns the top margin.

        @returns: Top margin in centimeters
        @rtype: float
        """
        return self.__tmargin

    def get_bottom_margin(self):
        """
        Returns the bottom margin.

        @returns: Bottom margin in centimeters
        @rtype: float
        """
        return self.__bmargin

#------------------------------------------------------------------------
#
# FontStyle
#
#------------------------------------------------------------------------
class FontStyle:
    """
    Defines a font style. Controls the font face, size, color, and
    attributes. In order to remain generic, the only font faces available
    are FONT_SERIF and FONT_SANS_SERIF. Document formatters should convert
    these to the appropriate fonts for the target format.

    The FontStyle represents the desired characteristics. There are no
    guarentees that the document format generator will be able implement
    all or any of the characteristics.
    """
    
    def __init__(self, style=None):
        """
        Creates a new FontStyle object, accepting the default values.

        @param style: if specified, initializes the FontStyle from the passed
            FontStyle instead of using the defaults.
        """
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
            self.color  = (0, 0, 0)
            self.under  = 0
            
    def set(self, face=None, size=None, italic=None, bold=None,
            underline=None, color=None):
        """
        Sets font characteristics.

        @param face: font type face, either FONT_SERIF or FONT_SANS_SERIF
        @param size: type face size in points
        @param italic: True enables italics, False disables italics
        @param bold: True enables bold face, False disables bold face
        @param underline: True enables underline, False disables underline
        @param color: an RGB color representation in the form of three integers
            in the range of 0-255 represeting the red, green, and blue
            components of a color.
        """
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

    def set_italic(self, val):
        "0 disables italics, 1 enables italics"
        self.italic = val

    def get_italic(self):
        "1 indicates use italics"
        return self.italic

    def set_bold(self, val):
        "0 disables bold face, 1 enables bold face"
        self.bold = val

    def get_bold(self):
        "1 indicates use bold face"
        return self.bold

    def set_color(self, val):
        "sets the color using an RGB color tuple"
        self.color = val

    def get_color(self):
        "Returns an RGB color tuple"
        return self.color

    def set_size(self, val):
        "sets font size in points"
        self.size = val

    def get_size(self):
        "returns font size in points"
        return self.size

    def set_type_face(self, val):
        "sets the font face type"
        self.face = val

    def get_type_face(self):
        "returns the font face type"
        return self.face

    def set_underline(self, val):
        "1 enables underlining"
        self.under = val

    def get_underline(self):
        "1 indicates underlining"
        return self.under

#------------------------------------------------------------------------
#
# TableStyle
#
#------------------------------------------------------------------------
class TableStyle:
    """
    Specifies the style or format of a table. The TableStyle contains the
    characteristics of table width (in percentage of the full width), the
    number of columns, and the width of each column as a percentage of the
    width of the table.
    """
    def __init__(self, obj=None):
        """
        Creates a new TableStyle object, with the values initialized to
        empty, with allocating space for up to 100 columns.

        @param obj: if not None, then the object created gets is attributes
            from the passed object instead of being initialized to empty.
        """
        if obj:
            self.width = obj.width
            self.columns = obj.columns
            self.colwid  = obj.colwid[:]
        else:
            self.width = 0
            self.columns = 0
            self.colwid = [ 0 ] * 100

    def set_width(self, width):
        """
        Sets the width of the table in terms of percent of the available
        width
        """
        self.width = width

    def get_width(self):
        """
        Returns the specified width as a percentage of the available space
        """
        return self.width

    def set_columns(self, columns):
        """
        Sets the number of columns.

        @param columns: number of columns that should be used.
        """
        self.columns = columns

    def get_columns(self):
        """
        Returns the number of columns
        """
        return self.columns 

    def set_column_widths(self, clist):
        """
        Sets the width of all the columns at once, taking the percentages
        from the passed list.
        """
        self.columns = len(clist)
        for i in range(self.columns):
            self.colwid[i] = clist[i]

    def set_column_width(self, index, width):
        """
        Sets the width of a specified column to the specified width.

        @param index: column being set (index starts at 0)
        @param width: percentage of the table width assigned to the column
        """
        self.colwid[index] = width

    def get_column_width(self, index):
        """
        Returns the column width of the specified column as a percentage of
        the entire table width.

        @param index: column to return (index starts at 0)
        """
        return self.colwid[index]

#------------------------------------------------------------------------
#
# TableCellStyle
#
#------------------------------------------------------------------------
class TableCellStyle:
    """
    Defines the style of a particular table cell. Characteristics are:
    right border, left border, top border, bottom border, and padding.
    """
    def __init__(self, obj=None):
        """
        Creates a new TableCellStyle instance.

        @param obj: if not None, specifies that the values should be
            copied from the passed object instead of being initialized to empty.
        """
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
    
    def set_padding(self, val):
        "Returns the cell padding in centimeters"
        self.padding = val

    def set_right_border(self, val):
        """
        Defines if a right border in used

        @param val: if True, a right border is used, if False, it is not
        """
        self.rborder = val

    def set_left_border(self, val):
        """
        Defines if a left border in used

        @param val: if True, a left border is used, if False, it is not
        """
        self.lborder = val

    def set_top_border(self, val):
        """
        Defines if a top border in used

        @param val: if True, a top border is used, if False, it is not
        """
        self.tborder = val

    def set_bottom_border(self, val):
        """
        Defines if a bottom border in used

        @param val: if 1, a bottom border is used, if 0, it is not
        """
        self.bborder = val

    def set_longlist(self, val):
        self.longlist = val

    def get_padding(self):
        "Returns the cell padding in centimeters"
        return self.padding

    def get_right_border(self):
        "Returns 1 if a right border is requested"
        return self.rborder

    def get_left_border(self):
        "Returns 1 if a left border is requested"
        return self.lborder

    def get_top_border(self):
        "Returns 1 if a top border is requested"
        return self.tborder

    def get_bottom_border(self):
        "Returns 1 if a bottom border is requested"
        return self.bborder

    def get_longlist(self):
        return self.longlist

#------------------------------------------------------------------------
#
# ParagraphStyle
#
#------------------------------------------------------------------------
class ParagraphStyle:
    """
    Defines the characteristics of a paragraph. The characteristics are:
    font (a FontStyle instance), right margin, left margin, first indent,
    top margin, bottom margin, alignment, level, top border, bottom border,
    right border, left border, padding, and background color.

    """
    def __init__(self, source=None):
        """
        @param source: if not None, then the ParagraphStyle is created
            using the values of the source instead of the default values.
        """
        if source:
            self.font = FontStyle(source.font)
            self.rmargin = source.rmargin
            self.lmargin = source.lmargin
            self.first_indent = source.first_indent
            self.tmargin = source.tmargin
            self.bmargin = source.bmargin
            self.align = source.align
            self.level = source.level
            self.top_border = source.top_border
            self.bottom_border = source.bottom_border
            self.right_border = source.right_border
            self.left_border = source.left_border
            self.pad = source.pad
            self.bgcolor = source.bgcolor
            self.description = source.description
            self.tabs = source.tabs
        else:
            self.font = FontStyle()
            self.rmargin = 0
            self.lmargin = 0
            self.tmargin = 0
            self.bmargin = 0
            self.first_indent = 0
            self.align = PARA_ALIGN_LEFT
            self.level = 0
            self.top_border = 0
            self.bottom_border = 0
            self.right_border = 0
            self.left_border = 0
            self.pad = 0
            self.bgcolor = (255, 255, 255)
            self.description = ""
            self.tabs = []

    def set_description(self, text):
        """
        Sets the desciption of the paragraph
        """
        self.description = text

    def get_description(self):
        """
        Returns the desciption of the paragraph
        """
        return self.description

    def set(self, rmargin=None, lmargin=None, first_indent=None,
            tmargin=None, bmargin=None, align=None,
            tborder=None, bborder=None, rborder=None, lborder=None,
            pad=None, bgcolor=None, font=None):
        """
        Allows the values of the object to be set.

        @param rmargin: right indent in centimeters
        @param lmargin: left indent in centimeters
        @param first_indent: first line indent in centimeters
        @param tmargin: space above paragraph in centimeters
        @param bmargin: space below paragraph in centimeters
        @param align: alignment type (PARA_ALIGN_LEFT, PARA_ALIGN_RIGHT, PARA_ALIGN_CENTER, or PARA_ALIGN_JUSTIFY)
        @param tborder: non zero indicates that a top border should be used
        @param bborder: non zero indicates that a bottom border should be used
        @param rborder: non zero indicates that a right border should be used
        @param lborder: non zero indicates that a left border should be used
        @param pad: padding in centimeters
        @param bgcolor: background color of the paragraph as an RGB tuple.
        @param font: FontStyle instance that defines the font
        """
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
        if tmargin != None:
            self.set_top_margin(tmargin)
        if bmargin != None:
            self.set_bottom_margin(bmargin)
            
    def set_header_level(self, level):
        """
        Sets the header level for the paragraph. This is useful for
        numbered paragraphs. A value of 1 indicates a header level
        format of X, a value of two implies X.X, etc. A value of zero
        means no header level.
        """
        self.level = level

    def get_header_level(self):
        "Returns the header level of the paragraph"
        return self.level

    def set_font(self, font):
        """
        Sets the font style of the paragraph.

        @param font: FontStyle object containing the font definition to use.
        """
        self.font = FontStyle(font)

    def get_font(self):
        "Returns the FontStyle of the paragraph"
        return self.font

    def set_padding(self, val):
        """
        Sets the paragraph padding in centimeters

        @param val: floating point value indicating the padding in centimeters
        """
        self.pad = val

    def get_padding(self):
        """Returns a the padding of the paragraph"""
        return self.pad

    def set_top_border(self, val):
        """
        Sets the presence or absence of top border.

        @param val: True indicates a border should be used, False indicates
            no border.
        """
        self.top_border = val

    def get_top_border(self):
        "Returns 1 if a top border is specified"
        return self.top_border

    def set_bottom_border(self, val):
        """
        Sets the presence or absence of bottom border.

        @param val: True indicates a border should be used, False
            indicates no border.
        """
        self.bottom_border = val

    def get_bottom_border(self):
        "Returns 1 if a bottom border is specified"
        return self.bottom_border

    def set_left_border(self, val):
        """
        Sets the presence or absence of left border.

        @param val: True indicates a border should be used, False
            indicates no border.
        """
        self.left_border = val

    def get_left_border(self):
        "Returns 1 if a left border is specified"
        return self.left_border

    def set_right_border(self, val):
        """
        Sets the presence or absence of rigth border.

        @param val: True indicates a border should be used, False
            indicates no border.
        """
        self.right_border = val

    def get_right_border(self):
        "Returns 1 if a right border is specified"
        return self.right_border

    def get_background_color(self):
        """
        Returns a tuple indicating the RGB components of the background
        color
        """
        return self.bgcolor

    def set_background_color(self, color):
        """
        Sets the background color of the paragraph.

        @param color: tuple representing the RGB components of a color
            (0,0,0) to (255,255,255)
        """
        self.bgcolor = color

    def set_alignment(self, align):
        """
        Sets the paragraph alignment.

        @param align: PARA_ALIGN_LEFT, PARA_ALIGN_RIGHT, PARA_ALIGN_CENTER,
            or PARA_ALIGN_JUSTIFY
        """
        self.align = align

    def get_alignment(self):
        "Returns the alignment of the paragraph"
        return self.align

    def get_alignment_text(self):
        """
        Returns a text string representing the alginment, either 'left',
        'right', 'center', or 'justify'
        """
        if self.align == PARA_ALIGN_LEFT:
            return "left"
        elif self.align == PARA_ALIGN_CENTER:
            return "center"
        elif self.align == PARA_ALIGN_RIGHT:
            return "right"
        elif self.align == PARA_ALIGN_JUSTIFY:
            return "justify"
        return "unknown"

    def set_left_margin(self, value):
        "sets the left indent in centimeters"
        self.lmargin = value

    def set_right_margin(self, value):
        "sets the right indent in centimeters"
        self.rmargin = value

    def set_first_indent(self, value):
        "sets the first line indent in centimeters"
        self.first_indent = value

    def set_top_margin(self, value):
        "sets the space above paragraph in centimeters"
        self.tmargin = value

    def set_bottom_margin(self, value):
        "sets the space below paragraph in centimeters"
        self.bmargin = value

    def get_left_margin(self):
        "returns the left indent in centimeters"
        return self.lmargin

    def get_right_margin(self):
        "returns the right indent in centimeters"
        return self.rmargin

    def get_first_indent(self):
        "returns the first line indent in centimeters"
        return self.first_indent

    def get_top_margin(self):
        "returns the space above paragraph in centimeters"
        return self.tmargin

    def get_bottom_margin(self):
        "returns the space below paragraph in centimeters"
        return self.bmargin

    def set_tabs(self, tab_stops):
        assert(type(tab_stops) == type([]))
        self.tabs = tab_stops

    def get_tabs(self):
        return self.tabs

#------------------------------------------------------------------------
#
# StyleSheetList
#
#------------------------------------------------------------------------
class StyleSheetList:
    """
    Interface into the user's defined style sheets. Each StyleSheetList
    has a predefined default style specified by the report. Additional
    styles are loaded from a specified XML file if it exists.
    """
    
    def __init__(self, filename, defstyle):
        """
        Creates a new StyleSheetList from the specified default style and
        any other styles that may be defined in the specified file.

        file - XML file that contains style definitions
        defstyle - default style
        """
        defstyle.set_name('default')
        self.map = { "default" : defstyle }
        self.file = os.path.join(const.home_dir, filename)
        self.parse()

    def delete_style_sheet(self, name):
        """
        Removes a style from the list. Since each style must have a
        unique name, the name is used to delete the stylesheet.

        name - Name of the style to delete
        """
        del self.map[name]

    def get_style_sheet_map(self):
        """
        Returns the map of names to styles.
        """
        return self.map

    def get_style_sheet(self, name):
        """
        Returns the StyleSheet associated with the name

        name - name associated with the desired StyleSheet.
        """
        return self.map[name]

    def get_style_names(self):
        "Returns a list of all the style names in the StyleSheetList"
        return self.map.keys()

    def set_style_sheet(self, name, style):
        """
        Adds or replaces a StyleSheet in the StyleSheetList. The
        default style may not be replaced.

        name - name assocated with the StyleSheet to add or replace.
        style - definition of the StyleSheet
        """
        style.set_name(name)
        if name != "default":
            self.map[name] = style

    def save(self):
        """
        Saves the current StyleSheet definitions to the associated file.
        """
        xml_file = open(self.file,"w")
        xml_file.write("<?xml version=\"1.0\"?>\n")
        xml_file.write('<stylelist>\n')
        for name in self.map.keys():
            if name == "default":
                continue
            sheet = self.map[name]
            xml_file.write('<sheet name="%s">\n' % escxml(name))
            for p_name in sheet.get_paragraph_style_names():
                para = sheet.get_paragraph_style(p_name)
                xml_file.write('<style name="%s">\n' % escxml(p_name))
                font = para.get_font()
                xml_file.write('<font face="%d" ' % font.get_type_face())
                xml_file.write('size="%d" ' % font.get_size())
                xml_file.write('italic="%d" ' % font.get_italic())
                xml_file.write('bold="%d" ' % font.get_bold())
                xml_file.write('underline="%d" ' % font.get_underline())
                xml_file.write('color="#%02x%02x%02x"/>\n' % font.get_color())
                xml_file.write('<para ')
                rmargin = float(para.get_right_margin())
                lmargin = float(para.get_left_margin())
                findent = float(para.get_first_indent())
                tmargin = float(para.get_top_margin())
                bmargin = float(para.get_bottom_margin())
                padding = float(para.get_padding())
                xml_file.write('description="%s" ' % 
                               escxml(para.get_description()))
                xml_file.write('rmargin="%s" ' % Utils.gformat(rmargin))
                xml_file.write('lmargin="%s" ' % Utils.gformat(lmargin))
                xml_file.write('first="%s" ' % Utils.gformat(findent))
                xml_file.write('tmargin="%s" ' % Utils.gformat(tmargin))
                xml_file.write('bmargin="%s" ' % Utils.gformat(bmargin))
                xml_file.write('pad="%s" ' % Utils.gformat(padding))
                bg_color = para.get_background_color()
                xml_file.write('bgcolor="#%02x%02x%02x" ' % bg_color)
                xml_file.write('level="%d" ' % para.get_header_level())
                xml_file.write('align="%d" ' % para.get_alignment())
                xml_file.write('tborder="%d" ' % para.get_top_border())
                xml_file.write('lborder="%d" ' % para.get_left_border())
                xml_file.write('rborder="%d" ' % para.get_right_border())
                xml_file.write('bborder="%d"/>\n' % para.get_bottom_border())
                xml_file.write('</style>\n')
            xml_file.write('</sheet>\n')
        xml_file.write('</stylelist>\n')
        xml_file.close()
            
    def parse(self):
        """
        Loads the StyleSheets from the associated file, if it exists.
        """
        try:
            if os.path.isfile(self.file):
                parser = make_parser()
                parser.setContentHandler(SheetParser(self))
                the_file = open(self.file)
                parser.parse(the_file)
                the_file.close()
        except (IOError,OSError,SAXParseException):
            pass
        
#------------------------------------------------------------------------
#
# StyleSheet
#
#------------------------------------------------------------------------
class StyleSheet:
    """
    A collection of named paragraph styles.
    """
    
    def __init__(self, obj=None):
        """
        Creates a new empty StyleSheet.

        @param obj: if not None, creates the StyleSheet from the values in
            obj, instead of creating an empty StyleSheet
        """
        self.para_styles = {}
        self.draw_styles = {}
        self.table_styles = {}
        self.cell_styles = {}
        self.name = ""
        if obj != None:
            for style_name in obj.para_styles.keys():
                style = obj.para_styles[style_name]
                self.para_styles[style_name] = ParagraphStyle(style)
            for style_name in obj.draw_styles.keys():
                style = obj.draw_styles[style_name]
                self.draw_styles[style_name] = GraphicsStyle(style)
            for style_name in obj.table_styles.keys():
                style = obj.table_styles[style_name]
                self.table_styles[style_name] = TableStyle(style)
            for style_name in obj.cell_styles.keys():
                style = obj.cell_styles[style_name]
                self.cell_styles[style_name] = TableCellStyle(style)

    def set_name(self, name):
        """
        Sets the name of the StyleSheet
        
        @param name: The name to be given to the StyleSheet
        """
        self.name = name

    def get_name(self):
        """
        Returns the name of the StyleSheet
        """
        return self.name

    def clear(self):
        "Removes all styles from the StyleSheet"
        self.para_styles = {}
        self.draw_styles = {}
        self.table_styles = {}
        self.cell_styles = {}

    def add_paragraph_style(self, name, style):
        """
        Adds a paragraph style to the style sheet.

        @param name: The name of the ParagraphStyle
        @param style: ParagraphStyle instance to be added.
        """
        self.para_styles[name] = ParagraphStyle(style)
        
    def get_paragraph_style(self, name):
        """
        Returns the ParagraphStyle associated with the name

        @param name: name of the ParagraphStyle that is wanted
        """
        return ParagraphStyle(self.para_styles[name])

    def get_paragraph_style_names(self):
        "Returns the the list of paragraph names in the StyleSheet"
        return self.para_styles.keys()

    def add_draw_style(self, name, style):
        """
        Adds a draw style to the style sheet.

        @param name: The name of the GraphicsStyle
        @param style: GraphicsStyle instance to be added.
        """
        self.draw_styles[name] = GraphicsStyle(style)
        
    def get_draw_style(self, name):
        """
        Returns the GraphicsStyle associated with the name

        @param name: name of the GraphicsStyle that is wanted
        """
        return GraphicsStyle(self.draw_styles[name])

    def get_draw_style_names(self):
        "Returns the the list of draw style names in the StyleSheet"
        return self.draw_styles.keys()
    
    def add_table_style(self, name, style):
        """
        Adds a table style to the style sheet.

        @param name: The name of the TableStyle
        @param style: TableStyle instance to be added.
        """
        self.table_styles[name] = TableStyle(style)
        
    def get_table_style(self, name):
        """
        Returns the TableStyle associated with the name

        @param name: name of the TableStyle that is wanted
        """
        return TableStyle(self.table_styles[name])

    def get_table_style_names(self):
        "Returns the the list of table style names in the StyleSheet"
        return self.table_styles.keys()
    
    def add_cell_style(self, name, style):
        """
        Adds a cell style to the style sheet.

        @param name: The name of the TableCellStyle
        @param style: TableCellStyle instance to be added.
        """
        self.cell_styles[name] = TableCellStyle(style)
        
    def get_cell_style(self, name):
        """
        Returns the TableCellStyle associated with the name

        @param name: name of the TableCellStyle that is wanted
        """
        return TableCellStyle(self.cell_styles[name])

    def get_cell_style_names(self):
        "Returns the the list of cell style names in the StyleSheet"
        return self.cell_styles.keys()

#-------------------------------------------------------------------------
#
# SheetParser
#
#-------------------------------------------------------------------------
class SheetParser(handler.ContentHandler):
    """
    SAX parsing class for the StyleSheetList XML file.
    """
    
    def __init__(self, sheetlist):
        """
        Creates a SheetParser class that populates the passed StyleSheetList
        class.

        sheetlist - StyleSheetList instance to be loaded from the file.
        """
        handler.ContentHandler.__init__(self)
        self.sheetlist = sheetlist
        self.f = None
        self.p = None
        self.s = None
        self.sname = None
        self.pname = None
        
    def startElement(self, tag, attrs):
        """
        Overridden class that handles the start of a XML element
        """
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
            if attrs.has_key('description'):
                self.p.set_description(attrs['description'])
            self.p.set_right_margin(Utils.gfloat(attrs['rmargin']))
            self.p.set_right_margin(Utils.gfloat(attrs['rmargin']))
            self.p.set_left_margin(Utils.gfloat(attrs['lmargin']))
            self.p.set_first_indent(Utils.gfloat(attrs['first']))
            try:
                # This is needed to read older style files
                # lacking tmargin and bmargin
                self.p.set_top_margin(Utils.gfloat(attrs['tmargin']))
                self.p.set_bottom_margin(Utils.gfloat(attrs['bmargin']))
            except KeyError:
                pass
            self.p.set_padding(Utils.gfloat(attrs['pad']))
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

    def endElement(self, tag):
        "Overridden class that handles the start of a XML element"
        if tag == "style":
            self.p.set_font(self.f)
            self.s.add_paragraph_style(self.pname, self.p)
        elif tag == "sheet":
            self.sheetlist.set_style_sheet(self.sname, self.s)

#------------------------------------------------------------------------
#
# GraphicsStyle
#
#------------------------------------------------------------------------
class GraphicsStyle:
    """
    Defines the properties of graphics objects, such as line width,
    color, fill, ect.
    """
    def __init__(self, obj=None):
        """
        Initialize the object with default values, unless a source
        object is specified. In that case, make a copy of the source
        object.
        """
        if obj:
            self.para_name = obj.para_name
            self.shadow = obj.shadow
            self.shadow_space = obj.shadow_space
            self.color = obj.color
            self.fill_color = obj.fill_color
            self.lwidth = obj.lwidth
            self.lstyle = obj.lstyle
        else:
            self.para_name = ""
            self.shadow = 0
            self.shadow_space = 0.2
            self.lwidth = 0.5
            self.color = (0, 0, 0)
            self.fill_color = (255, 255, 255)
            self.lstyle = SOLID

    def set_line_width(self, val):
        """
        sets the line width
        """
        self.lwidth = val

    def get_line_width(self):
        """
        Returns the name of the StyleSheet
        """
        return self.lwidth

    def get_line_style(self):
        return self.lstyle

    def set_line_style(self, val):
        self.lstyle = val

    def set_paragraph_style(self, val):
        self.para_name = val

    def set_shadow(self, val, space=0.2):
        self.shadow = val
        self.shadow_space = space

    def get_shadow_space(self):
        return self.shadow_space

    def set_color(self, val):
        self.color = val

    def set_fill_color(self, val):
        self.fill_color = val

    def get_paragraph_style(self):
        return self.para_name

    def get_shadow(self):
        return self.shadow

    def get_color(self):
        return self.color

    def get_fill_color(self):
        return self.fill_color

#------------------------------------------------------------------------
#
# IndexMark
#
#------------------------------------------------------------------------
class IndexMark:
    """
    Defines a mark to be associated with text for indexing.
    """
    def __init__(self, key="", itype=INDEX_TYPE_ALP, level=1):
        """
        Initialize the object with default values, unless values are specified.
        """
        self.key = key
        self.type = itype
        self.level = level

#------------------------------------------------------------------------
#
# BaseDoc
#
#------------------------------------------------------------------------
class BaseDoc:
    """
    Base class for document generators. Different output formats,
    such as OpenOffice, AbiWord, and LaTeX are derived from this base
    class, providing a common interface to all document generators.
    """
    def __init__(self, styles, paper_style, template):
        """
        Creates a BaseDoc instance, which provides a document generation
        interface. This class should never be instantiated directly, but
        only through a derived class.

        @param styles: StyleSheet containing the styles used.
        @param paper_style: PaperStyle instance containing information about
            the paper. If set to None, then the document is not a page
            oriented document (e.g. HTML)
        @param template: Format template for document generators that are
            not page oriented.
        """
        self.template = template
        self.paper = paper_style
        self._style_sheet = styles
        self._creator = ""
        self.print_req = 0
        self.init_called = False

    def init(self):
        self.init_called = True
        
    def print_requested(self):
        self.print_req = 1

    def set_creator(self, name):
        "Sets the owner name"
        self._creator = name
        
    def get_creator(self):
        "Returns the owner name"
        return self._creator
        
    def get_style_sheet(self):
        """
        Returns the StyleSheet of the document.
        """
        return StyleSheet(self._style_sheet)
    
    def set_style_sheet(self, style_sheet):
        """
        Sets the StyleSheet of the document.

        @param style_sheet: The new style sheet for the document
        @type  style_sheet: StyleSheet
        """
        self._style_sheet = StyleSheet(style_sheet)

    def open(self, filename):
        """
        Opens the document.

        @param filename: path name of the file to create
        """
        raise NotImplementedError

    def close(self):
        "Closes the document"
        raise NotImplementedError

#------------------------------------------------------------------------
#
# TextDoc
#
#------------------------------------------------------------------------
class TextDoc:
    """
    Abstract Interface for text document generators. Output formats for
    text reports must implment this interface to be used by the report 
    system.
    """    
    def page_break(self):
        "Forces a page break, creating a new page"
        raise NotImplementedError

    def start_bold(self):
        raise NotImplementedError

    def end_bold(self):
        raise NotImplementedError

    def start_superscript(self):
        raise NotImplementedError

    def end_superscript(self):
        raise NotImplementedError

    def start_paragraph(self, style_name, leader=None):
        """
        Starts a new paragraph, using the specified style name.

        @param style_name: name of the ParagraphStyle to use for the
            paragraph.
        @param leader: Leading text for a paragraph. Typically used
            for numbering.
        """
        raise NotImplementedError

    def end_paragraph(self):
        "Ends the current parsgraph"
        raise NotImplementedError

    def start_table(self, name, style_name):
        """
        Starts a new table.

        @param name: Unique name of the table.
        @param style_name: TableStyle to use for the new table
        """
        raise NotImplementedError

    def end_table(self):
        "Ends the current table"
        raise NotImplementedError

    def start_row(self):
        "Starts a new row on the current table"
        raise NotImplementedError

    def end_row(self):
        "Ends the current row on the current table"
        raise NotImplementedError

    def start_cell(self, style_name, span=1):
        """
        Starts a new table cell, using the paragraph style specified.

        @param style_name: TableCellStyle to use for the cell
        @param span: number of columns to span
        """
        raise NotImplementedError

    def end_cell(self):
        "Ends the current table cell"
        raise NotImplementedError

    def write_note(self, text, format, style_name):
        """
        Writes the note's text and take care of paragraphs, 
        depending on the format. 

        @param text: text to write.
        @param format: format to use for writing. True for flowed text, 
            1 for preformatted text.
        """
        raise NotImplementedError

    def write_text(self, text, mark=None):
        """
        Writes the text in the current paragraph. Should only be used after a
        start_paragraph and before an end_paragraph.

        @param text: text to write.
        @param mark:  IndexMark to use for indexing (if supported)
        """
        raise NotImplementedError
    
    def add_media_object(self, name, align, w_cm, h_cm):
        """
        Adds a photo of the specified width (in centimeters)

        @param name: filename of the image to add
        @param align: alignment of the image. Valid values are 'left',
            'right', 'center', and 'single'
        @param w_cm: width in centimeters
        @param h_cm: height in centimeters
        """
        raise NotImplementedError

#------------------------------------------------------------------------
#
# DrawDoc
#
#------------------------------------------------------------------------
class DrawDoc:
    """
    Abstract Interface for graphical document generators. Output formats
    for graphical reports must implment this interface to be used by the
    report system.
    """

    def start_page(self):
        raise NotImplementedError

    def end_page(self):
        raise NotImplementedError

    def get_usable_width(self):
        """
        Returns the width of the text area in centimeters. The value is
        the page width less the margins.
        """
        width = self.paper.get_size().get_width()
        right = self.paper.get_right_margin()
        left = self.paper.get_left_margin()
        return width - (right + left)

    def get_usable_height(self):
        """
        Returns the height of the text area in centimeters. The value is
        the page height less the margins.
        """
        height = self.paper.get_size().get_height()
        top = self.paper.get_top_margin()
        bottom = self.paper.get_bottom_margin()
        return height - (top + bottom)

    def string_width(self, fontstyle, text):
        "Determine the width need for text in given font"
        return FontScale.string_width(fontstyle, text)

    def draw_path(self, style, path):
        raise NotImplementedError
    
    def draw_box(self, style, text, x, y, w, h):
        raise NotImplementedError

    def draw_text(self, style, text, x1, y1):
        raise NotImplementedError

    def center_text(self, style, text, x1, y1):
        raise NotImplementedError

    def rotate_text(self, style, text, x, y, angle):
        raise NotImplementedError
    
    def draw_line(self, style, x1, y1, x2, y2):
        raise NotImplementedError

