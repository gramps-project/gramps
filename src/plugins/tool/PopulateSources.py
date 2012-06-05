#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011       Tim G L Lyons
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

"""Tools/Debug/Populate sources and citations"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gui.utils import ProgressMeter
from gui.plug import tool
from QuestionDialog import OkDialog
from gui.managedwindow import ManagedWindow
import gen.lib
from gen.db import DbTxn

class PopulateSources(tool.Tool, ManagedWindow):
    """
    Gramplet that populates the database with sources and citations.
    """
    
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.label = 'Populate sources and citations tool'
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(gtk.Window(), gtk.Label(), '')
        tool.Tool.__init__(self, dbstate, options_class, name)
        
        dialog = self.display()
        response = dialog.run()
        dialog.destroy()
        
        if response == gtk.RESPONSE_ACCEPT:
            self.on_ok_clicked()
            OkDialog('Data generated',
                     "The requested sources and citations were generated")

        self.close()

    def display(self):
        """
        Constructs the GUI, consisting of a message, and fields to enter the
        required number of sources and citations
        """

        # retrieve options
        num_sources = self.options.handler.options_dict['sources']
        num_citations = self.options.handler.options_dict['citations']

        # GUI setup:
        dialog = gtk.Dialog("Populate sources and citations tool",
                                self.uistate.window,
                                gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                 gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        label = gtk.Label("Enter a valid number of sources and citations."
                          " This will create the requested number of sources,"
                          " and for each source, will create the requested"
                          " number of citations.")
        label.set_line_wrap(True)

        hbox1 = gtk.HBox()
        label_sources = gtk.Label("Number of sources" + ":")
        self.sources_entry = gtk.Entry()
        self.sources_entry.set_text("%d" % num_sources)
        hbox1.pack_start(label_sources, False)
        hbox1.pack_start(self.sources_entry, True)

        hbox2 = gtk.HBox()
        label_citations = gtk.Label("Number of citations" + ":")
        self.citations_entry = gtk.Entry()
        self.citations_entry.set_text("%d" % num_citations)
        hbox2.pack_start(label_citations, False)
        hbox2.pack_start(self.citations_entry, True)
        
        vbox = gtk.VBox()
        vbox.pack_start(label, True)
        vbox.pack_start(hbox1, False)
        vbox.pack_start(hbox2, False)

        dialog.vbox.set_spacing(10)
        dialog.vbox.pack_start(vbox)
        dialog.show_all()
        return dialog
    
    def on_ok_clicked(self):
        """
        Method that is run when you click the OK button. The numbers of sources
        and citations are retrieved from the entry box and used to govern the
        amount of data generated
        """
      
        num_sources_text = self.sources_entry.get_text()
        num_sources = int(num_sources_text)
        num_citations_text = self.citations_entry.get_text()
        num_citations = int(num_citations_text)
        
        self.progress = ProgressMeter(
            'Generating data', '')
        self.progress.set_pass('Generating data',
                               num_sources*num_citations)
        LOG.debug("sources %04d citations %04d" % (num_sources, 
                                                     num_citations))
        
        source = gen.lib.Source()
        citation = gen.lib.Citation()
        
        self.db.disable_signals()
        with DbTxn('Populate sources and citations', self.db) as trans:
            for i in range(num_sources):
                source.gramps_id = None
                source.handle = None
                source.title = "Source %04d" % (i + 1)
                source_handle = self.db.add_source(source, trans)
                
                for j in range(num_citations):
                    citation.gramps_id = None
                    citation.handle = None
                    citation.source_handle = source_handle
                    citation.page = "Page %04d" % (j + 1)
                    self.db.add_citation(citation, trans)
                    self.progress.step()
            LOG.debug("sources and citations added")
        self.db.enable_signals()
        self.db.request_rebuild()
        self.progress.close()
        
        self.options.handler.options_dict['sources'] = num_sources
        self.options.handler.options_dict['citations'] = num_citations
        # Save options
        self.options.handler.save_options()

class PopulateSourcesOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)

        # Options specific for this report
        self.options_dict = {
            'sources'   : 2,
            'citations' : 2,
        }
        self.options_help = {
            'sources'   : ("=num", 
                           "Number of sources to generate", 
                           "Integer number"),
            'citations' : ("=num",
                           "Number of citations to generate for each source",
                           "Integer number")
            }
