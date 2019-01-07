#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Zsolt Foldvari
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Brian Matherly
# Copyright (C) 2010       Peter Landgren
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011-2017  Paul Franklin
# Copyright (C) 2012       Craig Anderson
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Report output generator based on Cairo.
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from math import radians
import re

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug.docgen import (BaseDoc, TextDoc, DrawDoc, ParagraphStyle,
                        TableCellStyle, SOLID, FONT_SANS_SERIF, FONT_SERIF,
                        FONT_MONOSPACE, PARA_ALIGN_CENTER, PARA_ALIGN_LEFT)
from gramps.gen.plug.report import utils
from gramps.gen.errors import PluginError
from gramps.gen.plug.docbackend import CairoBackend
from gramps.gen.utils.image import resize_to_buffer
from gramps.gui.utils import SystemFonts

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".libcairodoc")

#-------------------------------------------------------------------------
#
# Pango modules
#
#-------------------------------------------------------------------------
from gi.repository import Pango, PangoCairo

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

# each element draws some extra information useful for debugging
DEBUG = False

#------------------------------------------------------------------------
#
# Font selection
#
#------------------------------------------------------------------------

_TTF_FREEFONT = {
    FONT_SERIF: 'FreeSerif',
    FONT_SANS_SERIF: 'FreeSans',
    FONT_MONOSPACE: 'FreeMono',
}

_MS_TTFONT = {
    FONT_SERIF: 'Times New Roman',
    FONT_SANS_SERIF: 'Arial',
    FONT_MONOSPACE: 'Courier New',
}

_GNOME_FONT = {
    FONT_SERIF: 'Serif',
    FONT_SANS_SERIF: 'Sans',
    FONT_MONOSPACE: 'Monospace',
}

font_families = _GNOME_FONT

# FIXME debug logging does not work here.
def set_font_families():
    """Set the used font families depending on availability.
    """
    global font_families

    fonts = SystemFonts()
    family_names = fonts.get_system_fonts()

    fam = [f for f in _TTF_FREEFONT.values() if f in family_names]
    if len(fam) == len(_TTF_FREEFONT):
        font_families = _TTF_FREEFONT
        log.debug('Using FreeFonts: %s' % font_families)
        return

    fam = [f for f in _MS_TTFONT.values() if f in family_names]
    if len(fam) == len(_MS_TTFONT):
        font_families = _MS_TTFONT
        log.debug('Using MS TrueType fonts: %s' % font_families)
        return

    fam = [f for f in _GNOME_FONT.values() if f in family_names]
    if len(fam) == len(_GNOME_FONT):
        font_families = _GNOME_FONT
        log.debug('Using Gnome fonts: %s' % font_families)
        return

    log.debug('No fonts found.')

set_font_families()

#------------------------------------------------------------------------
#
# Converter functions
#
#------------------------------------------------------------------------

def fontstyle_to_fontdescription(font_style):
    """Convert a FontStyle instance to a Pango.FontDescription one.

    Font color and underline are not implemented in Pango.FontDescription,
    and have to be set with Pango.Layout.set_attributes(attrlist) method.

    """
    if font_style.get_bold():
        f_weight = Pango.Weight.BOLD
    else:
        f_weight = Pango.Weight.NORMAL

    if font_style.get_italic():
        f_style = Pango.Style.ITALIC
    else:
        f_style = Pango.Style.NORMAL

    font_description = Pango.FontDescription(font_families[font_style.face])
    font_description.set_size(int(round(font_style.get_size() * Pango.SCALE)))
    font_description.set_weight(f_weight)
    font_description.set_style(f_style)

    return font_description

def tabstops_to_tabarray(tab_stops, dpi):
    """Convert a list of tabs given in cm to a Pango.TabArray.
    """
    tab_array = Pango.TabArray.new(initial_size=len(tab_stops),
                                            positions_in_pixels=False)

    for index in range(len(tab_stops)):
        location = tab_stops[index] * dpi * Pango.SCALE / 2.54
        tab_array.set_tab(index, Pango.TabAlign.LEFT, int(location))

    return tab_array

def raw_length(s):
    """
    Return the length of the raw string after all pango markup has been removed.
    """
    s = re.sub('<.*?>', '', s)
    s = s.replace('&amp;', '&')
    s = s.replace('&lt;', '<')
    s = s.replace('&gt;', '>')
    s = s.replace('&quot;', '"')
    s = s.replace('&apos;', "'")
    return len(s)

###------------------------------------------------------------------------
###
### Table row style
###
###------------------------------------------------------------------------

##class RowStyle(list):
    ##"""Specifies the format of a table row.

    ##RowStyle extents the available styles in

    ##The RowStyle contains the width of each column as a percentage of the
    ##width of the full row. Note! The width of the row is not known until
    ##divide() or draw() method is called.

    ##"""
    ##def __init__(self):
        ##self.columns = []

    ##def set_columns(self, columns):
        ##"""Set the number of columns.

        ##@param columns: number of columns that should be used.
        ##@param type: int

        ##"""
        ##self.columns = columns

    ##def get_columns(self):
        ##"""Return the number of columns.
        ##"""
        ##return self.columns

    ##def set_column_widths(self, clist):
        ##"""Set the width of all the columns at once.

        ##@param clist: list of width of columns in % of the full row.
        ##@param tyle: list

        ##"""
        ##self.columns = len(clist)
        ##for i in range(self.columns):
            ##self.colwid[i] = clist[i]

    ##def set_column_width(self, index, width):
        ##"""
        ##Set the width of a specified column to the specified width.

        ##@param index: column being set (index starts at 0)
        ##@param width: percentage of the table width assigned to the column
        ##"""
        ##self.colwid[index] = width

    ##def get_column_width(self, index):
        ##"""
        ##Return the column width of the specified column as a percentage of
        ##the entire table width.

        ##@param index: column to return (index starts at 0)
        ##"""
        ##return self.colwid[index]

