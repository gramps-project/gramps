#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
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


"Text editor subclassed from Gtk.TextView handling :class:`.StyledText`."

__all__ = ["StyledTextEditor"]

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

import logging
_LOG = logging.getLogger(".widgets.styledtexteditor")

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository.Gio import SimpleActionGroup
from gi.repository.GLib import Variant

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import StyledTextTagType
from .styledtextbuffer import (ALLOWED_STYLES,
                                          MATCH_START, MATCH_END,
                                          MATCH_FLAVOR, MATCH_STRING,
                                          LinkTag)
from .undoablestyledbuffer import UndoableStyledBuffer
from ..spell import Spell
from ..display import display_url
from ..utils import SystemFonts, match_primary_mask, get_link_color
from gramps.gen.config import config
from gramps.gen.constfunc import has_display, mac
from ..uimanager import ActionGroup

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
if has_display():
    display = Gdk.Display.get_default()
    HAND_CURSOR = Gdk.Cursor.new_for_display(display, Gdk.CursorType.HAND2)
    REGULAR_CURSOR = Gdk.Cursor.new_for_display(display, Gdk.CursorType.XTERM)

FORMAT_TOOLBAR = (
    '''<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkToolbar" id="ToolBar">
    <property name="hexpand">True</property>
    <property name="toolbar-style">GTK_TOOLBAR_ICONS</property>
    <style>
      <class name="primary-toolbar"/>
    </style>
    <child>
      <object class="GtkToggleToolButton">
        <property name="icon-name">format-text-italic</property>
        <property name="action-name">ste.ITALIC</property>
        <property name="tooltip_text" translatable="yes">Italic</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkToggleToolButton">
        <property name="icon-name">format-text-bold</property>
        <property name="action-name">ste.BOLD</property>
        <property name="tooltip_text" translatable="yes">Bold</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkToggleToolButton">
        <property name="icon-name">format-text-underline</property>
        <property name="action-name">ste.UNDERLINE</property>
        <property name="tooltip_text" translatable="yes">Underline</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkToolItem">
        <property name="tooltip_text" translatable="yes">Font family</property>
        <child>
          <object class="ShortlistComboEntry" id="Fontface"></object>
        </child>
      </object>
    </child>
    <child>
      <object class="GtkToolItem">
        <property name="tooltip_text" translatable="yes">Font size</property>
        <child>
          <object class="ShortlistComboEntry" id="Fontsize"></object>
        </child>
      </object>
    </child>
    <child>
      <object class="GtkToolButton">
        <property name="icon-name">edit-undo</property>
        <property name="action-name">ste.STUndo</property>
        <property name="tooltip_text" translatable="yes">Undo</property>
        <property name="label" translatable="yes">Undo</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkToolButton">
        <property name="icon-name">edit-redo</property>
        <property name="action-name">ste.STRedo</property>
        <property name="tooltip_text" translatable="yes">Redo</property>
        <property name="label" translatable="yes">Redo</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-font-color</property>
        <property name="action-name">ste.FONTCOLOR</property>
        <property name="tooltip_text" translatable="yes">Font Color</property>
        <property name="label" translatable="yes">Font Color</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-font-bgcolor</property>
        <property name="action-name">ste.HIGHLIGHT</property>
        <property name="tooltip_text" translatable="yes">'''
    '''Background Color</property>
        <property name="label" translatable="yes">Background Color</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkToolButton">
        <property name="icon-name">go-jump</property>
        <property name="action-name">ste.LINK</property>
        <property name="tooltip_text" translatable="yes">Link</property>
        <property name="label" translatable="yes">Link</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child>
      <object class="GtkSeparatorToolItem">
        <property name="draw">False</property>
        <property name="hexpand">True</property>
      </object>
      <packing>
        <property name="expand">True</property>
      </packing>
    </child>
    <child>
      <object class="GtkToolButton">
        <property name="icon-name">edit-clear</property>
        <property name="action-name">ste.CLEAR</property>
        <property name="tooltip_text" translatable="yes">'''
    '''Clear Markup</property>
        <property name="label" translatable="yes">Clear Markup</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
  </object>
</interface>
''')
FONT_SIZES = [8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22,
              24, 26, 28, 32, 36, 40, 48, 56, 64, 72]

