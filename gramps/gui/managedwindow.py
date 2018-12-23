#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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
Provide the managed window interface, which allows Gramps to track
the create/deletion of dialog windows.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os
from io import StringIO
import html
#-------------------------------------------------------------------------
#
# GNOME/GTK
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GLADE_FILE, ICON
from gramps.gen.errors import WindowActiveError
from gramps.gen.config import config
from gramps.gen.constfunc import is_quartz
from .uimanager import ActionGroup
from .glade import Glade

#-------------------------------------------------------------------------
#
# Window manager
#
#-------------------------------------------------------------------------

_win_top = '<section id="WinMenu">\n'
_win_btm = '</section>\n'
DISABLED = -1

#-----------------------------------------------------------------------
#
# Helper function
#
#-----------------------------------------------------------------------

def get_object(self,value):
    raise DeprecationWarning("ManagedWindow.get_object: shouldn't get here")
    if self.get_name() == value:
        return self
    elif hasattr(self,'get_children'):
        for child in self.get_children():
            object = get_object(child, value)
            if object is not None:
                return object
    return None

class GrampsWindowManager:
    """
    Manage hierarchy of open Gramps windows.

    This class's purpose is to manage the hierarchy of open windows.
    The idea is to maintain the tree of branches and leaves.
    A leaf does not have children and corresponds to a single open window.
    A branch has children and corresponds to a group of windows.

    We will follow the convention of having first leaf in any given
    branch represent a parent window of the group, and the rest of the
    children leaves/branches represent windows spawned from the parent.

    The tree structure is maintained as a list of items.
    Items which are lists are branches.
    Items which are not lists are leaves.

    Lookup of an item is done via track sequence. The elements of
    the track sequence specify the lookup order: [2,3,1] means
    'take the second item of the tree, take its third child, and
    then the first child of that child'.

    Lookup can be also done by ID for windows that are identifiable.
    """

    def __init__(self, uimanager):
        # initialize empty tree and lookup dictionary
        self.uimanager = uimanager
        self.window_tree = []
        self.id2item = {}
        self.action_group = ActionGroup(name='WindowManger')
        self.active = DISABLED
        self.ui = _win_top + _win_btm

    def disable(self):
        """
        Remove the UI and action groups if the navigation is enabled
        """
        if self.active != DISABLED:
            self.uimanager.remove_ui(self.active)
            self.uimanager.remove_action_group(self.action_group)
            self.active = DISABLED

    def enable(self):
        """
        Enables the UI and action groups
        """
        self.uimanager.insert_action_group(self.action_group)
        self.active = self.uimanager.add_ui_from_string([self.ui])
        self.uimanager.update_menu()

    def get_item_from_track(self, track):
        # Recursively find an item given track sequence
        item = self.window_tree
        for index in track:
            item = item[index]
        return item

    def get_item_from_id(self, item_id):
        # Find an item given its ID
        # Return None if the ID is not found
        return self.id2item.get(item_id, None)

    def get_item_from_window(self, window):
        """ This finds a ManagedWindow from a Gtk top_level object (typicaly
        a window).

        For example, to find my managedwindow track within a class of Gtk
        widget:
            mywindow = self.get_toplevel()  # finds top level Gtk object
            managed_window = self.uistate.gwm.get_item_from_window(mywindow)
            track = managed_window.track
        """
        for key, item in self.id2item.items():
            if item.window == window:
                return self.id2item[key]
        return None

    def find_modal_window(self, window):
        """ This finds a ManagedWindow that is modal, if any, excluding the
        'window' that is a parameter.  There should be only one.
        If no ManagedWindow is modal, returns None.
        """
        for dummy, item in self.id2item.items():
            if item.window != window and item.window.get_modal():
                return item.window
        return None

    def close_track(self, track):
        # This is called when item needs to be closed
        # Closes all its children and then removes the item from the tree.
        try:
            item = self.get_item_from_track(track)
            self.recursive_action(item, self.close_item)
            # This only needs to be run once for the highest level point
            # to remove.
            self.remove_item(track)
        except IndexError:
            print("Missing item from window manager", track, self.close_item)

    def recursive_action(self, item, func, *args):
        # This function recursively calls itself over the child items
        # starting with the given item.
        # Eventualy, every non-list item (leaf) will be reached
        # and the func(item,*args) will be called on that item.
        if isinstance(item, list):
            # If this item is a branch
            # close the children except for the first one
            for sub_item in item[1:]:
                self.recursive_action(sub_item, func, *args)
            # return the first child
            last_item = item[0]
        else:
            # This item is a leaf -- no children to close
            # return itself
            last_item = item
        func(last_item, *args)

    def close_item(self, item, *args):
        # Given an item, close its window and remove it's ID from the dict
        if item.opened:
            item.close()
        if item.window_id:
            del self.id2item[item.window_id]
            item.window_id = None
        if item.get_window():
            item.get_window().destroy()
            item.window = None

    def remove_item(self, track):
        # We need the whole gymnastics below because our item
        # may actually be a list consisting of a single real
        # item and empty lists.

        # find the track corresponding to the parent item
        parent_track = track[:-1]
        # find index of our item in parent
        child_in_parent = track[-1:][0]
        # obtain parent item and remove our item from it
        parent_item = self.get_item_from_track(parent_track)
        parent_item.pop(child_in_parent)
        # Adjust each item following the removed one
        # so that it's track is down by one on this level
        for ix in range(child_in_parent, len(parent_item)):
            item = parent_item[ix]
            self.recursive_action(item, self.move_item_down, len(track)-1)
        # Rebuild menu
        self.build_windows_menu()

    def move_item_down(self, item, *args):
        # Given an item and an index, adjust the item's track
        # by subtracting 1 from that index's level
        index = args[0]
        item.track[index] -= 1

    def add_item(self, track, item):
        # if the item is identifiable then we need to remember
        # its id so that in the future we recall this window
        # instead of spawning a new one
        # So people can make as many windows of type item.window_id = None
        # Use this for add dialogs, where users may add as many values
        # simultaneously as they want.
        # Actually, we should do this away, as requiring at least id(obj)
        #  is not a big requirement ?
        if item.window_id:
            self.id2item[item.window_id] = item

        # Make sure we have a track
        parent_item = self.get_item_from_track(track)
        assert isinstance(parent_item, list) or track == [], \
               "Gwm: add_item: Incorrect track - Is parent not a leaf?"

        # Prepare a new item, depending on whether it is branch or leaf
        if item.submenu_label:
            # This is an item with potential children -- branch
            new_item = [item]
        else:
            # This is an item without children -- leaf
            new_item = item

        # append new item to the parent
        parent_item.append(new_item)

        # rebuild the Windows menu based on the new tree
        self.build_windows_menu()

        # prepare new track corresponding to the added item and return it
        new_track = track + [len(parent_item)-1]
        return new_track

    def call_back_factory(self, item):
        if not isinstance(item, list):
            def func(*obj):
                if item.window_id and self.id2item.get(item.window_id):
                    self.id2item[item.window_id]._present()
        else:
            def func(*obj):
                pass
        return func

    def generate_id(self, item):
        return 'wm/' + str(item.window_id)

    def display_menu_list(self, data, action_data, mlist):
        menuitem = ('<item>\n'
                    '<attribute name="action">win.%s</attribute>\n'
                    '<attribute name="label" translatable="yes">'
                    '%s...</attribute>\n'
                    '</item>\n')
        if isinstance(mlist, (list, tuple)):
            i = mlist[0]
            idval = self.generate_id(i)
            data.write('<submenu>\n<attribute name="label"'
                       ' translatable="yes">%s</attribute>\n' %
                       html.escape(i.submenu_label))
        else:
            i = mlist
            idval = self.generate_id(i)

        data.write(menuitem % (idval, html.escape(i.menu_label)))
        action_data.append((idval, self.call_back_factory(i)))

        if isinstance(mlist, (list, tuple)) and (len(mlist) > 1):
            for i in mlist[1:]:
                if isinstance(i, list):
                    self.display_menu_list(data, action_data, i)
                else:
                    idval = self.generate_id(i)
                    data.write(menuitem % (idval, html.escape(i.menu_label)))
                    action_data.append((idval, self.call_back_factory(i)))
        if isinstance(mlist, (list, tuple)):
            data.write('</submenu>\n')

    def build_windows_menu(self):
        if self.active != DISABLED:
            self.uimanager.remove_ui(self.active)
            self.uimanager.remove_action_group(self.action_group)

        self.action_group = ActionGroup(name='WindowManger')
        action_data = []

        data = StringIO()
        data.write(_win_top)
        for i in self.window_tree:
            self.display_menu_list(data, action_data, i)
        data.write(_win_btm)
        self.ui = data.getvalue()
        data.close()
        self.action_group.add_actions(action_data)
        self.enable()