class FrameStyle:
    """Define the style properties of a Frame.

    - width: Width of the frame in cm.
    - height: Height of the frame in cm.
    - align: Horizontal position to entire page.
             Available values: 'left','center', 'right'.
    - spacing: Tuple of spacing around the frame in cm. Order of values:
               (left, right, top, bottom).

    """
    def __init__(self, width=0, height=0, align='left', spacing=(0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.align = align
        self.spacing = spacing

#------------------------------------------------------------------------
#
# Document element classes
#
#------------------------------------------------------------------------

class GtkDocBaseElement:
    """Base of all document elements.

    Support document element structuring and can render itself onto
    a Cairo surface.

    There are two categories of methods:
      1. hierarchy building methods (add_child, get_children, set_parent,
         get_parent);
      2. rendering methods (divide, draw).

    The hierarchy building methods generally don't have to be overridden in
    the subclass, while the rendering methods (divide, draw) must be
    implemented in the subclasses.

    """
    _type = 'BASE'
    _allowed_children = []

    def __init__(self, style=None):
        self._parent = None
        self._children = []
        self._style = style

    def get_type(self):
        """Get the type of this element.
        """
        return self._type

    def set_parent(self, parent):
        """Set the parent element of this element.
        """
        self._parent = parent

    def get_parent(self):
        """Get the parent element of this element.
        """
        return self._parent

    def add_child(self, element):
        """Add a child element.

        Returns False if the child cannot be added (e.g. not an allowed type),
        or True otherwise.

        """
        # check if it is an allowed child for this type
        if element.get_type() not in self._allowed_children:
            log.debug("%r is not an allowed child for %r" %
                      (element.__class__, self.__class__))
            return False

        # append the child and set its parent
        self._children.append(element)
        element.set_parent(self)
        return True

    def get_children(self):
        """Get the list of children of this element.
        """
        return self._children

    def get_marks(self):
        """Get the list of index marks for this element.
        """
        marks = []
        for child in self._children:
            marks.extend(child.get_marks())
        return marks

    def divide(self, layout, width, height, dpi_x, dpi_y):
        """Divide the element into two depending on available space.

        @param layout: pango layout to write on
        @param type: Pango.Layout
        @param width: width of available space for this element
        @param type: device points
        @param height: height of available space for this element
        @param type: device points
        @param dpi_x: the horizontal resolution
        @param type: dots per inch
        @param dpi_y: the vertical resolution
        @param type: dots per inch

        @return: the divided element, and the height of the first part
        @rtype: (GtkDocXXX-1, GtkDocXXX-2), device points

        """
        raise NotImplementedError

    def draw(self, cairo_context, pango_layout, width, dpi_x, dpi_y):
        """Draw itself onto a cairo surface.

        @param cairo_context: context to draw on
        @param type: cairo.Context class
        @param pango_layout: pango layout to write on
        @param type: Pango.Layout class
        @param width: width of available space for this element
        @param type: device points
        @param dpi_x: the horizontal resolution
        @param type: dots per inch
        @param dpi_y: the vertical resolution
        @param type: dots per inch

        @return: height of the element
        @rtype: device points

        """
        raise NotImplementedError

class GtkDocDocument(GtkDocBaseElement):
    """The whole document or a page.
    """
    _type = 'DOCUMENT'
    _allowed_children = ['PARAGRAPH', 'PAGEBREAK', 'TABLE', 'IMAGE', 'FRAME',
                         'TOC', 'INDEX']

    def draw(self, cairo_context, pango_layout, width, dpi_x, dpi_y):

        x = y = elem_height = 0

        for elem in self._children:
            cairo_context.translate(x, elem_height)
            elem_height = elem.draw(cairo_context, pango_layout,
                                    width, dpi_x, dpi_y)
            y += elem_height

        return y

    def has_toc(self):
        for elem in self._children:
            if elem.get_type() == 'TOC':
                return True
        return False

    def has_index(self):
        for elem in self._children:
            if elem.get_type() == 'INDEX':
                return True
        return False

class GtkDocPagebreak(GtkDocBaseElement):
    """Implement a page break.
    """
    _type = 'PAGEBREAK'
    _allowed_children = []

    def divide(self, layout, width, height, dpi_x, dpi_y):
        return (None, None), 0

class GtkDocTableOfContents(GtkDocBaseElement):
    """Implement a table of contents.
    """
    _type = 'TOC'
    _allowed_children = []

    def divide(self, layout, width, height, dpi_x, dpi_y):
        return (self, None), 0

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        return 0

class GtkDocAlphabeticalIndex(GtkDocBaseElement):
    """Implement an alphabetical index.
    """
    _type = 'INDEX'
    _allowed_children = []

    def divide(self, layout, width, height, dpi_x, dpi_y):
        return (self, None), 0

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        return 0

class GtkDocParagraph(GtkDocBaseElement):
    """Paragraph.
    """
    _type = 'PARAGRAPH'
    _allowed_children = []

    # line spacing is not defined in ParagraphStyle
    spacingfractionfont = 0.2

    def __init__(self, style, leader=None):
        GtkDocBaseElement.__init__(self, style)

        if leader:
            self._text = leader + '\t'
            # FIXME append new tab to the existing tab list
            self._style.set_tabs([-1 * self._style.get_first_indent()])
        else:
            self._text = ''

        self._plaintext = None
        self._attrlist = None

        self._marklist = []

    def add_text(self, text):
        if self._plaintext is not None:
            raise PluginError('CairoDoc: text is already parsed.'
                            ' You cannot add text anymore')
        self._text = self._text + text

    def add_mark(self, mark):
        """
        Add an index mark to this paragraph
        """
        self._marklist.append((mark, raw_length(self._text)))

    def get_marks(self):
        """
        Return a list of index marks for this paragraph
        """
        return [elem[0] for elem in self._marklist]

    def __set_marklist(self, marklist):
        """
        Internal method to allow for splitting of paragraphs
        """
        self._marklist = marklist

    def __set_plaintext(self, plaintext):
        """
        Internal method to allow for splitting of paragraphs
        """
        if not isinstance(plaintext, str):
            self._plaintext = plaintext.decode('utf-8')
        else:
            self._plaintext = plaintext

    def __set_attrlist(self, attrlist):
        """
        Internal method to allow for splitting of paragraphs
        """
        self._attrlist = attrlist

    def __parse_text(self):
        """
        Parse the markup text. This method will only do this if not
        done already
        """
        if self._plaintext is None:
            parse_ok, self._attrlist, self._plaintext, accel_char= \
                                Pango.parse_markup(self._text, -1, '\000')

    def divide(self, layout, width, height, dpi_x, dpi_y):
        self.__parse_text()

        l_margin = self._style.get_left_margin() * dpi_x / 2.54
        r_margin = self._style.get_right_margin() * dpi_x / 2.54
        t_margin = self._style.get_top_margin() * dpi_y / 2.54
        b_margin = self._style.get_bottom_margin() * dpi_y / 2.54
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54
        f_indent = self._style.get_first_indent() * dpi_x / 2.54

        # calculate real width available for text
        text_width = width - l_margin - 2 * h_padding - r_margin
        if f_indent < 0:
            text_width -= f_indent
        layout.set_width(int(text_width * Pango.SCALE))

        # set paragraph properties
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_indent(int(f_indent * Pango.SCALE))
        layout.set_tabs(tabstops_to_tabarray(self._style.get_tabs(), dpi_x))
        #
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.LEFT)
        elif align == 'right':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.RIGHT)
        elif align == 'center':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.CENTER)
        elif align == 'justify':
            #We have a problem, in pango, justify works only on full lines,
            # and we need an alignment for the partial lines. We don't know
            # for justify what alignment the user wants however. We assume
            # here LEFT ...
            layout.set_alignment(Pango.Alignment.LEFT)
            layout.set_justify(True)
        else:
            raise ValueError
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))
        #set line spacing based on font:
        spacing = font_style.get_size() * self.spacingfractionfont
        layout.set_spacing(int(round(spacing * Pango.SCALE)))

        text_height = height - t_margin - 2 * v_padding

        # calculate where to cut the paragraph
        layout.set_text(self._plaintext, -1)
        layout.set_attributes(self._attrlist)
        layout_width, layout_height = layout.get_pixel_size()
        line_count = layout.get_line_count()
        spacing = layout.get_spacing() / Pango.SCALE

        # if all paragraph fits we don't need to cut
        if layout_height - spacing <= text_height:
            paragraph_height = layout_height + spacing +t_margin + (2 * v_padding)
            if height - paragraph_height > b_margin:
                paragraph_height += b_margin
            return (self, None), paragraph_height

        # we need to cut paragraph:

        # 1. if paragraph part of a cell, we do not divide if only small part,
        # of paragraph can be shown, instead move to next page
        if  line_count < 4 and self._parent._type == 'CELL':
            return (None, self), 0

        lineiter = layout.get_iter()

        linenr = 0
        linerange = lineiter.get_line_yrange()
        # 2. if nothing fits, move to next page without split
        #  there is a spacing above and under the text
        if linerange[1] - linerange[0] + 2.*spacing \
                    > text_height * Pango.SCALE:
            return (None, self), 0

        # 3. split the paragraph
        startheight = linerange[0]
        endheight = linerange[1]
        splitline = -1
        if lineiter.at_last_line():
            #only one line of text that does not fit
            return (None, self), 0

        while not lineiter.at_last_line():
            #go to next line, see if all fits, if not split
            lineiter.next_line()
            linenr += 1
            linerange = lineiter.get_line_yrange()
            if linerange[1] - startheight  + 2.*spacing \
                        > text_height * Pango.SCALE:
                splitline = linenr
                break
            endheight = linerange[1]
        if splitline == -1:
            print('CairoDoc STRANGE ')
            return (None, self), 0
        #we split at splitline
        # get index of first character which doesn't fit on available height
        layout_line = layout.get_line(splitline)
        index = layout_line.start_index
        # and divide the text, first create the second part
        new_style = ParagraphStyle(self._style)
        new_style.set_top_margin(0)
        #we split a paragraph, text should begin in correct position: no indent
        #as if the paragraph just continues from normal text
        new_style.set_first_indent(0)
        new_paragraph = GtkDocParagraph(new_style)
        #index is in bytecode in the text..
        new_paragraph.__set_plaintext(self._plaintext.encode('utf-8')[index:])
        #now recalculate the attrilist:
        newattrlist = layout.get_attributes().copy()
        newattrlist.filter(self.filterattr, index)

