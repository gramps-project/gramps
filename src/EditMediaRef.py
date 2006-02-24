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
# Standard python modules
#
#-------------------------------------------------------------------------
import urlparse
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import GrampsKeys
import NameDisplay
import PluginMgr
import RelLib
import RelImage
import ListModel
import GrampsMime
import ImgManip
import DisplayState
import GrampsDisplay

from QuestionDialog import ErrorDialog
from DdTargets import DdTargets
from WindowUtils import GladeIf

import DisplayState
from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# LocalMediaProperties
#
#-------------------------------------------------------------------------
class EditMediaRef(DisplayState.ManagedWindow):
    def __init__(self, state, uistate, track, 
                 media, media_ref, update):
        self.db = state.db
        self.state = state
        self.media_ref = media_ref
        self.media = media
        self.update = update
        
        self.db = self.state.db

        DisplayState.ManagedWindow.__init__(self, uistate, track, media_ref)
        if self.already_exist:
            return

        fname = self.media.get_path()
        self.change_dialog = gtk.glade.XML(const.gladeFile,
                                           "change_description","gramps")

        title = _('Media Reference Editor')
        self.window = self.change_dialog.get_widget('change_description')
        Utils.set_titles(self.window,
                         self.change_dialog.get_widget('title'), title)
        
        self.descr_window = MonitoredEntry(
            self.change_dialog.get_widget("description"),
            self.media.set_description,
            self.media.get_description,
            self.db.readonly)

        PrivacyButton(self.change_dialog.get_widget("private"),
                      self.media_ref,self.db.readonly)

        mtype = self.media.get_mime_type()

        self.pix = ImgManip.get_thumbnail_image(self.media.get_path(),mtype)
        self.pixmap = self.change_dialog.get_widget("pixmap")
        self.pixmap.set_from_pixbuf(self.pix)

        coord = media_ref.get_rectangle()

        if coord and type(coord) == tuple:
            self.change_dialog.get_widget("upperx").set_value(coord[0])
            self.change_dialog.get_widget("uppery").set_value(coord[1])
            self.change_dialog.get_widget("lowerx").set_value(coord[2])
            self.change_dialog.get_widget("lowery").set_value(coord[3])
        
        self.gid = MonitoredEntry(
            self.change_dialog.get_widget("gid"),
            self.media.set_gramps_id,
            self.media.get_gramps_id,
            self.db.readonly)

        self.path_obj = MonitoredEntry(
            self.change_dialog.get_widget("path"),
            self.media.set_path,
            self.media.get_path,
            self.db.readonly)

        mt = GrampsMime.get_description(mtype)
        if mt:
            self.change_dialog.get_widget("type").set_text(mt)
        else:
            self.change_dialog.get_widget("type").set_text("")

        self.gladeif = GladeIf(self.change_dialog)
        self.window.connect('delete_event',self.on_delete_event)
        self.gladeif.connect('button84','clicked',self.close)
        self.gladeif.connect('button82','clicked',self.on_ok_clicked)
        self.gladeif.connect('button104','clicked',self.on_help_clicked)

        self.notebook_ref = self.change_dialog.get_widget('notebook_ref')
        self.notebook_src = self.change_dialog.get_widget('notebook_shared')

        self._create_tabbed_pages()
            
        self.show()

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """
        self.srcref_list = self._add_ref_page(SourceEmbedList(
            self.state,self.uistate, self.track,
            self.media_ref.source_list))

        self.attr_list = self._add_ref_page(AttrEmbedList(
            self.state,self.uistate,self.track,
            self.media_ref.get_attribute_list()))

        self.backref_list = self._add_src_page(MediaBackRefList(
            self.state,self.uistate,self.track,
            self.db.find_backlink_handles(self.media.handle)))

        self.note_ref_tab = self._add_ref_page(NoteTab(
            self.state, self.uistate, self.track,
            self.media_ref.get_note_object()))

        self.src_srcref_list = self._add_src_page(SourceEmbedList(
            self.state,self.uistate, self.track,
            self.media.source_list))

        self.src_attr_list = self._add_src_page(AttrEmbedList(
            self.state,self.uistate,self.track,
            self.media.get_attribute_list()))

        self.src_note_ref_tab = self._add_src_page(NoteTab(
            self.state, self.uistate, self.track,
            self.media.get_note_object()))

    def _add_ref_page(self,page):
        self.notebook_ref.insert_page(page)
        self.notebook_ref.set_tab_label(page,page.get_tab_widget())
        return page

    def _add_src_page(self,page):
        self.notebook_src.insert_page(page)
        self.notebook_src.set_tab_label(page,page.get_tab_widget())
        return page

    def on_delete_event(self,obj,b):
        self.gladeif.close()

    def close(self,obj):
        self.gladeif.close()
        self.window.destroy()

    def on_apply_clicked(self):

        coord = (
            self.change_dialog.get_widget("upperx").get_value_as_int(),
            self.change_dialog.get_widget("uppery").get_value_as_int(),
            self.change_dialog.get_widget("lowerx").get_value_as_int(),
            self.change_dialog.get_widget("lowery").get_value_as_int(),
            )
        if (coord[0] == None and coord[1] == None
            and coord[2] == None and coord[3] == None):
            coord = None

        self.media_ref.set_rectangle(coord)

        orig = self.db.get_object_from_handle(self.media.handle)

        if cmp(orig.serialize(),self.media.serialize()):
            trans = self.db.transaction_begin()
            self.db.commit_media_object(self.media,trans)        
            self.db.transaction_commit(trans,_("Edit Media Object"))

        self.update(self.media_ref)

    def on_help_clicked(self, obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-edit-complete')
        
    def on_ok_clicked(self,obj):
        self.on_apply_clicked()
        self.close(obj)