#-------------------------------------------------------------------------
#
# Gramps Managed Window class
#
#-------------------------------------------------------------------------
class ManagedWindow:
    """
    Managed window base class.

    This class provides all the goodies necessary for user-friendly window
    management in GRAMPS: registering the menu item under the Windows
    menu, keeping track of child windows, closing them on close/delete
    event, and presenting itself when selected or attempted to create again.
    """
    def __init__(self, uistate, track, obj, modal=False):
        """
        Create child windows and add itself to menu, if not there already.


        The usage from derived classes is envisioned as follows:


        from .managedwindow import ManagedWindow
        class SomeWindowClass(ManagedWindow):
            def __init__(self, uistate, track, obj, modal):
                window_id = self        # Or e.g. window_id = person.handle
                ManagedWindow.__init__(self,
                                       uistate,
                                       track,
                                       window_id,
                                       modal=False)
                # Proceed with the class.
                window = Gtk.Dialog()  # Some Gtk window object to manage
                self.set_window(window, None, None)  # See set_window def below
                # setup window size, position tracking configuration
                self.setup_configs(self, "interface.mywindow", 680, 400)
                ...
                self.close()

            def build_menu_names(self, obj):
                ''' Define menu labels.  If your ManagedWindow can have
                ManagedWindow children, you must include a submenu_label
                string; However, if modal, that string is never seen and can
                be ' '.
                '''
                submenu_label = None    # This window cannot have children
                menu_label = 'Menu label for this window'
                return (menu_label, submenu_label)

        :param uistate:  gramps uistate
        :param track:    {list of parent windows, [] if the main Gramps window
                            is the parent}
        :param obj:      The object that is used to id the managed window,
                            The inheriting object needs a method
                            build_menu_names(self, obj)
                            which works on this obj and creates menu labels
                            for use in the Gramps Window Menu.
                            If self.submenu_label ='' then leaf, else branch
        :param modal:    True/False, if True, this window is made modal
                            (always on top, and always has focus).  Any child
                            windows are also automatically made modal by moving
                            the modal flag to the child.  On close of a child
                            the modal flag is sent back to the parent.

        If a modal window is used and has children, its and any child 'track'
        parameters must properly be set to the parents 'self.track'.
        Only one modal window can be supported by Gtk without potentially
        hiding of a modal window while it has focus.  So don't use
        non-managed Gtk windows as children and set them modal.

        If you use the 'Gtk.Dialog.run()' within your ManagedWindow, Gtk makes
        the dialog modal.  Accordingly you MUST also set the ManagedWindow
        modal for proper operation of any child windows.

        You must use 'self.show()' in order for your ManagedWindow to work
        properly, this in turn calls the Gtk.Window.show_all() for you.

        The ManagedWindow uses 'track' to properly do a
        Gtk.Window.set_transient_for() for you; you don't have to do it
        yourself.  If you need a 'parent=' to call an unmanaged window,
        self.window is available.

        """
        window_key = self.build_window_key(obj)
        menu_label, submenu_label = self.build_menu_names(obj)
        self._gladeobj = None
        self.isWindow = None
        self.width_key = None
        self.height_key = None
        self.horiz_position_key = None
        self.vert_position_key = None
        self.__refs_for_deletion = []
        self.modal = modal
        self.other_modal_window = None

        if uistate and uistate.gwm.get_item_from_id(window_key):
            uistate.gwm.get_item_from_id(window_key)._present()
            raise WindowActiveError('This window is already active')
        else:
            self.window_id = window_key
            self.submenu_label = submenu_label
            self.menu_label = menu_label
            self.uistate = uistate
            if uistate:
                self.track = self.uistate.gwm.add_item(track, self)
            else:
                self.track = []
            # Work out parent_window
            if len(self.track) > 1:
            # We don't belong to the lop level
                if self.track[-1] > 0:
                # If we are not the first in the group,
                # then first in that same group is our parent
                    parent_item_track = self.track[:-1]
                    parent_item_track.append(0)
                else:
                # If we're first in the group, then our parent
                # is the first in the group one level up
                    parent_item_track = self.track[:-2]
                    parent_item_track.append(0)

                # Based on the track, get item and then window object
                managed_parent = self.uistate.gwm.get_item_from_track(
                    parent_item_track)
                self.parent_window = managed_parent.window
            else:
                # On the top level: we use gramps top window
                if self.uistate:
                    self.parent_window = self.uistate.window
                else:
                    self.parent_window = None

    def set_window(self, window, title, text, msg=None, isWindow=False):
        """
        Set the window that is managed.

        :param window:   if isWindow=False window must be a Gtk.Window() object
                         (or a subclass such as Gtk.Dialog), otherwise None
        :param title:    a label widget in which to write the title,
                         else None if not needed
        :param text:     text to use as title of window and in title param
                         can also be None if Glade defines title
        :param msg:      if not None, use msg as title of window instead of text
        :param isWindow: {if isWindow than self is the window
                            (so self inherits from Gtk.Window and
                            from ManagedWindow)
                         if not isWindow, than window is the Window to manage,
                            and after this method self.window stores it.
                        }

        """
        self.isWindow = isWindow
        self.msg = msg
        self.titlelabel = title
        if self.isWindow :
            set_titles(self, title, text, msg)
            self.window = self
        else :
            set_titles(window, title, text, msg)
            #closing the Gtk.Window must also close ManagedWindow
            self.window = window
            self.window.connect('delete-event', self.close)
        #Set the mnemonic modifier on Macs to alt-ctrl so that it
        #doesn't interfere with the extended keyboard, see
        #https://gramps-project.org/bugs/view.php?id=6943
        if is_quartz():
            self.window.set_mnemonic_modifier(
                Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK)

        if self.modal:
            self.window.set_modal(True)
        # The following makes sure that we only have one modal window open;
        # if more the older ones get temporarily made non-modal.
        if self.uistate:
            self.other_modal_window = self.uistate.gwm.find_modal_window(
                window)
        if self.other_modal_window:
            self.other_modal_window.set_modal(False)
            self.window.set_modal(True)
            self.modal = True


    def get_window(self):
        """
        Return the managed window.
        """
        if self.isWindow:
            return self
        else:
            return self.window

    def update_title(self, text):
        if self.isWindow:
            set_titles(self, self.titlelabel, text, self.msg)
        else:
            set_titles(self.window, self.titlelabel, text, self.msg)

    def build_menu_names(self, obj):
        return ('Undefined Menu','Undefined Submenu')

    def build_window_key(self, obj):
        return id(obj)

    def define_glade(self, top_module, glade_file=None, also_load=[]):
        if glade_file is None:
            raise TypeError("ManagedWindow.define_glade: no glade file")
            glade_file = GLADE_FILE
        self._gladeobj = Glade(glade_file, None, top_module, also_load)
        return self._gladeobj

    def get_widget(self, name):
        assert(self._gladeobj)
        object = self._gladeobj.get_child_object(name)
        if object is not None:
            return object
        raise ValueError(
            'ManagedWindow.get_widget: "%s" widget not found in "%s/%s"' %
            (name, self._gladeobj.dirname, self._gladeobj.filename))
        return object

    def connect_button(self, button_name, function):
        assert(self._gladeobj)
        self.get_widget(button_name).connect('clicked', function)

    def show(self):
        """ The following covers a case where there are multiple modal windows
        to be open; possibly not in parent child relation.  If this occurs,
        we use most recent modal window as parent.  This occurs during startup
        when both the 'Available Gramps Updates for Addons' and 'Family Trees'
        windows are started by the viewmanager.
        """
        assert self.window, "ManagedWindow: self.window does not exist!"
        if self.other_modal_window:
            self.window.set_transient_for(self.other_modal_window)
        else:
            self.window.set_transient_for(self.parent_window)
        self.opened = True
        self.window.show_all()

    def close(self, *obj):
        """
        Close itself.

        Takes care of closing children and removing itself from menu.
        """
        self.opened = False
        self._save_position(save_config=False)  # the next line will save it
        self._save_size()
        self.uistate.gwm.close_track(self.track)
        self.clean_up()
        # put a previously modal window back to modal, now that we are closing
        if self.other_modal_window:
            self.other_modal_window.set_modal(True)
        self.parent_window.present()

    def _present(self):
        """
        Present window (unroll/unminimize/bring to top).
        """
        assert hasattr(self, 'window'), \
               "ManagedWindow: self.window does not exist!"
        self.window.present()

    def _set_size(self):
        """
        Set the dimensions of the window
        """
        # self.width_key is set in the subclass (or in setup_configs)
        if self.width_key is not None:
            width = config.get(self.width_key)
            height = config.get(self.height_key)
            self.window.resize(width, height)

    def _save_size(self):
        """
        Save the dimensions of the window to the config file
        """
        # self.width_key is set in the subclass (or in setup_configs)
        if self.width_key is not None:
            (width, height) = self.window.get_size()
            config.set(self.width_key, width)
            config.set(self.height_key, height)
            config.save()

    def _set_position(self):
        """
        Set the position of the window
        """
        # self.horiz_position_key is set in the subclass (or in setup_configs)
        if self.horiz_position_key is not None:
            horiz_position = config.get(self.horiz_position_key)
            vert_position = config.get(self.vert_position_key)
            self.window.move(horiz_position, vert_position)

    def _save_position(self, save_config=True):
        """
        Save the window's position to the config file

        (You can set save_config False if a _save_size() will instantly follow)
        """
        # self.horiz_position_key is set in the subclass (or in setup_configs)
        if self.horiz_position_key is not None:
            (horiz_position, vert_position) = self.window.get_position()
            config.set(self.horiz_position_key, horiz_position)
            config.set(self.vert_position_key, vert_position)
            if save_config:
                config.save()

    def setup_configs(self, config_base,
                      default_width, default_height,
                      default_horiz_position=None, default_vert_position=None,
                      p_width=None, p_height=None): # for fullscreen
        """
        Helper method to setup the window's configuration settings

        @param config_base: the common config name, e.g. 'interface.clipboard'
        @type config_base: str
        @param default_width, default_height: the default width and height
        @type default_width, default_height: int
        @param default_horiz_position, default_vert_position: if either is None
            then that position is centered on the parent, else explicitly set
        @type default_horiz_position, default_vert_position: int or None
        @param p_width, p_height: the parent's width and height
        @type p_width, p_height: int or None
        """
        self.width_key = config_base + '-width'
        self.height_key = config_base + '-height'
        self.horiz_position_key = config_base + '-horiz-position'
        self.vert_position_key = config_base + '-vert-position'
        if p_width is None and p_height is None: # default case
            (p_width, p_height) = self.parent_window.get_size()
            (p_horiz, p_vert) = self.parent_window.get_position()
        else:
            p_horiz = p_vert = 0 # fullscreen
        if default_horiz_position is None:
            default_horiz_position = p_horiz + ((p_width - default_width) // 2)
        if default_vert_position is None:
            default_vert_position = p_vert + ((p_height - default_height) // 2)
        config.register(self.width_key, default_width)
        config.register(self.height_key, default_height)
        config.register(self.horiz_position_key, default_horiz_position)
        config.register(self.vert_position_key, default_vert_position)
        self._set_size()
        self._set_position()

    def track_ref_for_deletion(self, ref):
        """
        Record references of instance variables that need to be removed
        from scope so that the class can be garbage collected
        """
        if ref not in self.__refs_for_deletion:
            self.__refs_for_deletion.append(ref)

    def clean_up(self):
        """
        Remove any instance variables from scope which point to non-glade
        GTK objects so that the class can be garbage collected.
        If the object is a Gramps widget then it should have a clean_up method
        which can be called that removes any other GTK object it contains.
        """
        while len(self.__refs_for_deletion):
            attr = self.__refs_for_deletion.pop()
            obj = getattr(self, attr)
            if hasattr(obj, 'clean_up'):
                obj.clean_up()
            delattr(self, attr)
#-------------------------------------------------------------------------
#
# Helper functions
#
#-------------------------------------------------------------------------
def set_titles(window, title, text, msg=None):
    if title:
        title.set_text('<span weight="bold" size="larger">%s</span>' % text)
        title.set_use_markup(True)
    if msg:
        window.set_title('%s - Gramps' % msg)
    elif text:
        window.set_title('%s - Gramps' % text)
    window.set_icon_from_file(ICON)
