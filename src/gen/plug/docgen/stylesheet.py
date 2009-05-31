#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Gary Burton
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

# $Id: basedoc.py 12591 2009-05-29 22:25:44Z bmcage $

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
import const
from gen.plug.utils import gformat, gfloat
from paragraphstyle import ParagraphStyle
from fontstyle import FontStyle
from tablestyle import TableStyle, TableCellStyle
from graphicstyle import GraphicsStyle

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".stylesheet")

#-------------------------------------------------------------------------
#
# SAX interface
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser, handler, SAXParseException
except ImportError:
    from _xmlplus.sax import make_parser, handler, SAXParseException

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
# StyleSheetList
#
#------------------------------------------------------------------------
class StyleSheetList(object):
    """
    Interface into the user's defined style sheets. Each StyleSheetList
    has a predefined default style specified by the report. Additional
    styles are loaded from a specified XML file if it exists.
    """
    
    def __init__(self, filename, defstyle):
        """
        Create a new StyleSheetList from the specified default style and
        any other styles that may be defined in the specified file.

        file - XML file that contains style definitions
        defstyle - default style
        """
        defstyle.set_name('default')
        self.map = { "default" : defstyle }
        self.file = os.path.join(const.HOME_DIR, filename)
        self.parse()

    def delete_style_sheet(self, name):
        """
        Remove a style from the list. Since each style must have a
        unique name, the name is used to delete the stylesheet.

        name - Name of the style to delete
        """
        del self.map[name]

    def get_style_sheet_map(self):
        """
        Return the map of names to styles.
        """
        return self.map

    def get_style_sheet(self, name):
        """
        Return the StyleSheet associated with the name

        name - name associated with the desired StyleSheet.
        """
        return self.map[name]

    def get_style_names(self):
        "Return a list of all the style names in the StyleSheetList"
        return self.map.keys()

    def set_style_sheet(self, name, style):
        """
        Add or replaces a StyleSheet in the StyleSheetList. The
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
        
        for name, sheet in self.map.iteritems():
            if name == "default":
                continue
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
                xml_file.write('rmargin="%s" ' % gformat(rmargin))
                xml_file.write('lmargin="%s" ' % gformat(lmargin))
                xml_file.write('first="%s" ' % gformat(findent))
                xml_file.write('tmargin="%s" ' % gformat(tmargin))
                xml_file.write('bmargin="%s" ' % gformat(bmargin))
                xml_file.write('pad="%s" ' % gformat(padding))
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
class StyleSheet(object):
    """
    A collection of named paragraph styles.
    """
    
    def __init__(self, obj=None):
        """
        Create a new empty StyleSheet.

        @param obj: if not None, creates the StyleSheet from the values in
            obj, instead of creating an empty StyleSheet
        """
        self.para_styles = {}
        self.draw_styles = {}
        self.table_styles = {}
        self.cell_styles = {}
        self.name = ""
        if obj is not None:
            for style_name, style in obj.para_styles.iteritems():
                self.para_styles[style_name] = ParagraphStyle(style)
            for style_name, style in obj.draw_styles.iteritems():
                self.draw_styles[style_name] = GraphicsStyle(style)
            for style_name, style in obj.table_styles.iteritems():
                self.table_styles[style_name] = TableStyle(style)
            for style_name, style in obj.cell_styles.iteritems():
                self.cell_styles[style_name] = TableCellStyle(style)

    def set_name(self, name):
        """
        Set the name of the StyleSheet
        
        @param name: The name to be given to the StyleSheet
        """
        self.name = name

    def get_name(self):
        """
        Return the name of the StyleSheet
        """
        return self.name

    def clear(self):
        "Remove all styles from the StyleSheet"
        self.para_styles = {}
        self.draw_styles = {}
        self.table_styles = {}
        self.cell_styles = {}
        
    def is_empty(self):
        "Checks if any styles are defined"
        style_count = len(self.para_styles)  + \
                      len(self.draw_styles)  + \
                      len(self.table_styles) + \
                      len(self.cell_styles)
        if style_count > 0:
            return False
        else:
            return True      

    def add_paragraph_style(self, name, style):
        """
        Add a paragraph style to the style sheet.

        @param name: The name of the ParagraphStyle
        @param style: ParagraphStyle instance to be added.
        """
        self.para_styles[name] = ParagraphStyle(style)
        
    def get_paragraph_style(self, name):
        """
        Return the ParagraphStyle associated with the name

        @param name: name of the ParagraphStyle that is wanted
        """
        return ParagraphStyle(self.para_styles[name])

    def get_paragraph_style_names(self):
        "Return the the list of paragraph names in the StyleSheet"
        return self.para_styles.keys()

    def add_draw_style(self, name, style):
        """
        Add a draw style to the style sheet.

        @param name: The name of the GraphicsStyle
        @param style: GraphicsStyle instance to be added.
        """
        self.draw_styles[name] = GraphicsStyle(style)
        
    def get_draw_style(self, name):
        """
        Return the GraphicsStyle associated with the name

        @param name: name of the GraphicsStyle that is wanted
        """
        return GraphicsStyle(self.draw_styles[name])

    def get_draw_style_names(self):
        "Return the the list of draw style names in the StyleSheet"
        return self.draw_styles.keys()
    
    def add_table_style(self, name, style):
        """
        Add a table style to the style sheet.

        @param name: The name of the TableStyle
        @param style: TableStyle instance to be added.
        """
        self.table_styles[name] = TableStyle(style)
        
    def get_table_style(self, name):
        """
        Return the TableStyle associated with the name

        @param name: name of the TableStyle that is wanted
        """
        return TableStyle(self.table_styles[name])

    def get_table_style_names(self):
        "Return the the list of table style names in the StyleSheet"
        return self.table_styles.keys()
    
    def add_cell_style(self, name, style):
        """
        Add a cell style to the style sheet.

        @param name: The name of the TableCellStyle
        @param style: TableCellStyle instance to be added.
        """
        self.cell_styles[name] = TableCellStyle(style)
        
    def get_cell_style(self, name):
        """
        Return the TableCellStyle associated with the name

        @param name: name of the TableCellStyle that is wanted
        """
        return TableCellStyle(self.cell_styles[name])

    def get_cell_style_names(self):
        "Return the the list of cell style names in the StyleSheet"
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
        Create a SheetParser class that populates the passed StyleSheetList
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
            self.p.set_right_margin(gfloat(attrs['rmargin']))
            self.p.set_right_margin(gfloat(attrs['rmargin']))
            self.p.set_left_margin(gfloat(attrs['lmargin']))
            self.p.set_first_indent(gfloat(attrs['first']))
            try:
                # This is needed to read older style files
                # lacking tmargin and bmargin
                self.p.set_top_margin(gfloat(attrs['tmargin']))
                self.p.set_bottom_margin(gfloat(attrs['bmargin']))
            except KeyError:
                pass
            self.p.set_padding(gfloat(attrs['pad']))
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
