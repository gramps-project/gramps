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

# $Id$

"""
Gramplet that populates the database with sources and citations.
"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".citation")

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import Gramplet
from gen.ggettext import sgettext as _
import DateHandler
from QuickReports import run_quick_report_by_name
import gen.lib
from gen.db import DbTxn

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class PopulateGramplet(Gramplet):
    """
    Gramplet that populates the database with sources and citations.
    """
    def init(self):
        """
        Constructs the GUI, consisting of a message, an entry, and 
        a Run button.
        """
        import gtk
        # GUI setup:
        self.set_tooltip(_("Enter a date, click Run"))
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        # label, entry
        description = gtk.TextView()
        description.set_wrap_mode(gtk.WRAP_WORD)
        description.set_editable(False)
        buffer = description.get_buffer()
        buffer.set_text(_("Enter a valid number of sources and citations."
                          " This will create the requested number of sources,"
                          " and for each source, will create the requested"
                          " number of citations."))
        label_sources = gtk.Label()
        label_sources.set_text(_("Number of sources") + ":")
        self.num_sources = gtk.Entry()
        label_citations = gtk.Label()
        label_citations.set_text(_("Number of citations") + ":")
        self.num_citations = gtk.Entry()
        button = gtk.Button(_("Run"))
        button.connect("clicked", self.run)
        ##self.filter = 
        hbox.pack_start(label_sources, False)
        hbox.pack_start(self.num_sources, True)
        hbox.pack_start(label_citations, False)
        hbox.pack_start(self.num_citations, True)
        vbox.pack_start(description, True)
        vbox.pack_start(hbox, False)
        vbox.pack_start(button, False)
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(vbox)
        vbox.show_all()

    def post_init(self):
        self.disconnect("active-changed")

    def run(self, obj):
        """
        Method that is run when you click the Run button.
        The date is retrieved from the entry box, parsed as a date,
        and then handed to the quick report.
        """
        num_sources_text = self.num_sources.get_text()
        num_sources = int(num_sources_text)
        num_citations_text = self.num_citations.get_text()
        num_citations = int(num_citations_text)
        
        LOG.debug("sources %04d citations %04d" % (num_sources, 
                                                     num_citations))
        
        source = gen.lib.Source()
        citation = gen.lib.Citation()
        db = self.gui.dbstate.db
        
        db.disable_signals()
        with DbTxn('Populate citations', db) as trans:
            for i in range(num_sources):
                source.gramps_id = None
                source.handle = None
                source.title = "Source %04d" % (i + 1)
                source_handle = db.add_source(source, trans)
                
                for j in range(num_citations):
                    citation.gramps_id = None
                    citation.handle = None
                    citation.source_handle = source_handle
                    citation.page = "Page %04d" % (j + 1)
                    db.add_citation(citation, trans)
            LOG.debug("sources and citations added")
        db.enable_signals()
        db.request_rebuild()
        
