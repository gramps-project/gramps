#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"""Printing interface based on gtk.Print* classes.
"""

__revision__ = "$Revision$"
__author__   = "Zsolt Foldvari"

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
import os
##try:
    ##from cStringIO import StringIO
##except:
    ##from StringIO import StringIO

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
import const
import BaseDoc
from PluginUtils import register_text_doc, register_draw_doc, register_book_doc
import Errors

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".GtkPrint")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
import cairo
import pango
import pangocairo

if gtk.pygtk_version < (2,10,0):
    raise Errors.UnavailableError(_("PyGtk 2.10 or later is required"))

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
PRINTER_DPI = 72.0
PRINTER_SCALE = 1.0

MARGIN = 6

(ZOOM_BEST_FIT,
 ZOOM_FIT_WIDTH,
 ZOOM_FREE,) = range(3)

#------------------------------------------------------------------------
#
# PrintPreview class
#
#------------------------------------------------------------------------
class PrintPreview:
    """Implement a dialog to show print preview.
    """
    zoom_factors = {
        0.50: '50%',
        0.75: '75%',
        1.00: '100%',
        1.25: '125%',
        1.50: '150%',
        1.75: '175%',
        2.00: '200%',
        3.00: '300%',
        4.00: '400%',
    }
    
    def __init__(self, operation, preview, context, parent):
        self._operation = operation
        self._preview = preview
        self._context = context
        
        self.__build_window()
        self._current_page = None

    # Private
    
    def __build_window(self):
        """Build the window from Glade.
        """
        glade_file = os.path.join(os.path.dirname(__file__),
                                  'gtkprintpreview.glade')

        window_xml = gtk.glade.XML(glade_file, 'window', 'gramps')
        self._window = window_xml.get_widget('window')
        #self._window.set_transient_for(parent)
 
        # remember active widgets for future use
        self._swin = window_xml.get_widget('swin')
        self._drawing_area = window_xml.get_widget('drawingarea')
        self._first_button = window_xml.get_widget('first')
        self._prev_button = window_xml.get_widget('prev')
        self._next_button = window_xml.get_widget('next')
        self._last_button = window_xml.get_widget('last')
        self._pages_entry = window_xml.get_widget('entry')
        self._pages_label = window_xml.get_widget('label')
        self._zoom_fit_width_button = window_xml.get_widget('zoom_fit_width')
        self._zoom_fit_width_button.set_stock_id('gramps-zoom-fit-width')
        self._zoom_best_fit_button = window_xml.get_widget('zoom_best_fit')
        self._zoom_in_button = window_xml.get_widget('zoom_in')
        self._zoom_out_button = window_xml.get_widget('zoom_out')

        # connect the signals
        window_xml.signal_autoconnect({
            'on_drawingarea_expose_event': self.on_drawingarea_expose_event,
            'on_swin_size_allocate': self.on_swin_size_allocate,
            'on_quit_clicked': self.on_quit_clicked,
            'on_print_clicked': self.on_print_clicked,
            'on_first_clicked': self.on_first_clicked,
            'on_prev_clicked': self.on_prev_clicked,
            'on_next_clicked': self.on_next_clicked,
            'on_last_clicked': self.on_last_clicked,
            'on_zoom_fit_width_toggled': self.on_zoom_fit_width_toggled,
            'on_zoom_best_fit_toggled': self.on_zoom_best_fit_toggled,
            'on_zoom_in_clicked': self.on_zoom_in_clicked,
            'on_zoom_out_clicked': self.on_zoom_out_clicked,
            'on_window_delete_event': self.on_window_delete_event,
            'on_entry_activate': self.on_entry_activate,
        })

    ##def create_surface(self):
        ##return cairo.PDFSurface(StringIO(),
                                ##self._context.get_width(),
                                ##self._context.get_height())
    
    ##def get_page(self, page_no):
        ##"""Get the cairo surface of the given page.
        
        ##Surfaces are also cached for instant access.
        
        ##"""
        ##if page_no >= len(self._page_numbers):
            ##log.debug("Page number %d doesn't exist." % page_no)
            ##page_no = 0
        
        ##if not self._page_surfaces.has_key(page_no):
            ##surface = self.create_surface()
            ##cr = cairo.Context(surface)
            
            ##if PRINTER_SCALE != 1.0:
                ##cr.scale(PRINTER_SCALE, PRINTER_SCALE)
                
            ##self._context.set_cairo_context(cr, PRINTER_DPI, PRINTER_DPI)
            ##self._preview.render_page(self._page_numbers[page_no])
            
            ##self._page_surfaces[page_no] = surface
            
        ##return self._page_surfaces[page_no]
    
    def __set_page(self, page_no):
        if page_no < 0 or page_no >= self._page_no:
            return
        
        if self._current_page != page_no:
            self._drawing_area.queue_draw()
        
        self._current_page = page_no

        self._first_button.set_sensitive(self._current_page)
        self._prev_button.set_sensitive(self._current_page)
        self._next_button.set_sensitive(self._current_page < self._page_no - 1)
        self._last_button.set_sensitive(self._current_page < self._page_no - 1)
        
        self._pages_entry.set_text('%d' % (self._current_page + 1))
        
    def __set_zoom(self, zoom):
        self._zoom = zoom

        screen_width = int(self._paper_width * self._zoom + 2 * MARGIN)
        screen_height = int(self._paper_height * self._zoom + 2 * MARGIN)
        self._drawing_area.set_size_request(screen_width, screen_height)
        self._drawing_area.queue_draw()
        
        self._zoom_in_button.set_sensitive(self._zoom !=
                                           max(self.zoom_factors.keys()))
        self._zoom_out_button.set_sensitive(self._zoom !=
                                            min(self.zoom_factors.keys()))
        
    def __zoom_in(self):
        zoom = [z for z in self.zoom_factors.keys() if z > self._zoom]

        if zoom:
            return min(zoom)
        else:
            return self._zoom
            
    def __zoom_out(self):
        zoom = [z for z in self.zoom_factors.keys() if z < self._zoom]
        
        if zoom:
            return max(zoom)
        else:
            return self._zoom

    def __zoom_fit_width(self):
        width, height, vsb_w, hsb_h = self.__get_view_size()

        zoom = width / self._paper_width
        if self._paper_height * zoom > height:
            zoom = (width - vsb_w) / self._paper_width

        return zoom

    def __zoom_best_fit(self):
        width, height, vsb_w, hsb_h = self.__get_view_size()

        zoom = min(width / self._paper_width, height / self._paper_height)

        return zoom
        
    def __get_view_size(self):
        """Get the dimensions of the scrolled window.
        """
        width = self._swin.allocation.width - 2 * MARGIN
        height = self._swin.allocation.height - 2 * MARGIN

        if self._swin.get_shadow_type() != gtk.SHADOW_NONE:
            width -= 2 * self._swin.style.xthickness
            height -= 2 * self._swin.style.ythickness

        spacing = self._swin.style_get_property('scrollbar-spacing')
        
        vsb_w, vsb_h = self._swin.get_vscrollbar().size_request()
        vsb_w += spacing
        
        hsb_w, hsb_h = self._swin.get_hscrollbar().size_request()
        hsb_h += spacing
        
        return width, height, vsb_w, hsb_h
        
    def __end_preview(self):
        self._operation.end_preview()
        
    # Signal handlers
    
    def on_drawingarea_expose_event(self, drawing_area, event):
        cr = drawing_area.window.cairo_create()
        cr.rectangle(event.area)
        cr.clip()
        
        # get the extents of the page and the screen
        paper_w = self._paper_width * self._zoom
        paper_h = self._paper_height * self._zoom

        width, height, vsb_w, hsb_h = self.__get_view_size()
        if paper_h > height:
            width -= vsb_w
        if paper_w > width:
            height -= hsb_h
        
        # put the paper on the middle of the window
        xtranslate = MARGIN
        if  paper_w < width:
            xtranslate += (width - paper_w) / 2
            
        ytranslate = MARGIN
        if  paper_h < height:
            ytranslate += (height - paper_h) / 2
            
        cr.translate(xtranslate, ytranslate)
        
        # draw an empty white page
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, paper_w, paper_h)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()
        
        ##page_setup = self._context.get_page_setup()
        ##cr.translate(page_setup.get_left_margin(gtk.UNIT_POINTS),
                     ##page_setup.get_top_margin(gtk.UNIT_POINTS))
        
        ##cr.set_source_surface(self.get_page(0))
        ##cr.paint()
        
        # draw the content of the currently selected page
        dpi = PRINTER_DPI * self._zoom
        self._context.set_cairo_context(cr, dpi, dpi)
        self._preview.render_page(self._current_page)
    
    def on_swin_size_allocate(self, scrolledwindow, allocation):
        if self._zoom_mode == ZOOM_FIT_WIDTH:
            self.__set_zoom(self.__zoom_fit_width())
        
        if self._zoom_mode == ZOOM_BEST_FIT:
            self.__set_zoom(self.__zoom_best_fit())

    def on_print_clicked(self, toolbutton):
        pass
    
    def on_first_clicked(self, toolbutton):
        self.__set_page(0)
    
    def on_prev_clicked(self, toolbutton):
        self.__set_page(self._current_page - 1)
    
    def on_next_clicked(self, toolbutton):
        self.__set_page(self._current_page + 1)
    
    def on_last_clicked(self, toolbutton):
        self.__set_page(self._page_no - 1)
    
    def on_entry_activate(self, entry):
        try:
            new_page = int(entry.get_text()) - 1
        except ValueError:
            new_page = self._current_page
        
        if new_page < 0 or new_page >= self._page_no:
            new_page = self._current_page
            
        self.__set_page(new_page)
        
    def on_zoom_fit_width_toggled(self, toggletoolbutton):
        if toggletoolbutton.get_active():
            self._zoom_best_fit_button.set_active(False)
            self._zoom_mode = ZOOM_FIT_WIDTH
            self.__set_zoom(self.__zoom_fit_width())
        else:
            self._zoom_mode = ZOOM_FREE
        
    def on_zoom_best_fit_toggled(self, toggletoolbutton):
        if toggletoolbutton.get_active():
            self._zoom_fit_width_button.set_active(False)
            self._zoom_mode = ZOOM_BEST_FIT
            self.__set_zoom(self.__zoom_best_fit())
        else:
            self._zoom_mode = ZOOM_FREE

    def on_zoom_in_clicked(self, toolbutton):
        self._zoom_fit_width_button.set_active(False)
        self._zoom_best_fit_button.set_active(False)
        self._zoom_mode = ZOOM_FREE
        self.__set_zoom(self.__zoom_in())
    
    def on_zoom_out_clicked(self, toolbutton):
        self._zoom_fit_width_button.set_active(False)
        self._zoom_best_fit_button.set_active(False)
        self._zoom_mode = ZOOM_FREE
        self.__set_zoom(self.__zoom_out())
        
    def on_window_delete_event(self, widget, event):
        self.__end_preview()
        return False

    def on_quit_clicked(self, toolbutton):
        self.__end_preview()
        self._window.destroy()

    # Public

    def start(self):
        # get paper/page dimensions
        page_setup = self._context.get_page_setup()
        self._paper_width = page_setup.get_paper_width(gtk.UNIT_POINTS)
        self._paper_height = page_setup.get_paper_height(gtk.UNIT_POINTS)
        self._page_width = page_setup.get_page_width(gtk.UNIT_POINTS)
        self._page_height = page_setup.get_page_height(gtk.UNIT_POINTS)

        # get the total number of pages
        ##self._page_numbers = [0,]
        ##self._page_surfaces = {}
        self._page_no = self._operation.get_property('n_pages')
        self._pages_label.set_text('of %d' % self._page_no)

        # set zoom level and initial page number
        self._zoom_mode = ZOOM_FREE
        self.__set_zoom(1.0)
        self.__set_page(0)
        
        # let's the show begin...
        self._window.show()
    
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

