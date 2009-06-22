# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
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

#-------------------------------------------------------------------------
#
# Global modules
#
#-------------------------------------------------------------------------


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
import gen.lib
import PageView
import DisplayModels
from gui.utils import add_menuitem
import Errors
import Bookmarks
import Config
from QuestionDialog import ErrorDialog
from gen.plug import PluginManager
from DdTargets import DdTargets
from Editors import EditPlace, DeletePlaceQuery
from Filters.SideBar import PlaceSidebarFilter

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _


#-------------------------------------------------------------------------
#
# PlaceView
#
#-------------------------------------------------------------------------
class PlaceView(PageView.ListView):
    
    COLUMN_NAMES = [
        _('Place Name'),
        _('ID'),
        _('Church Parish'),
        _('ZIP/Postal Code'),
        _('City'),
        _('County'),
        _('State'),
        _('Country'),
        _('Latitude'),
        _('Longitude'),
        _('Last Changed'),
        _('Street'),
        ]

    ADD_MSG     = _("Add a new place")
    EDIT_MSG    = _("Edit the selected place")
    DEL_MSG     = _("Delete the selected place")
    FILTER_TYPE = "Place"

    def __init__(self, dbstate, uistate):

        signal_map = {
            'place-add'     : self.row_add,
            'place-update'  : self.row_update,
            'place-delete'  : self.row_delete,
            'place-rebuild' : self.object_build,
            }

        self.func_list = {
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            }

        self.mapservice = Config.get(Config.MAPSERVICE)
        self.mapservicedata = {}

        PageView.ListView.__init__(
            self, _('Places'), dbstate, uistate, PlaceView.COLUMN_NAMES,
            len(PlaceView.COLUMN_NAMES), 
            DisplayModels.PlaceModel, signal_map,
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
        self._add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                         _('_Column Editor'), callback=self._column_editor)
        self._add_action('FastMerge', None, _('_Merge...'),
                         callback=self.fast_merge)
        self._add_toolmenu_action('MapsList', _('Loading...'),
                        _("Attempt to see selected locations with a Map "
                                "Service (OpenstreetMap, Google Maps, ...)"),
                        self.gotomap,
                        _('Select a Map Service'))
        self._add_action('GotoMap', gtk.STOCK_JUMP_TO, 
                        _('_Look up with Map Service'),
                        callback=self.gotomap,
                        tip=_("Attempt to see this location with a Map "
                                "Service (OpenstreetMap, Google Maps, ...)"))
        self._add_action('FilterEdit', None, _('Place Filter Editor'),
                         callback=self.filter_editor)

    def change_page(self):
        """
        Called by viewmanager at end of realization when arriving on the page
        At this point the Toolbar is created. We need to:
          1. get the menutoolbutton
          2. add all possible map services in the drop down menu
          3. add the actions that correspond to clicking in this drop down menu
          4. set icon and label of the menutoolbutton now that it is realized
          5. store label so it can be changed when selection changes
        """
        PageView.ListView.change_page(self)
        #menutoolbutton actions are stored in PageView class, 
        # obtain the widgets where we need to add to menu
        actionservices = self.action_toolmenu['MapsList']
        widgets = actionservices.get_proxies()
        mmenu = self.__create_maps_menu_actions()

        if not self.mapservicedata:
            return

        self.mapslistlabel = []
        if not self.mapservice in self.mapservicedata: 
            #stored val no longer exists, use the first key instead
            self.set_mapservice(self.mapservicedata.keys()[0])

        #store all gtk labels to be able to update label on selection change
        for widget in widgets :
            if isinstance(widget, gtk.MenuToolButton):
                widget.set_menu(mmenu)
                if gtk.pygtk_version >= (2, 12, 0):
                    widget.set_arrow_tooltip_text(actionservices.arrowtooltip)
                lbl = gtk.Label(self.mapservice_label())
                lbl.show()
                self.mapslistlabel.append(lbl)
                widget.set_label_widget(self.mapslistlabel[-1])
                widget.set_stock_id(gtk.STOCK_JUMP_TO)

    def __create_maps_menu_actions(self):
        """
        Function creating a menu and actions that are used as dropdown menu
        from the menutoolbutton
        """
        menu = gtk.Menu()
        
        #select the map services to show
        self.mapservicedata = {}
        servlist = PluginManager.get_instance().get_mapservice_list()
        for i, service in zip(range(len(servlist)), servlist):
            key = service[2].replace(' ', '-')
            add_menuitem(menu, service[1], None, 
                               make_callback(self.set_mapservice, key))
            self.mapservicedata[key] = (service[0], service[2], service[3])

        return menu

    def set_mapservice(self, mapkey):
        """
        change the service that runs on click of the menutoolbutton
        used as callback menu on menu clicks
        """
        self.mapservice = mapkey
        for label in self.mapslistlabel:
            label.set_label(self.mapservice_label())
            label.show()
        Config.set(Config.MAPSERVICE, mapkey)
        Config.sync()
    
    def mapservice_label(self):
        """
        return the current label for the menutoolbutton
        """
        return self.mapservicedata[self.mapservice][1]

    def gotomap(self, obj):
        """
        Run the map service 
        """
        #First test if any map service is available
        if not len(self.mapservicedata):
            msg = _("No map service is available.")
            msg2 = _("Check your installation.")
            ErrorDialog(msg, msg2)
            return
        
        place_handles = self.selected_handles()
        try:
            place_handle = self.selected_handles()[0]
        except IndexError:
            msg = _("No place selected.")
            msg2 = _("You need to select a place to be able to view it"
                     " on a map. Some Map Services might support multiple"
                     " selections.")
            ErrorDialog(msg, msg2)
            return
        
        #TODO: support for descriptions in some cases. For now, pass None
        #TODO: Later this might be 'Birth of William' ....
        places = [(x, None) for x in place_handles]
        
        #run the mapservice:
        self.mapservicedata[self.mapservice][0](self.dbstate.db, places)

    def drag_info(self):
        return DdTargets.PLACE_LINK

    def _column_editor(self, obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Place Columns'),
            self.uistate,
            self.dbstate.db.get_place_column_order(),
            PlaceView.COLUMN_NAMES,
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
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
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
              <toolitem action="MapsList"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <menuitem action="GotoMap"/>
          </popup>
        </ui>'''

    def add(self, obj):
        try:
            EditPlace(self.dbstate, self.uistate, [], gen.lib.Place())
        except Errors.WindowActiveError:
            pass

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        person_list = [
            item[1] for item in
            self.dbstate.db.find_backlink_handles(handle,['Person'])]

        family_list = [
            item[1] for item in
            self.dbstate.db.find_backlink_handles(handle,['Family'])]
        
        event_list = [
            item[1] for item in
            self.dbstate.db.find_backlink_handles(handle,['Event'])]
        
        object = self.dbstate.db.get_place_from_handle(handle)
        query = DeletePlaceQuery(self.dbstate, self.uistate, object,
                                 person_list, family_list, event_list)

        is_used = len(person_list) + len(family_list) + len(event_list) > 0
        return (query, is_used, object)

    def edit(self, obj):
        for handle in self.selected_handles():
            place = self.dbstate.db.get_place_from_handle(handle)
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
            except Errors.WindowActiveError:
                pass

    def fast_merge(self, obj):
        mlist = self.selected_handles()
        
        if len(mlist) != 2:
            msg = _("Cannot merge places.")
            msg2 = _("Exactly two places must be selected to perform a merge. "
                     "A second place can be selected by holding down the "
                     "control key while clicking on the desired place.")
            ErrorDialog(msg, msg2)
        else:
            import Merge
            Merge.MergePlaces(self.dbstate, self.uistate, mlist[0], mlist[1])

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_place_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

def make_callback(func, val):
    return lambda x: func(val)
