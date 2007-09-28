#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Zsolt Foldvari
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

"""Report output generator based on Cairo.
"""

__revision__ = "$Revision$"
__author__   = "Zsolt Foldvari"

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
from math import radians

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
from ReportBase import ReportUtils
##rgb_color = ReportUtils.rgb_color

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".CairoDoc")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
import cairo
import pango
import pangocairo

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
    BaseDoc.FONT_SERIF: 'FreeSerif',
    BaseDoc.FONT_SANS_SERIF: 'FreeSans',
    BaseDoc.FONT_MONOSPACE: 'FreeMono',
}

_MS_TTFONT = {
    BaseDoc.FONT_SERIF: 'Times New Roman',
    BaseDoc.FONT_SANS_SERIF: 'Arial',
    BaseDoc.FONT_MONOSPACE: 'Courier New',
}

_GNOME_FONT = {
    BaseDoc.FONT_SERIF: 'Serif',
    BaseDoc.FONT_SANS_SERIF: 'Sans',
    BaseDoc.FONT_MONOSPACE: 'Monospace',
}

font_families = _GNOME_FONT

# FIXME debug logging does not work here.
def set_font_families():
##def set_font_families(pango_context):
    """Set the used font families depending on availability.
    """
    global font_families
    
    ##families = pango_context.list_families()
    families = pangocairo.cairo_font_map_get_default().list_families()
    family_names = [family.get_name() for family in families]
    
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
    """Convert a BaseDoc.FontStyle instance to a pango.FontDescription one.
    
    Font color and underline are not implemented in pango.FontDescription,
    and have to be set with pango.Layout.set_attributes(attrlist) method.
    
    """
    if font_style.get_bold():
        f_weight = pango.WEIGHT_BOLD
    else:
        f_weight = pango.WEIGHT_NORMAL
        
    if font_style.get_italic():
        f_style = pango.STYLE_ITALIC
    else:
        f_style = pango.STYLE_NORMAL
        
    font_description = pango.FontDescription(font_families[font_style.face])
    font_description.set_size(int(round(font_style.get_size() * pango.SCALE)))
    font_description.set_weight(f_weight)
    font_description.set_style(f_style)
    
    return font_description

def tabstops_to_tabarray(tab_stops, dpi):
    """Convert a list of tabs given in cm to a pango.TabArray.
    """
    tab_array = pango.TabArray(len(tab_stops), False)
    
    for index in range(len(tab_stops)):
        location = tab_stops[index] * dpi * pango.SCALE / 2.54
        tab_array.set_tab(index, pango.TAB_LEFT, int(location))
        
    return tab_array

###------------------------------------------------------------------------
###
### Table row style
###
###------------------------------------------------------------------------
        
##class RowStyle(list):
    ##"""Specifies the format of a table row.
    
    ##RowStyle extents the available styles in BaseDoc.
    
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
        ##Sets the width of a specified column to the specified width.

        ##@param index: column being set (index starts at 0)
        ##@param width: percentage of the table width assigned to the column
        ##"""
        ##self.colwid[index] = width

    ##def get_column_width(self, index):
        ##"""
        ##Returns the column width of the specified column as a percentage of
        ##the entire table width.

        ##@param index: column to return (index starts at 0)
        ##"""
        ##return self.colwid[index]

class FrameStyle(object):
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
        
class GtkDocBaseElement(object):
    """Base of all document elements.
    
    Support document element structuring and can render itself onto
    a Cairo surface.
    
    There are two cathegories of methods:
      1. hierarchy building methods (add_child, get_children, set_parent,
         get_parent);
      2. rendering methods (divide, draw).
      
    The hierarchy building methods generally don't have to be overriden in
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
        
        # append the child and set it's parent
        self._children.append(element)
        element.set_parent(self)
        return True
        
    def get_children(self):
        """Get the list of children of this element.
        """
        return self._children
    
    def divide(self, layout, width, height, dpi_x, dpi_y):
        """Divide the element into two depending on available space.
        
        @param layout: pango layout to write on
        @param type: pango.Layout
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
        @param type: pango.Layout class
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
    _allowed_children = ['PARAGRAPH', 'PAGEBREAK', 'TABLE', 'IMAGE', 'FRAME']
    
    def draw(self, cairo_context, pango_layout, width, dpi_x, dpi_y):
            
        x = y = elem_height = 0
        
        for elem in self._children:
            cairo_context.translate(x, elem_height)
            elem_height = elem.draw(cairo_context, pango_layout,
                                    width, dpi_x, dpi_y)
            y += elem_height
            
        return y
    
