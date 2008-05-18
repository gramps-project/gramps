#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007 Zsolt Foldvari
# Copyright (C) 2008 Brian G. Matherly
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

"""PDF output generator based on Cairo.
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from CairoDoc import CairoDoc
from PluginUtils import PluginManager
import Utils
import Mime

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".PdfDoc")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import pango
import cairo
import pangocairo

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

# resolution
DPI = 72.0

#------------------------------------------------------------------------
#
# PdfDoc class
#
#------------------------------------------------------------------------
class PdfDoc(CairoDoc):
    """Render the document into PDF file using Cairo.
    """
    def run(self):
        """Create the PDF output.
        """
        # get paper dimensions
        paper_width = self.paper.get_size().get_width() * DPI / 2.54
        paper_height = self.paper.get_size().get_height() * DPI / 2.54
        page_width = round(self.paper.get_usable_width() * DPI / 2.54)
        page_height = round(self.paper.get_usable_height() * DPI / 2.54)
        left_margin = self.paper.get_left_margin() * DPI / 2.54
        top_margin = self.paper.get_top_margin() * DPI / 2.54

        # create cairo context and pango layout
        surface = cairo.PDFSurface(self._filename, paper_width, paper_height)
        surface.set_fallback_resolution(300, 300)
        cr = pangocairo.CairoContext(cairo.Context(surface))

        fontmap = pangocairo.cairo_font_map_get_default()
        saved_resolution = fontmap.get_resolution()
        fontmap.set_resolution(DPI)
        
        pango_context = fontmap.create_context()
        options = cairo.FontOptions()
        options.set_hint_metrics(cairo.HINT_METRICS_OFF)
        pangocairo.context_set_font_options(pango_context, options)
        layout = pango.Layout(pango_context)
        cr.update_context(pango_context)
        
        # paginate the document
        finished = self.paginate(layout, page_width, page_height, DPI, DPI)
        while not finished:
            finished = self.paginate(layout, page_width, page_height, DPI, DPI)

        # render the pages
        for page_nr in range(len(self._pages)):
            cr.save()
            cr.translate(left_margin, top_margin)
            self.draw_page(page_nr, cr, layout,
                           page_width, page_height,
                           DPI, DPI)
            cr.show_page()
            cr.restore()
            
        # close the surface (file)
        surface.finish()
        
        # Restore the resolution. On windows, Gramps UI fonts will be smaller
        # if we don't restore the resolution.
        fontmap.set_resolution(saved_resolution)

        # load the result into an external viewer
        if self.print_req:
            app = Mime.get_application('application/pdf')
            Utils.launch(app[0], self._filename) 
            
#------------------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------------------
def register_docgen():
    """Register the docgen with the GRAMPS plugin system.
    """
    try:
        mprog = Mime.get_application("application/pdf")
        mtype = Mime.get_description("application/pdf")
        
        if Utils.search_for(mprog[0]):
            print_label = _("Open in %s") % mprog[1]
        else:
            print_label = None
    except:
        mtype = _('PDF document')
        print_label = None
        
    pmgr = PluginManager.get_instance()
    pmgr.register_text_doc(mtype, PdfDoc, 1, 1, 1, ".pdf", print_label)
    pmgr.register_draw_doc(mtype, PdfDoc, 1, 1, ".pdf", print_label)
    pmgr.register_book_doc(mtype, PdfDoc, 1, 1, 1, ".pdf", print_label)

register_docgen()