def set_font_families(pango_context):
    """Set the used font families depending on availability.
    """
    global font_families
    
    families = pango_context.list_families()
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
    
#------------------------------------------------------------------------
#
# Converter functions
#
#------------------------------------------------------------------------

def paperstyle_to_pagesetup(paper_style):
    """Convert a BaseDoc.PaperStyle instance into a gtk.PageSetup instance.
    
    @param paper_style: Gramps paper style object to convert
    @param type: BaseDoc.PaperStyle
    @return: page_setup
    @rtype: gtk.PageSetup
    """
    gramps_to_gtk = {
        "Letter": "na_letter",
        "Legal": "na_legal",
        "A0": "iso_a0",
        "A1": "iso_a1",
        "A2": "iso_a2",
        "A3": "iso_a3",
        "A4": "iso_a4",
        "A5": "iso_a5",
        "B0": "iso_b0",
        "B1": "iso_b1",
        "B2": "iso_b2",
        "B3": "iso_b3",
        "B4": "iso_b4",
        "B5": "iso_b5",
        "B6": "iso_b6",
        "B": "iso_b",
        "C": "iso_c",
        "D": "iso_d",
        "E": "iso_e",
    }

    # First set the paper size
    gramps_paper_size = paper_style.get_size()
    gramps_paper_name = gramps_paper_size.get_name()
    
    if gramps_to_gtk.has_key(gramps_paper_name):
        paper_size = gtk.PaperSize(gramps_to_gtk[gramps_paper_name])
    elif gramps_paper_name == "Custom Size":
        paper_width = gramps_paper_size.get_width() * 10
        paper_height = gramps_paper_size.get_height() * 10
        paper_size = gtk.paper_size_new_custom("custom",
                                               "Custom Size",
                                               paper_width,
                                               paper_height,
                                               gtk.UNIT_MM)
    else:
        def_paper_size_name = gtk.paper_size_get_default()
        paper_size = gtk.PaperSize(def_paper_size_name)
        log.debug("Unknown paper size, falling back to the default: %s" %
                  def_paper_size_name)
        
    page_setup = gtk.PageSetup()
    page_setup.set_paper_size(paper_size)
    
    # Set paper orientation
    if paper_style.get_orientation() == BaseDoc.PAPER_PORTRAIT:
        page_setup.set_orientation(gtk.PAGE_ORIENTATION_PORTRAIT)
    else:
        page_setup.set_orientation(gtk.PAGE_ORIENTATION_LANDSCAPE)

    # gtk.PageSize provides default margins for the standard papers.
    # Anyhow, we overwrite those with the settings from Gramps,
    # though at the moment all of them are fixed at 1 inch.
    page_setup.set_top_margin(paper_style.get_top_margin() * 10,
                              gtk.UNIT_MM)
    page_setup.set_bottom_margin(paper_style.get_bottom_margin() * 10,
                                 gtk.UNIT_MM)
    page_setup.set_left_margin(paper_style.get_left_margin() * 10,
                               gtk.UNIT_MM)
    page_setup.set_right_margin(paper_style.get_right_margin() * 10,
                                gtk.UNIT_MM)
    
    return page_setup

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
    font_description.set_size(font_style.get_size() * pango.SCALE)
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
    """Define a Frame's style properties.
    
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
        #
        font_style = self._style.get_font()
        layout.set_font_description(fontstyle_to_fontdescription(font_style))
        
        # calculate the height of one line
        layout.set_text('Test')
        layout_width, layout_height = layout.get_size()
        line_height = layout_height / pango.SCALE + self.spacing
        # and the number of lines fit on the available height
        text_height = height - t_margin - 2 * v_padding
        line_per_height = text_height / line_height
        
        # if nothing fits
        if line_per_height < 1:
            return (None, self), 0
        
        # calculate where to cut the paragraph
        layout.set_markup(self._text)
        layout_width, layout_height = layout.get_size()
        line_count = layout.get_line_count()
        
        # if all paragraph fits we don't need to cut
        if line_count <= line_per_height:
            paragraph_height = ((layout_height / pango.SCALE) +
                                t_margin +
                                (2 * v_padding))
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
        layout_width, layout_height = layout.get_size()
        
        # render the layout onto the cairo surface
        x = l_margin + h_padding
        if f_indent < 0:
            x += f_indent
        cr.move_to(x, t_margin + v_padding)
        cr.set_source_rgb(0, 0, 0)
        cr.show_layout(layout)
        
        # calculate the full paragraph height
        height = layout_height/pango.SCALE + t_margin + 2*v_padding + b_margin

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
        frame_width = self._style.width * dpi_x / 2.54
        frame_height = self._style.height * dpi_y / 2.54
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
        t_margin = self._style.spacing[2] * dpi_y / 2.54
        b_margin = self._style.spacing[3] * dpi_y / 2.54
 
        if self._style.align == 'right':
            l_margin = width - frame_width
        elif self._style.align == 'center':
            l_margin = (width - frame_width) / 2.0
        else:
            l_margin = 0

        # draw each element in the frame
        cr.save()
        cr.translate(l_margin, t_margin)
        cr.rectangle(0, 0, frame_width, frame_height)
        cr.clip()
        
        for elem in self._children:
            elem.draw(cr, layout, frame_width, dpi_x, dpi_y)
        
        cr.restore()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(1.0, 0, 0)
            cr.rectangle(l_margin, t_margin, frame_width, frame_height)
            cr.stroke()

        return frame_height + t_margin + b_margin
    
class GtkDocLine(GtkDocBaseElement):
    """Implement a frame.
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
        r, g, b = self._style.get_color()
        
        cr.save()
        cr.set_source_rgb(r / 256.0, g / 256.0, b / 256.0)
        cr.set_line_width(self._style.get_line_width())
        # TODO line style
        cr.move_to(*start)
        cr.line_to(*end)
        cr.stroke()
        cr.restore()
        
        return 0

