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
import RelLib
import PageView
import DisplayModels
import ImageSelect
import ImgManip
import const
import Utils
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

        PageView.ListView.__init__(self,'Media View',dbstate,uistate,
                                   column_names,len(column_names),
                                   DisplayModels.MediaModel,
                                   signal_map)

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
#         label = gtk.Label('<b>%s</b>' % _('Preview'))
#         label.set_use_markup(True)
#         frame = gtk.Frame()
#         frame.set_label_widget(label)
#         frame.add(self.image)
        vbox.pack_start(self.image,False)
        vbox.pack_start(base,True)

        self.selection.connect('changed',self.row_change)
        return vbox

    def row_change(self,obj):
        handle = self.first_selected()
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

    def on_double_click(self,obj,event):
        handle = self.first_selected()
        place = self.dbstate.db.get_place_from_handle(handle)
        #EditPlace.EditPlace(place,self.dbstate, self.uistate)

    def add(self,obj):
        """Add a new media object to the media list"""
        import AddMedia
        am = AddMedia.AddMediaObject(self.dbstate.db)
        am.run()

    def remove(self,obj):
        handle = self.first_selected()
        the_lists = Utils.get_media_referents(handle,self.dbstate.db)

        ans = ImageSelect.DeleteMediaQuery(handle,self.dbstate.db,the_lists)
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
        
        obj = self.dbstate.db.get_object_from_handle(handle)
        if obj.get_mime_type():
            ImageSelect.GlobalMediaProperties(self.dbstate,self.uistate, [],
                                              obj)
        else:
            import NoteEdit
            NoteEdit.NoteEditor(obj,self.parent,self.topWindow,
                                self.note_callback)
