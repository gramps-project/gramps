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
import Sources
import Witness
import const
import Utils
import AutoComp
import RelLib
from DateHandler import parser as _dp, displayer as _dd
import DateEdit
import GrampsDisplay
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
        if self.already_exist:
            return

        self.update = update

        self.title = _('Source Reference Editor')

        self.top = gtk.glade.XML(const.gladeFile, "source_ref_edit","gramps")
        self.window = self.top.get_widget('source_ref_edit')
        
        self.ref_note_field = self.top.get_widget('eer_ref_note')
        self.role_combo = self.top.get_widget('eer_role_combo')
        self.date_field  = self.top.get_widget("eer_date")
        self.place_field = self.top.get_widget("eer_place")
        self.cause_field = self.top.get_widget("eer_cause")
        self.ev_note_field = self.top.get_widget("eer_ev_note")
        self.type_combo = self.top.get_widget("eer_type_combo")
        self.general_label = self.top.get_widget("eer_general_tab")
        self.ok = self.top.get_widget('ok')
        self.expander = self.top.get_widget("src_expander")
        self.warning = self.top.get_widget("warn_box")
        self.notebook = self.top.get_widget('notebook')

        if self.source:
            self.source_added = False
            if self.source_ref:
                self.expander.set_expanded(False)
                self.warning.show_all()
        else:
            self.source = RelLib.Source()
            self.source.set_handle(self.db.create_id())
            self.source_added = True
            self.expander.set_expanded(True)
            self.warning.hide()

        if not self.source_ref:
            self.source_ref = RelLib.SourceRef()
            self.source_ref.set_reference_handle(self.source.get_handle())

        self.privacy = PrivacyButton(self.top.get_widget('privacy'),
                                     self.source_ref)

        self.volume = MonitoredEntry(self.top.get_widget("volume"),
                                     self.source.set_volume,
                                     self.source.get_volume, False)

        Utils.set_titles(self.window, self.top.get_widget('source_title'),
                         self.title)

        self.date_check = DateEdit.DateEdit(
            self.date, self.date_field,
            self.top.get_widget("date_stat"), self.window)

        self.date_field.set_text(_dd.display(self.date))

        self._create_tabbed_pages()

        self.show()

    def _add_page(self,page):
        self.notebook.insert_page(page)
        self.notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """

        self.srcref_list = self._add_page(SourceEmbedList(
            self.state,self.uistate, self.track,
            self.source.source_list))
        self.note_tab = self._add_page(NoteTab(
            self.state, self.uistate, self.track,
            self.source.get_note_object()))
        self.gallery_tab = self._add_page(GalleryTab(
            self.state, self.uistate, self.track,
            self.source.get_media_list()))

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

    def on_ok_clicked(self,obj):

        # first, save source if changed
        etype = self.type_selector.get_values()
        eplace_obj = get_place(self.place_field,self.pmap,self.db)
        self.update_source(etype,self.date,eplace_obj)
        
        trans = self.db.transaction_begin()
        self.db.commit_source(self.source,trans)
        if self.source_added:
            self.db.transaction_commit(trans,_("Add Source"))
        else:
            self.db.transaction_commit(trans,_("Modify Source"))
        
        # then, set properties of the source_ref
        self.source_ref.set_role(self.role_selector.get_values())
        self.source_ref.set_privacy(self.ref_privacy.get_active())
        self.close(None)

        if self.update:
            self.update((self.source_ref,self.source))

    def update_source(self,the_type,date,place):
        if place:
            if self.source.get_place_handle() != place.get_handle():
                self.source.set_place_handle(place.get_handle())
        else:
            if self.source.get_place_handle():
                self.source.set_place_handle("")
        
        if self.source.get_type() != the_type:
            self.source.set_type(the_type)
        
        dobj = self.source.get_date_object()

        if not dobj.is_equal(date):
            self.source.set_date_object(date)

