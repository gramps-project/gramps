#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

try:
    set()
except:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import AutoComp
import RelLib
import DisplayState

from QuestionDialog import WarningDialog, ErrorDialog
from WindowUtils import GladeIf
from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditSourceRef class
#
#-------------------------------------------------------------------------
class EditSourceRef(DisplayState.ManagedWindow):
    def __init__(self, state, uistate, track, 
                 source, source_ref, update):
        self.db = state.db
        self.state = state
        self.uistate = uistate
        self.source_ref = source_ref
        self.source = source

        DisplayState.ManagedWindow.__init__(self, uistate, track, source_ref)

        self.update = update

        self.title = _('Source Reference Editor')

        self.top = gtk.glade.XML(const.gladeFile, "source_ref_edit","gramps")
        self.window = self.top.get_widget('source_ref_edit')
        
        self.notebook_src = self.top.get_widget('notebook_src')
        self.notebook_ref = self.top.get_widget('notebook_ref')

        expander = self.top.get_widget("src_expander")
        expander.set_expanded(True)

        warning = self.top.get_widget("warn_box")
        if self.source.handle:
            warning.show_all()
        else:
            warning.hide()

        if self.source:
            self.source_added = False
        else:
            self.source = RelLib.Source()
            self.source.set_handle(self.db.create_id())
            self.source_added = True

        if not self.source_ref:
            self.source_ref = RelLib.SourceRef()
            self.source_ref.set_reference_handle(self.source.get_handle())

        Utils.set_titles(self.window, self.top.get_widget('source_title'),
                         self.title)

        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        self.show()

    def _connect_signals(self):
        self.top.get_widget('ok').connect('clicked',self.ok_clicked)
        self.top.get_widget('cancel').connect('clicked',self.cancel_clicked)
        
    def _setup_fields(self):
        self.privacy = PrivacyButton(
            self.top.get_widget('privacy'), self.source_ref)

        self.volume = MonitoredEntry(
            self.top.get_widget("volume"), self.source_ref.set_page,
            self.source_ref.get_page, False)
        
        self.gid = MonitoredEntry(
            self.top.get_widget('gid'), self.source.set_gramps_id,
            self.source.get_gramps_id,False)
        
        self.title = MonitoredEntry(
            self.top.get_widget('title'), self.source.set_title,
            self.source.get_title,False)
        
        self.abbrev = MonitoredEntry(
            self.top.get_widget('abbrev'), self.source.set_abbreviation,
            self.source.get_abbreviation,False)

        self.author = MonitoredEntry(
            self.top.get_widget('author'), self.source.set_author,
            self.source.get_author,False)
        
        self.pubinfo = MonitoredEntry(
            self.top.get_widget('pub_info'), self.source.set_publication_info,
            self.source.get_publication_info,False)

        self.text_data = MonitoredText(
            self.top.get_widget('text'), self.source_ref.set_text,
            self.source_ref.get_text,False)

        self.type_mon = MonitoredMenu(
            self.top.get_widget('confidence'), self.source_ref.set_confidence_level,
            self.source_ref.get_confidence_level, [
            (_('Very Low'), RelLib.SourceRef.CONF_VERY_LOW),
            (_('Low'), RelLib.SourceRef.CONF_LOW),
            (_('Normal'), RelLib.SourceRef.CONF_NORMAL),
            (_('High'), RelLib.SourceRef.CONF_HIGH),
            (_('Very High'), RelLib.SourceRef.CONF_VERY_HIGH)])


        self.date = MonitoredDate(self.top.get_widget("date"),
                                  self.top.get_widget("date_stat"), 
                                  self.source_ref.get_date_object(),self.window)

    def _add_source_page(self,page):
        self.notebook_src.insert_page(page)
        self.notebook_src.set_tab_label(page,page.get_tab_widget())
        return page

    def _add_ref_page(self,page):
        self.notebook_ref.insert_page(page)
        self.notebook_ref.set_tab_label(page,page.get_tab_widget())
        return page

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """
        self.note_tab = self._add_source_page(NoteTab(
            self.state, self.uistate, self.track,
            self.source.get_note_object()))
        self.gallery_tab = self._add_source_page(GalleryTab(
            self.state, self.uistate, self.track,
            self.source.get_media_list()))
        self.srcref_list = self._add_source_page(SourceBackRefList(
            self.state,self.uistate, self.track,
            self.db.find_backlink_handles(self.source.handle)))

        self.comment_tab = self._add_ref_page(NoteTab(
            self.state, self.uistate, self.track,
            self.source_ref.get_note_object(),_('Comments')))

    def build_menu_names(self,sourceref):
        if self.source:
            source_name = self.source.get_title()
            submenu_label = _('Source: %s')  % source_name
        else:
            submenu_label = _('New Source')
        return (_('Source Reference Editor'),submenu_label)
        
    def build_window_key(self,sourceref):
        if self.source:
            return self.source.get_handle()
        else:
            return id(self)

    def on_help_clicked(self,obj):
        pass

    def ok_clicked(self,obj):

        trans = self.db.transaction_begin()
        self.db.commit_source(self.source,trans)
        if self.source_added:
            self.db.transaction_commit(trans,_("Add Source"))
        else:
            self.db.transaction_commit(trans,_("Modify Source"))
        self.close(None)

        if self.update:
            self.update((self.source_ref,self.source))

    def cancel_clicked(self,obj):
        self.close()