class GtkDocBox(GtkDocBaseElement):
    """Implement a frame.
    """
    _type = 'BOX'
    _allowed_children = []

    def __init__(self, style, x, y, width, height, text):
        GtkDocBaseElement.__init__(self, style)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._text = text
        
    def draw(self, cr, layout, width, dpi_x, dpi_y):
        box_x = self._x * dpi_x / 2.54
        box_y = self._y * dpi_y / 2.54
        box_width = self._width * dpi_x / 2.54
        box_height = self._height * dpi_y / 2.54
        
        cr.save()
        
        cr.set_line_width(self._style.get_line_width())

        if self._style.get_shadow():
            shadow_x = box_x + self._style.get_shadow_space() * dpi_x / 2.54
            shadow_y = box_y + self._style.get_shadow_space() * dpi_y / 2.54

            cr.set_source_rgb(192 / 256.0, 192 / 256.0, 192 / 256.0)
            cr.rectangle(shadow_x, shadow_y, box_width, box_height)
            cr.fill()
            
        cr.rectangle(box_x, box_y, box_width, box_height)
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.stroke()

        cr.restore()
        
        return 0
        
#------------------------------------------------------------------------
#
# CairoDoc and GtkPrint class
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
    
    def close(self):
        self.run()

    def run(self):
        """End the meta document.
        
        It must be implemented in the subclasses. The idea is that with
        different subclass different output could be generated:
        e.g. Print, PDF, PS, PNG (which are currently supported by Cairo).
        
        """
        raise NotImplementedError
    
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
        new_frame_style = FrameStyle(width=self.get_usable_width(),
                                     height=self.get_usable_height())
        new_frame = GtkDocFrame(new_frame_style)
        
        self._active_element.add_child(new_frame)
        self._active_element = new_frame
    
    def end_page(self):
        self._active_element = self._active_element.get_parent()
        self._active_element.add_child(GtkDocPagebreak())
    
    def draw_path(self, style, path):
        pass
        
    def draw_box(self, style_name, text, x, y, w, h):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)

        new_box = GtkDocBox(style, x, y, w, h, text)
        self._active_element.add_child(new_box)
    
    def draw_text(self, style, text, x, y):
        pass
    
    def center_text(self, style, text, x, y):
        pass
    
    def draw_line(self, style_name, x1, y1, x2, y2):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_draw_style(style_name)

        new_line = GtkDocLine(style, x1, y1, x2, y2)
        self._active_element.add_child(new_line)

    def rotate_text(self, style, text, x, y, angle):
        pass

