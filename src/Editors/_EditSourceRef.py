#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#               2009       Gary Burton
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import config
import gen.lib
from glade import Glade
from DisplayTabs import (NoteTab, GalleryTab, SourceBackRefList, 
                         DataEmbedList, RepoEmbedList)
from gui.widgets import (PrivacyButton, MonitoredEntry, MonitoredMenu, 
                     MonitoredDate)
from _EditReference import RefTab, EditReference

#-------------------------------------------------------------------------
#
# EditSourceRef class
#
#-------------------------------------------------------------------------
class EditSourceRef(EditReference):

    def __init__(self, state, uistate, track, source, source_ref, update):

        EditReference.__init__(self, state, uistate, track, source,
                               source_ref, update)

    def _local_init(self):
        self.width_key = 'interface.event-ref-width'
        self.height_key = 'interface.event-ref-height'
        
        self.top = Glade()
        
        self.set_window(self.top.toplevel,
                        self.top.get_object('source_title'),        
                        _('Source Reference Editor'))

        self.define_warn_box(self.top.get_object("warn_box"))
        self.define_expander(self.top.get_object("src_expander"))

        tblref =  self.top.get_object('table67')
        notebook = self.top.get_object('notebook_ref')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.reftab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)
        tblref =  self.top.get_object('table68')
        notebook = self.top.get_object('notebook_src')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.primtab = RefTab(self.dbstate, self.uistate, self.track, 
                              _('General'), tblref)

    def _connect_signals(self):
        self.define_ok_button(self.top.get_object('ok'),self.ok_clicked)
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_help_button(self.top.get_object("help"))

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected. 
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('source-rebuild', self.close)
        self._add_db_signal('source-delete', self.check_for_close)
        #note: at the moment, a source cannot be updated while an editor with
        #   that source shown is open. So no need to connect to source-update

    def _setup_fields(self):
        self.ref_privacy = PrivacyButton(
            self.top.get_object('privacy'), self.source_ref, self.db.readonly)

        self.volume = MonitoredEntry(
            self.top.get_object("volume"), self.source_ref.set_page,
            self.source_ref.get_page, self.db.readonly)
        
        self.gid = MonitoredEntry(
            self.top.get_object('gid'), self.source.set_gramps_id,
            self.source.get_gramps_id,self.db.readonly)
        
        self.source_privacy = PrivacyButton(
            self.top.get_object("private"),
            self.source, self.db.readonly)

        self.title = MonitoredEntry(
            self.top.get_object('title'), 
            self.source.set_title,
            self.source.get_title,
            self.db.readonly)
        
        self.abbrev = MonitoredEntry(
            self.top.get_object('abbrev'), self.source.set_abbreviation,
            self.source.get_abbreviation,self.db.readonly)

        self.author = MonitoredEntry(
            self.top.get_object('author'), self.source.set_author,
            self.source.get_author,self.db.readonly)
        
        self.pubinfo = MonitoredEntry(
            self.top.get_object('pub_info'), self.source.set_publication_info,
            self.source.get_publication_info,self.db.readonly)

        self.type_mon = MonitoredMenu(
            self.top.get_object('confidence'),
            self.source_ref.set_confidence_level,
            self.source_ref.get_confidence_level, [
            (_('Very Low'), gen.lib.SourceRef.CONF_VERY_LOW),
            (_('Low'), gen.lib.SourceRef.CONF_LOW),
            (_('Normal'), gen.lib.SourceRef.CONF_NORMAL),
            (_('High'), gen.lib.SourceRef.CONF_HIGH),
            (_('Very High'), gen.lib.SourceRef.CONF_VERY_HIGH)],
            self.db.readonly)

        self.date = MonitoredDate(
            self.top.get_object("date_entry"),
            self.top.get_object("date_stat"), 
            self.source_ref.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

    def _create_tabbed_pages(self):
        """
        Create the notebook tabs and inserts them into the main
        window.
        """
        notebook_src = self.top.get_object('notebook_src')
        notebook_ref = self.top.get_object('notebook_ref')

        self._add_tab(notebook_src, self.primtab)
        self._add_tab(notebook_ref, self.reftab)

        self.note_tab = self._add_tab(
            notebook_src,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source.get_note_list(), 
                    notetype=gen.lib.NoteType.SOURCE))
        
        self.gallery_tab = self._add_tab(
            notebook_src,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.source.get_media_list()))
        
        self.data_tab = self._add_tab(
            notebook_src,
            DataEmbedList(self.dbstate, self.uistate, self.track,
                          self.source))
                                       
        self.repo_tab = self._add_tab(
            notebook_src,
            RepoEmbedList(self.dbstate, self.uistate, self.track,
                          self.source.get_reporef_list()))
        
        self.srcref_list = self._add_tab(
            notebook_src,
            SourceBackRefList(self.dbstate,self.uistate, self.track,
                              self.db.find_backlink_handles(self.source.handle),
                              self.enable_warnbox
                              ))

        self.comment_tab = self._add_tab(
            notebook_ref,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source_ref.get_note_list(),
                    notetype=gen.lib.NoteType.SOURCEREF))

        self._setup_notebook_tabs( notebook_src)
        self._setup_notebook_tabs( notebook_ref)

    def build_menu_names(self,sourceref):
        if self.source:
            source_name = self.source.get_title()
            submenu_label = _('Source: %s')  % source_name
        else:
            submenu_label = _('New Source')
        return (_('Source Reference Editor'),submenu_label)
        
    def ok_clicked(self, obj):

        trans = self.db.transaction_begin()
        if self.source.handle:
            self.db.commit_source(self.source,trans)
            self.db.transaction_commit(trans,_("Modify Source"))
        else:
            self.db.add_source(self.source,trans)
            self.db.transaction_commit(trans,_("Add Source"))

        if self.update:
            self.update(self.source_ref,self.source)

        self.close()
