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
import RelLib
import Mime
import ImgManip
import DisplayState
import GrampsDisplay

from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# LocalMediaProperties
#
#-------------------------------------------------------------------------
class EditMediaRef(DisplayState.ManagedWindow):
    def __init__(self, state, uistate, track, media, media_ref, update):

        self.db = state.db
        self.state = state
        self.media_ref = media_ref
        self.media = media
        self.update = update
        
        self.db = self.state.db

        DisplayState.ManagedWindow.__init__(self, uistate, track, media_ref)

        self.top = gtk.glade.XML(const.gladeFile,
                                           "change_description","gramps")

        title = _('Media Reference Editor')
        self.window = self.top.get_widget('change_description')
        Utils.set_titles(self.window,
                         self.top.get_widget('title'), title)
        
        mtype = self.media.get_mime_type()

        self.pix = ImgManip.get_thumbnail_image(self.media.get_path(),mtype)
        self.pixmap = self.top.get_widget("pixmap")
        self.pixmap.set_from_pixbuf(self.pix)

        coord = media_ref.get_rectangle()

        if coord and type(coord) == tuple:
            self.top.get_widget("upperx").set_value(coord[0])
            self.top.get_widget("uppery").set_value(coord[1])
            self.top.get_widget("lowerx").set_value(coord[2])
            self.top.get_widget("lowery").set_value(coord[3])
        
        self.descr_window = MonitoredEntry(
            self.top.get_widget("description"),
            self.media.set_description,
            self.media.get_description,
            self.db.readonly)

        self.privacy = PrivacyButton(
            self.top.get_widget("private"),
            self.media_ref,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_widget("gid"),
            self.media.set_gramps_id,
            self.media.get_gramps_id,
            self.db.readonly)

        self.path_obj = MonitoredEntry(
            self.top.get_widget("path"),
            self.media.set_path,
            self.media.get_path,
            self.db.readonly)

        mt = Mime.get_description(mtype)
        if mt:
            self.top.get_widget("type").set_text(mt)
        else:
            self.top.get_widget("type").set_text("")

        self.notebook_ref = self.top.get_widget('notebook_ref')
        self.notebook_src = self.top.get_widget('notebook_shared')

        self._create_tabbed_pages()
        self._connect_signals()
        self.show()

    def _connect_signals(self):
        self.window.connect('delete_event',self.on_delete_event)
        self.top.get_widget('button84').connect('clicked',self.close_window)
        self.top.get_widget('button82').connect('clicked',self.on_ok_clicked)
        self.top.get_widget('button104').connect('clicked',self.on_help_clicked)

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
        self.close()

    def close_window(self,obj):
        self.window.destroy()
        self.close()

    def on_apply_clicked(self):

        coord = (
            self.top.get_widget("upperx").get_value_as_int(),
            self.top.get_widget("uppery").get_value_as_int(),
            self.top.get_widget("lowerx").get_value_as_int(),
            self.top.get_widget("lowery").get_value_as_int(),
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
        self.close()