##      GTK3 PROBLEM: get_iterator no longer available!!
##      REFERENCES:
##          http://www.gramps-project.org/bugs/view.php?id=6208
##          https://bugzilla.gnome.org/show_bug.cgi?id=646788
##          workaround: https://github.com/matasbbb/pitivit/commit/da815339e5ce3631b122a72158ba9ffcc9ee4372
##      OLD EASY CODE:
##        oldattrlist = newattrlist.get_iterator()
##        while oldattrlist.next():
##            vals = oldattrlist.get_attrs()
##            #print (vals)
##            for attr in vals:
##                newattr = attr.copy()
##                newattr.start_index -= index if newattr.start_index > index \
##                                                else 0
##                newattr.end_index -= index
##                newattrlist.insert(newattr)
##      ## START OF WORKAROUND
        oldtext = self._text
        pos = 0
        realpos = 0
        markstarts = []
        #index is in bytecode in the text.. !!
        while pos < index:
            if realpos >= len(oldtext):
                break
            char = oldtext[realpos]
            if char == '<' and oldtext[realpos+1] != '/':
                # a markup starts
                end = realpos + oldtext[realpos:].find('>') + 1
                markstarts += [oldtext[realpos:end]]
                realpos = end
            elif char == '<':
                #this is the closing tag, we did not stop yet, so remove tag!
                realpos = realpos + oldtext[realpos:].find('>') + 1
                markstarts.pop()
            else:
                pos += len(char.encode('utf-8'))
                realpos += 1
        #now construct the marked up text to use
        newtext = ''.join(markstarts)
        newtext += oldtext[realpos:]
        #have it parsed
        parse_ok, newattrlist, _plaintext, accel_char= \
                                Pango.parse_markup(newtext, -1, '\000')
