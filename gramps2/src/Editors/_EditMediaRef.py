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
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Config
import Mime
import ImgManip

from DisplayTabs import \
     SourceEmbedList,AttrEmbedList,MediaBackRefList,NoteTab
from GrampsWidgets import *
from _EditReference import EditReference

#-------------------------------------------------------------------------
#
# EditMediaRef
#
#-------------------------------------------------------------------------
class EditMediaRef(EditReference):

    WIDTH_KEY = Config.MEDIA_REF_WIDTH
    HEIGHT_KEY = Config.MEDIA_REF_HEIGHT

    def __init__(self, state, uistate, track, media, media_ref, update):

        EditReference.__init__(self, state, uistate, track, media,
                               media_ref, update)

    def _local_init(self):

        self.top = gtk.glade.XML(const.gladeFile,
                                 "change_description","gramps")

        self.set_window(self.top.get_widget('change_description'),
                        self.top.get_widget('title'),
                        _('Media Reference Editor'))
        self.define_warn_box(self.top.get_widget("warn_box"))
        
    def _setup_fields(self):
        
        mtype = self.source.get_mime_type()

        self.pix = ImgManip.get_thumbnail_image(self.source.get_path(),mtype)
        self.pixmap = self.top.get_widget("pixmap")
        ebox = self.top.get_widget('eventbox')
        ebox.connect('button-press-event', self.button_press_event)

        self.pixmap.set_from_pixbuf(self.pix)

        coord = self.source_ref.get_rectangle()

        if coord and type(coord) == tuple:
            self.top.get_widget("upperx").set_value(coord[0])
            self.top.get_widget("uppery").set_value(coord[1])
            self.top.get_widget("lowerx").set_value(coord[2])
            self.top.get_widget("lowery").set_value(coord[3])
        if self.dbstate.db.readonly:
            self.top.get_widget("upperx").set_sensitive(False)
            self.top.get_widget("uppery").set_sensitive(False)
            self.top.get_widget("lowerx").set_sensitive(False)
            self.top.get_widget("lowery").set_sensitive(False)
        
        self.descr_window = MonitoredEntry(
            self.top.get_widget("description"),
            self.source.set_description,
            self.source.get_description,
            self.db.readonly)

        self.ref_privacy = PrivacyButton(
            self.top.get_widget("private"),
            self.source_ref,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_widget("gid"),
            self.source.set_gramps_id,
            self.source.get_gramps_id,
            self.db.readonly)

        self.privacy = PrivacyButton(
            self.top.get_widget("privacy"),
            self.source,
            self.db.readonly)

        self.path_obj = MonitoredEntry(
            self.top.get_widget("path"),
            self.source.set_path,
            self.source.get_path,
            self.db.readonly)

        mt = Mime.get_description(mtype)
        if mt:
            self.top.get_widget("type").set_text(mt)
        else:
            self.top.get_widget("type").set_text("")

    def button_press_event(self, obj, event):
        if event.button==1 and event.type == gtk.gdk._2BUTTON_PRESS:
            self.view_media(obj)

    def view_media(self, obj):
        mime_type = self.source.get_mime_type()
        app = Mime.get_application(mime_type)
        if app:
            import Utils
            Utils.launch(app[0],self.source.get_path())

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget('button84'))
        self.define_ok_button(self.top.get_widget('button82'),self.save)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """
        notebook_ref = self.top.get_widget('notebook_ref')
        notebook_src = self.top.get_widget('notebook_shared')
        
        self.srcref_list = self._add_tab(
            notebook_ref,
            SourceEmbedList(self.dbstate,self.uistate,self.track,
                            self.source_ref))

        self.attr_list = self._add_tab(
            notebook_ref,
            AttrEmbedList(self.dbstate,self.uistate,self.track,
                          self.source_ref.get_attribute_list()))

        self.backref_list = self._add_tab(
            notebook_src,
            MediaBackRefList(self.dbstate,self.uistate,self.track,
                             self.db.find_backlink_handles(self.source.handle),
                             self.enable_warnbox
                             ))

        self.note_ref_tab = self._add_tab(
            notebook_ref,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source_ref.get_note_object()))

        self.src_srcref_list = self._add_tab(
            notebook_src,
            SourceEmbedList(self.dbstate,self.uistate,self.track,
                            self.source))

        self.src_attr_list = self._add_tab(
            notebook_src,
            AttrEmbedList(self.dbstate,self.uistate,self.track,
                          self.source.get_attribute_list()))

        self.src_note_ref_tab = self._add_tab(
            notebook_src,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source.get_note_object()))

        self._setup_notebook_tabs( notebook_src)
        self._setup_notebook_tabs( notebook_ref)

    def save(self,*obj):

        coord = (
            self.top.get_widget("upperx").get_value_as_int(),
            self.top.get_widget("uppery").get_value_as_int(),
            self.top.get_widget("lowerx").get_value_as_int(),
            self.top.get_widget("lowery").get_value_as_int(),
            )

        if (coord[0] == None and coord[1] == None
            and coord[2] == None and coord[3] == None):
            coord = None

        self.source_ref.set_rectangle(coord)

        orig = self.db.get_object_from_handle(self.source.handle)

        if cmp(orig.serialize(),self.source.serialize()):
            trans = self.db.transaction_begin()
            self.db.commit_media_object(self.source,trans)        
            self.db.transaction_commit(trans,_("Edit Media Object"))

        if self.update:
            self.update(self.source_ref,self.source)
        self.close()
