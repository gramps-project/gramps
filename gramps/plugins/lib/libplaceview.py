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
from gramps.gui.uimanager import ActionGroup

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext


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
        self.map_action_group = None

        ListView.__init__(
            self, title, pdata, dbstate, uistate,
            model, signal_map,
            PlaceBookmarks, nav_group,
            multiple=True,
            filter_class=PlaceSidebarFilter)

        uistate.connect('placeformat-changed', self.build_tree)

        _ui = self.__create_maps_menu_actions()
        self.additional_uis.append(_ui)

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
        self._add_action('GotoMap', self.gotomap)

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

    def __create_maps_menu_actions(self):
        """
        Function creating a menu and actions that are used as dropdown menu
        from the menutoolbutton
        """
        _bar = '''
            <item>
              <attribute name="action">win.MapChoice</attribute>
              <attribute name="target">%s</attribute>
              <attribute name="label" translatable="yes">%s</attribute>
            </item>
            '''
        menu = ''

        #select the map services to show
        self.mapservicedata = {}
        servlist = GuiPluginManager.get_instance().get_reg_mapservices()
        for pdata in servlist:
            key = pdata.id.replace(' ', '-')
            menu += _bar % (key, pdata.name)
            self.mapservicedata[key] = pdata

        if not self.mapservicedata:
            return self.additional_ui
        if self.mapservice not in self.mapservicedata:
            #stored val no longer exists, use the most recent key instead
            self.set_mapservice(None, key)

        self._add_toggle_action('MapChoice', self.set_mapservice, '',
                                self.mapservice)

        label = self.mapservice_label()
        _ui = self.additional_ui[:]
        _ui.append(self.map_ui_menu % menu)
        _ui.append(self.map_ui % label)
        return _ui

    def set_mapservice(self, action, value):
        """
        change the service that runs on click of the menutoolbutton
        used as callback menu on menu clicks
        """
        if action:
            action.set_state(value)
        self.mapservice = mapkey = value.get_string()
        config.set('interface.mapservice', mapkey)
        config.save()
        _ui = self.__create_maps_menu_actions()
        self.uimanager.add_ui_from_string(_ui)
        self.uimanager.update_menu()
        return False

    def mapservice_label(self):
        """
        return the current label for the menutoolbutton
        """
        return self.mapservicedata[self.mapservice].name

    def gotomap(self, *obj):
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

    #
    # Defines the UI string for UIManager
    #
    additional_ui = [
        '''
      <placeholder id="LocalExport">
        <item>
          <attribute name="action">win.ExportTab</attribute>
          <attribute name="label" translatable="yes">Export View...</attribute>
        </item>
      </placeholder>
''',
        '''
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
''' % _('Organize Bookmarks'),
        '''
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      </placeholder>
''',
        '''
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label" translatable="yes">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
''' % _("action|_Edit..."),  # to use sgettext()
        '''
        <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">'''
        '''Place Filter Editor</attribute>
        </item>
        </placeholder>
''',  # Following are the Toolbar items
        '''
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
''',
        '''
    <placeholder id='BarCommonEdit'>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-add</property>
        <property name="action-name">win.Add</property>
        <property name="tooltip_text" translatable="yes">%s</property>
        <property name="label" translatable="yes">_Add...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text" translatable="yes">%s</property>
        <property name="label" translatable="yes">Edit...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-remove</property>
        <property name="action-name">win.Remove</property>
        <property name="tooltip_text" translatable="yes">%s</property>
        <property name="label" translatable="yes">_Delete</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-merge</property>
        <property name="action-name">win.Merge</property>
        <property name="tooltip_text" translatable="yes">%s</property>
        <property name="label" translatable="yes">_Merge...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <placeholder id="PlaceMapUi"> </placeholder>
    </placeholder>
''' % (ADD_MSG, EDIT_MSG, DEL_MSG, MERGE_MSG),
        '''
    <menu id="Popup">
      <section id="PopUpTree">
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">Forward</attribute>
        </item>
      </section>
      <section>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label" translatable="yes">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
      <section>
        <placeholder id='QuickReport'>
        </placeholder>
      </section>
      <section>
        <item>
          <attribute name="action">win.GotoMap</attribute>
          <attribute name="label" translatable="yes">'''
        '''_Look up with Map Service</attribute>
        </item>
      </section>
    </menu>
''' % _('action|_Edit...')]  # to use sgettext()

    map_ui_menu = '''
      <menu id="MapBtnMenu">
        %s
      </menu>
    '''

    map_ui = (
        '''<placeholder id="PlaceMapUi">
    <child>
      <object class="GtkToolButton" id="GotoMap">
        <property name="icon-name">go-jump</property>
        <property name="action-name">win.GotoMap</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Attempt to see selected locations with a Map Service '''
        '''(OpenstreetMap, Google Maps, ...)</property>
        <property name="label" translatable="yes">%s</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
     </child>
    <child>
      <object class="GtkToolItem">
        <child>
          <object class="GtkMenuButton">
            <property name="tooltip_text" translatable="yes">'''
        '''Select a Map Service</property>
            <property name="menu-model">MapBtnMenu</property>
            <property name="relief">GTK_RELIEF_NONE</property>
            <property name="use-popover">False</property>
          </object>
        </child>
      </object>
    </child>
    </placeholder>
    ''')

    def add(self, *obj):
        try:
            EditPlace(self.dbstate, self.uistate, [], Place())
        except WindowActiveError:
            pass

    def remove(self, *obj):
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

    def edit(self, *obj):
        for handle in self.selected_handles():
            place = self.dbstate.db.get_place_from_handle(handle)
            try:
                EditPlace(self.dbstate, self.uistate, [], place)
            except WindowActiveError:
                pass

    def merge(self, *obj):
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
    return lambda x, y: func(val)
