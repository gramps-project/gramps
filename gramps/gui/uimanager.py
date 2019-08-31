#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2018      Paul Culley
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
A replacement UIManager and ActionGroup.
"""

import copy
import sys
import logging
import xml.etree.ElementTree as ET

from gi.repository import GLib, Gio, Gtk

from ..gen.const import GRAMPS_LOCALE as glocale
from ..gen.config import config


LOG = logging.getLogger('gui.uimanager')


ACTION_NAME = 0  # tuple index for action name
ACTION_CB = 1    # tuple index for action callback
ACTION_ACC = 2   # tuple index for action accelerator
ACTION_ST = 3    # tuple index for action state


class ActionGroup():
    """ This class represents a group of actions that con be manipulated
    together.
    """
    def __init__(self, name, actionlist=None, prefix='win'):
        """
        @param name: the action group name, used to match to the 'groups'
                     attribute in the ui xml.
        @type name: string
        @type actionlist: list
        @param actionlist: the list of actions to add
            The list contains tuples with the following contents:
            string: Action Name
            method: signal callback function.
                    None if just adding an accelerator
            string: accelerator ex: '<Primary>Enter' or '' for no accelerator.
                    optional for non-stateful actions.
            state: initial state for stateful actions.
                'True' or 'False': the action is interpreted as a checkbox.
                'None': non stateful action (optional)
                'string': the action is interpreted as a Radio button
        @type prefix: str
        @param prefix: the prefix used by this group.  If not provided, 'win'
                       is assumed.
        """
        self.name = name
        self.actionlist = actionlist if actionlist else []
        self.prefix = prefix + '.'
        self.act_group = None
        self.sensitive = True

    def add_actions(self, actionlist):
        """  Add a list of actions to the current list
        @type actionlist: list
        @param actionlist: the list of actions to add
        """
        self.actionlist.extend(actionlist)


class UIManager():
    """
    This is Gramps UIManager, it is designed to replace the deprecated Gtk
    UIManager.  The replacement is not exact, but performs similar
    functions, in some case with the same method names and parameters.
    It is designed to be a singleton.  The menu portion of this is responsible
    only for Gramps main window menus and toolbar.
    This was implemented to extend Gtk.Builder functions to allow editing
    (merging) of the original builder XML with additional XML fragments during
    operations.  This allows changing of the menus and toolbar when the tree is
    loaded, views are changed etc.

    The ActionGroup portions can also be used by other windows.  Other windows
    needing menus or toolbars can create them via Gtk.Builder.
    """

    def __init__(self, app, initial_xml):
        """
        @param app: Gramps Gtk.Application reference
        @type app: Gtk.Application
        @param initial_xml: Initial (primary) XML string for Gramps menus and
            toolbar
        @type changexml: string

        The xml is basically Gtk Builder xml, in particular the various menu
        and toolbar elements.  It is possible to add other elements as well.
        The xml this supports has been extended in two ways;
        1) there is an added "groups=" attribute to elements.  This
           attribute associates the element with one or more named ActionGroups
           for making the element visible or not.  If 'groups' is missing, the
           element will be shown as long as enclosing elements are shown.  The
           element will be shown if the group is present and considered visible
           by the uimanager.  If more than one group is needed, they should be
           separated by a space.
        2) there is an added <placeholder> tag supported; this is used to mark
           a place where merged UI XML can be inserted.  During the update_menu
           processing, elements enclosed in this tag pair are promoted to the
           level of the placeholder tag, and the placeholder tag is removed.

        Note that any elements can be merged (replaced) by the
        add_ui_from_string method, not just placeholders.  This works by
        matching the "id=" attribute on the element, and replacing the
        original element with the one from the add method.

        Note that when added elements are removed by the remove_ui method, they
        are replaced by the containing xml (with the 'id=') only, so don't put
        anything inside of the containing xml to start with as it will be lost
        during editing.
        """
        self.app = app  # the Gtk.Application of Gramps
        self.et_xml = ET.fromstring(initial_xml)
        self.builder = None
        self.toolbar = None
        self.action_groups = []  # current list of action groups
        self.show_groups = []  # groups to show at the moment
        self.accel_dict = {}  # used to store accel overrides from file

    def update_menu(self, init=False):
        """ This updates the menus and toolbar when there is a change in the
        ui; any addition or removal or set_visible operation needs to call
        this.  It is best to make the call only once, at the end, if multiple
        changes are to be made.
        It starts with the ET xml stored in self, cleans it up to meet the
        Gtk.Builder specifications, and then updates the ui.

        @param init: When True, this is first call and we set the builder
                     toolbar and menu to the application.
                     When False, we update the menus and toolbar
        @type init: bool
        """

        def iterator(parents):
            """ This recursively goes through the ET xml and deals with the
            'groups' attribute and <placeholder> tags, which are not valid for
            builder.  Empty submenus are also removed.
            Groups processing removes elements that are not shown, as well as
            the 'groups' attribute itself.
            <placeholder> tags are removed and their enclosed elements are
            promoted to the level of the placeholder.

            @param parents: the current element to recursively process
            @type parents: ET element
            """
            indx = 0
            while indx < len(parents):
                child = parents[indx]
                if len(child) >= 1:
                    # Recurse until we have a stand-alone child
                    iterator(child)
                if((len(child) == 1 and child.tag == "submenu") or
                   (len(child) == 0 and child.tag == "section")):
                    # remove empty submenus and sections
                    # print('del', child.tag, child.attrib)
                    del parents[indx]
                    continue
                # print(child.attrib)
                groups = child.get('groups')
                if not groups:
                    indx += 1
                    continue
                del child.attrib['groups']
                for group in groups.split(' '):
                    if group in self.show_groups:
                        indx += 1
                        break
                    else:
                        #print('del', child.tag, child.attrib, parents.tag,
                        #      parents.attrib)
                        del parents[indx]
                        break
            # The following looks for 'placeholder' elements and if found,
            # promotes any children to the same level as the placeholder.
            # this allows the user to insert elements without using a section.
            indx = 0
            while indx < len(parents):
                if parents[indx].tag == "placeholder":
                    subtree = parents[indx]
                    #print('placholder del', parents[indx].tag,
                    #      parents[indx].attrib, parents.tag, parents.attrib)
                    del parents[indx]
                    for child in subtree:
                        parents.insert(indx, child)
                        indx += 1
                else:
                    indx += 1

        if self.builder:
            toolbar = self.builder.get_object("ToolBar")  # previous toolbar

        # need to copy the tree so we can preserve original for later edits.
        editable = copy.deepcopy(self.et_xml)
        iterator(editable)  # clean up tree to builder specifications
        # The following should work, but seems to have a Gtk bug
        # xml_str = ET.tostring(editable, encoding="unicode")

        xml_str = ET.tostring(editable).decode(encoding='ascii')

        # debugging
        # with open('try.xml', 'w', encoding='utf8') as file:
        #     file.write(xml_str)
        # with open('try.xml', encoding='utf8') as file:
        #     xml_str = file.read()
        # print(xml_str)
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(glocale.get_localedomain())
        self.builder.add_from_string(xml_str)
        if init:
            self.app.menubar = self.builder.get_object("menubar")
            self.app.set_menubar(self.app.menubar)
            return
        # The following is the only way I have found to update the menus.
        # app.set_menubar can apparently only be used once, before
        # ApplicationWindow creation, further uses do NOT cause the menus to
        # update.
        self.app.menubar.remove_all()
        section = self.builder.get_object('menubar-update')
        self.app.menubar.append_section(None, section)

        # the following updates the toolbar from the new builder
        toolbar_parent = toolbar.get_parent()
        tb_show = toolbar.get_visible()
        toolbar_parent.remove(toolbar)
        toolbar = self.builder.get_object("ToolBar")  # new toolbar
        if config.get('interface.toolbar-text'):
            toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        toolbar_parent.pack_start(toolbar, False, True, 0)
        if tb_show:
            toolbar.show_all()
        else:
            toolbar.hide()
        #print('*** Update ui')

    def add_ui_from_string(self, changexml):
        """ This performs a merge operation on the xml elements that have
        matching 'id's between the current ui xml and change xml strings.
        The 'changexml' is a list of xml fragment strings used to replace
        matching elements in the current xml.

        There MUST one and only one matching id in the orig xml.
        @param changexml: list of xml fragments to merge into main
        @type changexml: list
        @return: changexml
        """
        try:
            for xml in changexml:
                if not xml:
                    # allow an xml fragment to be an empty string
                    continue
                update = ET.fromstring(xml)
                el_id = update.attrib['id']
                # find the parent of the id'd element in original xml
                parent = self.et_xml.find(".//*[@id='%s'].." % el_id)
                if parent:
                    # we found it, now delete original, inset updated
                    for indx in range(len(parent)):
                        if parent[indx].get('id') == el_id:
                            del parent[indx]
                            parent.insert(indx, update)
                else:
                    # updated item not present in original, just add it
                    # This allow addition of popups etc.
                    self.et_xml.append(update)
            #results = ET.tostring(self.et_xml, encoding="unicode")
            #print(results)
            #print ('*** Add ui')
            return changexml
        except:
            # the following is only here to assist debug
            print('*****', sys.exc_info())
            print(xml)
            print(changexml)
            assert False

    def remove_ui(self, change_xml):
        """ This removes the 'change_xml' from the current ui xml.  It works on
        any element with matching 'id', the actual element remains but any
        children are removed.
        The 'change_xml' is a list of xml strings originally used to replace
        matching elements in the current ui xml.
        @param change_xml: list of xml fragments to remove from main
        @type change_xml: list
        """
#         if not change_xml:
#             import pydevd
#             pydevd.settrace()
        for xml in change_xml:
            if not xml:
                continue
            update = ET.fromstring(xml)
            el_id = update.attrib['id']
            # find parent of id'd element
            element = self.et_xml.find(".//*[@id='%s']" % el_id)
            if element:  # element may have already been deleted
                for dummy in range(len(element)):
                    del element[0]
        #results = ET.tostring(self.et_xml, encoding="unicode")
        #print(results)
        #print ('*** Remove ui')
        return

    def get_widget(self, obj):
        """ Get the object from the builder.
        @param obj: the widget to get
        @type obj: string
        @return: the object
        """
        return self.builder.get_object(obj)

    def insert_action_group(self, group, gio_group=None):
        """
        This inserts (actually overwrites any matching actions) the action
        group's actions to the app.
        By default (with no gio_group), the action group is added to the main
        Gramps window and the group assumes a 'win' prefix.
        If not using the main window, the window MUST have the 'application'
        property set for the accels to work.  In this case the actiongroups
        must be created like the following:

            # create Gramps ActionGroup
            self.action_group = ActionGroup('name', actions, 'prefix')
            # create Gio action group
            act_grp = SimpleActionGroup()
            # associate window with Gio group and its prefix
            window.insert_action_group('prefix', act_grp)
            # make the window 'application' aware
            window.set_application(uimanager.app)
            # tell the uimanager about the groups.
            uimanager.insert_action_group(self.action_group, act_grp)

        @param group: the action group
        @type group: ActionGroup
        @param gio_group: the Gio action group associated with a window.
        @type gio_group: Gio.SimpleActionGroup
        """
        try:
            assert isinstance(group.actionlist, list)
            if gio_group:
                window_group = group.act_group = gio_group
            elif group.act_group:
                window_group = group.act_group
            else:
                window_group = group.act_group = self.app.window
            for item in group.actionlist:
                if not Gio.action_name_is_valid(item[ACTION_NAME]):
                    LOG.warning('**Invalid action name %s', item[ACTION_NAME])
                # deal with accelerator overrides from a file
                accel = self.accel_dict.get(group.prefix + item[ACTION_NAME])
                if accel:
                    self.app.set_accels_for_action(
                        group.prefix + item[ACTION_NAME], [accel])
                elif len(item) > 2 and item[ACTION_ACC]:
                    # deal with accelerators defined in the group
                    accels = self.app.get_actions_for_accel(item[ACTION_ACC])
                    if accels:
                        # diagnostic printout; a duplicate accelerator may be
                        # a problem if both are valid for the same window at
                        # the same time.  If the actions are for a different
                        # window, this is not an error.  Here we assume a
                        # different prefix is used for different windows.
                        for accel in accels:
                            if group.prefix in accel:
                                LOG.warning('**Duplicate Accelerator %s',
                                            item[ACTION_ACC])
                    self.app.set_accels_for_action(
                        group.prefix + item[ACTION_NAME], [item[ACTION_ACC]])
                if len(item) <= 3:
                    # Normal stateless actions
                    action = Gio.SimpleAction.new(item[ACTION_NAME], None)
                    if item[ACTION_CB]:  # in case we have only accelerator
                        action.connect("activate", item[ACTION_CB])
                elif isinstance(item[ACTION_ST], str):
                    # Radio Actions
                    action = Gio.SimpleAction.new_stateful(
                        item[ACTION_NAME], GLib.VariantType.new("s"),
                        GLib.Variant("s", item[ACTION_ST]))
                    action.connect("change-state", item[ACTION_CB])
                elif isinstance(item[ACTION_ST], bool):
                    # Checkbox actions
                    action = Gio.SimpleAction.new_stateful(
                        item[ACTION_NAME], None,
                        GLib.Variant.new_boolean(item[ACTION_ST]))
                    action.connect("change-state", item[ACTION_CB])
                window_group.add_action(action)
            self.action_groups.append(group)
            # if action sensitivity was set prior to actually inserting into
            # UIManager, we need to do it now that we have the action
            if not group.sensitive:
                self.set_actions_sensitive(group, False)
        except:
            # the following is only to assist in debug
            print(group.name, item)
            assert False

    def remove_action_group(self, group):
        """ This removes the ActionGroup from the UIManager

        @param group: the action group
        @type group: ActionGroup
        """
        if group.act_group:
            window_group = group.act_group
        else:
            window_group = self.app.window
        for item in group.actionlist:
            window_group.remove_action(item[ACTION_NAME])
            self.app.set_accels_for_action(group.prefix + item[ACTION_NAME],
                                           [])
        self.action_groups.remove(group)

    def get_action_groups(self):
        """ This returns a list of action Groups installed into the UIManager.
        @return: list of groups
        """
        return self.action_groups

    def set_actions_sensitive(self, group, value):
        """ This sets an ActionGroup enabled or disabled.  A disabled action
        will be greyed out in the UI.

        @param group: the action group
        @type group: ActionGroup
        @param value: the state of the group
        @type value: bool
        """
        if group.act_group:
            for item in group.actionlist:
                action = group.act_group.lookup_action(item[ACTION_NAME])
                if action:
                    # We check in case the group has not been inserted into
                    # UIManager yet
                    action.set_enabled(value)
        group.sensitive = value

    def get_actions_sensitive(self, group):
        """ This gets an ActionGroup sensitive setting.  A disabled action
        will be greyed out in the UI.
        We assume that the first action represents the group.

        @param group: the action group
        @type group: ActionGroup
        @return: the state of the group
        """
        item = group.actionlist[0]
        action = group.act_group.lookup_action(item[ACTION_NAME])
        return action.get_enabled()

    def set_actions_visible(self, group, value):
        """ This sets an ActionGroup visible and enabled or invisible and
        disabled.  Make sure that the menuitems or sections and toolbar items
        have the 'groups=' xml attribute matching the group name for this to
        work correctly.

        @param group: the action group
        @type group: ActionGroup
        @param value: the state of the group
        @type value: bool
        """
        self.set_actions_sensitive(group, value)
        if value:
            if group.name not in self.show_groups:
                self.show_groups.append(group.name)
        else:
            if group.name in self.show_groups:
                self.show_groups.remove(group.name)

    def get_action(self, group, actionname):
        """ Return a single action from the group.
        @param group: the action group
        @type group: ActionGroup
        @param actionname: the action name
        @type actionname: string
        @return: Gio.Action
        """
        return group.act_group.lookup_action(actionname)

    def dump_all_accels(self):
        ''' A function used diagnostically to see what accels are present.
        This will only dump the current accel set, if other non-open windows
        or views have accels, you will need to open them and run this again
        and manually merge the result files.  The results are in a
        'gramps.accel' file located in the current working directory.'''
        out_dict = {}
        for group in self.action_groups:
            for item in group.actionlist:
                act = group.prefix + item[ACTION_NAME]
                accels = self.app.get_accels_for_action(
                    group.prefix + item[ACTION_NAME])
                out_dict[act] = accels[0] if accels else ''
        import json
        with open('gramps.accel', 'w', ) as hndl:
            accels = json.dumps(out_dict, indent=0).replace('\n"', '\n# "')
            hndl.write(accels)

    def load_accels(self, filename):
        """ This function loads accels from a file such as created by
        dump_all_accels.  The file contents is basically a Python dict
        definition.  As such it contains a line for each dict element.
        These elements can be commented out with '#' at the beginning of the
        line.

        If used, this file overrides the accels defined in other Gramps code.
        As such it must be loaded before any insert_action_group calls.
        """
        import ast
        with open(filename, 'r') as hndl:
            accels = hndl.read()
            self.accel_dict = ast.literal_eval(accels)


INVALID_CHARS = [' ', '_', '(', ')', ',', "'"]


def valid_action_name(text):
    """ This function cleans up action names to avoid some illegal
    characters.  It does NOT clean up non-ASCII characters.
    This is used for plugin IDs to clean them up.  It would be better if we
    made all plugin ids:
    ASCII Alphanumeric and the '.' or '-' characters."""
    for char in INVALID_CHARS:
        text = text.replace(char, '-')
    return text