##      ##END OF WORKAROUND
        new_paragraph.__set_attrlist(newattrlist)
        # then update the first one
        self.__set_plaintext(self._plaintext.encode('utf-8')[:index])
        self._style.set_bottom_margin(0)

        # split the list of index marks
        para1 = []
        para2 = []
        for mark, position in self._marklist:
            if position < index:
                para1.append((mark, position))
            else:
                para2.append((mark, position - index))
        self.__set_marklist(para1)
        new_paragraph.__set_marklist(para2)

        paragraph_height = endheight - startheight + spacing + t_margin + 2 * v_padding
        return (self, new_paragraph), paragraph_height

    def filterattr(self, attr, index):
        """callback to filter out attributes in the removed piece at beginning
        """
        if attr.start_index > index or \
                (attr.start_index < index and attr.end_index > index):
            return False
        return True

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        self.__parse_text()

        l_margin = self._style.get_left_margin() * dpi_x / 2.54
        r_margin = self._style.get_right_margin() * dpi_x / 2.54
        t_margin = self._style.get_top_margin() * dpi_y / 2.54
        b_margin = self._style.get_bottom_margin() * dpi_y / 2.54
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54
        f_indent = self._style.get_first_indent() * dpi_x / 2.54

        # calculate real width available for text
        text_width = width - l_margin - 2 * h_padding - r_margin
        if f_indent < 0:
            text_width -= f_indent
        layout.set_width(int(text_width * Pango.SCALE))

        # set paragraph properties
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_indent(int(f_indent * Pango.SCALE))
        layout.set_tabs(tabstops_to_tabarray(self._style.get_tabs(), dpi_x))
        #
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.LEFT)
        elif align == 'right':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.RIGHT)
        elif align == 'center':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.CENTER)
        elif align == 'justify':
            #We have a problem, in pango, justify works only on full lines,
            # and we need an alignment for the partial lines. We don't know
            # for justify what alignment the user wants however. We assume
            # here LEFT ...
            layout.set_alignment(Pango.Alignment.LEFT)
            layout.set_justify(True)
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))
        #set line spacing based on font:
        spacing = font_style.get_size() * self.spacingfractionfont
        layout.set_spacing(int(round(spacing * Pango.SCALE)))

        # layout the text
        layout.set_text(self._plaintext, -1)
        layout.set_attributes(self._attrlist)
        layout_width, layout_height = layout.get_pixel_size()

        # render the layout onto the cairo surface
        x = l_margin + h_padding
        if f_indent < 0:
            x += f_indent
        # 3/4 of the spacing is added above the text, 1/4 is added below
        cr.move_to(x, t_margin + v_padding + spacing * 0.75)
        cr.set_source_rgb(*utils.rgb_color(font_style.get_color()))
        PangoCairo.show_layout(cr, layout)

        # calculate the full paragraph height
        height = layout_height + spacing + t_margin + 2*v_padding + b_margin

        # draw the borders
        if self._style.get_top_border():
            cr.move_to(l_margin, t_margin)
            cr.rel_line_to(width - l_margin - r_margin, 0)
        if self._style.get_right_border():
            cr.move_to(width - r_margin, t_margin)
            cr.rel_line_to(0, height - t_margin - b_margin)
        if self._style.get_bottom_border():
            cr.move_to(l_margin, height - b_margin)
            cr.rel_line_to(width - l_margin - r_margin, 0)
        if self._style.get_left_border():
            cr.move_to(l_margin, t_margin)
            cr.line_to(0, height - t_margin - b_margin)

        cr.set_line_width(1)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(0, 0, width, height)
            cr.stroke()
            cr.set_source_rgb(0, 0, 1.0)
            cr.rectangle(l_margin, t_margin,
                         width-l_margin-r_margin, height-t_margin-b_margin)
            cr.stroke()

        return height

class GtkDocTable(GtkDocBaseElement):
    """Implement a table.
    """
    _type = 'TABLE'
    _allowed_children = ['ROW']

    def divide(self, layout, width, height, dpi_x, dpi_y):
        #calculate real table width
        table_width = width * self._style.get_width() / 100

        # calculate the height of each row
        table_height = 0
        row_index = 0
        while row_index < len(self._children):
            row = self._children[row_index]
            (r1, r2), row_height = row.divide(layout, table_width, height,
                                              dpi_x, dpi_y)
            if r2 is not None:
                #break the table in two parts
                break
            table_height += row_height
            row_index += 1
            height -= row_height

        # divide the table if any row did not fit
        new_table = None
        if row_index < len(self._children):
            new_table = GtkDocTable(self._style)
            #add the split row
            new_table.add_child(r2)
            list(map(new_table.add_child, self._children[row_index+1:]))
            del self._children[row_index+1:]

        return (self, new_table), table_height

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        #calculate real table width
        table_width = width * self._style.get_width() / 100
        # TODO is a table always left aligned??
        table_height = 0

        # draw all the rows
        for row in self._children:
            cr.save()
            cr.translate(0, table_height)
            row_height = row.draw(cr, layout, table_width, dpi_x, dpi_y)
            cr.restore()
            table_height += row_height

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(0, 0, table_width, table_height)
            cr.stroke()

        return table_height

class GtkDocTableRow(GtkDocBaseElement):
    """Implement a row in a table.
    """
    _type = 'ROW'
    _allowed_children = ['CELL']

    def divide(self, layout, width, height, dpi_x, dpi_y):
        # the highest cell gives the height of the row
        cell_heights = []
        dividedrow = False
        cell_width_iter = self._style.__iter__()
        new_row = GtkDocTableRow(self._style)
        for cell in self._children:
            cell_width = 0
            for i in range(cell.get_span()):
                cell_width += next(cell_width_iter)
            cell_width = cell_width * width / 100
            (c1, c2), cell_height = cell.divide(layout, cell_width, height,
                                                dpi_x, dpi_y)
            cell_heights.append(cell_height)
            if c2 is None:
                emptycell = GtkDocTableCell(c1._style, c1.get_span())
                new_row.add_child(emptycell)
            else:
                dividedrow = True
                new_row.add_child(c2)

        # save height [inch] of the row to be able to draw exact cell border
        row_height = max(cell_heights)
        self.height = row_height / dpi_y

        # return the new row if dividing was needed
        if dividedrow:
            if row_height == 0:
                for cell in self._children:
                    cell._style.set_top_border(False)
                    cell._style.set_left_border(False)
                    cell._style.set_right_border(False)
            return (self, new_row), row_height
        else:
            return (self, None), row_height

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        cr.save()

        # get the height of this row
        row_height = self.height * dpi_y

        # draw all the cells in the row
        cell_width_iter = self._style.__iter__()
        for cell in self._children:
            cell_width = 0
            for i in range(cell.get_span()):
                cell_width += next(cell_width_iter)
            cell_width = cell_width * width / 100
            cell.draw(cr, layout, cell_width, row_height, dpi_x, dpi_y)
            cr.translate(cell_width, 0)
        cr.restore()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(0, 0, 1.0)
            cr.rectangle(0, 0, width, row_height)
            cr.stroke()

        return row_height

