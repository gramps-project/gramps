#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Zsolt Foldvari
# Copyright (C) 2008-2009  Brian G. Matherly
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

"""Printing interface based on Gtk.Print* classes.
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from math import radians
import logging

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
import cairo

try:  # the Gramps-Connect server has no DISPLAY
    from gi.repository import GObject
    from gi.repository import Gtk
except:
    pass

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug.docgen import PAPER_PORTRAIT
import gramps.plugins.lib.libcairodoc as libcairodoc
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
LOG = logging.getLogger(".GtkPrint")

# ------------------------------------------------------------------------
#
# Constants
#
# ------------------------------------------------------------------------

# printer settings (might be needed to align for different platforms)
PRINTER_DPI = 72.0
PRINTER_SCALE = 1.0

# the print settings to remember between print sessions
PRINT_SETTINGS = None

# minimum spacing around a page in print preview
MARGIN = 6

# zoom modes in print preview
(
    ZOOM_BEST_FIT,
    ZOOM_FIT_WIDTH,
    ZOOM_FREE,
) = list(range(3))

# ------------------------------------------------------------------------
#
# Converter functions
#
# ------------------------------------------------------------------------


def paperstyle_to_pagesetup(paper_style):
    """Convert a PaperStyle instance into a Gtk.PageSetup instance.

    @param paper_style: Gramps paper style object to convert
    @param type: PaperStyle
    @return: page_setup
    @rtype: Gtk.PageSetup
    """
    # paper size names according to 'PWG Candidate Standard 5101.1-2002'
    # ftp://ftp.pwg.org/pub/pwg/candidates/cs-pwgmsn10-20020226-5101.1.pdf
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
        "B": "na_ledger",
        "C": "na_c",
        "D": "na_d",
        "E": "na_e",
    }

    # First set the paper size
    gramps_paper_size = paper_style.get_size()
    gramps_paper_name = gramps_paper_size.get_name()

    # All sizes not included in the translation table (even if a standard size)
    # are handled as custom format, because we are not intelligent enough.
    if gramps_paper_name in gramps_to_gtk:
        paper_size = Gtk.PaperSize.new(name=gramps_to_gtk[gramps_paper_name])
        LOG.debug("Selected paper size: %s", gramps_to_gtk[gramps_paper_name])
    else:
        if paper_style.get_orientation() == PAPER_PORTRAIT:
            paper_width = gramps_paper_size.get_width() * 10
            paper_height = gramps_paper_size.get_height() * 10
        else:
            paper_width = gramps_paper_size.get_height() * 10
            paper_height = gramps_paper_size.get_width() * 10
        paper_size = Gtk.PaperSize.new_custom(
            "custom", "Custom Size", paper_width, paper_height, Gtk.Unit.MM
        )
        LOG.debug("Selected paper size: (%f,%f)", paper_width, paper_height)

    page_setup = Gtk.PageSetup()
    page_setup.set_paper_size(paper_size)

    # Set paper orientation
    if paper_style.get_orientation() == PAPER_PORTRAIT:
        page_setup.set_orientation(Gtk.PageOrientation.PORTRAIT)
    else:
        page_setup.set_orientation(Gtk.PageOrientation.LANDSCAPE)

    # Set paper margins
    page_setup.set_top_margin(paper_style.get_top_margin() * 10, Gtk.Unit.MM)
    page_setup.set_bottom_margin(paper_style.get_bottom_margin() * 10, Gtk.Unit.MM)
    page_setup.set_left_margin(paper_style.get_left_margin() * 10, Gtk.Unit.MM)
    page_setup.set_right_margin(paper_style.get_right_margin() * 10, Gtk.Unit.MM)

    return page_setup


# ------------------------------------------------------------------------
#
# PrintPreview class
#
# ------------------------------------------------------------------------
class PrintPreview:
    """Implement a dialog to show print preview."""

    zoom_factors = {
        0.50: "50%",
        0.75: "75%",
        1.00: "100%",
        1.25: "125%",
        1.50: "150%",
        1.75: "175%",
        2.00: "200%",
        3.00: "300%",
        4.00: "400%",
    }

    def __init__(self, operation, preview, context, parent):
        self._operation = operation
        self._preview = preview
        self._context = context
        self._parent = parent

        self.__build_window()
        self._current_page = None

    # Private

    def __build_window(self):
        """Build the window from Glade."""
        from gramps.gui.glade import Glade

        glade_xml = Glade()
        self._window = glade_xml.toplevel
        self._window.set_transient_for(self._parent)

        # remember active widgets for future use
        self._swin = glade_xml.get_object("swin")
        self._drawing_area = glade_xml.get_object("drawingarea")
        self._first_button = glade_xml.get_object("first")
        self._prev_button = glade_xml.get_object("prev")
        self._next_button = glade_xml.get_object("next")
        self._last_button = glade_xml.get_object("last")
        self._pages_entry = glade_xml.get_object("entry")
        self._pages_label = glade_xml.get_object("label")
        self._zoom_fit_width_button = glade_xml.get_object("zoom_fit_width")
        self._zoom_fit_width_button.set_stock_id("gramps-zoom-fit-width")
        self._zoom_best_fit_button = glade_xml.get_object("zoom_best_fit")
        self._zoom_best_fit_button.set_stock_id("gramps-zoom-best-fit")
        self._zoom_in_button = glade_xml.get_object("zoom_in")
        self._zoom_in_button.set_stock_id("gramps-zoom-in")
        self._zoom_out_button = glade_xml.get_object("zoom_out")
        self._zoom_out_button.set_stock_id("gramps-zoom-out")

        # connect the signals
        glade_xml.connect_signals(self)
        self._drawing_area.connect("draw", self.on_drawingarea_draw_event)

    ##def create_surface(self):
    ##return cairo.PDFSurface(StringIO(),
    ##self._context.get_width(),
    ##self._context.get_height())

    ##def get_page(self, page_no):
    ##"""Get the cairo surface of the given page.

    ##Surfaces are also cached for instant access.

    ##"""
    ##if page_no >= len(self._page_numbers):
    ##LOG.debug("Page number %d doesn't exist." % page_no)
    ##page_no = 0

    ##if page_no not in self._page_surfaces:
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

        self._pages_entry.set_text("%d" % (self._current_page + 1))

    def __set_zoom(self, zoom):
        self._zoom = zoom

        screen_width = int(self._paper_width * self._zoom + 2 * MARGIN)
        screen_height = int(self._paper_height * self._zoom + 2 * MARGIN)
        self._drawing_area.set_size_request(screen_width, screen_height)
        self._drawing_area.queue_draw()

        self._zoom_in_button.set_sensitive(self._zoom != max(self.zoom_factors))
        self._zoom_out_button.set_sensitive(self._zoom != min(self.zoom_factors))

    def __zoom_in(self):
        zoom = [z for z in self.zoom_factors if z > self._zoom]

        if zoom:
            return min(zoom)
        else:
            return self._zoom

    def __zoom_out(self):
        zoom = [z for z in self.zoom_factors if z < self._zoom]

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
        """Get the dimensions of the scrolled window."""
        width = self._swin.get_allocated_width() - 2 * MARGIN
        height = self._swin.get_allocated_height() - 2 * MARGIN

        if self._swin.get_shadow_type() != Gtk.ShadowType.NONE:
            width -= 2 * self._swin.get_style().xthickness
            height -= 2 * self._swin.get_style().ythickness

        spacing = GObject.Value()
        spacing.init(GObject.TYPE_INT)
        spacing = self._swin.style_get_property("scrollbar-spacing", spacing)
        if spacing:
            spacing = spacing.get_int()
        else:
            spacing = 0

        reqmin, req = self._swin.get_vscrollbar().get_preferred_size()
        vsb_w = spacing + req.width
        reqmin, req = self._swin.get_hscrollbar().get_preferred_size()
        hsb_h = spacing + req.height

        return width, height, vsb_w, hsb_h

    def __end_preview(self):
        self._operation.end_preview()

    # Signal handlers

    def on_drawingarea_draw_event(self, drawing_area, context):
        cr = context
        # cr.rectangle(event.area)
        # cr.clip()

        # get the extents of the page and the screen
        paper_w = int(self._paper_width * self._zoom)
        paper_h = int(self._paper_height * self._zoom)

        width, height, vsb_w, hsb_h = self.__get_view_size()
        if paper_h > height:
            width -= vsb_w
        if paper_w > width:
            height -= hsb_h

        # put the paper on the middle of the window
        xtranslate = MARGIN
        if paper_w < width:
            xtranslate += (width - paper_w) / 2

        ytranslate = MARGIN
        if paper_h < height:
            ytranslate += (height - paper_h) / 2

        cr.translate(xtranslate, ytranslate)

        # draw an empty white page
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(0, 0, paper_w, paper_h)
        cr.fill_preserve()
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.stroke()

        if self._orientation == Gtk.PageOrientation.LANDSCAPE:
            cr.rotate(radians(-90))
            cr.translate(-paper_h, 0)

        ##page_setup = self._context.get_page_setup()
        ##cr.translate(page_setup.get_left_margin(Gtk.Unit.POINTS),
        ##page_setup.get_top_margin(Gtk.Unit.POINTS))

        ##cr.set_source_surface(self.get_page(0))
        ##cr.paint()

        # draw the content of the currently selected page
        #     Here we use dpi scaling instead of scaling the cairo context,
        #     because it gives better result. In the latter case the distance
        #     of glyphs was changing.
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
        self._paper_width = page_setup.get_paper_width(Gtk.Unit.POINTS)
        self._paper_height = page_setup.get_paper_height(Gtk.Unit.POINTS)
        self._page_width = page_setup.get_page_width(Gtk.Unit.POINTS)
        self._page_height = page_setup.get_page_height(Gtk.Unit.POINTS)
        self._orientation = page_setup.get_orientation()

        # get the total number of pages
        ##self._page_numbers = [0,]
        ##self._page_surfaces = {}
        self._page_no = self._operation.get_property("n_pages")
        self._pages_label.set_text(_("of %d") % self._page_no)

        # set zoom level and initial page number
        self._zoom_mode = ZOOM_FREE
        self.__set_zoom(1.0)
        self.__set_page(0)

        # let's the show begin...
        self._window.show()


