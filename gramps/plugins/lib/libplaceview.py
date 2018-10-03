# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Base view for Place Views
"""

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Place
from gramps.gui.views.listview import ListView, TEXT, ICON
from gramps.gui.widgets.menuitem import add_menuitem
from gramps.gen.errors import WindowActiveError
from gramps.gui.views.bookmarks import PlaceBookmarks
from gramps.gen.config import config
from gramps.gui.dialog import ErrorDialog
from gramps.gui.pluginmanager import GuiPluginManager
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditPlace, DeletePlaceQuery
from gramps.gui.filters.sidebar import PlaceSidebarFilter
from gramps.gui.merge import MergePlace
from gramps.gen.plug import CATEGORY_QR_PLACE
from gramps.gen.utils.location import located_in

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# PlaceBaseView
#
#-------------------------------------------------------------------------
class PlaceBaseView(ListView):
    """ base view class for place views, be they flat list or tree
    """
    COL_NAME = 0
    COL_ID = 1
    COL_TITLE = 2
    COL_TYPE = 3
    COL_CODE = 4
    COL_LAT = 5
    COL_LON = 6
    COL_PRIV = 7
    COL_TAGS = 8
    COL_CHAN = 9
    COL_SEARCH = 11
    # column definitions
    COLUMNS = [
        (_('Name'), TEXT, None),
        (_('ID'), TEXT, None),
        (_('Title'), TEXT, None),
        (_('Type'), TEXT, None),
        (_('Code'), TEXT, None),
        (_('Latitude'), TEXT, None),
        (_('Longitude'), TEXT, None),
        (_('Private'), ICON, 'gramps-lock'),
        (_('Tags'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_NAME, COL_ID, COL_TYPE, COL_CODE]),
        ('columns.rank', [COL_NAME, COL_TITLE, COL_ID, COL_TYPE, COL_CODE,
                          COL_LAT, COL_LON, COL_PRIV, COL_TAGS, COL_CHAN]),
        ('columns.size', [250, 250, 75, 100, 100, 150, 150, 40, 100, 100])
        )
    ADD_MSG     = _("Add a new place")
    EDIT_MSG    = _("Edit the selected place")
    DEL_MSG     = _("Delete the selected place")
    MERGE_MSG   = _("Merge the selected places")
    FILTER_TYPE = "Place"
    QR_CATEGORY = CATEGORY_QR_PLACE

    def __init__(self, pdata, dbstate, uistate, title, model, nav_group):

        signal_map = {
            'place-add'     : self.row_add,
            'place-update'  : self.row_update,
            'place-delete'  : self.row_delete,
            'place-rebuild' : self.object_build,
            }

        self.mapservice = config.get('interface.mapservice')
        self.mapservicedata = {}

        ListView.__init__(
            self, title, pdata, dbstate, uistate,
            model, signal_map,
            PlaceBookmarks, nav_group,
            multiple=True,
            filter_class=PlaceSidebarFilter)

        self.func_list.update({
            '<PRIMARY>J' : self.jump,
            '<PRIMARY>BackSpace' : self.key_delete,
            })
        self.maptoolbtn = None

        uistate.connect('placeformat-changed', self.build_tree)

        self.additional_uis.append(self.additional_ui())

    def navigation_type(self):
        return 'Place'

    def setup_filter(self):
        """Build the default filters and add them to the filter menu.
        This overrides the listview method because we use the hidden
        COL_SEARCH that has alt names as well as primary name for name
        searching"""
        self.search_bar.setup_filter(
            [(self.COLUMNS[pair[1]][0],
              self.COL_SEARCH if pair[1] == self.COL_NAME else pair[1],
              pair[1] in self.exact_search())
                for pair in self.column_order() if pair[0]])

    def define_actions(self):
        ListView.define_actions(self)
        self._add_toolmenu_action('MapsList', _('Loading...'),
                        _("Attempt to see selected locations with a Map "
                                "Service (OpenstreetMap, Google Maps, ...)"),
                        self.gotomap,
                        _('Select a Map Service'))
        self._add_action('GotoMap', 'go-jump',
                        _('_Look up with Map Service'),
                        callback=self.gotomap,
                        tip=_("Attempt to see this location with a Map "
                                "Service (OpenstreetMap, Google Maps, ...)"))
        self._add_action('FilterEdit', None, _('Place Filter Editor'),
                         callback=self.filter_editor)
        self._add_action('QuickReport', None, _("Quick View"), None, None, None)

    def set_inactive(self):
        """called by viewmanager when moving away from the page
        Here we need to remove the menutoolbutton from the menu
        """
        tb = self.uistate.viewmanager.uimanager.get_widget('/ToolBar')
        tb.remove(self.maptoolbtn)
        ListView.set_inactive(self)

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
        ListView.change_page(self)
        #menutoolbutton has to be made and added in correct place on toolbar
        if not self.maptoolbtn:
            self.maptoolbtn = Gtk.MenuToolButton()
            self.maptoolbtn.set_icon_name('go-jump')
            self.maptoolbtn.connect('clicked', self.gotomap)
            self.mmenu = self.__create_maps_menu_actions()
            self.maptoolbtn.set_menu(self.mmenu)
            self.maptoolbtn.show()
        tb = self.uistate.viewmanager.uimanager.get_widget('/ToolBar')
        ind = tb.get_item_index(self.uistate.viewmanager.uimanager.get_widget(
                        '/ToolBar/CommonEdit/Merge'))
        tb.insert(self.maptoolbtn, ind+1)
        widget = self.maptoolbtn

        if not self.mapservicedata:
            return

        self.mapslistlabel = []
        if not self.mapservice in self.mapservicedata:
            #stored val no longer exists, use the first key instead
            self.set_mapservice(list(self.mapservicedata.keys())[0])

        #store all gtk labels to be able to update label on selection change_('Loading...'),
        widget.set_menu(self.mmenu)
        widget.set_arrow_tooltip_text(_('Select a Map Service'))
        widget.set_tooltip_text(
                          _("Attempt to see selected locations with a Map "
                            "Service (OpenstreetMap, Google Maps, ...)"))
        lbl = Gtk.Label(label=self.mapservice_label())
        lbl.show()
        self.mapslistlabel.append(lbl)
        widget.set_label_widget(self.mapslistlabel[-1])
        widget.set_icon_name('go-jump')

    def __create_maps_menu_actions(self):
        """
        Function creating a menu and actions that are used as dropdown menu
        from the menutoolbutton
        """
        menu = Gtk.Menu()

        #select the map services to show
        self.mapservicedata = {}
        servlist = GuiPluginManager.get_instance().get_reg_mapservices()
        for i, pdata in enumerate(servlist):
            key = pdata.id.replace(' ', '-')
            add_menuitem(menu, pdata.name, None,
                               make_callback(self.set_mapservice, key))
            self.mapservicedata[key] = pdata

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
        config.set('interface.mapservice', mapkey)
        config.save()

    def mapservice_label(self):
        """
        return the current label for the menutoolbutton
        """
        return self.mapservicedata[self.mapservice].name

    def gotomap(self, obj):
        """
        Run the map service
        """
        #First test if any map service is available
        if not len(self.mapservicedata):
            msg = _("No map service is available.")
            msg2 = _("Check your installation.")
            ErrorDialog(msg, msg2, parent=self.uistate.window)
            return

        place_handles = self.selected_handles()
        try:
            place_handle = self.selected_handles()[0]
        except IndexError:
            msg = _("No place selected.")
            msg2 = _("You need to select a place to be able to view it"
                     " on a map. Some Map Services might support multiple"
                     " selections.")
            ErrorDialog(msg, msg2, parent=self.uistate.window)
            return

        #TODO: support for descriptions in some cases. For now, pass None
        #TODO: Later this might be 'Birth of William' ....
        places = [(x, None) for x in place_handles]

        #run the mapservice:
        pmgr = GuiPluginManager.get_instance()
        serv = self.mapservicedata[self.mapservice]
        mod = pmgr.load_plugin(serv)
        if mod:
            servfunc = eval('mod.' +  serv.mapservice)
            servfunc()(self.dbstate.db, places, self.uistate)
        else:
            print('Failed to load map plugin, see Plugin Manager')

    def drag_info(self):
        return DdTargets.PLACE_LINK

    def get_stock(self):
        return 'gramps-place'

    def additional_ui(self):
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
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
                <menuitem action="Merge"/>
              </placeholder>
              <menuitem action="FilterEdit"/>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>
              <toolitem action="Forward"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
              <toolitem action="Merge"/>
              <separator/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
            <menuitem action="Merge"/>
            <separator/>
            <menu name="QuickReport" action="QuickReport"/>
            <separator/>
            <menuitem action="GotoMap"/>
          </popup>
        </ui>'''

    def add(self, obj):
        try:
            EditPlace(self.dbstate, self.uistate, [], Place())
        except WindowActiveError:
            pass

    def remove(self, obj):
        for handle in self.selected_handles():
            for link in self.dbstate.db.find_backlink_handles(handle,['Place']):
                msg = _("Cannot delete place.")
                msg2 = _("This place is currently referenced by another place. "
                         "First remove the places it contains.")
                ErrorDialog(msg, msg2, parent=self.uistate.window)
                return
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
            except WindowActiveError:
                pass

    def merge(self, obj):
        """
        Merge the selected places.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge places.")
            msg2 = _("Exactly two places must be selected to perform a merge. "
                     "A second place can be selected by holding down the "
                     "control key while clicking on the desired place.")
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            if (located_in(self.dbstate.db, mlist[0], mlist[1]) or
                located_in(self.dbstate.db, mlist[1], mlist[0])):
                msg = _("Cannot merge places.")
                msg2 = _("Merging these places would create a cycle in the "
                         "place hierarchy.")
                ErrorDialog(msg, msg2, parent=self.uistate.window)
            else:
                MergePlace(self.dbstate, self.uistate, [], mlist[0], mlist[1],
                           self.merged)

    def merged(self):
        """
        Rebuild the model after a merge to reflect changes in the hierarchy.
        """
        if not (self.model.get_flags() & Gtk.TreeModelFlags.LIST_ONLY):
            self.build_tree()

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_place_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        all_links = set([])
        for tag_handle in handle_list:
            links = set([link[1] for link in
                         self.dbstate.db.find_backlink_handles(tag_handle,
                                                    include_classes='Place')])
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, place_handle, tag_handle):
        """
        Add the given tag to the given place.
        """
        place = self.dbstate.db.get_place_from_handle(place_handle)
        place.add_tag(tag_handle)
        self.dbstate.db.commit_place(place, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Place Filter",),
                ("Place Details",
                 "Place Enclosed By",
                 "Place Encloses",
                 "Place Gallery",
                 "Place Citations",
                 "Place Notes",
                 "Place Backlinks"))

def make_callback(func, val):
    return lambda x: func(val)
