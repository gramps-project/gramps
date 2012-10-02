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
from gramps.gen.ggettext import gettext as _
import sys

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
import gramps.plugins.lib.libcairodoc as libcairodoc
from gramps.gen.plug.docgen import INDEX_TYPE_ALP, INDEX_TYPE_TOC
from gramps.gen.errors import ReportError

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
from gi.repository import Pango, PangoCairo
import cairo

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
class PdfDoc(libcairodoc.CairoDoc):
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
        filename = self._backend.filename.encode(sys.getfilesystemencoding())
        try:
            surface = cairo.PDFSurface(filename, paper_width, paper_height)
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % filename, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % filename)
        surface.set_fallback_resolution(300, 300)
        cr = cairo.Context(surface)
        fontmap = PangoCairo.font_map_new()
        fontmap.set_resolution(DPI)
        pango_context = fontmap.create_context()
        options = cairo.FontOptions()
        options.set_hint_metrics(cairo.HINT_METRICS_OFF)
        PangoCairo.context_set_font_options(pango_context, options)
        layout = Pango.Layout(pango_context)
        PangoCairo.update_context(cr, pango_context)
        # paginate the document
        self.paginate_document(layout, page_width, page_height, DPI, DPI)
        body_pages = self._pages

        # build the table of contents and alphabetical index
        toc_page = None
        index_page = None
        toc = []
        index = {}
        for page_nr, page in enumerate(body_pages):
            if page.has_toc():
                toc_page = page_nr
            if page.has_index():
                index_page = page_nr
            for mark in page.get_marks():
                if mark.type == INDEX_TYPE_ALP:
                    if mark.key in index:
                        if page_nr + 1 not in index[mark.key]:
                            index[mark.key].append(page_nr + 1)
                    else:
                        index[mark.key] = [page_nr + 1]
                elif mark.type == INDEX_TYPE_TOC:
                    toc.append([mark, page_nr + 1])

        # paginate the table of contents
        rebuild_required = False
        if toc_page is not None:
            toc_pages = self.__generate_toc(layout, page_width, page_height, 
                                            toc)
            offset = len(toc_pages) - 1
            if offset > 0:
                self.__increment_pages(toc, index, toc_page, offset)
                rebuild_required = True
        else:
            toc_pages = []
        
        # paginate the index
        if index_page is not None:
            index_pages = self.__generate_index(layout, page_width, page_height,
                                                index)
            offset = len(index_pages) - 1
            if offset > 0:
                self.__increment_pages(toc, index, index_page, offset)
                rebuild_required = True
        else:
            index_pages = []
            
        # rebuild the table of contents and index if required
        if rebuild_required:
            if toc_page is not None:
                toc_pages = self.__generate_toc(layout, page_width, page_height, 
                                                toc)
            if index_page is not None:
                index_pages = self.__generate_index(layout, page_width, 
                                                    page_height, index)

        # render the pages
        if toc_page is not None:
            body_pages = body_pages[:toc_page] + toc_pages + \
                         body_pages[toc_page+1:]
        if index_page is not None:
            body_pages = body_pages[:index_page] + index_pages + \
                         body_pages[index_page+1:]
        self._pages = body_pages
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

    def __increment_pages(self, toc, index, start_page, offset):
        """
        Increment the page numbers in the table of contents and index.
        """
        for n, value in enumerate(toc):
            page_nr = toc[n][1]
            toc[n][1] = page_nr + (offset if page_nr > start_page else 0)
        for key, value in index.iteritems():
            index[key] = [page_nr + (offset if page_nr > start_page else 0)
                          for page_nr in value]

    def __generate_toc(self, layout, page_width, page_height, toc):
        """
        Generate the table of contents.
        """
        self._doc = libcairodoc.GtkDocDocument()
        self._active_element = self._doc
        self._pages = []
        write_toc(toc, self)
        self.paginate_document(layout, page_width, page_height, DPI, DPI)
        return self._pages

    def __generate_index(self, layout, page_width, page_height, index):
        """
        Generate the index.
        """
        self._doc = libcairodoc.GtkDocDocument()
        self._active_element = self._doc
        self._pages = []
        write_index(index, self)
        self.paginate_document(layout, page_width, page_height, DPI, DPI)
        return self._pages
        
def write_toc(toc, doc):
    """
    Write the table of contents.
    """
    if not toc:
        return

    doc.start_paragraph('TOC-Title')
    doc.write_text(_('Contents'))
    doc.end_paragraph()
    
    doc.start_table('toc', 'TOC-Table')
    for mark, page_nr in toc:
        doc.start_row()
        doc.start_cell('TOC-Cell')
        if mark.level == 1:
            style_name = "TOC-Heading1"
        elif mark.level == 2:
            style_name = "TOC-Heading2"
        else:
            style_name = "TOC-Heading3"
        doc.start_paragraph(style_name)
        doc.write_text(mark.key)
        doc.end_paragraph()
        doc.end_cell()
        doc.start_cell('TOC-Cell')
        doc.start_paragraph(style_name)
        doc.write_text(str(page_nr))
        doc.end_paragraph()
        doc.end_cell()
        doc.end_row()
    doc.end_table()
    
def write_index(index, doc):
    """
    Write the alphabetical index.
    """
    if not index:
        return

    doc.start_paragraph('IDX-Title')
    doc.write_text(_('Index'))
    doc.end_paragraph()
    
    doc.start_table('index', 'IDX-Table')
    for key in sorted(index.iterkeys()):
        doc.start_row()
        doc.start_cell('IDX-Cell')
        doc.start_paragraph('IDX-Entry')
        doc.write_text(key)
        doc.end_paragraph()
        doc.end_cell()
        doc.start_cell('IDX-Cell')
        doc.start_paragraph('IDX-Entry')
        pages = [str(page_nr) for page_nr in index[key]]
        doc.write_text(', '.join(pages))
        doc.end_paragraph()
        doc.end_cell()
        doc.end_row()
    doc.end_table()
