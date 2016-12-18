#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Nick Hall
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
Provide the base classes for GRAMPS' DataView classes
"""

#----------------------------------------------------------------
#
# python modules
#
#----------------------------------------------------------------
from abc import abstractmethod
import logging

_LOG = logging.getLogger('.navigationview')

#----------------------------------------------------------------
#
# gtk
#
#----------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#----------------------------------------------------------------
#
# Gramps
#
#----------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from .pageview import PageView
from ..actiongroup import ActionGroup
from gramps.gen.utils.db import navigation_label
from gramps.gen.constfunc import mod_key

DISABLED = -1
MRU_SIZE = 10

MRU_TOP = [
    '<ui>'
    '<menubar name="MenuBar">'
    '<menu action="GoMenu">'
    '<placeholder name="CommonHistory">'
    ]

MRU_BTM = [
    '</placeholder>'
    '</menu>'
    '</menubar>'
    '</ui>'
    ]
#------------------------------------------------------------------------------
#
# NavigationView
#
#------------------------------------------------------------------------------
class NavigationView(PageView):
    """
    The NavigationView class is the base class for all Data Views that require
    navigation functionalilty. Views that need bookmarks and forward/backward
    should derive from this class.
    """

    def __init__(self, title, pdata, state, uistate, bm_type, nav_group):
        PageView.__init__(self, title, pdata, state, uistate)
        self.bookmarks = bm_type(self.dbstate, self.uistate, self.change_active)

        self.fwd_action = None
        self.back_action = None
        self.book_action = None
        self.other_action = None
        self.active_signal = None
        self.mru_signal = None
        self.nav_group = nav_group
        self.mru_active = DISABLED

        self.uistate.register(state, self.navigation_type(), self.nav_group)


    def navigation_type(self):
        """
        Indictates the navigation type. Navigation type can be the string
        name of any of the primary Objects. A History object will be
        created for it, see DisplayState.History
        """
        return None

    def define_actions(self):
        """
        Define menu actions.
        """
        PageView.define_actions(self)
        self.bookmark_actions()
        self.navigation_actions()

    def disable_action_group(self):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.disable_action_group(self)

        self.fwd_action.set_visible(False)
        self.back_action.set_visible(False)

    def enable_action_group(self, obj):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.enable_action_group(self, obj)

        self.fwd_action.set_visible(True)
        self.back_action.set_visible(True)
        hobj = self.get_history()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

    def change_page(self):
        """
        Called when the page changes.
        """
        hobj = self.get_history()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())
        self.other_action.set_sensitive(not self.dbstate.db.readonly)
        self.uistate.modify_statusbar(self.dbstate)

    def set_active(self):
        """
        Called when the page becomes active (displayed).
        """
        PageView.set_active(self)
        self.bookmarks.display()

        hobj = self.get_history()
        self.active_signal = hobj.connect('active-changed', self.goto_active)
        self.mru_signal = hobj.connect('mru-changed', self.update_mru_menu)
        self.update_mru_menu(hobj.mru)

        self.goto_active(None)

    def set_inactive(self):
        """
        Called when the page becomes inactive (not displayed).
        """
        if self.active:
            PageView.set_inactive(self)
            self.bookmarks.undisplay()
            hobj = self.get_history()
            hobj.disconnect(self.active_signal)
            hobj.disconnect(self.mru_signal)
            self.mru_disable()

    def navigation_group(self):
        """
        Return the navigation group.
        """
        return self.nav_group

    def get_history(self):
        """
        Return the history object.
        """
        return self.uistate.get_history(self.navigation_type(),
                                        self.navigation_group())

    def goto_active(self, active_handle):
        """
        Callback (and usable function) that selects the active person
        in the display tree.
        """
        active_handle = self.uistate.get_active(self.navigation_type(),
                                                self.navigation_group())
        if active_handle:
            self.goto_handle(active_handle)

        hobj = self.get_history()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

    def get_active(self):
        """
        Return the handle of the active object.
        """
        hobj = self.uistate.get_history(self.navigation_type(),
                                        self.navigation_group())
        return hobj.present()

    def change_active(self, handle):
        """
        Changes the active object.
        """
        hobj = self.get_history()
        if handle and not hobj.lock and not (handle == hobj.present()):
            hobj.push(handle)

    @abstractmethod
    def goto_handle(self, handle):
        """
        Needs to be implemented by classes derived from this.
        Used to move to the given handle.
        """

    def selected_handles(self):
        """
        Return the active person's handle in a list. Used for
        compatibility with those list views that can return multiply
        selected items.
        """
        active_handle = self.uistate.get_active(self.navigation_type(),
                                                self.navigation_group())
        return [active_handle] if active_handle else []

    ####################################################################
    # BOOKMARKS
    ####################################################################
    def add_bookmark(self, obj):
        """
        Add a bookmark to the list.
        """
        from gramps.gen.display.name import displayer as name_displayer

        active_handle = self.uistate.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        if active_person:
            self.bookmarks.add(active_handle)
            name = name_displayer.display(active_person)
            self.uistate.push_message(self.dbstate,
                                      _("%s has been bookmarked") % name)
        else:
            from ..dialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"),
                _("A bookmark could not be set because "
                  "no one was selected."),
                parent=self.uistate.window)

    def edit_bookmarks(self, obj):
        """
        Call the bookmark editor.
        """
        self.bookmarks.edit()

    def bookmark_actions(self):
        """
        Define the bookmark menu actions.
        """
        self.book_action = ActionGroup(name=self.title + '/Bookmark')
        self.book_action.add_actions([
            ('AddBook', 'gramps-bookmark-new', _('_Add Bookmark'),
             '<PRIMARY>d', None, self.add_bookmark),
            ('EditBook', 'gramps-bookmark-edit',
             _("%(title)s...") % {'title': _("Organize Bookmarks")},
             '<shift><PRIMARY>D', None,
             self.edit_bookmarks),
            ])

        self._add_action_group(self.book_action)

    ####################################################################
    # NAVIGATION
    ####################################################################
    def navigation_actions(self):
        """
        Define the navigation menu actions.
        """
        # add the Forward action group to handle the Forward button
        self.fwd_action = ActionGroup(name=self.title + '/Forward')
        self.fwd_action.add_actions([
            ('Forward', 'go-next', _("_Forward"),
             "%sRight" % mod_key(), _("Go to the next object in the history"),
             self.fwd_clicked)
            ])

        # add the Backward action group to handle the Forward button
        self.back_action = ActionGroup(name=self.title + '/Backward')
        self.back_action.add_actions([
            ('Back', 'go-previous', _("_Back"),
             "%sLeft" % mod_key(), _("Go to the previous object in the history"),
             self.back_clicked)
            ])

        self._add_action('HomePerson', 'go-home', _("_Home"),
                         accel="%sHome" % mod_key(),
                         tip=_("Go to the default person"), callback=self.home)

        self.other_action = ActionGroup(name=self.title + '/PersonOther')
        self.other_action.add_actions([
                ('SetActive', 'go-home', _("Set _Home Person"), None,
                 None, self.set_default_person),
                ])

        self._add_action_group(self.back_action)
        self._add_action_group(self.fwd_action)
        self._add_action_group(self.other_action)

    def set_default_person(self, obj):
        """
        Set the default person.
        """
        active = self.uistate.get_active('Person')
        if active:
            self.dbstate.db.set_default_person_handle(active)

    def home(self, obj):
        """
        Move to the default person.
        """
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.change_active(defperson.get_handle())
        else:
            from ..dialog import WarningDialog
            WarningDialog(_("No Home Person"),
                _("You need to set a 'default person' to go to. "
                  "Select the People View, select the person you want as "
                  "'Home Person', then confirm your choice "
                  "via the menu Edit ->Set Home Person."),
                parent=self.uistate.window)

    def jump(self):
        """
        A dialog to move to a Gramps ID entered by the user.
        """
        dialog = Gtk.Dialog(_('Jump to by Gramps ID'), self.uistate.window)
        dialog.set_border_width(12)
        label = Gtk.Label(label='<span weight="bold" size="larger">%s</span>' %
                          _('Jump to by Gramps ID'))
        label.set_use_markup(True)
        dialog.vbox.add(label)
        dialog.vbox.set_spacing(10)
        dialog.vbox.set_border_width(12)
        hbox = Gtk.Box()
        hbox.pack_start(Gtk.Label(label=_("%s: ") % _('ID')), True, True, 0)
        text = Gtk.Entry()
        text.set_activates_default(True)
        hbox.pack_start(text, False, True, 0)
        dialog.vbox.pack_start(hbox, False, True, 0)
        dialog.add_buttons(_('_Cancel'), Gtk.ResponseType.CANCEL,
                           _('_Jump to'), Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.vbox.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            gid = text.get_text()
            handle = self.get_handle_from_gramps_id(gid)
            if handle is not None:
                self.change_active(handle)
            else:
                self.uistate.push_message(
                    self.dbstate,
                    _("Error: %s is not a valid Gramps ID") % gid)
        dialog.destroy()

    def get_handle_from_gramps_id(self, gid):
        """
        Get an object handle from its Gramps ID.
        Needs to be implemented by the inheriting class.
        """
        pass

    def fwd_clicked(self, obj):
        """
        Move forward one object in the history.
        """
        hobj = self.get_history()
        hobj.lock = True
        if not hobj.at_end():
            hobj.forward()
            self.uistate.modify_statusbar(self.dbstate)
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(True)
        hobj.lock = False

    def back_clicked(self, obj):
        """
        Move backward one object in the history.
        """
        hobj = self.get_history()
        hobj.lock = True
        if not hobj.at_front():
            hobj.back()
            self.uistate.modify_statusbar(self.dbstate)
        self.back_action.set_sensitive(not hobj.at_front())
        self.fwd_action.set_sensitive(True)
        hobj.lock = False

    ####################################################################
    # MRU functions
    ####################################################################

    def mru_disable(self):
        """
        Remove the UI and action groups for the MRU list.
        """
        if self.mru_active != DISABLED:
            self.uistate.uimanager.remove_ui(self.mru_active)
            self.uistate.uimanager.remove_action_group(self.mru_action)
            self.mru_active = DISABLED

    def mru_enable(self):
        """
        Enables the UI and action groups for the MRU list.
        """
        if self.mru_active == DISABLED:
            self.uistate.uimanager.insert_action_group(self.mru_action, 1)
            self.mru_active = self.uistate.uimanager.add_ui_from_string(self.mru_ui)
            self.uistate.uimanager.ensure_update()

    def update_mru_menu(self, items):
        """
        Builds the UI and action group for the MRU list.
        """
        self.mru_disable()
        nav_type = self.navigation_type()
        hobj = self.get_history()
        menu_len = min(len(items) - 1, MRU_SIZE)

        entry = '<menuitem action="%s%02d"/>'
        data = [entry % (nav_type, index) for index in range(0, menu_len)]
        self.mru_ui = "".join(MRU_TOP) + "".join(data) + "".join(MRU_BTM)

        mitems = items[-MRU_SIZE - 1:-1] # Ignore current handle
        mitems.reverse()
        data = []
        for index, handle in enumerate(mitems):
            name, obj = navigation_label(self.dbstate.db, nav_type, handle)
            data.append(('%s%02d'%(nav_type, index), None,  name,
                         "%s%d" % (mod_key(), index), None,
                         make_callback(hobj.push, handle)))

        self.mru_action = ActionGroup(name=self.title + '/MRU')
        self.mru_action.add_actions(data)
        self.mru_enable()

    ####################################################################
    # Template functions
    ####################################################################
    @abstractmethod
    def build_tree(self):
        """
        Rebuilds the current display. This must be overridden by the derived
        class.
        """

    @abstractmethod
    def build_widget(self):
        """
        Builds the container widget for the interface. Must be overridden by the
        the base class. Returns a gtk container widget.
        """

    def key_press_handler(self, widget, event):
        """
        Handle the control+c (copy) and control+v (paste), or pass it on.
        """
        if self.active:
            if event.type == Gdk.EventType.KEY_PRESS:
                if (event.keyval == Gdk.KEY_c and
                    (event.get_state() & Gdk.ModifierType.CONTROL_MASK)):
                    self.call_copy()
                    return True
        return super(NavigationView, self).key_press_handler(widget, event)

    def call_copy(self):
        """
        Navigation specific copy (control+c) hander. If the
        copy can be handled, it returns true, otherwise false.

        The code brings up the Clipboard (if already exists) or
        creates it. The copy is handled through the drag and drop
        system.
        """
        nav_type = self.navigation_type()
        handles = self.selected_handles()
        return self.copy_to_clipboard(nav_type, handles)

def make_callback(func, handle):
    """
    Generates a callback function based off the passed arguments
    """
    return lambda x: func(handle)
