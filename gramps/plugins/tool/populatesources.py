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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

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
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import COLON, GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gui.utils import ProgressMeter
from gramps.gui.plug import tool
from gramps.gui.dialog import OkDialog
from gramps.gui.managedwindow import ManagedWindow
from gramps.gen.lib import Citation, Source
from gramps.gen.db import DbTxn

class PopulateSources(tool.Tool, ManagedWindow):
    """
    Tool that populates the database with sources and citations.
    """

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.label = 'Populate sources and citations tool'
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        self.set_window(Gtk.Window(), Gtk.Label(), '')
        tool.Tool.__init__(self, dbstate, options_class, name)

        dialog = self.display()
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.ACCEPT:
            self.on_ok_clicked()
            OkDialog('Data generated',
                     "The requested sources and citations were generated",
                     parent=uistate.window)

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
        dialog = Gtk.Dialog(title="Populate sources and citations tool",
                            transient_for=self.uistate.window,
                            modal=True, destroy_with_parent=True)
        dialog.add_buttons(_('_Cancel'), Gtk.ResponseType.REJECT,
                           _('_OK'), Gtk.ResponseType.ACCEPT)
        label = Gtk.Label(
            label="Enter a valid number of sources and citations."
            " This will create the requested number of sources,"
            " and for each source, will create the requested"
            " number of citations.")
        label.set_line_wrap(True)

        hbox1 = Gtk.Box()
        label_sources = Gtk.Label(label="Number of sources" + COLON)
        self.sources_entry = Gtk.Entry()
        self.sources_entry.set_text("%d" % num_sources)
        hbox1.pack_start(label_sources, False, True, 0)
        hbox1.pack_start(self.sources_entry, True, True, 0)

        hbox2 = Gtk.Box()
        label_citations = Gtk.Label(label="Number of citations" + COLON)
        self.citations_entry = Gtk.Entry()
        self.citations_entry.set_text("%d" % num_citations)
        hbox2.pack_start(label_citations, False, True, 0)
        hbox2.pack_start(self.citations_entry, True, True, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(label, True, True, 0)
        vbox.pack_start(hbox1, False, True, 0)
        vbox.pack_start(hbox2, False, True, 0)

        dialog.vbox.set_spacing(10)
        dialog.vbox.pack_start(vbox, True, True, 0)
        dialog.show_all()
        return dialog

    def on_ok_clicked(self):
        """
        Method that is run when you click the OK button. The numbers of sources
        and citations are retrieved from the entry box and used to govern the
        amount of data generated
        """

        num_sources_text = self.sources_entry.get_text()
        try:
            num_sources = int(num_sources_text)
        except:
            return
        num_citations_text = self.citations_entry.get_text()
        num_citations = int(num_citations_text)

        self.progress = ProgressMeter(
            'Generating data', '', parent=self.uistate.window)
        self.progress.set_pass('Generating data',
                               num_sources*num_citations)
        LOG.debug("sources %04d citations %04d" % (num_sources,
                                                     num_citations))

        source = Source()
        citation = Citation()

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
