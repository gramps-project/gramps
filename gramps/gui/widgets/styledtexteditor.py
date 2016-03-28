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

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import StyledTextTagType
from .styledtextbuffer import (ALLOWED_STYLES,
                                          MATCH_START, MATCH_END,
                                          MATCH_FLAVOR, MATCH_STRING,
                                          LinkTag)
from .undoablestyledbuffer import UndoableStyledBuffer
from .valueaction import ValueAction
from .toolcomboentry import ToolComboEntry
from .springseparator import SpringSeparatorAction
from ..spell import Spell
from ..display import display_url
from ..utils import SystemFonts, rgb_to_hex
from gramps.gen.config import config
from gramps.gen.constfunc import has_display
from ..actiongroup import ActionGroup

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
if has_display():
    HAND_CURSOR = Gdk.Cursor.new(Gdk.CursorType.HAND2)
    REGULAR_CURSOR = Gdk.Cursor.new(Gdk.CursorType.XTERM)

FORMAT_TOOLBAR = '''
<ui>
<toolbar name="ToolBar">
  <toolitem action="%d"/>  
  <toolitem action="%d"/>  
  <toolitem action="%d"/>
  <toolitem action="Undo"/>
  <toolitem action="Redo"/>
  <toolitem action="%d"/>
  <toolitem action="%d"/>
  <toolitem action="%d"/>
  <toolitem action="%d"/>
  <toolitem action="%d"/>
  <toolitem action="spring"/>
  <toolitem action="clear"/>
</toolbar>
</ui>
''' % (StyledTextTagType.ITALIC,
       StyledTextTagType.BOLD,
       StyledTextTagType.UNDERLINE,
       StyledTextTagType.FONTFACE,
       StyledTextTagType.FONTSIZE,
       StyledTextTagType.FONTCOLOR,
       StyledTextTagType.HIGHLIGHT,
       StyledTextTagType.LINK,
   )

FONT_SIZES = [8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22,
              24, 26, 28, 32, 36, 40, 48, 56, 64, 72]

