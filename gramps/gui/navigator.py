#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010 Nick Hall
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
A module that provides pluggable sidebars.  These provide an interface to
manage pages in the main Gramps window.
"""

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.plug import START, END
from gramps.gen.config import config
from .pluginmanager import GuiPluginManager
from .uimanager import ActionGroup

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
UICATEGORY = """      <section id="ViewsInCategory">
        %s
      </section>
    """
UICATEGORYBAR = """    <placeholder id='ViewsInCategoryBar'>
        %s
      </placeholder>
    """
UICATEGORYBAR_SIMPLE = """    <placeholder id='ViewsInCategoryBar'>
      <child>
        <object class="GtkToolButton" id="ViewButton">
          <property name="icon-name">view-list-symbolic</property>
          <property name="action-name">win.ViewButton</property>
          <property name="tooltip_text" translatable="yes">Switch view</property>
          <property name="label" translatable="yes">View</property>
        </object>
        <packing>
          <property name="homogeneous">False</property>
        </packing>
      </child>
    </placeholder>
    """
UIVIEWPOPUP = """<menu id='ViewButtonPopup'>
%s
</menu>"""
UIVIEWPOPUP_ITEM = """  <item>
    <attribute name="action">win.ViewInCategory</attribute>
    <attribute name="label" translatable="yes">%s</attribute>
    <attribute name="target">%s</attribute>
  </item>