class GtkDocTableCell(GtkDocBaseElement):
    """Implement a cell in a table row.
    """
    _type = 'CELL'
    _allowed_children = ['PARAGRAPH', 'IMAGE']

    def __init__(self, style, span=1):
        GtkDocBaseElement.__init__(self, style)
        self._span = span

    def get_span(self):
        return self._span

    def divide(self, layout, width, height, dpi_x, dpi_y):
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54

        # calculate real available width
        width -= 2 * h_padding
        available_height = height

        # calculate height of each child
        cell_height = 0
        new_cell = None
        e2 = None

        childnr = 0
        for child in self._children:
            if new_cell is None:
                (e1, e2), child_height = child.divide(layout, width,
                                                available_height, dpi_x, dpi_y)
                cell_height += child_height
                available_height -= child_height
                if e2 is not None:
                    #divide the cell
                    new_style = TableCellStyle(self._style)
                    if e1 is not None:
                        new_style.set_top_border(False)
                    new_cell = GtkDocTableCell(new_style, self._span)
                    new_cell.add_child(e2)
                    # then update this cell
                    self._style.set_bottom_border(False)
                if e1 is not None:
                    childnr += 1
            else:
                #cell has been divided
                new_cell.add_child(child)

        self._children = self._children[:childnr]
        # calculate real height
        if cell_height != 0:
            cell_height += 2 * v_padding

        # a cell can't be divided, return the height
        return (self, new_cell), cell_height

    def draw(self, cr, layout, width, cell_height, dpi_x, dpi_y):
        """Draw a cell.

        This draw method is a bit different from the others, as common
        cell height of all cells in a row is also given as parameter.
        This is needed to be able to draw proper vertical borders around
        each cell, i.e. the border should be as long as the highest cell
        in the given row.

        """
        h_padding = self._style.get_padding() * dpi_x / 2.54
        v_padding = self._style.get_padding() * dpi_y / 2.54

        # calculate real available width
        i_width = width - 2 * h_padding

        # draw children
        cr.save()
        cr.translate(h_padding, v_padding)
        for child in self._children:
            child_height = child.draw(cr, layout, i_width, dpi_x, dpi_y)
            cr.translate(0, child_height)
        cr.restore()

        # draw the borders
        if self._style.get_top_border():
            cr.move_to(0, 0)
            cr.rel_line_to(width , 0)
        if self._style.get_right_border():
            cr.move_to(width, 0)
            cr.rel_line_to(0, cell_height)
        if self._style.get_bottom_border():
            cr.move_to(0, cell_height)
            cr.rel_line_to(width, 0)
        if self._style.get_left_border():
            cr.move_to(0, 0)
            cr.line_to(0, cell_height)

        cr.set_line_width(1)
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(0, 1.0, 0)
            cr.rectangle(0, 0, width, cell_height)
            cr.stroke()

        return cell_height

class GtkDocPicture(GtkDocBaseElement):
    """Implement an image.
    """
    _type = 'IMAGE'
    _allowed_children = []

    def __init__(self, style, filename, width, height, crop=None):
        GtkDocBaseElement.__init__(self, style)
        self._filename = filename
        self._width = width
        self._height = height
        self._crop = crop

    def divide(self, layout, width, height, dpi_x, dpi_y):
        img_width = self._width * dpi_x / 2.54
        img_height = self._height * dpi_y / 2.54

        # image can't be divided, a new page must begin
        # if it can't fit on the current one
        if img_height <= height:
            return (self, None), img_height
        else:
            return (None, self), 0

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        from gi.repository import Gtk, Gdk
        img_width = self._width * dpi_x / 2.54
        img_height = self._height * dpi_y / 2.54

        if self._style == 'right':
            l_margin = width - img_width
        elif self._style == 'center':
            l_margin = (width - img_width) / 2.0
        else:
            l_margin = 0

        # load the image and get its extents
        pixbuf = resize_to_buffer(self._filename, [img_width, img_height],
                                  self._crop)
        pixbuf_width = pixbuf.get_width()
        pixbuf_height = pixbuf.get_height()

        # calculate the scale to fit image into the set extents
        scale = min(img_width / pixbuf_width, img_height / pixbuf_height)

        # draw the image
        cr.save()
        cr.translate(l_margin, 0)
        cr.scale(scale, scale)
        Gdk.cairo_set_source_pixbuf(cr, pixbuf,
                              (img_width / scale - pixbuf_width) / 2,
                              (img_height / scale - pixbuf_height) / 2)
        cr.rectangle(0 , 0, img_width / scale, img_height / scale)
        ##gcr.set_source_pixbuf(pixbuf,
                              ##(img_width - pixbuf_width) / 2,
                              ##(img_height - pixbuf_height) / 2)
        ##cr.rectangle(0 , 0, img_width, img_height)
        ##cr.scale(scale, scale)
        cr.fill()
        cr.restore()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(l_margin, 0, img_width, img_height)
            cr.stroke()

        return (img_height)

class GtkDocFrame(GtkDocBaseElement):
    """Implement a frame.
    """
    _type = 'FRAME'
    _allowed_children = ['LINE', 'POLYGON', 'BOX', 'TEXT']

    def divide(self, layout, width, height, dpi_x, dpi_y):
        frame_width = round(self._style.width * dpi_x / 2.54)
        frame_height = round(self._style.height * dpi_y / 2.54)
        t_margin = self._style.spacing[2] * dpi_y / 2.54
        b_margin = self._style.spacing[3] * dpi_y / 2.54

        # frame can't be divided, a new page must begin
        # if it can't fit on the current one
        if frame_height + t_margin + b_margin <= height:
            return (self, None), frame_height + t_margin + b_margin
        elif frame_height + t_margin <= height:
            return (self, None), height
        else:
            return (None, self), 0

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        frame_width = self._style.width * dpi_x / 2.54
        frame_height = self._style.height * dpi_y / 2.54
        l_margin = self._style.spacing[0] * dpi_x / 2.54
        r_margin = self._style.spacing[1] * dpi_x / 2.54
        t_margin = self._style.spacing[2] * dpi_y / 2.54
        b_margin = self._style.spacing[3] * dpi_y / 2.54

        if self._style.align == 'left':
            x_offset = l_margin
        elif self._style.align == 'right':
            x_offset = width - r_margin - frame_width
        elif self._style.align == 'center':
            x_offset = (width - frame_width) / 2.0
        else:
            raise ValueError

        # draw each element in the frame
        cr.save()
        cr.translate(x_offset, t_margin)
        cr.rectangle(0, 0, frame_width, frame_height)
        cr.clip()

        for elem in self._children:
            elem.draw(cr, layout, frame_width, dpi_x, dpi_y)

        cr.restore()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(x_offset, t_margin, frame_width, frame_height)
            cr.stroke()

        return frame_height + t_margin + b_margin