USERCHARS = "-A-Za-z0-9"
PASSCHARS = "-A-Za-z0-9,?;.:/!%$^*&~\"#'"
HOSTCHARS = "-A-Za-z0-9"
PATHCHARS = "-A-Za-z0-9_$.+!*(),;:@&=?/~#%"
#SCHEME = "(news:|telnet:|nntp:|file:/|https?:|ftps?:|webcal:)"
SCHEME = "(file:/|https?:|ftps?:|webcal:)"
USER = "[" + USERCHARS + "]+(:[" + PASSCHARS + "]+)?"
URLPATH = "/[" + PATHCHARS + "]*[^]'.}>) \t\r\n,\\\"]"

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
        GObject.GObject.__init__(self)
        self.set_buffer(self.textbuffer)

        st_cont = self.get_style_context()
        col = st_cont.lookup_color('link_color')
        if col[0]:
            self.linkcolor = rgb_to_hex((col[1].red, col[1].green, col[1].blue))
        else:
            self.linkcolor = 'blue'
        self.textbuffer.linkcolor = self.linkcolor

        self.match = None
        self.last_match = None
        self._init_url_match()
        self.url_match = None

        self.toolbar = self._create_toolbar()
        self.spellcheck = Spell(self)
        self._internal_style_change = False

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
        
    def on_key_press_event(self, widget, event):
        """Signal handler.
        
        Handle formatting shortcuts.
        
        """
        if ((Gdk.keyval_name(event.keyval) == 'Z') and
            (event.get_state() & Gdk.ModifierType.CONTROL_MASK) and 
            (event.get_state() & Gdk.ModifierType.SHIFT_MASK)):
            self.redo()
            return True
        elif ((Gdk.keyval_name(event.keyval) == 'z') and
              (event.get_state() & Gdk.ModifierType.CONTROL_MASK)):
            self.undo()
            return True
        else:
            for accel, accel_name in self.action_accels.items():
                key, mod = Gtk.accelerator_parse(accel)
                if ((event.keyval == key) and (event.get_state() & mod)):
                    action_name = accel_name
                    action = self.action_group.get_action(action_name)
                    action.activate()
                    return True
        return False
        
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
        if not self.match:
            for tag in (tag for tag in iter_at_location.get_tags()
                        if tag.get_property('name').startswith("link")):
                self.match = (x, y, LINK, tag.data, tag)
                tooltip = self.make_tooltip_from_link(tag)
                break
        
        if self.match != self.last_match:
            self.emit('match-changed', self.match)

        self.last_match = self.match
        self.get_root_window().get_pointer()
        if tooltip:
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
        return display

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
            (event.button == 1) and
            (event.get_state() and Gdk.ModifierType.CONTROL_MASK) and
            (self.url_match)):
            
            flavor = self.url_match[MATCH_FLAVOR]
            url = self.url_match[MATCH_STRING]
            self._open_url_cb(None, url, flavor)
        elif (event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1) :
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

            if flavor == LINK:
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
        self.undo_action.set_sensitive(False)
        self.redo_action.set_sensitive(False)

    # private methods
    
    def _connect_signals(self):
        """Connect to several signals of the super class Gtk.TextView."""
        self.connect('key-press-event', self.on_key_press_event)
        self.connect('insert-at-cursor', self.on_insert_at_cursor)
        self.connect('delete-from-cursor', self.on_delete_from_cursor)
        self.connect('paste-clipboard', self.on_paste_clipboard)
        self.connect('motion-notify-event', self.on_motion_notify_event)
        self.connect('button-press-event', self.on_button_press_event)
        self.connect('button-release-event', self.on_button_release_event)
        self.connect('populate-popup', self.on_populate_popup)
        
    def _create_toolbar(self):
        """
        Create a formatting toolbar.
        
        :returns: toolbar containing text formatting toolitems.
        :rtype: Gtk.Toolbar
        """
        # define the actions...
        # ...first the toggle actions, which have a ToggleToolButton as proxy
        format_toggle_actions = [
            (str(StyledTextTagType.ITALIC), 'format-text-italic', None, None,
             _('Italic'), self._on_toggle_action_activate),
            (str(StyledTextTagType.BOLD), 'format-text-bold', None, None,
             _('Bold'), self._on_toggle_action_activate),
            (str(StyledTextTagType.UNDERLINE), 'format-text-underline', None,
            None, _('Underline'), self._on_toggle_action_activate),
        ]
        
        self.toggle_actions = [action[0] for action in format_toggle_actions]

        # ...then the normal actions, which have a ToolButton as proxy
        format_actions = [
            (str(StyledTextTagType.FONTCOLOR), 'gramps-font-color', None, None,
             _('Font Color'), self._on_action_activate),
            (str(StyledTextTagType.HIGHLIGHT), 'gramps-font-bgcolor', None,
            None, _('Background Color'), self._on_action_activate),
            (str(StyledTextTagType.LINK), 'go-jump', None, None,
             _('Link'), self._on_link_activate),
            ('clear', 'edit-clear', None, None,
             _('Clear Markup'), self._format_clear_cb),
        ]
        
        # ...last the custom actions, which have custom proxies
        default = StyledTextTagType.STYLE_DEFAULT[StyledTextTagType.FONTFACE]
        fonts = SystemFonts()        
        fontface_action = ValueAction(str(StyledTextTagType.FONTFACE),
                                      _("Font family"),
                                      default,
                                      ToolComboEntry,
                                      fonts.get_system_fonts(),
                                      False, #editable
                                      True, #shortlist
                                      None) # validator
        fontface_action.connect('changed', self._on_valueaction_changed)

        items = FONT_SIZES
        default = StyledTextTagType.STYLE_DEFAULT[StyledTextTagType.FONTSIZE]
        fontsize_action = ValueAction(str(StyledTextTagType.FONTSIZE),
                                      _("Font size"),
                                      default,
                                      ToolComboEntry,
                                      items,
                                      True, #editable
                                      False, #shortlist
                                      is_valid_fontsize) #validator
        fontsize_action.connect('changed', self._on_valueaction_changed)

        spring = SpringSeparatorAction("spring", "", "", None)
        
        # action accelerators
        self.action_accels = {
            '<PRIMARY>i': str(StyledTextTagType.ITALIC),
            '<PRIMARY>b': str(StyledTextTagType.BOLD),
            '<PRIMARY>u': str(StyledTextTagType.UNDERLINE),
        }

        # create the action group and insert all the actions
        self.action_group = ActionGroup(name='Format')
        self.action_group.add_toggle_actions(format_toggle_actions)
        self.undo_action = Gtk.Action(name="Undo", label=_('Undo'),
                                      tooltip=_('Undo'))
        self.undo_action.set_icon_name('edit-undo')
        self.undo_action.connect('activate', self.undo)
        self.redo_action = Gtk.Action.new(name="Redo", label=_('Redo'),
                                          tooltip=_('Redo'))
        self.redo_action.set_icon_name('edit-redo')
        self.redo_action.connect('activate', self.redo)
        self.action_group.add_action(self.undo_action)
        self.action_group.add_action(self.redo_action)
        self.action_group.add_actions(format_actions)
        self.action_group.add_action(fontface_action)
        self.action_group.add_action(fontsize_action)
        self.action_group.add_action(spring)
        
        # define the toolbar and create the proxies via ensure_update()
        uimanager = Gtk.UIManager()
        uimanager.insert_action_group(self.action_group, 0)
        uimanager.add_ui_from_string(FORMAT_TOOLBAR)
        uimanager.ensure_update()
        
        # get the toolbar and set it's style
        toolbar = uimanager.get_widget('/ToolBar')      
        toolbar.set_style(Gtk.ToolbarStyle.ICONS)
        self.undo_action.set_sensitive(False)
        self.redo_action.set_sensitive(False)

        return toolbar
        
    def _init_url_match(self):
        """Setup regexp matching for URL match."""
        self.textbuffer.create_tag('hyperlink',
                                   underline=Pango.Underline.SINGLE,
                                   foreground=self.linkcolor)
        self.textbuffer.match_add(SCHEME + "//(" + USER + "@)?[" +
                                  HOSTCHARS + ".]+" + "(:[0-9]+)?(" +
                                  URLPATH + ")?/?", GENURL)
        self.textbuffer.match_add("(www|ftp)[" + HOSTCHARS + "]*\\.[" +
                                  HOSTCHARS + ".]+" + "(:[0-9]+)?(" +
                                  URLPATH + ")?/?", HTTP)
        self.textbuffer.match_add("(mailto:)?[a-z0-9][a-z0-9.-]*@[a-z0-9]"
                                  "[a-z0-9-]*(\\.[a-z0-9][a-z0-9-]*)+", MAIL)
        
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
    
    def _on_toggle_action_activate(self, action):
        """
        Toggle a style.
        
        Toggle styles are e.g. 'bold', 'italic', 'underline'.
        """
        if self._internal_style_change:
            return

        style = int(action.get_name())
        value = action.get_active()
        _LOG.debug("applying style '%d' with value '%s'" % (style, str(value)))
        self.textbuffer.apply_style(style, value)

    def _on_link_activate(self, action):
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


    def _on_action_activate(self, action):
        """Apply a format set from a Gtk.Action type of action."""
        style = int(action.get_name())
        current_value = self.textbuffer.get_style_at_cursor(style)

        if style == StyledTextTagType.FONTCOLOR:
            color_dialog = Gtk.ColorChooserDialog(_("Select font color"))
        elif style == StyledTextTagType.HIGHLIGHT:
            color_dialog = Gtk.ColorChooserDialog(_("Select background color"))
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

    def _on_valueaction_changed(self, action):
        """Apply a format set by a ValueAction type of action."""
        if self._internal_style_change:
            return
        
        style = int(action.get_name())

        value = action.get_value()
        try:
            value = StyledTextTagType.STYLE_TYPE[style](value)
            _LOG.debug("applying style '%d' with value '%s'" %
                       (style, str(value)))
            self.textbuffer.apply_style(style, value)
        except ValueError:
            _LOG.debug("unable to convert '%s' to '%s'" %
                       (text, StyledTextTagType.STYLE_TYPE[style]))

    def _format_clear_cb(self, action):
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
        self.undo_action.set_sensitive(self.textbuffer.can_undo)
        self.redo_action.set_sensitive(self.textbuffer.can_redo)

    def _on_buffer_style_changed(self, buffer, changed_styles):
        """Synchronize actions as the format changes at the buffer's cursor."""
        for style, style_value in changed_styles.items():
            if str(style) in self.toggle_actions:
                action = self.action_group.get_action(str(style))
                self._internal_style_change = True
                action.set_active(style_value)
                self._internal_style_change = False
            
            if ((style == StyledTextTagType.FONTFACE) or
                (style == StyledTextTagType.FONTSIZE)):
                action = self.action_group.get_action(str(style))
                self._internal_style_change = True
                action.set_value(style_value)
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
    
    def get_toolbar(self):
        """
        Get the formatting toolbar of the editor.
        
        :returns: toolbar widget to use as formatting GUI.
        :rtype: Gtk.Toolbar
        """
        return self.toolbar

    def undo(self, obj=None):
        self.textbuffer.undo()

    def redo(self, obj=None):
        self.textbuffer.redo()

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
        EditLink(obj.dbstate, obj.uistate, obj.track, uri, callback)

#-------------------------------------------------------------------------
#
# Module functions
#
#-------------------------------------------------------------------------

def is_valid_fontsize(size):
    """Validator function for font size selector widget."""
    return (size > 0) and (size < 73)
