# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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

"""
Place View
"""

__author__ = "Don Allingham"
__revision__ = "$Revision$"

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
import RelLib
import PageView
import DisplayModels
import Utils
import Errors
import Bookmarks
import const
import Config
from DdTargets import DdTargets
from Editors import EditPlace, DeletePlaceQuery
from QuestionDialog import QuestionDialog, ErrorDialog
from Filters.SideBar import PlaceSidebarFilter

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

column_names = [
    _('Place Name'),
    _('ID'),
    _('Church Parish'),
    _('ZIP/Postal Code'),
    _('City'),
    _('County'),
    _('State'),
    _('Country'),
    _('Longitude'),
    _('Latitude'),
    _('Last Changed'),
    _('Street'),
    ]

#-------------------------------------------------------------------------
#
# PlaceView
#
#-------------------------------------------------------------------------
class PlaceView(PageView.ListView):

    ADD_MSG     = _("Add a new place")
    EDIT_MSG    = _("Edit the selected place")
    DEL_MSG     = _("Delete the selected place")
    FILTER_TYPE = "Place"

    def __init__(self, dbstate, uistate):

        signal_map = {
            'place-add'     : self.row_add,
            'place-update'  : self.row_update,
            'place-delete'  : self.row_delete,
            'place-rebuild' : self.build_tree,
            }

        PageView.ListView.__init__(
            self, _('Places'), dbstate, uistate, column_names,
            len(column_names), DisplayModels.PlaceModel, signal_map,
            dbstate.db.get_place_bookmarks(),
            Bookmarks.PlaceBookmarks, 
            multiple=True,
            filter_class=PlaceSidebarFilter)

        Config.client.notify_add("/apps/gramps/interface/filter",
                                 self.filter_toggle)

    def get_bookmarks(self):
        return self.dbstate.db.get_place_bookmarks()

    def define_actions(self):
        PageView.ListView.define_actions(self)
        self.add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                        _('_Column Editor'), callback=self.column_editor)
        self.add_action('FastMerge', None, _('_Merge'),
                        callback=self.fast_merge)
        self.add_action('GoogleMaps', gtk.STOCK_JUMP_TO, _('_Google Maps'),
                        callback=self.google,
                        tip=_("Attempt to map location on Google Maps"))
        self.add_action('FilterEdit', None, _('Place Filter Editor'),
                        callback=self.filter_editor,)

    def drag_info(self):
        return DdTargets.PLACE_LINK

    def google(self, obj):
        import GrampsDisplay
        from PlaceUtils import conv_lat_lon

        try:
            place_handle = self.selected_handles()[0]
        except IndexError:
            return
        place = self.dbstate.db.get_place_from_handle(place_handle)
        descr = place.get_title()
        longitude = place.get_longitude()
        latitude = place.get_latitude()
        latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
        city = place.get_main_location().get_city()
        country = place.get_main_location().get_country()

        if longitude and latitude:
            path = "http://maps.google.com/?sll=%s,%s&z=15" % (latitude, longitude)
        elif city and country:
            path = "http://maps.google.com/maps?q=%s,%s" % (city, country)
        else:
            path = "http://maps.google.com/maps?q=%s" % '+'.join(descr.split())
        GrampsDisplay.url(path)
        
    def column_editor(self, obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Place Columns'),
            self.uistate,
            self.dbstate.db.get_place_column_order(),
            column_names,
            self.set_column_order)

    def set_column_order(self, clist):
        self.dbstate.db.set_place_column_order(clist)
        self.build_columns()

    def column_order(self):
        return self.dbstate.db.get_place_column_order()

    def get_stock(self):
        return 'gramps-place'

    def ui_definition(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="ColumnEdit"/>
              <menuitem action="FilterEdit"/>
              <placeholder name="Merge">
                <menuitem action="FastMerge"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
              <separator/>
              <toolitem action="GoogleMaps"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <menuitem action="GoogleMaps"/>
          </popup>
        </ui>'''

    def on_double_click(self, obj, event):
        handle = self.first_selected()
        place = self.dbstate.db.get_place_from_handle(handle)
        try:
            EditPlace(self.dbstate, self.uistate, [], place)
        except Errors.WindowActiveError:
            pass

    def add(self, obj):
        try:
            EditPlace(self.dbstate, self.uistate, [], RelLib.Place())
        except Errors.WindowActiveError:
            pass

    def remove(self, obj):
        for place_handle in self.selected_handles():
            db = self.dbstate.db
            person_list = [ h for h in
                            db.get_person_handles(False)
                            if db.get_person_from_handle(h).has_handle_reference('Place', place_handle) ]
            family_list = [ h for h in
                            db.get_family_handles()
                            if db.get_family_from_handle(h).has_handle_reference('Place', place_handle) ]
            
            place = db.get_place_from_handle(place_handle)
            
            ans = DeletePlaceQuery(place, db)

            if len(person_list) + len(family_list) > 0:
                msg = _('This place is currently being used. Deleting it '
                        'will remove it from the database and from all '
                        'people and families that reference it.')
            else:
                msg = _('Deleting place will remove it from the database.')
            
            msg = "%s %s" % (msg, Utils.data_recover_msg)
            descr = place.get_title()
            if descr == "":
                descr = place.get_gramps_id()
                
            QuestionDialog(_('Delete %s?') % descr, msg,
                           _('_Delete Place'), ans.query_response)

    def edit(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)

        for handle in mlist:
            place = self.dbstate.db.get_place_from_handle(handle)
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
            except Errors.WindowActiveError:
                pass

    def fast_merge(self, obj):
        mlist = []
        self.selection.selected_foreach(self.blist, mlist)
        
        if len(mlist) != 2:
            msg = _("Cannot merge places.")
            msg2 = _("Exactly two places must be selected to perform a merge. "
                     "A second place can be selected by holding down the "
                     "control key while clicking on the desired place.")
            ErrorDialog(msg, msg2)
        else:
            import Merge
            Merge.MergePlaces(self.dbstate, self.uistate, mlist[0], mlist[1])

    
