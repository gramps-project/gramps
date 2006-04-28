# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import PageView
import DisplayModels
import ImgManip
import const
import Utils
import Bookmarks

from QuestionDialog import QuestionDialog, ErrorDialog

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('Title'),
    _('ID'),
    _('Type'),
    _('Path'),
    _('Last Changed'),
    _('Date'),
    ]

#-------------------------------------------------------------------------
#
# MediaView
#
#-------------------------------------------------------------------------
class MediaView(PageView.ListView):
    def __init__(self,dbstate,uistate):

        signal_map = {
            'media-add'     : self.row_add,
            'media-update'  : self.row_update,
            'media-delete'  : self.row_delete,
            'media-rebuild' : self.build_tree,
            }

        PageView.ListView.__init__(
            self, _('Media'), dbstate, uistate,
            column_names,len(column_names), DisplayModels.MediaModel,
            signal_map, dbstate.db.get_media_bookmarks(),
            Bookmarks.MediaBookmarks)

    def get_bookmarks(self):
        return self.dbstate.db.get_media_bookmarks()

    def define_actions(self):
        PageView.ListView.define_actions(self)
        self.add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                        '_Column Editor', callback=self.column_editor)
                        

    def column_editor(self,obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Media Columns'),
            self.uistate,
            self.dbstate.db.get_media_column_order(),
            column_names,
            self.set_column_order)

    def set_column_order(self,list):
        self.dbstate.db.set_media_column_order(list)
        self.build_columns()

    def column_order(self):
        return self.dbstate.db.get_media_column_order()

    def get_stock(self):
        return 'gramps-media'

    def build_widget(self):
        base = PageView.ListView.build_widget(self)
        vbox = gtk.VBox()
        vbox.set_border_width(4)
        vbox.set_spacing(4)

        self.image = gtk.Image()
        self.image.set_size_request(int(const.thumbScale),
                                    int(const.thumbScale))
        vbox.pack_start(self.image,False)
        vbox.pack_start(base,True)

        self.selection.connect('changed',self.row_change)
        return vbox

    def row_change(self,obj):
        handle = self.first_selected()
        if not handle:
            return
        obj = self.dbstate.db.get_object_from_handle(handle)
        pix = ImgManip.get_thumbnail_image(obj.get_path())
        self.image.set_from_pixbuf(pix)
    
    def ui_definition(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="ColumnEdit"/>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
          </popup>
        </ui>'''

    def add(self,obj):
        """Add a new media object to the media list"""
        import AddMedia
        am = AddMedia.AddMediaObject(self.dbstate, self.uistate, [])
        am.run()

    def remove(self,obj):
        handle = self.first_selected()
        if not handle:
            return
        the_lists = Utils.get_media_referents(handle,self.dbstate.db)

        ans = DeleteMediaQuery(handle,self.dbstate.db,the_lists)
        if filter(None,the_lists): # quick test for non-emptiness
            msg = _('This media object is currently being used. '
                    'If you delete this object, it will be removed from '
                    'the database and from all records that reference it.')
        else:
            msg = _('Deleting media object will remove it from the database.')

        msg = "%s %s" % (msg,Utils.data_recover_msg)
        QuestionDialog(_('Delete Media Object?'),msg,
                      _('_Delete Media Object'),ans.query_response)

    def edit(self,obj):
        handle = self.first_selected()
        if not handle:
            return
        
        obj = self.dbstate.db.get_object_from_handle(handle)
        from Editors import EditMedia
        EditMedia(self.dbstate,self.uistate, [], obj)

class DeleteMediaQuery:

    def __init__(self,media_handle,db,the_lists):
        self.db = db
        self.media_handle = media_handle
        self.the_lists = the_lists
        
    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list,family_list,event_list,
                place_list,source_list) = self.the_lists

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            new_list = [ photo for photo in person.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            person.set_media_list(new_list)
            self.db.commit_person(person,trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            new_list = [ photo for photo in family.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            family.set_media_list(new_list)
            self.db.commit_family(family,trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            new_list = [ photo for photo in event.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            event.set_media_list(new_list)
            self.db.commit_event(event,trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            new_list = [ photo for photo in place.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            place.set_media_list(new_list)
            self.db.commit_place(place,trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            new_list = [ photo for photo in source.get_media_list() \
                        if photo.get_reference_handle() != self.media_handle ]
            source.set_media_list(new_list)
            self.db.commit_source(source,trans)

        self.db.enable_signals()
        self.db.remove_object(self.media_handle,trans)
        self.db.transaction_commit(trans,_("Remove Media Object"))