class GtkDocPagebreak(GtkDocBaseElement):
    """Implement a page break.
    """
    _type = 'PAGEBREAK'
    _allowed_children = []
    
    def divide(self, layout, width, height, dpi_x, dpi_y):
        return (None, None), 0
    
class GtkDocParagraph(GtkDocBaseElement):
    """Paragraph.
    """
    _type = 'PARAGRAPH'
    _allowed_children = []
    
    # line spacing is not defined in BaseDoc.ParagraphStyle
    spacing = 2
    
    def __init__(self, style, leader=None):
        GtkDocBaseElement.__init__(self, style)

        if leader:
            self._text = leader + '\t'
            # FIXME append new tab to the existing tab list
            self._style.set_tabs([-1 * self._style.get_first_indent()])
        else:
            self._text = ''
        
    def add_text(self, text):
        self._text = self._text + text
        
    def divide(self, layout, width, height, dpi_x, dpi_y):
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
        layout.set_width(int(text_width * pango.SCALE))
        
        # set paragraph properties
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        layout.set_spacing(self.spacing * pango.SCALE)
        layout.set_indent(int(f_indent * pango.SCALE))
        layout.set_tabs(tabstops_to_tabarray(self._style.get_tabs(), dpi_x))
        #
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_alignment(pango.ALIGN_LEFT)
        elif align == 'right':
            layout.set_alignment(pango.ALIGN_RIGHT)
        elif align == 'center':
            layout.set_alignment(pango.ALIGN_CENTER)
        elif align == 'justify':
            layout.set_justify(True)
        else:
            raise ValueError
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))
        
        # calculate the height of one line
        layout.set_text('Test')
        layout_width, layout_height = layout.get_pixel_size()
        line_height = layout_height + self.spacing
        # and the number of lines fit on the available height
        text_height = height - t_margin - 2 * v_padding
        line_per_height = text_height / line_height
        
        # if nothing fits
        if line_per_height < 1:
            return (None, self), 0
        
        # calculate where to cut the paragraph
        layout.set_markup(self._text)
        layout_width, layout_height = layout.get_pixel_size()
        line_count = layout.get_line_count()
        
        # if all paragraph fits we don't need to cut
        if line_count <= line_per_height:
            paragraph_height = (layout_height + t_margin + (2 * v_padding))
            if height - paragraph_height > b_margin:
                paragraph_height += b_margin
            return (self, None), paragraph_height
        
        # get index of first character which doesn't fit on available height
        layout_line = layout.get_line(int(line_per_height))
        index = layout_line.start_index
        # and divide the text, first create the second part
        new_style = BaseDoc.ParagraphStyle(self._style)
        new_style.set_top_margin(0)
        new_paragraph = GtkDocParagraph(new_style)
        new_paragraph.add_text(self._text.encode('utf-8')[index:])
        # then update the first one
        self._text = self._text.encode('utf-8')[:index]
        self._style.set_bottom_margin(0)
        
        # FIXME do we need to return the proper height???
        #paragraph_height = line_height * line_count + t_margin + 2 * v_padding
        paragraph_height = 0
        return (self, new_paragraph), paragraph_height
    
    def draw(self, cr, layout, width, dpi_x, dpi_y):
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
        layout.set_width(int(text_width * pango.SCALE))
        
        # set paragraph properties
        layout.set_wrap(pango.WRAP_WORD_CHAR)
        layout.set_spacing(self.spacing * pango.SCALE)
        layout.set_indent(int(f_indent * pango.SCALE))
        layout.set_tabs(tabstops_to_tabarray(self._style.get_tabs(), dpi_x))
        #
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_alignment(pango.ALIGN_LEFT)
        elif align == 'right':
            layout.set_alignment(pango.ALIGN_RIGHT)
        elif align == 'center':
            layout.set_alignment(pango.ALIGN_CENTER)
        elif align == 'justify':
            layout.set_justify(True)
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))

        # layout the text
        layout.set_markup(self._text)
        layout_width, layout_height = layout.get_pixel_size()
        
        # render the layout onto the cairo surface
        x = l_margin + h_padding
        if f_indent < 0:
            x += f_indent
        cr.move_to(x, t_margin + v_padding)
        cr.set_source_rgb(*ReportUtils.rgb_color(font_style.get_color()))
        cr.show_layout(layout)
        
        # calculate the full paragraph height
        height = layout_height + t_margin + 2*v_padding + b_margin

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
            if table_height + row_height >= height:
                break
            table_height += row_height
            row_index += 1
            
        # divide the table if any row did not fit
        new_table = None
        if row_index < len(self._children):
            new_table = GtkDocTable(self._style)
            for row in self._children[row_index:]:
                new_table.add_child(row)
            del self._children[row_index:]
            
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
        cell_width_iter = self._style.__iter__()
        for cell in self._children:
            cell_width = 0
            for i in range(cell.get_span()):
                cell_width += cell_width_iter.next()
            cell_width = cell_width * width / 100
            (c1, c2), cell_height = cell.divide(layout, cell_width, height,
                                                dpi_x, dpi_y)
            cell_heights.append(cell_height)
        
        # save height [inch] of the row to be able to draw exact cell border
        row_height = max(cell_heights)
        self.height = row_height / dpi_y
        
        # a row can't be divided, return the height
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
                cell_width += cell_width_iter.next()
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

        # calculate height of each children
        cell_height = 0
        for child in self._children:
            (e1, e2), child_height = child.divide(layout, width, height,
                                                 dpi_x, dpi_y)
            cell_height += child_height
        
        # calculate real height
        cell_height += 2 * v_padding
        
        # a cell can't be divided, return the heigth
        return (self, None), cell_height
    
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
    
    def __init__(self, style, filename, width, height):
        GtkDocBaseElement.__init__(self, style)
        self._filename = filename
        self._width = width
        self._height = height
    
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
        img_width = self._width * dpi_x / 2.54
        img_height = self._height * dpi_y / 2.54
        
        if self._style == 'right':
            l_margin = width - img_width
        elif self._style == 'center':
            l_margin = (width - img_width) / 2.0
        else:
            l_margin = 0
        
        # load the image and get its extents
        pixbuf = gtk.gdk.pixbuf_new_from_file(self._filename)
        pixbuf_width = pixbuf.get_width()
        pixbuf_height = pixbuf.get_height()
        
        # calculate the scale to fit image into the set extents
        scale = min(img_width / pixbuf_width, img_height / pixbuf_height)
        
        # draw the image
        cr.save()
        cr.translate(l_margin, 0)
        cr.scale(scale, scale)
        gcr = gtk.gdk.CairoContext(cr)
        gcr.set_source_pixbuf(pixbuf,
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
        l_margin = self._style.spacing[0] * dpi_y / 2.54
        r_margin = self._style.spacing[1] * dpi_y / 2.54
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
        line_color = ReportUtils.rgb_color(self._style.get_color())
        
        cr.save()
        cr.set_source_rgb(*line_color)
        cr.set_line_width(self._style.get_line_width())
        # TODO line style
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
        path_stroke_color = ReportUtils.rgb_color(self._style.get_color())
        path_fill_color = ReportUtils.rgb_color(self._style.get_fill_color())
        
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
        
        box_stroke_color = ReportUtils.rgb_color((0, 0, 0))
        box_fill_color = ReportUtils.rgb_color(self._style.get_fill_color())
        shadow_color = ReportUtils.rgb_color((192, 192, 192))
        
        cr.save()
        
        cr.set_line_width(self._style.get_line_width())
        # TODO line style

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

    # line spacing is not defined in BaseDoc.ParagraphStyle
    spacing = 1
    
    def __init__(self, style, vertical_alignment, text, x, y, angle=0):
        GtkDocBaseElement.__init__(self, style)
        self._align_y = vertical_alignment
        self._text = text
        self._x = x
        self._y = y
        self._angle = angle
        
    def draw(self, cr, layout, width, dpi_x, dpi_y):
        text_x = self._x * dpi_x / 2.54
        text_y = self._y * dpi_y / 2.54

        # turn off text wrapping
        layout.set_width(-1)
        
        # set paragraph properties
        layout.set_spacing(self.spacing * pango.SCALE)
        #
        align = self._style.get_alignment_text()
        if align == 'left':
            layout.set_alignment(pango.ALIGN_LEFT)
        elif align == 'right':
            layout.set_alignment(pango.ALIGN_RIGHT)
        elif align == 'center':
            layout.set_alignment(pango.ALIGN_CENTER)
        elif align == 'justify':
            layout.set_justify(True)
        else:
            raise ValueError
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))

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
        cr.set_source_rgb(*ReportUtils.rgb_color(font_style.get_color()))
        cr.show_layout(layout)
        cr.restore()

        return layout_height

