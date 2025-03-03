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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
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
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.plug import START, END
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
                # allow for switching views in a category
                self.ui_category[cat_num] = [
                    UICATEGORY % uimenuitems,
                    UICATEGORYBAR % uibaritems,
                ]

        for pdata in plugman.get_reg_sidebars():
            module = plugman.load_plugin(pdata)
            if not module:
                print("Error loading sidebar '%s': skipping content" % pdata.name)
                continue

            sidebar_class = getattr(module, pdata.sidebarclass)
            sidebar_page = sidebar_class(dbstate, uistate, categories, views)
            self.add(pdata.menu_label, sidebar_page, pdata.order)

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
            action = (
                "ViewInCategory",
                self.cb_view_clicked,
                "",
                str(cat_num) + " " + str(view_num),
            )
            self.cat_view_group = ActionGroup("viewmenu", [action])
            uimanager.insert_action_group(self.cat_view_group)
            mergeid = uimanager.add_ui_from_string(self.ui_category[cat_num])
            self.merge_ids.append(mergeid)

        # Call the view_changed method for the active sidebar
        try:
            sidebar = self.pages[self.stack.get_visible_child_name()]
        except KeyError:
            return
        sidebar.view_changed(cat_num, view_num)

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