class GtkDocLine(GtkDocBaseElement):
    """Implement a line.
    """
    _type = 'LINE'
    _allowed_children = []

    def __init__(self, style, x1, y1, x2, y2):
        GtkDocBaseElement.__init__(self, style)
        self._start = (x1, y1)
        self._end = (x2, y2)

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        start = (self._start[0] * dpi_x / 2.54, self._start[1] * dpi_y / 2.54)
        end = (self._end[0] * dpi_x / 2.54, self._end[1] * dpi_y / 2.54)
        line_color = utils.rgb_color(self._style.get_color())

        cr.save()
        cr.set_source_rgb(*line_color)
        cr.set_line_width(self._style.get_line_width())
        # TODO line style
        line_style = self._style.get_line_style()
        if line_style != SOLID:
            cr.set_dash(self._style.get_dash_style(line_style), 0)
        cr.move_to(*start)
        cr.line_to(*end)
        cr.stroke()
        cr.restore()

        return 0

class GtkDocPolygon(GtkDocBaseElement):
    """Implement a line.
    """
    _type = 'POLYGON'
    _allowed_children = []

    def __init__(self, style, path):
        GtkDocBaseElement.__init__(self, style)
        self._path = path

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        path = [(x * dpi_x / 2.54, y * dpi_y / 2.54) for (x, y) in self._path]
        path_start = path.pop(0)
        path_stroke_color = utils.rgb_color(self._style.get_color())
        path_fill_color = utils.rgb_color(self._style.get_fill_color())

        cr.save()
        cr.move_to(*path_start)
        for (x, y) in path:
            cr.line_to(x, y)
        cr.close_path()
        cr.set_source_rgb(*path_fill_color)
        cr.fill_preserve()
        cr.set_source_rgb(*path_stroke_color)
        cr.set_line_width(self._style.get_line_width())
        # TODO line style
        line_style = self._style.get_line_style()
        if line_style != SOLID:
            cr.set_dash(self._style.get_dash_style(line_style), 0)
        cr.stroke()
        cr.restore()

        return 0

class GtkDocBox(GtkDocBaseElement):
    """Implement a box with optional shadow around it.
    """
    _type = 'BOX'
    _allowed_children = []

    def __init__(self, style, x, y, width, height):
        GtkDocBaseElement.__init__(self, style)
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        box_x = self._x * dpi_x / 2.54
        box_y = self._y * dpi_y / 2.54
        box_width = self._width * dpi_x / 2.54
        box_height = self._height * dpi_y / 2.54

        box_stroke_color = utils.rgb_color((0, 0, 0))
        box_fill_color = utils.rgb_color(self._style.get_fill_color())
        shadow_color = utils.rgb_color((192, 192, 192))

        cr.save()

        cr.set_line_width(self._style.get_line_width())
        # TODO line style
        line_style = self._style.get_line_style()
        if line_style != SOLID:
            cr.set_dash(self._style.get_dash_style(line_style), 0)

        if self._style.get_shadow():
            shadow_x = box_x + self._style.get_shadow_space() * dpi_x / 2.54
            shadow_y = box_y + self._style.get_shadow_space() * dpi_y / 2.54

            cr.set_source_rgb(*shadow_color)
            cr.rectangle(shadow_x, shadow_y, box_width, box_height)
            cr.fill()

        cr.rectangle(box_x, box_y, box_width, box_height)
        cr.set_source_rgb(*box_fill_color)
        cr.fill_preserve()
        cr.set_source_rgb(*box_stroke_color)
        cr.stroke()

        cr.restore()

        return 0

class GtkDocText(GtkDocBaseElement):
    """Implement a text on graphical reports.
    """
    _type = 'TEXT'
    _allowed_children = []

    # line spacing is not defined in ParagraphStyle
    spacingfractionfont = 0.2

    def __init__(self, style, vertical_alignment, text, x, y,
                 angle=0, mark=None):
        GtkDocBaseElement.__init__(self, style)
        self._align_y = vertical_alignment
        self._text = text
        self._x = x
        self._y = y
        self._angle = angle
        self._marklist = []
        if mark:
            self._marklist = [mark]

    def draw(self, cr, layout, width, dpi_x, dpi_y):
        text_x = self._x * dpi_x / 2.54
        text_y = self._y * dpi_y / 2.54

        # turn off text wrapping
        layout.set_width(-1)

        # set paragraph properties
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.LEFT)
        elif align == 'right':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.RIGHT)
        elif align == 'center':
            layout.set_justify(False)
            layout.set_alignment(Pango.Alignment.CENTER)
        elif align == 'justify':
            #We have a problem, in pango, justify works only on full lines,
            # and we need an alignment for the partial lines. We don't know
            # for justify what alignment the user wants however. We assume
            # here CENTER ...
            layout.set_alignment(Pango.Alignment.CENTER)
            layout.set_justify(True)
        else:
            raise ValueError
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))
        #set line spacing based on font:
        spacing = font_style.get_size() * self.spacingfractionfont
        layout.set_spacing(int(round(spacing * Pango.SCALE)))

        # layout the text
        layout.set_markup(self._text)
        layout_width, layout_height = layout.get_pixel_size()

        # calculate horizontal and vertical alignment shift
        if align == 'left':
            align_x = 0
        elif align == 'right':
            align_x = - layout_width
        elif align == 'center' or align == 'justify':
            align_x = - layout_width / 2
        else:
            raise ValueError

        if self._align_y == 'top':
            align_y = 0
        elif self._align_y == 'center':
            align_y = - layout_height / 2
        elif self._align_y == 'bottom':
            align_y = - layout_height
        else:
            raise ValueError

        # render the layout onto the cairo surface
        cr.save()
        cr.translate(text_x, text_y)
        cr.rotate(radians(self._angle))
        cr.move_to(align_x, align_y)
        cr.set_source_rgb(*utils.rgb_color(font_style.get_color()))
        PangoCairo.show_layout(cr, layout)
        cr.restore()

        return layout_height

    def get_marks(self):
        """
        Return the index mark for this text
        """
        return self._marklist