# ------------------------------------------------------------------------
#
# GtkPrint class
#
# ------------------------------------------------------------------------
class GtkPrint(libcairodoc.CairoDoc):
    """Print document via GtkPrint* interface.

    Requires Gtk+ 2.10.

    """

    def run(self):
        """Run the Gtk Print operation."""
        global PRINT_SETTINGS

        # get a page setup from the paper style we have
        page_setup = paperstyle_to_pagesetup(self.paper)

        # set up a print operation
        operation = Gtk.PrintOperation()
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
            res = operation.run(
                Gtk.PrintOperationAction.PRINT_DIALOG, self.uistate.window
            )
            if self.preview is None:  # cancel or print
                break
            # set up printing again; can't reuse PrintOperation?
            operation = Gtk.PrintOperation()
            operation.set_default_page_setup(page_setup)
            operation.connect("begin_print", self.on_begin_print)
            operation.connect("draw_page", self.on_draw_page)
            operation.connect("paginate", self.on_paginate)
            operation.connect("preview", self.on_preview)
            # set print settings if it was stored previously
            if PRINT_SETTINGS is not None:
                operation.set_print_settings(PRINT_SETTINGS)

        # store print settings if printing was successful
        if res == Gtk.PrintOperationResult.APPLY:
            PRINT_SETTINGS = operation.get_print_settings()

    def on_begin_print(self, operation, context):
        """Setup environment for printing."""
        # get data from context here only once to save time on pagination
        self.page_width = round(context.get_width())
        self.page_height = round(context.get_height())
        self.dpi_x = context.get_dpi_x()
        self.dpi_y = context.get_dpi_y()

    def on_paginate(self, operation, context):
        """Paginate the whole document in chunks."""
        layout = context.create_pango_layout()

        finished = self.paginate(
            layout, self.page_width, self.page_height, self.dpi_x, self.dpi_y
        )
        # update page number
        operation.set_n_pages(len(self._pages))

        # start preview if needed
        if finished and self.preview:
            self.preview.start()

        return finished

    def on_draw_page(self, operation, context, page_nr):
        """Draw the requested page."""
        cr = context.get_cairo_context()
        layout = context.create_pango_layout()
        width = round(context.get_width())
        height = round(context.get_height())
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()

        self.draw_page(page_nr, cr, layout, width, height, dpi_x, dpi_y)

    def on_preview(self, operation, preview, context, parent):
        """Implement custom print preview functionality."""
        ##if constfunc.win()':
        ##return False

        self.preview = PrintPreview(operation, preview, context, parent)

        # give a dummy cairo context to Gtk.PrintContext,
        # PrintPreview will update it with the real one
        try:
            width = int(round(context.get_width()))
        except ValueError:
            width = 0
        try:
            height = int(round(context.get_height()))
        except ValueError:
            height = 0
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(surface)
        context.set_cairo_context(cr, PRINTER_DPI, PRINTER_DPI)

        return True