# the print settings to remember between print sessions
PRINT_SETTINGS = None

class GtkPrint(CairoDoc):
    """Print document via GtkPrint* interface.
    
    Requires Gtk+ 2.10.
    
    """
    def run(self):
        """Run the Gtk Print operation.
        """
        global PRINT_SETTINGS

        # get a page setup from the paper style we have
        page_setup = paperstyle_to_pagesetup(self.paper)
        
        # set up a print operation
        operation = gtk.PrintOperation()
        operation.set_default_page_setup(page_setup)
        operation.connect("begin_print", self.on_begin_print)
        operation.connect("draw_page", self.on_draw_page)
        operation.connect("paginate", self.on_paginate)
        operation.connect("preview", self.on_preview)

        # set print settings if it was stored previously
        if PRINT_SETTINGS is not None:
            operation.set_print_settings(PRINT_SETTINGS)

        # run print dialog
        while True:
            self.preview = None
            res = operation.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, None)
            if self.preview is None:
                break
        
        # store print settings if printing was successful
        if res == gtk.PRINT_OPERATION_RESULT_APPLY:
            PRINT_SETTINGS = operation.get_print_settings()

    def on_begin_print(self, operation, context):
        """Setup environment for printing.
        """
        # choose installed font faces
        set_font_families(context.create_pango_context())
        
        # get page size
        self.page_width = context.get_width()
        self.page_height = context.get_height()
        
        # get all document level elements and beging a new page
        self.elements_to_paginate = self._doc.get_children()[:]
        self._pages = [GtkDocDocument(),]
        self.available_height = self.page_height
       
    def on_paginate(self, operation, context):
        """Paginate the whole document in chunks.
        
        Only one document level element is handled at one run.
        
        """
        layout = context.create_pango_layout()
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()
        
        # try to fit the next element to current page, divide it if needed
        elem = self.elements_to_paginate.pop(0)
        (e1, e2), e1_h = elem.divide(layout,
                                     self.page_width,
                                     self.available_height,
                                     dpi_x,
                                     dpi_y)

        # if (part of) it fits on current page add it
        if e1 is not None:
            self._pages[len(self._pages) - 1].add_child(e1)

        # if elem was divided remember the second half to be processed
        if e2 is not None:
            self.elements_to_paginate.insert(0, e2)

        # calculate how much space left on current page
        self.available_height -= e1_h

        # start new page if needed
        if (e1 is None) or (e2 is not None):
            self._pages.append(GtkDocDocument())
            self.available_height = self.page_height
            
        # update page number
        operation.set_n_pages(len(self._pages))
        
        # tell operation whether we finished or not and...
        finished = len(self.elements_to_paginate) == 0
        # ...start preview if needed
        if finished and self.preview:
            self.preview.start()
        return finished

    def on_draw_page(self, operation, context, page_nr):
        """Draw the requested page.
        """
        cr = context.get_cairo_context()
        layout = context.create_pango_layout()
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()
        width = context.get_width()
        height = context.get_height()

        if DEBUG:
            cr.set_line_width(0.1)
            cr.set_source_rgb(0, 1.0, 0)
            cr.rectangle(0, 0, width, height)
            cr.stroke()

        self._pages[page_nr].draw(cr, layout, width, dpi_x, dpi_y)
        
    def on_preview(self, operation, preview, context, parent):
        """Implement custom print preview functionality.
        """
        ##if os.sys.platform == 'win32':
            ##return False
            
        self.preview = PrintPreview(operation, preview, context, parent)
        
        # give a dummy cairo context to gtk.PrintContext,
        # PrintPreview will update it with the real one
        width = int(context.get_width())
        height = int(context.get_height())
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(surface)
        context.set_cairo_context(cr, PRINTER_DPI, PRINTER_DPI)
        
        return True
    
#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------
DEBUG = True
#raise Errors.UnavailableError("Work in progress...")
register_text_doc(_('Print... (Gtk+)'), GtkPrint, 1, 1, 1, "", None)
##register_draw_doc(_('Print... (Gtk+)'), GtkPrint, 1, 1, "", None)
##register_book_doc(_("GtkPrint"), GtkPrint, 1, 1, 1, "", None)