USERCHARS = r"-\w"
PASSCHARS = r"-\w,?;.:/!%$^*&~\"#'"
HOSTCHARS = r"-\w"
PATHCHARS = r"-\w$.+!*(),;:@&=?/~#%"
#SCHEME = "(news:|telnet:|nntp:|file:/|https?:|ftps?:|webcal:)"
SCHEME = "(file:/|https?:|ftps?:|webcal:)"
USER = "[" + USERCHARS + "]+(:[" + PASSCHARS + "]+)?"
HOST = r"([-\w.]+|\[[0-9A-F:]+\])?"
URLPATH = "(/[" + PATHCHARS + "]*)?[^]'.:}> \t\r\n,\\\"]"

(GENURL, HTTP, MAIL, LINK) = list(range(4))

def find_parent_with_attr(self, attr="dbstate"):
    """
    """
    # Find a parent with attr:
    obj = self
    while obj:
        if hasattr(obj, attr):
            break
        obj = obj.get_parent()
    return obj

#-------------------------------------------------------------------------
#
# StyledTextEditor
#
#-------------------------------------------------------------------------
class StyledTextEditor(Gtk.TextView):
    """
    StyledTextEditor is an enhanced Gtk.TextView to edit :class:`.StyledText`.

    StyledTextEditor is a gui object for :class:`.StyledTextBuffer`. It offers
    :meth:`set_text` and :meth:`get_text` convenience methods to set and get the
    buffer's text.

    StyledTextEditor provides a formatting toolbar, which can be retrieved
    by the :meth:`get_toolbar` method.

    StyledTextEdit defines a new signal: 'match-changed', which is raised
    whenever the mouse cursor reaches or leaves a matched string in the text.
    The feature uses the regexp pattern mathing mechanism of
    :class:`.StyledTextBuffer`.
    The signal's default handler highlights the URL strings. URL's can be
    followed from the editor's popup menu or by pressing the <CTRL>Left
    mouse button.

    :ivar last_match: previously matched string, used for generating the
                      'match-changed' signal.
    :type last_match: tuple or None
    :ivar match: currently matched string, used for generating the
                 'match-changed' signal.
    :type match: tuple or None
    :ivar spellcheck: spell checker object created for the editor instance.
    :type spellcheck: :class:`.Spell`
    :ivar textbuffer: text buffer assigned to the edit instance.
    :type textbuffer: :class:`.StyledTextBuffer`
    :ivar toolbar: toolbar to be used for text formatting.
    :type toolbar: Gtk.Toolbar
    :ivar url_match: stores the matched URL and other mathing parameters.
    :type url_match: tuple or None

    """
    __gtype_name__ = 'StyledTextEditor'

    __gsignals__ = {
        'match-changed': (GObject.SignalFlags.RUN_FIRST,
                          None, #return value
                          (GObject.TYPE_PYOBJECT,)), # arguments
    }

    def __init__(self):
        """Setup initial instance variable values."""
        self.textbuffer = UndoableStyledBuffer()
        self.undo_disabled = self.textbuffer.undo_disabled # see bug 7097
        self.textbuffer.connect('style-changed', self._on_buffer_style_changed)
        self.textbuffer.connect('changed', self._on_buffer_changed)
        self.undo_action = self.redo_action = None
        Gtk.TextView.__init__(self)
        self.set_buffer(self.textbuffer)

        st_cont = self.get_style_context()
        self.linkcolor = get_link_color(st_cont)
        self.textbuffer.linkcolor = self.linkcolor

        self.match = None
        self.last_match = None
        self._init_url_match()
        self.url_match = None

        self.spellcheck = Spell(self)
        self._internal_style_change = False
        self.uimanager = None

        self._connect_signals()

        # variable to not copy to clipboard on double/triple click
        self.selclick = False

    # virtual methods

    def do_match_changed(self, match):
        """
        Default signal handler.

        URL highlighting.

        :param match: the new match parameters
        :type match: tuple or None

        .. warning:: Do not override the handler, but connect to the signal.
        """
        window = self.get_window(Gtk.TextWindowType.TEXT)
        start, end = self.textbuffer.get_bounds()
        self.textbuffer.remove_tag_by_name('hyperlink', start, end)
        if match and (match[MATCH_FLAVOR] in (GENURL, HTTP, MAIL)):
            start_offset = match[MATCH_START]
            end_offset = match[MATCH_END]

            start = self.textbuffer.get_iter_at_offset(start_offset)
            end = self.textbuffer.get_iter_at_offset(end_offset)

            self.textbuffer.apply_tag_by_name('hyperlink', start, end)
            window.set_cursor(HAND_CURSOR)
            self.url_match = match
        elif match and (match[MATCH_FLAVOR] in (LINK,)):
            window.set_cursor(HAND_CURSOR)
            self.url_match = match
        else:
            window.set_cursor(REGULAR_CURSOR)
            self.url_match = None

    def on_insert_at_cursor(self, widget, string):
        """Signal handler. for debugging only."""
        _LOG.debug("Textview insert '%s'" % string)

    def on_delete_from_cursor(self, widget, mode, count):
        """Signal handler. for debugging only."""
        _LOG.debug("Textview delete type %d count %d" % (mode, count))

    def on_paste_clipboard(self, widget):
        """Signal handler. for debugging only."""
        _LOG.debug("Textview paste clipboard")

    def on_motion_notify_event(self, widget, event):
        """
        Signal handler.

        As the mouse cursor moves the handler checks if there's a new
        regexp match at the new location. If match changes the
        'match-changed' signal is raised.
        """
        x, y = self.window_to_buffer_coords(Gtk.TextWindowType.WIDGET,
                                            int(event.x), int(event.y))
        iter_at_location = self.get_iter_at_location(x, y)
        if isinstance(iter_at_location, tuple):
            iter_at_location = iter_at_location[1]
        self.match = self.textbuffer.match_check(iter_at_location.get_offset())
        tooltip = None
        for tag in (tag for tag in iter_at_location.get_tags()
                    if tag.get_property('name').startswith("link")):
            self.match = (x, y, LINK, tag.data, tag)
            tooltip = self.make_tooltip_from_link(tag)
            break

        if self.match != self.last_match:
            self.emit('match-changed', self.match)

        self.last_match = self.match
        # self.get_root_window().get_pointer()  # Doesn't seem to do anythhing!
        self.set_tooltip_text(tooltip)
        return False

    def make_tooltip_from_link(self, link_tag):
        """
        Return a string useful for a tooltip given a LinkTag object.
        """
        from gramps.gen.simple import SimpleAccess
        win_obj = find_parent_with_attr(self, attr="dbstate")
        display = link_tag.data
        if win_obj:
            simple_access = SimpleAccess(win_obj.dbstate.db)
            url = link_tag.data
            if url.startswith("gramps://"):
                obj_class, prop, value = url[9:].split("/")
                display = simple_access.display(obj_class, prop, value) or url
        return display + ((_("\nCommand-Click to follow link") if mac() else
                           _("\nCtrl-Click to follow link"))
                          if self.get_editable() else '')

    def on_button_release_event(self, widget, event):
        """
        Copy selection to clipboard for left click if selection given
        """
        if (event.type == Gdk.EventType.BUTTON_RELEASE and self.selclick and
                event.button == 1):
            bounds = self.textbuffer.get_selection_bounds()
            if bounds:
                clip = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                        Gdk.SELECTION_PRIMARY)
                clip.set_text(str(self.textbuffer.get_text(bounds[0],
                                                        bounds[1], True)), -1)
        return False

    def on_button_press_event(self, widget, event):
        """
        Signal handler.

        Handles the <CTRL> + Left click over a URL match.
        """
        self.selclick=False
        if ((event.type == Gdk.EventType.BUTTON_PRESS) and
            (event.button == 1) and (self.url_match) and
            (match_primary_mask(event.get_state()) or
             not self.get_editable())):

            flavor = self.url_match[MATCH_FLAVOR]
            url = self.url_match[MATCH_STRING]
            self._open_url_cb(None, url, flavor)
        elif (event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1):
            #on release we will copy selected data to clipboard
            self.selclick = True
        #propagate click
        return False

    def on_populate_popup(self, widget, menu):
        """
        Signal handler.

        Insert extra menuitems:

        1. Insert spellcheck selector submenu for spell checking.
        2. Insert extra menus depending on ULR match result.
        """
        # spell checker submenu
        spell_menu = Gtk.MenuItem(label=_('Spellcheck'))
        spell_menu.set_submenu(self._create_spell_menu())
        spell_menu.show_all()
        menu.prepend(spell_menu)

        search_menu = Gtk.MenuItem(label=_("Search selection on web"))
        search_menu.connect('activate', self.search_web)
        search_menu.show_all()
        menu.append(search_menu)

        # url menu items
        if self.url_match:
            flavor = self.url_match[MATCH_FLAVOR]
            url = self.url_match[MATCH_STRING]

            if flavor == MAIL:
                open_menu = Gtk.MenuItem(label=_('_Send Mail To...'))
                open_menu.set_use_underline(True)
                copy_menu = Gtk.MenuItem(label=_('Copy _E-mail Address'))
                copy_menu.set_use_underline(True)
            else:
                open_menu = Gtk.MenuItem(label=_('_Open Link'))
                open_menu.set_use_underline(True)
                copy_menu = Gtk.MenuItem(label=_('Copy _Link Address'))
                copy_menu.set_use_underline(True)

            if flavor == LINK and self.get_editable():
                edit_menu = Gtk.MenuItem(label=_('_Edit Link'))
                edit_menu.set_use_underline(True)
                edit_menu.connect('activate', self._edit_url_cb,
                                  self.url_match[-1], # tag
                                  )
                edit_menu.show()
                menu.prepend(edit_menu)

            copy_menu.connect('activate', self._copy_url_cb, url, flavor)
            copy_menu.show()

            menu.prepend(copy_menu)

            open_menu.connect('activate', self._open_url_cb, url, flavor)
            open_menu.show()
            menu.prepend(open_menu)

    def search_web(self, widget):
        """
        Search the web for selected text.
        """
        selection = self.textbuffer.get_selection_bounds()
        if len(selection) > 0:
            display_url(config.get("behavior.web-search-url") %
                        {'text':
                         self.textbuffer.get_text(selection[0],
                                                  selection[1], True)})

    def reset(self):
        """
        Reset the undoable buffer
        """
        self.textbuffer.reset()
        self.undo_action.set_enabled(False)
        self.redo_action.set_enabled(False)

    # private methods

    def _connect_signals(self):
        """Connect to several signals of the super class Gtk.TextView."""
        self.connect('insert-at-cursor', self.on_insert_at_cursor)
        self.connect('delete-from-cursor', self.on_delete_from_cursor)
        self.connect('paste-clipboard', self.on_paste_clipboard)
        self.connect('motion-notify-event', self.on_motion_notify_event)
        self.connect('button-press-event', self.on_button_press_event)
        self.connect('button-release-event', self.on_button_release_event)
        self.connect('populate-popup', self.on_populate_popup)

    def create_toolbar(self, uimanager, window):
        """
        Create a formatting toolbar.

        :returns: toolbar containing text formatting toolitems.
        :rtype: Gtk.Toolbar
        """
        self.uimanager = uimanager
        # build the toolbar
        builder = Gtk.Builder()
        builder.set_translation_domain(glocale.get_localedomain())
        builder.add_from_string(FORMAT_TOOLBAR)
        # define the actions...
        _actions = [
            ('ITALIC', self._on_toggle_action_activate, '<PRIMARY>i', False),
            ('BOLD', self._on_toggle_action_activate, '<PRIMARY>b', False),
            ('UNDERLINE', self._on_toggle_action_activate, '<PRIMARY>u',
             False),
            ('FONTCOLOR', self._on_action_activate),
            ('HIGHLIGHT', self._on_action_activate),
            ('LINK', self._on_link_activate),
            ('CLEAR', self._format_clear_cb),
            ('STUndo', self.undo, '<primary>z'),
            ('STRedo', self.redo, '<primary><shift>z'),
        ]

        # the following are done manually rather than using actions
        fonts = SystemFonts()
        fontface = builder.get_object('Fontface')
        fontface.init(fonts.get_system_fonts(), shortlist=True, validator=None)
        fontface.set_entry_editable(False)
        fontface.connect('changed', make_cb(
            self._on_valueaction_changed, StyledTextTagType.FONTFACE))
        # set initial value
        default = StyledTextTagType.STYLE_DEFAULT[StyledTextTagType.FONTFACE]
        self.fontface = fontface.get_child()
        self.fontface.set_text(str(default))
        fontface.show()

        items = FONT_SIZES
        fontsize = builder.get_object('Fontsize')
        fontsize.init(items, shortlist=False, validator=is_valid_fontsize)
        fontsize.set_entry_editable(True)
        fontsize.connect('changed', make_cb(
            self._on_valueaction_changed, StyledTextTagType.FONTSIZE))
        # set initial value
        default = StyledTextTagType.STYLE_DEFAULT[StyledTextTagType.FONTSIZE]
        self.fontsize = fontsize.get_child()
        self.fontsize.set_text(str(default))
        fontsize.show()

        # create the action group and insert all the actions
        self.action_group = ActionGroup('Format', _actions, 'ste')
        act_grp = SimpleActionGroup()
        window.insert_action_group('ste', act_grp)
        window.set_application(uimanager.app)
        uimanager.insert_action_group(self.action_group, act_grp)

        self.undo_action = uimanager.get_action(self.action_group, "STUndo")
        self.redo_action = uimanager.get_action(self.action_group, "STRedo")
        # allow undo/redo to see actions if editable.
        self.textbuffer.connect('changed', self._on_buffer_changed)
        # undo/redo are initially greyed out, until something is changed
        self.undo_action.set_enabled(False)
        self.redo_action.set_enabled(False)

        # get the toolbar and set it's style
        toolbar = builder.get_object('ToolBar')

        return toolbar, self.action_group

    def set_transient_parent(self, parent=None):
        self.transient_parent = parent

    def _init_url_match(self):
        """Setup regexp matching for URL match."""
        self.textbuffer.create_tag('hyperlink',
                                   underline=Pango.Underline.SINGLE,
                                   foreground=self.linkcolor)
        self.textbuffer.match_add(SCHEME + "//(" + USER + "@)?" +
                                  HOST + "(:[0-9]+)?" +
                                  URLPATH, GENURL)
        self.textbuffer.match_add(r"(www\.|ftp\.)[" + HOSTCHARS + r"]*\.[" +
                                  HOSTCHARS + ".]+" + "(:[0-9]+)?" +
                                  URLPATH, HTTP)
        self.textbuffer.match_add(r"(mailto:)?[\w][-.\w]*@[\w]"
                                  r"[-\w]*(\.[\w][-.\w]*)+", MAIL)

    def _create_spell_menu(self):
        """
        Create a menu with all the installed spellchecks.

        It is called each time the popup menu is opened. Each spellcheck
        forms a radio menu item, and the selected spellcheck is set as active.

        :returns: menu containing all the installed spellchecks.
        :rtype: Gtk.Menu
        """
        active_spellcheck = self.spellcheck.get_active_spellcheck()

        menu = Gtk.Menu()
        group = None
        for lang in self.spellcheck.get_all_spellchecks():
            menuitem = Gtk.RadioMenuItem(label=lang)
            menuitem.set_active(lang == active_spellcheck)
            menuitem.connect('activate', self._spell_change_cb, lang)
            menu.append(menuitem)

            if group is None:
                group = menuitem

        return menu

    # Callback functions

    def _on_toggle_action_activate(self, action, value):
        """
        Toggle a style.

        Toggle styles are e.g. 'bold', 'italic', 'underline'.
        """
        action.set_state(value)
        if self._internal_style_change:
            return

        style = action.get_name()
        value = value.get_boolean()
        _LOG.debug("applying style '%s' with value '%s'" % (style, str(value)))
        self.textbuffer.apply_style(getattr(StyledTextTagType, style), value)

    def _on_link_activate(self, action, value):
        """
        Create a link of a selected region of text.
        """
        # Send in a default link. Could be based on active person.
        selection_bounds = self.textbuffer.get_selection_bounds()
        if selection_bounds:
            # Paste text to clipboards
            text = str(self.textbuffer.get_text(selection_bounds[0],
                                                selection_bounds[1], True))
            clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                        Gdk.SELECTION_CLIPBOARD)

            clipboard.set_text(text, -1)
            clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                        Gdk.SELECTION_PRIMARY)
            clipboard.set_text(text, -1)
            uri_dialog(self, None, self.setlink_callback)

    def setlink_callback(self, uri, tag=None):
        """
        Callback for setting or editing a link's object.
        """
        if uri:
            _LOG.debug("applying style 'link' with value '%s'" % uri)
            if not tag:
                tag = LinkTag(self.textbuffer,
                              data=uri,
                              underline=Pango.Underline.SINGLE,
                              foreground=self.linkcolor)
                selection_bounds = self.textbuffer.get_selection_bounds()
                self.textbuffer.apply_tag(tag,
                                          selection_bounds[0],
                                          selection_bounds[1])
            else:
                tag.data = uri

    def _on_action_activate(self, action, value):
        """Apply a format set from a Gtk.Action type of action."""
        style = getattr(StyledTextTagType, action.get_name())
        current_value = self.textbuffer.get_style_at_cursor(style)

        if style == StyledTextTagType.FONTCOLOR:
            color_dialog = Gtk.ColorChooserDialog(
                title=_("Select font color"),
                transient_for=self.transient_parent)
        elif style == StyledTextTagType.HIGHLIGHT:
            color_dialog = Gtk.ColorChooserDialog(
                title=_("Select background color"),
                transient_for=self.transient_parent)
        else:
            _LOG.debug("unknown style: '%d'" % style)
            return

        if current_value:
            rgba = Gdk.RGBA()
            rgba.parse(current_value)
            color_dialog.set_rgba(rgba)

        response = color_dialog.run()
        rgba = color_dialog.get_rgba()
        value = '#%02x%02x%02x' % (int(rgba.red * 255),
                                   int(rgba.green * 255),
                                   int(rgba.blue * 255))
        color_dialog.destroy()

        if response == Gtk.ResponseType.OK:
            _LOG.debug("applying style '%d' with value '%s'" %
                       (style, str(value)))
            self.textbuffer.apply_style(style, value)

    def _on_valueaction_changed(self, obj, style):
        """Apply a format set by a ShortListComboEntry."""
        if self._internal_style_change:
            return

        value = obj.get_active_data()
        try:
            value = StyledTextTagType.STYLE_TYPE[style](value)
            _LOG.debug("applying style '%d' with value '%s'" %
                       (style, str(value)))
            self.textbuffer.apply_style(style, value)
        except ValueError:
            _LOG.debug("unable to convert '%s' to '%s'" %
                       (value, StyledTextTagType.STYLE_TYPE[style]))

    def _format_clear_cb(self, action, value):
        """
        Remove all formats from the selection or from all.

        Remove only our own tags without touching other ones (e.g. Gtk.Spell),
        thus remove_all_tags() can not be used.
        """
        clear_anything = self.textbuffer.clear_selection()
        if not clear_anything:
            for style in ALLOWED_STYLES:
                self.textbuffer.remove_style(style)

            start, end = self.textbuffer.get_bounds()
            tags = self.textbuffer._get_tag_from_range(start.get_offset(),
                                                       end.get_offset())
            for tag_name, tag_data in tags.items():
                if tag_name.startswith("link"):
                    for start, end in tag_data:
                        self.textbuffer.remove_tag_by_name(tag_name,
                                      self.textbuffer.get_iter_at_offset(start),
                                      self.textbuffer.get_iter_at_offset(end+1))

    def _on_buffer_changed(self, buffer):
        """synchronize the undo/redo buttons with what is possible"""
        if self.undo_action:
            self.undo_action.set_enabled(self.textbuffer.can_undo)
            self.redo_action.set_enabled(self.textbuffer.can_redo)

    def _on_buffer_style_changed(self, buffer, changed_styles):
        """Synchronize actions as the format changes at the buffer's cursor."""
        if not self.uimanager:
            return  # never initialized a toolbar, not editable
        types = [StyledTextTagType.ITALIC, StyledTextTagType.BOLD,
                 StyledTextTagType.UNDERLINE]
        self._internal_style_change = True
        for style, style_value in changed_styles.items():
            if style in types:
                action = self.uimanager.get_action(
                    self.action_group,
                    StyledTextTagType(style).xml_str().upper())
                action.change_state(Variant.new_boolean(style_value))
            elif (style == StyledTextTagType.FONTFACE):
                self.fontface.set_text(style_value)
            elif style == StyledTextTagType.FONTSIZE:
                self.fontsize.set_text(str(style_value))
        self._internal_style_change = False

    def _spell_change_cb(self, menuitem, spellcheck):
        """Set spell checker spellcheck according to user selection."""
        self.spellcheck.set_active_spellcheck(spellcheck)

    def _open_url_cb(self, menuitem, url, flavor):
        """Open the URL in a browser."""
        if not url:
            return

        if flavor == HTTP:
            url = 'http:' + url
        elif flavor == MAIL:
            if not url.startswith('mailto:'):
                url = 'mailto:' + url
        elif flavor == GENURL:
            pass
        elif flavor == LINK:
            # gramps://person/id/VALUE
            # gramps://person/handle/VALUE
            if url.startswith("gramps://"):
                # if in a window:
                win_obj = find_parent_with_attr(self, attr="dbstate")
                if win_obj:
                    # Edit the object:
                    obj_class, prop, value = url[9:].split("/")
                    from ..editors import EditObject
                    EditObject(win_obj.dbstate,
                               win_obj.uistate,
                               win_obj.track,
                               obj_class, prop, value)
                    return
        else:
            return
        # If ok, then let's open
        obj = find_parent_with_attr(self, attr="dbstate")
        if obj:
            display_url(url, obj.uistate)
        else:
            display_url(url)

    def _copy_url_cb(self, menuitem, url, flavor):
        """Copy url to both useful selections."""
        clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                        Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(url, -1)

        clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                        Gdk.SELECTION_PRIMARY)
        clipboard.set_text(url, -1)


    def _edit_url_cb(self, menuitem, link_tag):
        """
        Edit the URI of the link.
        """
        # Paste text to clipboards
        bounds = self.textbuffer.get_selection_bounds()
        if bounds:
            text = str(self.textbuffer.get_text(bounds[0], bounds[1], True))
            clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                        Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(text, -1)
            clipboard = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(),
                        Gdk.SELECTION_PRIMARY)
            clipboard.set_text(text, -1)
        uri_dialog(self, link_tag.data,
                   lambda uri: self.setlink_callback(uri, link_tag))

    # public methods

    def set_text(self, text):
        """
        Set the text of the text buffer of the editor.

        :param text: formatted text to edit in the view.
        :type text: :class:`.StyledText`
        """
        self.textbuffer.set_text(text)
        self.textbuffer.place_cursor(self.textbuffer.get_start_iter())

    def get_text(self):
        """
        Get the text of the text buffer of the editor.

        :returns: the formatted text from the editor.
        :rtype: :class:`.StyledText`
        """
        start, end = self.textbuffer.get_bounds()
        return self.textbuffer.get_text(start, end, True)

    def undo(self, *obj):
        self.textbuffer.undo()

    def redo(self, *obj):
        self.textbuffer.redo()
#-------------------------------------------------------------------------
#
# Module functions
#
#-------------------------------------------------------------------------


def uri_dialog(self, uri, callback):
    """
    Function to spawn the link editor.
    """
    from ..editors.editlink import EditLink
    obj = find_parent_with_attr(self, attr="dbstate")
    if obj:
        if uri is None:
            # make a default link
            uri = "http://"
            # Check in order for an open page:
            for object_class in ["Person", "Place", "Event", "Family",
                                 "Repository", "Source", "Media"]:
                handle = obj.uistate.get_active(object_class)
                if handle:
                    uri = "gramps://%s/handle/%s" % (object_class, handle)
                    break
        EditLink(obj.dbstate, obj.uistate, obj.track, uri, callback)


def is_valid_fontsize(size):
    """Validator function for font size selector widget."""
    return (size > 0) and (size < 73)


def make_cb(func, value):
    """
    Generates a callback function based off the passed arguments
    """
    return lambda x: func(x, value)