"""

CATEGORY_ICON = {
    "Dashboard": "gramps-gramplet",
    "People": "gramps-person",
    "Relationships": "gramps-relation",
    "Families": "gramps-family",
    "Events": "gramps-event",
    "Ancestry": "gramps-pedigree",
    "Places": "gramps-place",
    "Geography": "gramps-geo",
    "Sources": "gramps-source",
    "Repositories": "gramps-repository",
    "Media": "gramps-media",
    "Notes": "gramps-notes",
    "Citations": "gramps-citation",
}


# -------------------------------------------------------------------------
#
# Navigator class
#
# -------------------------------------------------------------------------
class Navigator:
    """
    A class which defines the graphical representation of the Gramps navigator.
    """

    def __init__(self, viewmanager):
        self.viewmanager = viewmanager
        self.pages = {}
        self._active_page = None
        self.active_cat = None
        self.active_view = None

        self.ui_category = {}
        self.cat_view_group = None
        self.merge_ids = []

        self.use_simplified = config.get("interface.use-simplified-interface")

        self.config_name = "interface.favorite-menu"
        if not config.is_set(self.config_name):
            config.register(self.config_name, "")
        self.conf_ft = True

        self.top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top.show()

        self.select_button = Gtk.ComboBoxText()
        self.select_button.hide()
        self.top.pack_end(self.select_button, False, True, 0)

        self.stack = Gtk.Stack(homogeneous=False)
        self.stack.show()
        self.stack.connect("notify::visible-child-name", self.cb_switch_page)
        self.top.pack_start(self.stack, True, True, 0)

        self.select_button.bind_property(
            "active-id",
            self.stack,
            "visible-child-name",
            GObject.BindingFlags.BIDIRECTIONAL,
        )

    def load_plugins(self, dbstate, uistate):
        """
        Load the sidebar plugins.
        """
        menuitem = """
            <item>
              <attribute name="action">win.ViewInCategory</attribute>
              <attribute name="label" translatable="yes">%s</attribute>
              <attribute name="target">%d %d</attribute>
            </item>
            """
        baritem = """
            <child>
              <object class="GtkToggleToolButton" id="bar%d">
                <property name="action-name">win.ViewInCategory</property>
                <property name="action-target">'%d %d'</property>
                <property name="icon-name">%s</property>
                <property name="tooltip_text" translatable="yes">%s</property>
                <property name="label" translatable="yes">%s</property>
              </object>
              <packing>
                <property name="homogeneous">False</property>
              </packing>
            </child>
            """

        plugman = GuiPluginManager.get_instance()

        categories = []
        views = {}
        for cat_num, cat_views in enumerate(self.viewmanager.get_views()):
            uimenuitems = ""
            uibaritems = ""
            for view_num, page in enumerate(cat_views):
                if view_num == 0:
                    views[cat_num] = []
                    cat_name = page[0].category[1]
                    cat_icon = CATEGORY_ICON.get(page[0].category[0])
                    if cat_icon is None:
                        try:
                            cat_icon = page[0].stock_category_icon
                        except AttributeError:
                            try:
                                cat_icon = page[0].stock_icon
                            except AttributeError:
                                cat_icon = "gramps-view"
                    if cat_icon is None:
                        cat_icon = "gramps-view"
                    categories.append([cat_num, cat_name, cat_icon])

                if view_num < 9:
                    accel = "<PRIMARY><ALT>%d" % ((view_num % 9) + 1)
                    self.viewmanager.uimanager.app.set_accels_for_action(
                        "win.ViewInCategory('%d %d')" % (cat_num, view_num), [accel]
                    )
                uimenuitems += menuitem % (page[0].name, cat_num, view_num)

                stock_icon = page[0].stock_icon
                if stock_icon is None:
                    stock_icon = cat_icon
                uibaritems += baritem % (
                    view_num,
                    cat_num,
                    view_num,
                    stock_icon,
                    page[0].name,
                    page[0].name,
                )

                views[cat_num].append((view_num, page[0].name, stock_icon))

            if len(cat_views) > 1:
                if self.use_simplified:
                    popup_items = "".join(
                        UIVIEWPOPUP_ITEM % (name, "%d %d" % (cat_num, vnum))
                        for vnum, name, _icon in views[cat_num]
                    )
                    self.ui_category[cat_num] = [
                        UICATEGORY % uimenuitems,
                        UICATEGORYBAR_SIMPLE,
                        UIVIEWPOPUP % popup_items,
                    ]
                else:
                    self.ui_category[cat_num] = [
                        UICATEGORY % uimenuitems,
                        UICATEGORYBAR % uibaritems,
                    ]

        for pdata in plugman.get_reg_sidebars():
            if self.use_simplified and pdata.id != "categorysidebar":
                continue
            module = plugman.load_plugin(pdata)
            if not module:
                print("Error loading sidebar '%s': skipping content" % pdata.name)
                continue

            sidebar_class = getattr(module, pdata.sidebarclass)
            sidebar_page = sidebar_class(dbstate, uistate, categories, views)
            self.add(pdata.menu_label, sidebar_page, pdata.order)
        if not self.use_simplified:
            self.fav_menu = config.get(self.config_name)
            if self.fav_menu != "":
                self.stack.set_visible_child_name(self.fav_menu)

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.top

    def add(self, title, sidebar, order):
        """
        Add a page to the sidebar for a plugin.
        """
        self.pages[title] = sidebar
        page = sidebar.get_top()
        self.stack.add_named(page, title)

        if order == START:
            self.select_button.prepend(id=title, text=title)
            self.select_button.set_active_id(title)
        else:
            self.select_button.append(id=title, text=title)

        if len(self.stack.get_children()) == 2:
            self.select_button.show_all()

    def view_changed(self, cat_num, view_num):
        """
        Called when a Gramps view is changed.
        """
        self.active_cat = cat_num
        self.active_view = view_num

        # Add buttons to the menu for the different view in the category
        uimanager = self.viewmanager.uimanager
        if self.cat_view_group:
            if self.cat_view_group in uimanager.get_action_groups():
                uimanager.remove_action_group(self.cat_view_group)

            list(map(uimanager.remove_ui, self.merge_ids))

        if cat_num in self.ui_category:
            actions = [
                (
                    "ViewInCategory",
                    self.cb_view_clicked,
                    "",
                    str(cat_num) + " " + str(view_num),
                ),
            ]
            if self.use_simplified:
                actions.append(("ViewButton", self.cb_view_button))
            self.cat_view_group = ActionGroup("viewmenu", actions)
            uimanager.insert_action_group(self.cat_view_group)
            mergeid = uimanager.add_ui_from_string(self.ui_category[cat_num])
            self.merge_ids.append(mergeid)

        # Call the view_changed method for the active sidebar
        try:
            sidebar = self.pages[self.stack.get_visible_child_name()]
        except KeyError:
            return
        sidebar.view_changed(cat_num, view_num)

    def cb_view_button(self, *args):
        """
        Display the popup menu when the View toolbar button is clicked.
        """
        uimanager = self.viewmanager.uimanager
        menu_model = uimanager.get_widget("ViewButtonPopup")
        button = uimanager.get_widget("ViewButton")
        if menu_model and button:
            popup_menu = Gtk.Menu.new_from_model(menu_model)
            popup_menu.attach_to_widget(button, None)
            popup_menu.show_all()
            popup_menu.popup_at_widget(
                button, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None
            )

    def cb_view_clicked(self, radioaction, value):
        """
        Called when a view is selected from the menu.
        """
        cat_num, view_num = value.get_string().split()
        self.viewmanager.goto_page(int(cat_num), int(view_num))

    def cb_switch_page(self, stack, pspec):
        """
        Called when the user has switched to a new sidebar plugin page.
        """
        old_page = self._active_page
        if old_page is not None:
            self.pages[old_page].inactive()

        title = stack.get_visible_child_name()
        if title is None:
            # May happen during the time that the widgets have been created, but the
            # pages haven't been added.
            return
        self.pages[title].active(self.active_cat, self.active_view)
        if self.active_view is not None:
            self.pages[title].view_changed(self.active_cat, self.active_view)
        self._active_page = title
        if self.conf_ft:
            self.conf_ft = False
        else:
            config.set(self.config_name, self.stack.get_visible_child_name())