#------------------------------------------------------------------------
#
# CairoDoc class
#
#------------------------------------------------------------------------
class CairoDoc(BaseDoc, TextDoc, DrawDoc):
    """Act as an abstract document that can render onto a cairo context.

    Maintains an abstract model of the document. The root of this abstract
    document is self._doc. The model is build via the subclassed BaseDoc, and
    the implemented TextDoc, DrawDoc interface methods.

    It can render the model onto cairo context pages, according to the received
    page style.

    """

    # BaseDoc implementation
    EXT = 'pdf'

    def open(self, filename):
        fe = filename.split('.')
        if len(fe) == 1:
            filename = filename + '.' + self.EXT
        elif fe[-1] != self.EXT:
            # NOTE: the warning will be bogus
            # if the EXT isn't properly overridden by derived class
            log.warning(_(
"""Mismatch between selected extension %(ext)s and actual format.
 Writing to %(filename)s in format %(impliedext)s.""") %
                {'ext' : fe[-1],
                 'filename' : filename,
                 'impliedext' : self.EXT} )
        self._backend = CairoBackend(filename)
        self._doc = GtkDocDocument()
        self._active_element = self._doc
        self._pages = []
        self._elements_to_paginate = []
        self._links_error = False

    def close(self):
        self.run()

    # TextDoc implementation

    def page_break(self):
        self._active_element.add_child(GtkDocPagebreak())

    def start_bold(self):
        self.__write_text('<b>', markup=True)

    def end_bold(self):
        self.__write_text('</b>', markup=True)

    def start_superscript(self):
        self.__write_text('<small><sup>', markup=True)

    def end_superscript(self):
        self.__write_text('</sup></small>', markup=True)

    def start_paragraph(self, style_name, leader=None):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_paragraph_style(style_name)

        new_paragraph = GtkDocParagraph(style, leader)
        self._active_element.add_child(new_paragraph)
        self._active_element = new_paragraph

    def end_paragraph(self):
        self._active_element = self._active_element.get_parent()

    def start_table(self, name, style_name):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_table_style(style_name)

        new_table = GtkDocTable(style)
        self._active_element.add_child(new_table)
        self._active_element = new_table

        # we need to remember the column width list from the table style.
        # this is an ugly hack, but got no better idea.
        self._active_row_style = list(map(style.get_column_width,
                                        list(range(style.get_columns()))))
        if self.get_rtl_doc():
            self._active_row_style.reverse()

    def end_table(self):
        self._active_element = self._active_element.get_parent()

    def start_row(self):
        new_row = GtkDocTableRow(self._active_row_style)
        self._active_element.add_child(new_row)
        self._active_element = new_row

    def end_row(self):
        if self.get_rtl_doc():
            self._active_element._children.reverse()
        self._active_element = self._active_element.get_parent()

    def start_cell(self, style_name, span=1):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_cell_style(style_name)

        new_cell = GtkDocTableCell(style, span)
        self._active_element.add_child(new_cell)
        self._active_element = new_cell

    def end_cell(self):
        self._active_element = self._active_element.get_parent()

    def write_styled_note(self, styledtext, format, style_name,
                          contains_html=False, links=False):
        """
        Convenience function to write a styledtext to the cairo doc.
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        contains_html: bool, the backend should not check if html is present.
            If contains_html=True, then the textdoc is free to handle that in
            some way. Eg, a textdoc could remove all tags, or could make sure
            a link is clickable. CairoDoc does nothing different for html notes
        links:  bool, true if URLs should be made clickable
        """
        text = str(styledtext)

        s_tags = styledtext.get_tags()
        #FIXME: following split should be regex to match \n\s*\n instead?
        markuptext = self._backend.add_markup_from_styled(text, s_tags,
                                                          split='\n\n')

        if format == 1:
            #preformatted, retain whitespace. Cairo retains \n automatically,
            #so use \n\n for paragraph detection
            #FIXME: following split should be regex to match \n\s*\n instead?
            for line in markuptext.split('\n\n'):
                self.start_paragraph(style_name)
                self.__write_text(line, markup=True, links=links)
                self.end_paragraph()
        elif format == 0:
            #flowed
            #FIXME: following split should be regex to match \n\s*\n instead?
            for line in markuptext.split('\n\n'):
                self.start_paragraph(style_name)
                #flowed, normal whitespace goes away, but we keep linebreak
                lines = line.split('\n')
                newlines = []
                for singleline in lines:
                    newlines.append(' '.join(singleline.split()))
                self.__write_text('\n'.join(newlines), markup=True, links=links)
                self.end_paragraph()

    def __markup(self, text, markup=None):
        if not markup:
            # We need to escape the text here for later Pango.Layout.set_markup
            # calls. This way we save the markup created by the report
            # The markup in the note editor is not in the text so is not
            # considered. It must be added by pango too
            text = self._backend.ESCAPE_FUNC()(text)
        return text

    def __write_text(self, text, mark=None, markup=False, links=False):
        """
        @param text: text to write.
        @param mark:  IndexMark to use for indexing
        @param markup: True if text already contains markup info.
                       Then text will no longer be escaped
        @param links:  True if URLs should be made clickable
        """
        if links == True:
            import cairo

            if cairo.cairo_version() < 11210 and self._links_error == False:
                # Cairo v1.12 is suppose to be the first version
                # that supports clickable links
                print("""
WARNING: This version of cairo (%s) does NOT support clickable links.
The first version that is suppose to is v1.12.  See the roadmap:

    http://www.cairographics.org/roadmap/

The work around is to save to another format that supports clickable
links (like ODF) and write PDF from that format.
                """ % cairo.version)
                self._links_error = True

        text = self.__markup(text, markup)

        if mark:
            self._active_element.add_mark(mark)

        self._active_element.add_text(text)

    def write_text(self, text, mark=None, links=False):
        """Write a normal piece of text according to the
           present style
        @param text: text to write.
        @param mark:  IndexMark to use for indexing
        @param links:  True if URLs should be made clickable
        """
        self.__write_text(text, mark, links=links)

    def write_markup(self, text, s_tags, mark=None):
        """
        Writes the text in the current paragraph.  Should only be used after a
        start_paragraph and before an end_paragraph.

        @param text: text to write. The text is assumed to be _not_ escaped
        @param s_tags:  assumed to be list of styledtexttags to apply to the
                        text
        @param mark:  IndexMark to use for indexing
        """
        markuptext = self._backend.add_markup_from_styled(text, s_tags)
        self.__write_text(markuptext, mark=mark, markup=True)

    def add_media(self, name, pos, x_cm, y_cm, alt='',
                         style_name=None, crop=None):
        new_image = GtkDocPicture(pos, name, x_cm, y_cm, crop=crop)
        self._active_element.add_child(new_image)

        if len(alt):
            style_sheet = self.get_style_sheet()

            style = style_sheet.get_paragraph_style(style_name)
            style.set_alignment(PARA_ALIGN_CENTER)
            # Center the caption under the image
            if pos == "right":
                style.set_left_margin(self.get_usable_width() - new_image._width)
            else:
                style.set_right_margin(self.get_usable_width() - new_image._width)
            new_paragraph = GtkDocParagraph(style)
            new_paragraph.add_text('\n'.join(alt))
            self._active_element.add_child(new_paragraph)

    def insert_toc(self):
        """
        Insert a Table of Contents at this point in the document.
        """
        self._doc.add_child(GtkDocTableOfContents())

    def insert_index(self):
        """
        Insert an Alphabetical Index at this point in the document.
        """
        self._doc.add_child(GtkDocAlphabeticalIndex())

    # DrawDoc implementation

    def start_page(self):
        # if this is not the first page we need to "close" the previous one
        children = self._doc.get_children()
        if children and children[-1].get_type() != 'PAGEBREAK':
            self._doc.add_child(GtkDocPagebreak())

        new_frame_style = FrameStyle(width=self.get_usable_width(),
                                     height=self.get_usable_height())
        new_frame = GtkDocFrame(new_frame_style)

        self._active_element.add_child(new_frame)
        self._active_element = new_frame

    def end_page(self):
        self._active_element = self._active_element.get_parent()

    def draw_line(self, style_name, x1, y1, x2, y2):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)

        new_line = GtkDocLine(style, x1, y1, x2, y2)
        self._active_element.add_child(new_line)

    def draw_path(self, style_name, path):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)

        new_polygon = GtkDocPolygon(style, path)
        self._active_element.add_child(new_polygon)

    def draw_box(self, style_name, text, x, y, w, h, mark=None):
        """ @param mark:  IndexMark to use for indexing """
        # we handle the box and...
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)

        new_box = GtkDocBox(style, x, y, w, h)
        self._active_element.add_child(new_box)

        # ...the text separately
        paragraph_style_name = style.get_paragraph_style()
        if paragraph_style_name:
            paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
            paragraph_style.set_alignment(PARA_ALIGN_LEFT)

            # horizontal position of the text is not included in the style,
            # we assume that it is the size of the shadow, or 0.2mm
            if style.get_shadow():
                x_offset = style.get_shadow_space()
            else:
                x_offset = 0.2

            new_text = GtkDocText(paragraph_style, 'center',
                                  self.__markup(text),
                                  x + x_offset, y + h / 2, angle=0, mark=mark)
            self._active_element.add_child(new_text)

    def draw_text(self, style_name, text, x, y, mark=None):
        """ @param mark:  IndexMark to use for indexing """
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)
        paragraph_style_name = style.get_paragraph_style()
        paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
        paragraph_style.set_alignment(PARA_ALIGN_LEFT)

        new_text = GtkDocText(paragraph_style, 'top',
                              self.__markup(text), x, y, angle=0, mark=mark)
        self._active_element.add_child(new_text)

    def center_text(self, style_name, text, x, y, mark=None):
        """ @param mark:  IndexMark to use for indexing """
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)
        paragraph_style_name = style.get_paragraph_style()
        paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
        paragraph_style.set_alignment(PARA_ALIGN_CENTER)

        new_text = GtkDocText(paragraph_style, 'top',
                              self.__markup(text), x, y, angle=0, mark=mark)
        self._active_element.add_child(new_text)

    def rotate_text(self, style_name, text, x, y, angle, mark=None):
        """ @param mark:  IndexMark to use for indexing """
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)
        paragraph_style_name = style.get_paragraph_style()
        paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
        paragraph_style.set_alignment(PARA_ALIGN_CENTER)

        new_text = GtkDocText(paragraph_style, 'center',
                              self.__markup('\n'.join(text)), x, y, angle, mark)
        self._active_element.add_child(new_text)

    # paginating and drawing interface

    def run(self):
        """Create the physical output from the meta document.

        It must be implemented in the subclasses. The idea is that with
        different subclass different output could be generated:
        e.g. Print, PDF, PS, PNG (which are currently supported by Cairo).

        """
        raise NotImplementedError

    def paginate_document(self, layout, page_width, page_height, dpi_x, dpi_y):
        """Paginate the entire document.
        """
        while not self.paginate(layout, page_width, page_height, dpi_x, dpi_y):
            pass

    def paginate(self, layout, page_width, page_height, dpi_x, dpi_y):
        """Paginate the meta document in chunks.

        Only one document level element is handled at one run.

        """
        # if first time run than initialize the variables
        if not self._elements_to_paginate:
            self._elements_to_paginate = self._doc.get_children()[:]
            self._pages.append(GtkDocDocument())
            self._available_height = page_height

        # try to fit the next element to current page, divide it if needed
        if not self._elements_to_paginate:
            #this is a self._doc where nothing has been added. Empty page.
            return True
        elem = self._elements_to_paginate.pop(0)
        (e1, e2), e1_h = elem.divide(layout,
                                     page_width,
                                     self._available_height,
                                     dpi_x,
                                     dpi_y)

        # if (part of) it fits on current page add it
        if e1 is not None:
            self._pages[len(self._pages) - 1].add_child(e1)

        # if elem was divided remember the second half to be processed
        if e2 is not None:
            self._elements_to_paginate.insert(0, e2)

        # calculate how much space left on current page
        self._available_height -= e1_h

        # start new page if needed
        if (e1 is None) or (e2 is not None):
            self._pages.append(GtkDocDocument())
            self._available_height = page_height

        return len(self._elements_to_paginate) == 0

    def draw_page(self, page_nr, cr, layout, width, height, dpi_x, dpi_y):
        """Draw a page on a Cairo context.
        """
        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(0, 1.0, 0)
            cr.rectangle(0, 0, width, height)
            cr.stroke()

        self._pages[page_nr].draw(cr, layout, width, dpi_x, dpi_y)
