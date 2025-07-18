#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2024       Kari Kujansuu
# Copyright (C) 2025-      Serge Noiraud
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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import textwrap

# -------------------------------------------------------------------------
#
# GNOME modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE, URL_MANUAL_PAGE
from gramps.gen.config import config
from gramps.gui.basesidebar import BaseSidebar
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.display import display_help

_ = GRAMPS_LOCALE.translation.sgettext

WIKI_HELP_PAGE = URL_MANUAL_PAGE + "_-_Main_Window"
WIKI_HELP_SEC = _("Switching_Navigator_modes")
CLEAR = 1
SETALL = 2


# -------------------------------------------------------------------------
#
# Favorites class
#
# -------------------------------------------------------------------------
class FavoriteViews(ManagedWindow):

    def __init__(self, dialog, uistate, dbstate, views, categories, favorites):
        self.track = []
        self.favorites = favorites
        ManagedWindow.__init__(self, uistate, self.track, self._configure_favorite_view)
        self.dialog = dialog
        self.favorites = favorites
        self.categories = categories
        self.views = views
        self.check_views = []
        self.list_views = []
        self.config_name = "interface.favorite-views"
        self.dbstate = dbstate
        self.uistate = uistate
        self.set_window(
            Gtk.Dialog(title=_("Choose your favorite views")),
            None,
            _("Choose your favorite views"),
            None,
        )
        self.setup_configs("interface.favorites", 400, 300)
        help_btn = self.window.add_button(_("Help"), Gtk.ResponseType.HELP)
        help_btn.connect(
            "clicked", lambda x: display_help(WIKI_HELP_PAGE, WIKI_HELP_SEC)
        )
        self.window.add_button(_("Select All"), SETALL)
        self.window.add_button(_("Clear All"), CLEAR)
        self.window.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
        self.window.connect("response", self.on_response)
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_width(-1)
        box = self.window.get_content_area()
        box.pack_start(scroll, True, True, 0)
        vfav = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scroll.add(vfav)
        for cat_num, cat_name, cat_icon in categories:
            for view_num, view_name, view_icon in views[cat_num]:
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
                vfav.pack_start(hbox, True, True, 0)
                image = Gtk.Image()
                image.set_from_icon_name(view_icon, Gtk.IconSize.DND)
                image.show()
                hbox.pack_start(image, False, False, 0)
                button = Gtk.CheckButton()
                self.check_views.append(button)
                hbox.pack_start(button, False, False, 0)
                if view_name in favorites:
                    button.set_active(True)
                else:
                    button.set_active(False)
                button.connect("clicked", self._configure_favorite_view, view_name)
                title = Gtk.Label(label=view_name)
                title.set_justify(Gtk.Justification.LEFT)
                self.list_views.append(view_name)
                hbox.pack_start(title, False, True, 0)
        self.show()

    def _configure_favorite_view(self, button, viewname):
        """define your favorite views"""
        if button.get_active():
            if viewname not in self.favorites:
                self.favorites.append(viewname)
        elif viewname in self.favorites:
            self.favorites.remove(viewname)
        config.set(self.config_name, self.favorites)
        FavoritesSidebar.show_views(
            self.dialog, self.categories, self.views, self.favorites
        )

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.CLOSE:
            self.dialog.select.set_sensitive(True)
            dialog.destroy()
        if response == Gtk.ResponseType.HELP:
            display_help()
        elif response == SETALL:
            # set all views active
            self.set_views(setall=True)
        elif response == CLEAR:
            # set all views inactive
            self.set_views(setall=False)

    def set_views(self, setall=False):
        views = []
        for check in self.check_views:
            if setall:
                check.set_active(True)
                views = self.list_views
            else:
                check.set_active(False)
        config.set(self.config_name, views)