#------------------------------------------------------------------------
#
# CairoDoc class
#
#------------------------------------------------------------------------
class CairoDoc(BaseDoc.BaseDoc, BaseDoc.TextDoc, BaseDoc.DrawDoc):
    """Act as an abstract document that can render onto a cairo context.
    
    Maintains an abstract model of the document. The root of this abstract
    document is self._doc. The model is build via the subclassed BaseDoc, and
    the implemented TextDoc, DrawDoc interface methods.
    
    It can render the model onto cairo context pages, according to the received
    page style.
        
    """
    
    # BaseDoc implementation
    
    def open(self, filename):
        self._filename = filename
        self._doc = GtkDocDocument()
        self._active_element = self._doc
        self._pages = []
        self._elements_to_paginate = []
    
    def close(self):
        self.run()

    # TextDoc implementation
    
    def page_break(self):
        self._active_element.add_child(GtkDocPagebreak())

    def start_bold(self):
        self.write_text('<b>')
    
    def end_bold(self):
        self.write_text('</b>')
    
    def start_superscript(self):
        self.write_text('<small><sup>')
    
    def end_superscript(self):
        self.write_text('</sup></small>')
    
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
        self._active_row_style = []
        for i in range(style.get_columns()):
            self._active_row_style.append(style.get_column_width(i))
    
    def end_table(self):
        self._active_element = self._active_element.get_parent()
    
    def start_row(self):
        new_row = GtkDocTableRow(self._active_row_style)
        self._active_element.add_child(new_row)
        self._active_element = new_row
    
    def end_row(self):
        self._active_element = self._active_element.get_parent()
    
    def start_cell(self, style_name, span=1):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_cell_style(style_name)
        
        new_cell = GtkDocTableCell(style, span)
        self._active_element.add_child(new_cell)
        self._active_element = new_cell
    
    def end_cell(self):
        self._active_element = self._active_element.get_parent()
    
    def write_note(self, text, format, style_name):
        if format == 1:
            for line in text.split('\n'):
                self.start_paragraph(style_name)
                self.write_text(line)
                self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = ' '.join(line.split())
                self.write_text(line)
                self.end_paragraph()

    def write_text(self, text, mark=None):
        # FIXME this is ugly, do we really need it?
        text = text.replace('<super>', '<small><sup>')
        text = text.replace('</super>', '</sup></small>')
        self._active_element.add_text(text)
    
    def add_media_object(self, name, pos, x_cm, y_cm):
        new_image = GtkDocPicture(pos, name, x_cm, y_cm)
        self._active_element.add_child(new_image)

    # DrawDoc implementation
    
    def start_page(self):
        # if this is not the first page we need to "close" the previous one
        if self._doc.get_children():
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
        
    def draw_box(self, style_name, text, x, y, w, h):
        # we handle the box and...
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)

        new_box = GtkDocBox(style, x, y, w, h)
        self._active_element.add_child(new_box)

        # ...the text separately
        paragraph_style_name = style.get_paragraph_style()
        paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
        paragraph_style.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        
        # horizontal position of the text is not included in the style,
        # we assume that it is the size of the shadow, or 0.2mm
        if style.get_shadow():
            x_offset = style.get_shadow_space()
        else:
            x_offset = 0.2
            
        new_text = GtkDocText(paragraph_style, 'center', text,
                              x + x_offset , y + h / 2, angle=0)
        self._active_element.add_child(new_text)
    
    def draw_text(self, style_name, text, x, y):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)
        paragraph_style_name = style.get_paragraph_style()
        paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
        paragraph_style.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        
        new_text = GtkDocText(paragraph_style, 'top', text, x, y, angle=0)
        self._active_element.add_child(new_text)
        
    def center_text(self, style_name, text, x, y):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)
        paragraph_style_name = style.get_paragraph_style()
        paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
        paragraph_style.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        
        new_text = GtkDocText(paragraph_style, 'top', text, x, y, angle=0)
        self._active_element.add_child(new_text)
    
    def rotate_text(self, style_name, text, x, y, angle):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)
        paragraph_style_name = style.get_paragraph_style()
        paragraph_style = style_sheet.get_paragraph_style(paragraph_style_name)
        paragraph_style.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        
        new_text = GtkDocText(paragraph_style, 'center', '\n'.join(text),
                              x, y, angle)
        self._active_element.add_child(new_text)
    
    # paginating and drawing interface
    
    def run(self):
        """Create the physical output from the meta document.
        
        It must be implemented in the subclasses. The idea is that with
        different subclass different output could be generated:
        e.g. Print, PDF, PS, PNG (which are currently supported by Cairo).
        
        """
        raise NotImplementedError

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
