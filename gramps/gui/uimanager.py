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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
A replacement UIManager and ActionGroup.
"""

import copy
import json
import os
import sys
import logging
import xml.etree.ElementTree as ET
from collections.abc import Iterable

import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gio, Gtk

from ..gen.const import GRAMPS_LOCALE as glocale
from ..gen.const import KEYBINDING_THEMES_DIR, VERSION_DIR
from ..gen.config import config

_ = glocale.translation.gettext

LOG = logging.getLogger("gui.uimanager")


ACTION_NAME = 0  # tuple index for action name
ACTION_CB = 1  # tuple index for action callback
ACTION_ACC = 2  # tuple index for action accelerator
ACTION_ST = 3  # tuple index for action state

# Action groups whose actions are generated per open-window instance
# (e.g. the "Windows" switcher list) rather than representing a fixed
# command. Their action ids are not stable across sessions -- or even
# across the lifetime of the window they refer to -- so they are not
# meaningful targets for a customizable keyboard shortcut and must be
# excluded from the shortcut editor's action list.
_DYNAMIC_GROUP_NAMES = frozenset({"WindowManager"})

# Keyvals that must stay unmodified everywhere, because GTK's own focus
# and cursor navigation depends on receiving them within any widget.
_NAV_KEYVALS = frozenset(
    Gdk.keyval_from_name(name)
    for name in ("Tab", "ISO_Left_Tab", "Up", "Down", "Left", "Right")
)

# Keyvals safe to bind with no modifier at all: nothing in Gramps'
# editors or views consumes these for text entry, cursor movement, or
# list navigation.
_SAFE_BARE_KEYVALS = frozenset(
    Gdk.keyval_from_name(name) for name in [f"F{i}" for i in range(1, 13)] + ["Menu"]
)


def check_accel(accel: str) -> str:
    """Return '' if accel is safe for a user to bind, otherwise a
    user-facing reason it is reserved.

    Gtk.CellRendererAccelMode.OTHER (used by the shortcut editor) lets a
    user capture almost any key, including ones GTK itself never blocks
    -- a bare letter, Escape, Return, Delete -- that would collide with
    typing or in-place editing in Gramps' many text-entry fields.
    Gtk.accelerator_valid() alone does not protect against this: it only
    rejects Tab/arrow keys and bare modifier keys.

    :param accel: a Gtk accelerator string, e.g. '<Primary>c' or 'a'
    :type accel: str
    """
    if not accel:
        return ""
    accel = _normalize_accel(accel)
    parseable = accel
    if os.environ.get("GDK_BACKEND") == "-":
        # Without a real display, Gtk.accelerator_parse() can't resolve a
        # virtual modifier like <Primary> to a concrete one and silently
        # drops it instead -- which would make an ordinary "<Primary>c"
        # look like a bare, unmodified "c" below. Substitute a concrete
        # stand-in for this validity check only (the accel returned to
        # the caller is untouched); this only matters for headless test
        # runs, since a live Gramps process always has a real display for
        # Gtk to resolve it with.
        parseable = parseable.replace("<Primary>", "<Control>").replace(
            "<PRIMARY>", "<Control>"
        )
    keyval, mods = Gtk.accelerator_parse(parseable)
    mods &= Gtk.accelerator_get_default_mod_mask()
    if not Gtk.accelerator_valid(keyval, mods):
        return _("Not a valid keyboard shortcut.")
    if mods == 0 and keyval in _NAV_KEYVALS:
        return _("This key is reserved for keyboard navigation.")
    if mods == 0 and keyval not in _SAFE_BARE_KEYVALS:
        return _(
            "This key needs a modifier such as Ctrl, Alt, or Super -- "
            "otherwise it would conflict with typing in text fields."
        )
    return ""


def _normalize_accel(accel: str) -> str:
    """Normalize an accelerator string to Gtk's own canonical spelling
    (e.g. '<PRIMARY>b' and '<Primary>b' both become '<Primary>b'), so
    accels from different sources (hand-written literals, a captured
    keypress) compare equal.

    Without a real display connection, Gtk.accelerator_parse() silently
    drops virtual modifiers like <Primary> instead of raising, which
    would corrupt the value rather than normalize it. Since that only
    happens running headless (as this project's test suite always does,
    per its GDK_BACKEND=- convention), leave the string untouched in that
    case -- there's no live-captured value to reconcile against anyway.

    :param accel: a Gtk accelerator string, or '' for none
    :type accel: str
    """
    if not accel:
        return ""
    if os.environ.get("GDK_BACKEND") == "-":
        return accel
    key, mods = Gtk.accelerator_parse(accel)
    return Gtk.accelerator_name(key, mods) if key else accel


def accel_display_label(accel: str) -> str:
    """Return a human-readable label for a Gtk accelerator string, e.g.
    '<Primary>c' -> 'Ctrl+C', for display in tooltips and the shortcuts
    editor.

    :param accel: a Gtk accelerator string, or '' for none
    :type accel: str
    """
    if not accel:
        return ""
    key, mods = Gtk.accelerator_parse(accel)
    return Gtk.accelerator_get_label(key, mods) if key else accel


def theme_dirs() -> list[str]:
    """Directories to search for keybinding theme files, in precedence
    order -- user-saved themes take precedence over bundled ones with
    the same name."""
    return [os.path.join(VERSION_DIR, "keybinding_themes"), KEYBINDING_THEMES_DIR]


def theme_path(name: str) -> str | None:
    """Resolve a theme name to a file, preferring a user theme over a
    bundled one with the same name."""
    for theme_dir in theme_dirs():
        path = os.path.join(theme_dir, f"{name}.jsonl")
        if os.path.exists(path):
            return path
    return None


class ActionGroup:
    """This class represents a group of actions that con be manipulated
    together.
    """

    def __init__(self, name, actionlist=None, prefix="win"):
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
        self.prefix = prefix + "."
        self.act_group = None
        self.sensitive = True

    def add_actions(self, actionlist):
        """Add a list of actions to the current list
        @type actionlist: list
        @param actionlist: the list of actions to add
        """
        self.actionlist.extend(actionlist)


class UIManager:
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
        self.default_accels = {}  # hard-coded accel for each action_id
        self.static_registry = {}  # label/category for statically-known actions

    def update_menu(self, init=False):
        """This updates the menus and toolbar when there is a change in the
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
            """This recursively goes through the ET xml and deals with the
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
                if (len(child) == 1 and child.tag == "submenu") or (
                    len(child) == 0 and child.tag == "section"
                ):
                    # remove empty submenus and sections
                    LOG.debug(("del", child.tag, child.attrib))
                    del parents[indx]
                    continue
                LOG.debug((child.attrib))
                groups = child.get("groups")
                if not groups:
                    indx += 1
                    continue
                del child.attrib["groups"]
                for group in groups.split(" "):
                    if group in self.show_groups:
                        indx += 1
                        break
                    else:
                        LOG.debug(
                            (
                                "del",
                                child.tag,
                                child.attrib,
                                parents.tag,
                                parents.attrib,
                            )
                        )
                        del parents[indx]
                        break
            # The following looks for 'placeholder' elements and if found,
            # promotes any children to the same level as the placeholder.
            # this allows the user to insert elements without using a section.
            indx = 0
            while indx < len(parents):
                if parents[indx].tag == "placeholder":
                    subtree = parents[indx]
                    LOG.debug(
                        (
                            "placholder del",
                            parents[indx].tag,
                            parents[indx].attrib,
                            parents.tag,
                            parents.attrib,
                        )
                    )
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
        del iterator  # Needed for garbage collection
        # The following should work, but seems to have a Gtk bug
        # xml_str = ET.tostring(editable, encoding="unicode")

        xml_str = ET.tostring(editable).decode(encoding="ascii")

        # debugging
        # with open('try.xml', 'w', encoding='utf8') as file:
        #     file.write(xml_str)
        # with open('try.xml', encoding='utf8') as file:
        #     xml_str = file.read()
        # LOG.info(xml_str)
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
        section = self.builder.get_object("menubar-update")
        self.app.menubar.append_section(None, section)

        # the following updates the toolbar from the new builder
        toolbar_parent = toolbar.get_parent()
        tb_show = toolbar.get_visible()
        toolbar_parent.remove(toolbar)
        toolbar = self.builder.get_object("ToolBar")  # new toolbar
        toolbar_style = config.get("interface.toolbar-style")
        if toolbar_style == 0:
            toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        elif toolbar_style == 1:
            toolbar.set_style(Gtk.ToolbarStyle.TEXT)
        else:
            toolbar.set_style(Gtk.ToolbarStyle.ICONS)
        toolbar_parent.pack_start(toolbar, False, True, 0)
        if tb_show:
            toolbar.show_all()
        else:
            toolbar.hide()
        LOG.info("*** Update ui")

    def add_ui_from_string(self, changexml):
        """This performs a merge operation on the xml elements that have
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
                el_id = update.attrib["id"]
                # find the parent of the id'd element in original xml
                parent = self.et_xml.find(".//*[@id='%s'].." % el_id)
                if parent is not None:
                    # we found it, now delete original, inset updated
                    for indx in range(len(parent)):
                        if parent[indx].get("id") == el_id:
                            del parent[indx]
                            parent.insert(indx, update)
                else:
                    # updated item not present in original, just add it
                    # This allow addition of popups etc.
                    self.et_xml.append(update)
            # results = ET.tostring(self.et_xml, encoding="unicode")
            # LOG.info(results)
            LOG.info("*** Add ui")
            return changexml
        except:
            # the following is only here to assist debug
            LOG.debug("*****", sys.exc_info())
            LOG.debug(xml)
            LOG.debug(changexml)
            assert False

    def remove_ui(self, change_xml):
        """This removes the 'change_xml' from the current ui xml.  It works on
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
            el_id = update.attrib["id"]
            # find parent of id'd element
            element = self.et_xml.find(".//*[@id='%s']" % el_id)
            if element is not None:  # element may have already been deleted
                for dummy in range(len(element)):
                    del element[0]
        # results = ET.tostring(self.et_xml, encoding="unicode")
        # LOG.info(results)
        LOG.info("*** Remove ui")
        return

    def get_widget(self, obj):
        """Get the object from the builder.
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
                    LOG.warning("**Invalid action name %s", item[ACTION_NAME])
                action_id = group.prefix + item[ACTION_NAME]
                # record the hard-coded accelerator as the default, so a
                # user override can later be reset back to it
                if len(item) > 2 and item[ACTION_ACC]:
                    self.default_accels[action_id] = _normalize_accel(item[ACTION_ACC])
                # deal with accelerator overrides from a file
                accel = self.accel_dict.get(group.prefix + item[ACTION_NAME])
                if accel:
                    self.app.set_accels_for_action(
                        group.prefix + item[ACTION_NAME], [accel]
                    )
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
                                LOG.warning(
                                    "**Duplicate Accelerator %s", item[ACTION_ACC]
                                )
                    self.app.set_accels_for_action(
                        group.prefix + item[ACTION_NAME], [item[ACTION_ACC]]
                    )
                if len(item) <= 3:
                    # Normal stateless actions
                    action = Gio.SimpleAction.new(item[ACTION_NAME], None)
                    if item[ACTION_CB]:  # in case we have only accelerator
                        action.connect("activate", item[ACTION_CB])
                elif isinstance(item[ACTION_ST], str):
                    # Radio Actions
                    action = Gio.SimpleAction.new_stateful(
                        item[ACTION_NAME],
                        GLib.VariantType.new("s"),
                        GLib.Variant("s", item[ACTION_ST]),
                    )
                    action.connect("change-state", item[ACTION_CB])
                elif isinstance(item[ACTION_ST], bool):
                    # Checkbox actions
                    action = Gio.SimpleAction.new_stateful(
                        item[ACTION_NAME],
                        None,
                        GLib.Variant.new_boolean(item[ACTION_ST]),
                    )
                    action.connect("change-state", item[ACTION_CB])
                window_group.add_action(action)
            self.action_groups.append(group)
            # if action sensitivity was set prior to actually inserting into
            # UIManager, we need to do it now that we have the action
            if not group.sensitive:
                self.set_actions_sensitive(group, False)
        except:
            # the following is only to assist in debug
            LOG.debug(group.name, item)
            assert False

    def remove_action_group(self, group):
        """This removes the ActionGroup from the UIManager

        @param group: the action group
        @type group: ActionGroup
        """
        if group.act_group:
            window_group = group.act_group
        else:
            window_group = self.app.window
        for item in group.actionlist:
            window_group.remove_action(item[ACTION_NAME])
            self.app.set_accels_for_action(group.prefix + item[ACTION_NAME], [])
        self.action_groups.remove(group)

    def get_action_groups(self):
        """This returns a list of action Groups installed into the UIManager.
        @return: list of groups
        """
        return self.action_groups

    def set_actions_sensitive(self, group, value):
        """This sets an ActionGroup enabled or disabled.  A disabled action
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
        """This gets an ActionGroup sensitive setting.  A disabled action
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
        """This sets an ActionGroup visible and enabled or invisible and
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
        """Return a single action from the group.
        @param group: the action group
        @type group: ActionGroup
        @param actionname: the action name
        @type actionname: string
        @return: Gio.Action
        """
        return group.act_group.lookup_action(actionname)

    def enable_all_actions(self, state):
        for group in self.action_groups:
            if group.act_group:
                for item in group.actionlist:
                    action = group.act_group.lookup_action(item[ACTION_NAME])
                    if action:
                        # We check in case the group has not been inserted into
                        # UIManager yet
                        action.set_enabled(group.sensitive if state else False)

    def load_accels(self, filename: str, merge: bool = False) -> None:
        """Load accels from a JSON Lines file such as one written by
        save_accels: one JSON object per line, of the form
        ``{"id": action_id, "label": ..., "category": ..., "accel": ...}``.
        "label" and "category" are metadata for a human reader (so the
        file is self-documenting when opened directly in a text editor)
        and are ignored on load. Blank lines and lines starting with '#'
        are skipped, so an exported file can be hand-trimmed or annotated.

        A malformed *line* is logged and skipped rather than aborting the
        whole load: this file is meant to be safely hand-editable, and one
        typo should not cost every other binding in it. A caller that
        wants the whole load to be best-effort (e.g. at startup, where a
        bad keybinding file must never prevent Gramps from launching)
        should additionally catch OSError around the call; a caller that
        wants to report a genuinely unreadable file to the user (e.g. the
        shortcuts editor's theme switcher) can let it propagate.

        If used before any insert_action_group calls, this overrides the
        accels defined in other Gramps code.  If used afterwards (e.g. an
        "Import" of a user keymap while Gramps is running), the loaded
        accels are also applied immediately to any matching, already
        registered actions.

        :param filename: path of the accel file to load
        :type filename: str
        :param merge: when True, update the existing overrides instead of
            replacing them, so a system-level file and a user-level file
            can be layered
        :type merge: bool
        :raises OSError: if filename can't be opened
        """
        loaded: dict[str, str] = {}
        with open(filename, "r", encoding="utf-8") as hndl:
            lines = hndl.readlines()

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                entry = json.loads(line)
                action_id = entry["id"]
                if not isinstance(action_id, str):
                    raise TypeError(f"'id' must be a string, got {action_id!r}")
                accel = _normalize_accel(entry.get("accel", ""))
            except (json.JSONDecodeError, KeyError, TypeError) as err:
                LOG.warning(
                    "load_accels: skipping malformed line %d in %s: %s",
                    line_number,
                    filename,
                    err,
                )
                continue
            reason = check_accel(accel)
            if reason:
                LOG.warning(
                    "load_accels: skipping %r for %s in %s: %s",
                    accel,
                    action_id,
                    filename,
                    reason,
                )
                continue
            loaded[action_id] = accel

        if merge:
            self.accel_dict.update(loaded)
        else:
            self.accel_dict = loaded
        for action_id, accel in loaded.items():
            self.app.set_accels_for_action(action_id, [accel] if accel else [])

    def register_static_shortcuts(
        self, specs: list[tuple[str, str, str]], category: str, prefix: str = "win"
    ) -> None:
        """Register a fixed list of actions a view or widget type always
        defines, independent of whether any live instance of it currently
        exists. This lets the customizable keyboard shortcuts editor list
        every such action -- with its label, category and default -- even
        before a matching view has been visited in this session.

        :param specs: (action_name, default_accel, label) triples
        :type specs: list[tuple[str, str, str]]
        :param category: display category shown in the shortcuts editor
        :type category: str
        :param prefix: the action prefix, e.g. 'win' or 'ste'
        :type prefix: str
        """
        for name, accel, label in specs:
            action_id = f"{prefix}.{name}"
            if accel:
                self.default_accels[action_id] = _normalize_accel(accel)
            self.static_registry[action_id] = {"label": label, "group_name": category}

    def _all_known_action_ids(self) -> set[str]:
        """Return every action_id known from static registration, a saved
        override, a recorded default, or a currently live action group."""
        ids = (
            set(self.static_registry) | set(self.default_accels) | set(self.accel_dict)
        )
        for group in self.action_groups:
            for item in group.actionlist:
                ids.add(group.prefix + item[ACTION_NAME])
        return ids

    def _live_action_ids(self) -> set[str]:
        """Return action ids backed by an actual live Gio.SimpleAction."""
        return {
            group.prefix + item[ACTION_NAME]
            for group in self.action_groups
            for item in group.actionlist
        }

    def get_action_label(self, action_id: str) -> str:
        """Return a human-readable label for an action: from the static
        registry if known, otherwise from its menu entry if it has one,
        otherwise the raw action name.

        :param action_id: the fully prefixed action id, e.g. 'win.Clipboard'
        :type action_id: str
        :rtype: str
        """
        static = self.static_registry.get(action_id)
        if static:
            return static["label"].replace("_", "", 1)
        for item in self.et_xml.iter("item"):
            attrs = {
                attr.get("name"): (attr.text or "")
                for attr in item.findall("attribute")
            }
            if attrs.get("action") == action_id:
                label = attrs.get("label")
                if label:
                    return label.replace("_", "", 1)
        return action_id.split(".", 1)[-1]

    def menu_action_ids(self) -> set[str]:
        """Return the action ids that appear as a clickable entry
        somewhere in the current menu XML (main menu bar or a popup
        context menu), as opposed to being reachable only via a toolbar
        button or a bare keyboard shortcut.

        :rtype: set[str]
        """
        return {
            attr.text
            for item in self.et_xml.iter()
            if item.tag in ("item", "submenu")
            for attr in item.findall("attribute")
            if attr.get("name") == "action" and attr.text
        }

    def get_accel(self, action_id: str) -> str:
        """Return the current accelerator string for action_id, or ''.

        This is the saved override if there is one, otherwise the known
        default -- computed independent of whether action_id's action
        group is currently live, so it stays correct for actions
        belonging to a view or widget not yet instantiated this session.

        :param action_id: the fully prefixed action id
        :type action_id: str
        """
        return self.accel_dict.get(action_id, self.default_accels.get(action_id, ""))

    def list_actions(self) -> list[dict[str, str]]:
        """Return metadata for every known action -- statically registered
        or currently live -- for use by a keyboard-shortcut editor.

        :returns: one dict per action with keys 'action_id', 'label',
            'group_name', 'current_accel', 'default_accel'
        :rtype: list[dict]
        """
        actions = {}
        for action_id, meta in self.static_registry.items():
            actions[action_id] = {
                "action_id": action_id,
                "label": meta["label"].replace("_", "", 1),
                "group_name": meta["group_name"],
                "current_accel": self.get_accel(action_id),
                "default_accel": self.default_accels.get(action_id, ""),
            }
        for group in self.action_groups:
            if group.name in _DYNAMIC_GROUP_NAMES:
                continue
            for item in group.actionlist:
                action_id = group.prefix + item[ACTION_NAME]
                if action_id in actions:
                    continue
                actions[action_id] = {
                    "action_id": action_id,
                    "label": self.get_action_label(action_id),
                    "group_name": group.name,
                    "current_accel": self.get_accel(action_id),
                    "default_accel": self.default_accels.get(action_id, ""),
                }
        return list(actions.values())

    def check_accel(self, accel: str) -> str:
        """Return '' if accel is safe for a user to bind, otherwise a
        user-facing reason it is reserved. See the module-level
        :py:func:`check_accel` for details.

        :param accel: a Gtk accelerator string, e.g. '<Primary>c' or 'a'
        :type accel: str
        """
        return check_accel(accel)

    def set_accel(self, action_id: str, accel: str) -> list[str]:
        """Bind action_id to a new accelerator, recording the override.

        :param action_id: the fully prefixed action id
        :type action_id: str
        :param accel: the new Gtk accelerator string, e.g. '<Primary>c'
        :type accel: str
        :returns: any other action ids that were already bound to accel
        :rtype: list[str]
        """
        accel = _normalize_accel(accel)
        candidates: Iterable[str] = self._all_known_action_ids()
        if action_id.startswith("glade."):
            # Editor-dialog-local shortcuts only conflict with others in
            # the same dialog: each .glade file gets its own implicit
            # Gtk.AccelGroup, scoped to that dialog's own window, so the
            # same key in an unrelated dialog is never actually ambiguous.
            scope = action_id.rsplit(".", 1)[0] + "."
            candidates = [c for c in candidates if c.startswith(scope)]
        elif action_id.startswith("app.") and action_id not in self._live_action_ids():
            # Static-only "app." entries such as "dialog-ok"/"dialog-cancel"
            # have no live Gio.SimpleAction of their own: they are dispatched
            # by a per-dialog Gtk.AccelGroup (see ManagedWindow.set_window)
            # that only fires while that dialog holds keyboard focus. A
            # background view's "win." actions can never receive that same
            # keypress while a dialog is focused, so they can't really
            # conflict -- only a genuinely global "app." action (dispatched
            # regardless of window focus) or another dialog's own "glade."
            # shortcut (live in the same focused window) can.
            candidates = [
                c for c in candidates if c.startswith("app.") or c.startswith("glade.")
            ]
        conflicts = [
            other
            for other in candidates
            if other != action_id and self.get_accel(other) == accel
        ]
        self.app.set_accels_for_action(action_id, [accel])
        self.accel_dict[action_id] = accel
        return conflicts

    def clear_accel(self, action_id: str) -> None:
        """Remove any accelerator from action_id.

        :param action_id: the fully prefixed action id
        :type action_id: str
        """
        self.app.set_accels_for_action(action_id, [])
        self.accel_dict[action_id] = ""

    def reset_accel(self, action_id: str) -> None:
        """Restore action_id to its hard-coded default accelerator.

        :param action_id: the fully prefixed action id
        :type action_id: str
        """
        default = self.default_accels.get(action_id, "")
        self.app.set_accels_for_action(action_id, [default] if default else [])
        self.accel_dict.pop(action_id, None)

    def save_accels(self, filename: str, only_changed: bool = True) -> None:
        """Write the current accelerator set to filename, in the same JSON
        Lines format read by load_accels: one ``{"id", "label",
        "category", "accel"}`` object per line. "label" and "category" are
        included purely so the file is self-documenting to a human reader;
        load_accels ignores them.

        :param filename: path to write to
        :type filename: str
        :param only_changed: when True, only write accels that differ from
            their hard-coded default (a compact, forward-compatible
            personal override file); when False, write every currently
            known accel (a self-contained file suitable for export/sharing)
        :type only_changed: bool
        """
        if only_changed:
            action_ids = [
                action_id
                for action_id, accel in self.accel_dict.items()
                if accel != self.default_accels.get(action_id, "")
            ]
        else:
            action_ids = sorted(self._all_known_action_ids())
        meta_by_id = {action["action_id"]: action for action in self.list_actions()}
        with open(filename, "w", encoding="utf-8") as hndl:
            for action_id in action_ids:
                meta = meta_by_id.get(action_id, {})
                hndl.write(
                    json.dumps(
                        {
                            "id": action_id,
                            "label": meta.get("label", ""),
                            "category": meta.get("group_name", ""),
                            "accel": self.get_accel(action_id),
                        }
                    )
                    + "\n"
                )


INVALID_CHARS = [" ", "_", "(", ")", ",", "'"]


def valid_action_name(text):
    """This function cleans up action names to avoid some illegal
    characters.  It does NOT clean up non-ASCII characters.
    This is used for plugin IDs to clean them up.  It would be better if we
    made all plugin ids:
    ASCII Alphanumeric and the '.' or '-' characters."""
    for char in INVALID_CHARS:
        text = text.replace(char, "-")
    return text