# -------------------------------------------------------------------------
#
# Favorites Sidebar class
#
# -------------------------------------------------------------------------
class FavoritesSidebar(BaseSidebar):
    """
    A sidebar displaying a simple list of toggle buttons that allow the user to change the current view.
    """

    def __init__(self, dbstate, uistate, categories, views):
        self.viewmanager = uistate.viewmanager
        self.views = views

        self.buttons = []
        self.views = views
        self.categories = categories
        self.favorites = []
        self.config_name = "interface.favorite-views"
        if not config.is_set(self.config_name):
            config.register(self.config_name, [])
        self.favorites = config.get(self.config_name)
        self.button_handlers = []
        self.lookup = {}
        self.uistate = uistate
        self.dbstate = dbstate

        self.window = Gtk.ScrolledWindow()
        self.window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.show_views(self.categories, self.views, self.favorites)
        self.window.show()

    def show_views(self, categories, views, favorites):
        children = self.window.get_children()
        if children:
            children[0].destroy()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(vbox)
        use_text = config.get("interface.sidebar-text")
        for cat_num, cat_name, cat_icon in categories:
            catbox = Gtk.Box()
            image = Gtk.Image()
            image.set_from_icon_name(cat_icon, Gtk.IconSize.BUTTON)
            catbox.pack_start(image, False, False, 4)
            if use_text:
                label = Gtk.Label(label=cat_name)
                catbox.pack_start(label, False, True, 4)
            catbox.set_tooltip_text(cat_name)

            viewbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            for view_num, view_name, view_icon in views[cat_num]:
                if view_name in self.favorites:
                    # create the button and add it to the sidebar
                    button = self.__make_sidebar_button(
                        use_text, cat_num, view_num, view_name, view_icon
                    )
                    if view_num == 0:
                        button.set_margin_top(10)

                    viewbox.pack_start(button, False, False, 0)
            vbox.pack_start(viewbox, False, False, 0)

        self.select = self.__make_sidebar_button(
            use_text, 99, 0, _("Choose your favorite views"), "gramps-config"
        )
        self.select.set_margin_top(10)
        vbox.pack_start(self.select, False, False, 0)
        vbox.show_all()

    def get_top(self):
        """
        Return the top container widget for the GUI.
        """
        return self.window

    def view_changed(self, cat_num, view_num):
        """
        Called when the active view is changed.
        """
        # Expand category
        # Set new button as selected
        button_num = self.lookup.get((cat_num, view_num))
        self.__handlers_block()
        for index, button in enumerate(self.buttons):
            if index == button_num:
                button.set_active(True)
            else:
                button.set_active(False)
        self.__handlers_unblock()

    def __handlers_block(self):
        """
        Block signals to the buttons to prevent spurious events.
        """
        for idx, button in enumerate(self.buttons):
            button.handler_block(self.button_handlers[idx])

    def __handlers_unblock(self):
        """
        Unblock signals to the buttons.
        """
        for idx, button in enumerate(self.buttons):
            button.handler_unblock(self.button_handlers[idx])

    def cb_view_clicked(self, radioaction, current, cat_num):
        """
        Called when a button causes a view change.
        """
        view_num = radioaction.get_current_value()
        self.viewmanager.goto_page(cat_num, view_num)

    def __category_clicked(self, button, cat_num):
        """
        Called when a category button is clicked.
        """
        # Make the button active.  If it was already active the category will
        # not change.
        button.set_active(True)
        self.viewmanager.goto_page(cat_num, None)

    def __view_clicked(self, button, cat_num, view_num):
        """
        Called when a view button is clicked.
        """
        if cat_num == 99:
            # We configure the favorite bar
            self.select.set_sensitive(False)
            self.favorites = config.get(self.config_name)
            FavoriteViews(
                self,
                self.uistate,
                self.dbstate,
                self.views,
                self.categories,
                self.favorites,
            )
        else:
            self.viewmanager.goto_page(cat_num, view_num)

    def cb_menu_clicked(self, menuitem, cat_num, view_num):
        """
        Called when a view is selected from a drop-down menu.
        """
        self.viewmanager.goto_page(cat_num, view_num)

    def __make_sidebar_button(self, use_text, cat_num, view_num, view_name, view_icon):
        """
        Create the sidebar button. The page_title is the text associated with
        the button.
        """
        top = Gtk.Box()

        # create the button
        button = Gtk.ToggleButton()
        button.set_relief(Gtk.ReliefStyle.NONE)
        self.buttons.append(button)
        self.lookup[(cat_num, view_num)] = len(self.buttons) - 1

        # add the tooltip
        button.set_tooltip_text(view_name)

        # connect the signal, along with the index as user data
        handler_id = button.connect("clicked", self.__view_clicked, cat_num, view_num)
        self.button_handlers.append(handler_id)
        button.show()

        # add the image. If we are using text, use the BUTTON (larger) size.
        # otherwise, use the smaller size
        hbox = Gtk.Box()
        hbox.show()
        image = Gtk.Image()
        if use_text:
            image.set_from_icon_name(view_icon, Gtk.IconSize.BUTTON)
        else:
            image.set_from_icon_name(view_icon, Gtk.IconSize.DND)
        image.show()
        hbox.pack_start(image, False, False, 0)
        hbox.set_spacing(4)

        # add text if requested
        if use_text:
            width = 20
            lines = textwrap.wrap(view_name, width, break_long_words=False)
            labeltext = "\n".join(lines)
            label = Gtk.Label(label=labeltext)
            label.show()
            hbox.pack_start(label, False, True, 0)

        button.add(hbox)

        top.pack_start(button, False, True, 0)

        return top
