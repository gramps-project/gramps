# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2009 Serge Noiraud
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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
import cairo
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

# the print settings to remember between print sessions
PRINT_SETTINGS = None

#------------------------------------------------------------------------
#
# CairoPrintSave class
#
#------------------------------------------------------------------------
class CairoPrintSave():
    """Act as an abstract document that can render onto a cairo context.
    
    It can render the model onto cairo context pages, according to the received
    page style.
        
    """
    
    def __init__(self, widthpx, heightpx, drawfunc, parent):
        """
        This class provides the things needed so as to dump a cairo drawing on
        a context to output
        """
        self.widthpx = widthpx
        self.heightpx = heightpx
        self.drawfunc = drawfunc
        self.parent = parent
    
    def run(self):
        """Create the physical output from the meta document.
                
        """
        global PRINT_SETTINGS
        
        # set up a print operation
        operation = Gtk.PrintOperation()
        operation.connect("draw_page", self.on_draw_page)
        operation.connect("preview", self.on_preview)
        operation.connect("paginate", self.on_paginate)
        operation.set_n_pages(1)
        #paper_size = Gtk.PaperSize.new(name="iso_a4")
        ## WHY no Gtk.Unit.PIXEL ?? Is there a better way to convert 
        ## Pixels to MM ??
        paper_size = Gtk.PaperSize.new_custom("custom",
                                              "Custom Size",
                                              round(self.widthpx * 0.2646),
                                              round(self.heightpx * 0.2646),
                                              Gtk.Unit.MM)
        page_setup = Gtk.PageSetup()
        page_setup.set_paper_size(paper_size)
        #page_setup.set_orientation(Gtk.PageOrientation.PORTRAIT)
        operation.set_default_page_setup(page_setup)
        #operation.set_use_full_page(True)
        
        if PRINT_SETTINGS is not None:
            operation.set_print_settings(PRINT_SETTINGS)
        
        # run print dialog
        while True:
            self.preview = None
            res = operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, None)
            if self.preview is None: # cancel or print
                break
            # set up printing again; can't reuse PrintOperation?
            operation = Gtk.PrintOperation()
            operation.set_default_page_setup(page_setup)
            operation.connect("draw_page", self.on_draw_page)
            operation.connect("preview", self.on_preview)
            operation.connect("paginate", self.on_paginate)
            # set print settings if it was stored previously
            if PRINT_SETTINGS is not None:
                operation.set_print_settings(PRINT_SETTINGS)

        # store print settings if printing was successful
        if res == Gtk.PrintOperationResult.APPLY:
            PRINT_SETTINGS = operation.get_print_settings()
    
    def on_draw_page(self, operation, context, page_nr):
        """Draw a page on a Cairo context.
        """
        cr = context.get_cairo_context()
        self.drawfunc(self.parent, cr)

    def on_paginate(self, operation, context):
        """Paginate the whole document in chunks.
           We don't need this as there is only one page, however,
           we provide a dummy holder here, because on_preview crashes if no 
           default application is set with gir 3.3.2 (typically evince not installed)!
           It will provide the start of the preview dialog, which cannot be
           started in on_preview
        """
        finished = True
        # update page number
        operation.set_n_pages(1)
        
        # start preview if needed
        if self.preview:
            self.preview.run()
            
        return finished

    def on_preview(self, operation, preview, context, parent):
        """Implement custom print preview functionality.
           We provide a dummy holder here, because on_preview crashes if no 
           default application is set with gir 3.3.2 (typically evince not installed)!
        """
        dlg = Gtk.MessageDialog(parent,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.WARNING,
                                   buttons=Gtk.ButtonsType.CLOSE,
                                   message_format=_('No preview available'))
        self.preview = dlg
        self.previewopr = operation
        #dlg.format_secondary_markup(msg2)
        dlg.set_title("Map Preview - Gramps")
        dlg.connect('response', self.previewdestroy)
        
        # give a dummy cairo context to Gtk.PrintContext,
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
        context.set_cairo_context(cr, 72.0, 72.0)
        
        return True 

    def previewdestroy(self, dlg, res):
        self.preview.destroy()
        self.previewopr.end_preview()
