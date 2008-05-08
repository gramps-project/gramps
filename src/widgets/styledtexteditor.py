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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"Text editor subclassed from gtk.TextView handling L{StyledText}."

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

import logging
_LOG = logging.getLogger(".Editors.StyledTextEditor")

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gobject
import gtk
from pango import UNDERLINE_SINGLE

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib import StyledTextTagType
from widgets import (StyledTextBuffer, ALLOWED_STYLES,
                     MATCH_START, MATCH_END,
                     MATCH_FLAVOR, MATCH_STRING)
from Spell import Spell
from GrampsDisplay import url as display_url

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
HAND_CURSOR = gtk.gdk.Cursor(gtk.gdk.HAND2)
REGULAR_CURSOR = gtk.gdk.Cursor(gtk.gdk.XTERM)

FORMAT_TOOLBAR = '''
<ui>
<toolbar name="ToolBar">
  <toolitem action="%d"/>  
  <toolitem action="%d"/>  
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

(GENURL, HTTP, MAIL) = range(3)

#-------------------------------------------------------------------------
#
# StyledTextEditor
#
#-------------------------------------------------------------------------
class StyledTextEditor(gtk.TextView):
    """StyledTextEditor is an enhanced gtk.TextView to edit L{StyledText}.
    
    StyledTextEditor is a gui object for L{StyledTextBuffer}. It offers
    L{set_text} and L{get_text} convenience methods to set and get the 
    buffer's text.
    
    StyledTextEditor provides a formatting toolbar, which can be retrieved
    by the L{get_toolbar} method.
    
    StyledTextEdit defines a new signal: 'match-changed', which is raised
    whenever the mouse cursor reaches or leaves a matched string in the text.
    The feature uses the regexp pattern mathing mechanism L{StyledTextBuffer}.
    The signal's default handler highlights the URL strings. URL's can be
    followed from the editor's popup menu.
    
    @ivar last_match: previously matched string, used for generating the
    'match-changed' signal.
    @type last_match: tuple or None
    @ivar match: currently matched string, used for generating the
    'match-changed' signal.
    @type match: tuple or None
    @ivar show_unicode: stores the user's gtk.settings['gtk-show-unicode-menu']
    value.
    @type show_unicode: bool
    @ivar spellcheck: spell checker object created for the editor instance.
    @type spellcheck: L{Spell}
    @ivar textbuffer: text buffer assigned to the edit instance.
    @type textbuffer: L{StyledTextBuffer}
    @ivar toolbar: toolbar to be used for text formatting.
    @type toolbar: gtk.Toolbar
    @ivar url_match: stores the matched URL and other mathing parameters.
    @type url_match: tuple or None
    
    """
    __gtype_name__ = 'StyledTextEditor'
    
    __gsignals__ = {
        'match-changed': (gobject.SIGNAL_RUN_FIRST, 
                          gobject.TYPE_NONE, #return value
                          (gobject.TYPE_PYOBJECT,)), # arguments
    }    

    def __init__(self):
        """Setup initial instance variable values."""
        self.textbuffer = StyledTextBuffer()
        self.textbuffer.connect('style-changed', self._on_buffer_style_changed)
        gtk.TextView.__init__(self, self.textbuffer)

        self.match = None
        self.last_match = None
        self._init_url_match()
        self.url_match = None

        self.toolbar = self._create_toolbar()
        self.spellcheck = Spell(self)
        self._internal_style_change = False

        self._connect_signals()

        # we want to disable the unicode menu in the popup
        settings = gtk.settings_get_default()
        self.show_unicode = settings.get_property('gtk-show-unicode-menu')
        settings.set_property('gtk-show-unicode-menu', False)

    # virtual methods
    
    def do_match_changed(self, match):
        """Default signal handler.
        
        URL highlighting.
        
        @param match: the new match parameters
        @type match: tuple or None
        
        @attention: Do not override the handler, but connect to the signal.
        
        """
        window = self.get_window(gtk.TEXT_WINDOW_TEXT)
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
        else:
            window.set_cursor(REGULAR_CURSOR)
            self.url_match = None
        
    def on_unrealize(self, widget):
        """Signal handler.
        
        Set the default Gtk settings back before leaving.
        
        """
        settings = gtk.settings_get_default()
        settings.set_property('gtk-show-unicode-menu', self.show_unicode)
        
    def on_key_press_event(self, widget, event):
        """Signal handler.
        
        Handle formatting shortcuts.
        
        """
        for accel in self.action_accels.keys():
            key, mod = gtk.accelerator_parse(accel)
            if (event.keyval, event.state) == (key, mod):
                action_name = self.action_accels[accel]
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
        """Signal handler.
        
        As the mouse cursor moves the handler checks if there's a new
        regexp match at the new location. If match changes the
        'match-changed' signal is raised.
        
        """
        x, y = self.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
                                            int(event.x), int(event.y))
        iter_at_location = self.get_iter_at_location(x, y)
        self.match = self.textbuffer.match_check(iter_at_location.get_offset())
        
        if self.match != self.last_match:
            self.emit('match-changed', self.match)

        self.last_match = self.match
        
        self.window.get_pointer()
        return False

    def on_button_press_event(self, widget, event):
        """Signal handler.
        
        Handles the <CTRL> + Left click over a URL match.
        
        """
        if ((event.type == gtk.gdk.BUTTON_PRESS) and
            (event.button == 1) and
            (event.state and gtk.gdk.CONTROL_MASK) and
            (self.url_match)):
            
            flavor = self.url_match[MATCH_FLAVOR]
            url = self.url_match[MATCH_STRING]
            self._open_url_cb(None, url, flavor)
            
        return False
        
    def on_populate_popup(self, widget, menu):
        """Signal handler.
        
        Insert extra menuitems:
        1. Insert language selector submenu for spell checking.
        2. Insert extra menus depending on ULR match result.
        
        """
        # spell checker submenu
        spell_menu = gtk.MenuItem(_('Spell'))
        spell_menu.set_submenu(self._create_spell_menu())
        spell_menu.show_all()
        menu.prepend(spell_menu)
        
        # url menu items
        if self.url_match:
            flavor = self.url_match[MATCH_FLAVOR]
            url = self.url_match[MATCH_STRING]
            
            if flavor == MAIL:
                open_menu = gtk.MenuItem(_('_Send Mail To...'))
                copy_menu = gtk.MenuItem(_('Copy _E-mail Address'))
            else:
                open_menu = gtk.MenuItem(_('_Open Link'))
                copy_menu = gtk.MenuItem(_('Copy _Link Address'))

            copy_menu.connect('activate', self._copy_url_cb, url, flavor)
            copy_menu.show()
            menu.prepend(copy_menu)
            
            open_menu.connect('activate', self._open_url_cb, url, flavor)
            open_menu.show()
            menu.prepend(open_menu)

    # private methods
    
    def _connect_signals(self):
        """Connect to several signals of the super class gtk.TextView."""
        self.connect('key-press-event', self.on_key_press_event)
        self.connect('insert-at-cursor', self.on_insert_at_cursor)
        self.connect('delete-from-cursor', self.on_delete_from_cursor)
        self.connect('paste-clipboard', self.on_paste_clipboard)
        self.connect('motion-notify-event', self.on_motion_notify_event)
        self.connect('button-press-event', self.on_button_press_event)
        self.connect('populate-popup', self.on_populate_popup)
        self.connect('unrealize', self.on_unrealize)
        
    def _create_toolbar(self):
        """Create a formatting toolbar.
        
        @returns: toolbar containing text formatting toolitems.
        @returntype: gtk.Toolbar
        
        """
        # define the actions...
        # ...first the toggle actions, which have a ToggleToolButton as proxy
        format_toggle_actions = [
            (str(StyledTextTagType.ITALIC), gtk.STOCK_ITALIC, None, None,
             _('Italic'), self._on_toggle_action_activate),
            (str(StyledTextTagType.BOLD), gtk.STOCK_BOLD, None, None,
             _('Bold'), self._on_toggle_action_activate),
            (str(StyledTextTagType.UNDERLINE), gtk.STOCK_UNDERLINE, None, None,
             _('Underline'), self._on_toggle_action_activate),
        ]
        
        self.toggle_actions = [action[0] for action in format_toggle_actions]

        # ...then the normal actions, which have a ToolButton as proxy
        format_actions = [
            (str(StyledTextTagType.FONTCOLOR), 'gramps-font-color', None, None,
             _('Font Color'), self._on_action_activate),
            (str(StyledTextTagType.HIGHLIGHT), 'gramps-font-bgcolor', None, None,
             _('Background Color'), self._on_action_activate),
            ('clear', gtk.STOCK_CLEAR, None, None,
             _('Clear Markup'), self._format_clear_cb),
        ]
        
        # ...last the custom actions, which have custom proxies
        fontface_action = ComboToolAction(str(StyledTextTagType.FONTFACE),
                                          _("Font family"),
                                          _("Font family"), None)
        fontsize_action = ComboToolAction(str(StyledTextTagType.FONTSIZE),
                                          _("Font size"),
                                          _("Font size"), None)
        spring = SpringSeparatorAction("spring", "", "", None)
        
        # action accelerators
        self.action_accels = {
            '<Control>i': 'italic',
            '<Control>b': 'bold',
            '<Control>u': 'underline',
        }

        # create the action group and insert all the actions
        self.action_group = gtk.ActionGroup('Format')
        self.action_group.add_toggle_actions(format_toggle_actions)
        self.action_group.add_actions(format_actions)
        self.action_group.add_action(fontface_action)
        self.action_group.add_action(fontsize_action)
        self.action_group.add_action(spring)

        # define the toolbar and create the proxies via ensure_update()
        uimanager = gtk.UIManager()
        uimanager.insert_action_group(self.action_group, 0)
        uimanager.add_ui_from_string(FORMAT_TOOLBAR)
        uimanager.ensure_update()
        
        # now that widget is created for the custom actions set them up
        fontface = uimanager.get_widget('/ToolBar/%d' %
                                        StyledTextTagType.FONTFACE)
        set_fontface_toolitem(fontface, self._on_combotoolitem_changed)

        fontsize = uimanager.get_widget('/ToolBar/%d' %
                                        StyledTextTagType.FONTSIZE)
        set_fontsize_toolitem(fontsize, self._on_combotoolitem_changed)

        # get the toolbar and set it's style
        toolbar = uimanager.get_widget('/ToolBar')      
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        
        return toolbar
        
    def _init_url_match(self):
        """Setup regexp matching for URL match."""
        self.textbuffer.create_tag('hyperlink',
                                   underline=UNDERLINE_SINGLE,
                                   foreground='blue')
        self.textbuffer.match_add("(www|ftp)[" + HOSTCHARS + "]*\\.[" +
                                  HOSTCHARS + ".]+" + "(:[0-9]+)?(" +
                                  URLPATH + ")?/?", HTTP)
        self.textbuffer.match_add("(mailto:)?[a-z0-9][a-z0-9.-]*@[a-z0-9]"
                                  "[a-z0-9-]*(\\.[a-z0-9][a-z0-9-]*)+", MAIL)
        self.textbuffer.match_add(SCHEME + "//(" + USER + "@)?[" +
                                  HOSTCHARS + ".]+" + "(:[0-9]+)?(" +
                                  URLPATH + ")?/?", GENURL)
        
    def _create_spell_menu(self):
        """Create a menu with all the installed languages.
        
        It is called each time the popup menu is opened. Each language
        forms a radio menu item, and the selected language is set as active.
        
        @returns: menu containing all the installed languages.
        @returntype: gtk.Menu
        
        """
        active_language = self.spellcheck.get_active_language()

        menu = gtk.Menu()
        group = None
        for lang in self.spellcheck.get_all_languages():
            menuitem = gtk.RadioMenuItem(group, lang)
            menuitem.set_active(lang == active_language)
            menuitem.connect('activate', self._spell_change_cb, lang)
            menu.append(menuitem)
            
            if group is None:
                group = menuitem
            
        return menu

    # Callback functions
    
    def _on_toggle_action_activate(self, action):
        """Toggle a style.
        
        Toggle styles are e.g. 'bold', 'italic', 'underline'.
        
        """
        if self._internal_style_change:
            return

        style = int(action.get_name())
        value = action.get_active()
        _LOG.debug("applying style '%d' with value '%s'" % (style, str(value)))
        self.textbuffer.apply_style(style, value)

    def _on_action_activate(self, action):
        """Apply a format."""
        style = int(action.get_name())
        current_value = self.textbuffer.get_style_at_cursor(style)

        if style == StyledTextTagType.FONTCOLOR:
            color_selection = gtk.ColorSelectionDialog(_("Select font color"))
        elif style == StyledTextTagType.HIGHLIGHT:
            color_selection = gtk.ColorSelectionDialog(_("Select "
                                                         "background color"))
        else:
            _LOG.debug("unknown style: '%d'" % style)
            return

        if current_value:
            color_selection.colorsel.set_current_color(
                hex_to_color(current_value))

        response = color_selection.run()
        color = color_selection.colorsel.get_current_color()
        value = color_to_hex(color)
        color_selection.destroy()
        
        if response == gtk.RESPONSE_OK:
            _LOG.debug("applying style '%d' with value '%s'" %
                       (style, str(value)))
            self.textbuffer.apply_style(style, value)

    def _on_combotoolitem_changed(self, combobox, style):
        if self._internal_style_change:
            return
        
        value = StyledTextTagType.STYLE_TYPE[style](combobox.get_active_text())
        _LOG.debug("applying style '%d' with value '%s'" % (style, str(value)))
        self.textbuffer.apply_style(style, value)

    def _format_clear_cb(self, action):
        """Remove all formats from the selection.
        
        Remove only our own tags without touching other ones (e.g. gtk.Spell),
        thus remove_all_tags() can not be used.
        
        """
        for style in ALLOWED_STYLES:
            self.textbuffer.remove_style(style)

    def _on_buffer_style_changed(self, buffer, changed_styles):
        # set state of toggle action
        for style in changed_styles.keys():
            if str(style) in self.toggle_actions:
                action = self.action_group.get_action(str(style))
                self._internal_style_change = True
                action.set_active(changed_styles[style])
                self._internal_style_change = False
            
            if ((style == StyledTextTagType.FONTFACE) or
                (style == StyledTextTagType.FONTSIZE)):
                
                action = self.action_group.get_action(str(style))
                combo = action.get_proxies()[0].child
                model = combo.get_model()
                iter = model.get_iter_first()
                while iter:
                    if (StyledTextTagType.STYLE_TYPE[style](
                        model.get_value(iter, 0)) == changed_styles[style]):
                        break
                    iter = model.iter_next(iter)

                self._internal_style_change = True
                if iter is None:
                    combo.child.set_text(str(changed_styles[style]))
                    if style == StyledTextTagType.FONTFACE:
                        _LOG.debug('font family "%s" is not installed' %
                                   changed_styles[style])
                else:
                    combo.set_active_iter(iter)
                self._internal_style_change = False
            
    def _spell_change_cb(self, menuitem, language):
        """Set spell checker language according to user selection."""
        self.spellcheck.set_active_language(language)

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
        else:
            return
        
        display_url(url)
    
    def _copy_url_cb(self, menuitem, url, flavor):
        """Copy url to both useful selections."""
        clipboard = gtk.Clipboard(selection="CLIPBOARD")
        clipboard.set_text(url)
        
        clipboard = gtk.Clipboard(selection="PRIMARY")
        clipboard.set_text(url)
    
    # public methods
    
    def set_text(self, text):
        """Set the text of the text buffer of the editor.
        
        @param text: formatted text to edit in the view.
        @type text: L{StyledText}
        
        """
        self.textbuffer.set_text(text)
        self.textbuffer.place_cursor(self.textbuffer.get_start_iter())

    def get_text(self):
        """Get the text of the text buffer of the editor.
        
        @returns: the formatted text from the editor.
        @returntype: L{StyledText}
        
        """
        return self.textbuffer.get_text()
    
    def get_toolbar(self):
        """Get the formatting toolbar of the editor.
        
        @returns: toolbar widget to use as formatting GUI.
        @returntype: gtk.Toolbar
        
        """
        return self.toolbar

#-------------------------------------------------------------------------
#
# ComboToolItem class
#
#-------------------------------------------------------------------------
class ComboToolItem(gtk.ToolItem):
    
    __gtype_name__ = "ComboToolItem"
    
    def __init__(self):
        gtk.ToolItem.__init__(self)
        
        self.set_border_width(2)
        self.set_homogeneous(False)
        self.set_expand(False)
        
        self.combobox = gtk.combo_box_entry_new_text()
        self.combobox.show()
        self.add(self.combobox)
        
    def set_entry_editable(self, editable):
        self.combobox.child.set_editable(editable)

#-------------------------------------------------------------------------
#
# ComboToolAction class
#
#-------------------------------------------------------------------------
class ComboToolAction(gtk.Action):
    
    __gtype_name__ = "ComboToolAction"
    
    def __init__(self, name, label, tooltip, stock_id):
        gtk.Action.__init__(self, name, label, tooltip, stock_id)
        ##self.set_tool_item_type(ComboToolItem)
        
    ##def create_tool_item(self):
        ##combobox = ComboToolButton()
        ###self.connect_proxy(combobox)
        ##return combobox
        
    ##def connect_proxy(self, proxy):
        ##gtk.Action.connect_proxy(self, proxy)
        
        ##if isinstance(proxy, ComboToolButton):
            ##proxy.combobox.connect('changed', self.changed)

    ##def changed(self, combobox):
        ##self.activate()
ComboToolAction.set_tool_item_type(ComboToolItem)

#-------------------------------------------------------------------------
#
# SpringSeparatorToolItem class
#
#-------------------------------------------------------------------------
class SpringSeparatorToolItem(gtk.SeparatorToolItem):
    
    __gtype_name__ = "SpringSeparatorToolItem"
    
    def __init__(self):
        gtk.SeparatorToolItem.__init__(self)
        
        self.set_draw(False)
        self.set_expand(True)
        
#-------------------------------------------------------------------------
#
# SpringSeparatorAction class
#
#-------------------------------------------------------------------------
class SpringSeparatorAction(gtk.Action):
    
    __gtype_name__ = "SpringSeparatorAction"
    
    def __init__(self, name, label, tooltip, stock_id):
        gtk.Action.__init__(self, name, label, tooltip, stock_id)

SpringSeparatorAction.set_tool_item_type(SpringSeparatorToolItem)

#-------------------------------------------------------------------------
#
# Module functions
#
#-------------------------------------------------------------------------
def set_fontface_toolitem(combotoolitem, callback):
    """Setup font family comboboxentry."""
    combotoolitem.set_entry_editable(False)

    fontface = combotoolitem.child

    families = [family.get_name()
                for family in fontface.get_pango_context().list_families()]
    families.sort()
    for family in families:
        fontface.append_text(family)
            
    try:
        def_fam = StyledTextTagType.STYLE_DEFAULT[StyledTextTagType.FONTFACE]
        default = families.index(def_fam)
    except ValueError:
        default = 0
    fontface.set_active(default)

    fontface.connect('changed', callback, StyledTextTagType.FONTFACE)
    
def set_fontsize_toolitem(combotoolitem, callback):
    """Setup font size comboboxentry."""
    combotoolitem.set_size_request(60, -1)

    fontsize = combotoolitem.child

    for size in FONT_SIZES:
        fontsize.append_text(str(size))
        
    try:
        def_size = StyledTextTagType.STYLE_DEFAULT[StyledTextTagType.FONTSIZE]
        default = FONT_SIZES.index(def_size)
    except ValueError:
        default = 0
    fontsize.set_active(default)
    
    fontsize.connect('changed', callback, StyledTextTagType.FONTSIZE)

def color_to_hex(color):
    """Convert gtk.gdk.Color to hex string."""
    hexstring = ""
    for col in 'red', 'green', 'blue':
        hexfrag = hex(getattr(color, col) / (16 * 16)).split("x")[1]
        if len(hexfrag) < 2:
            hexfrag = "0" + hexfrag
        hexstring += hexfrag
    return '#' + hexstring
    
def hex_to_color(hex):
    """Convert hex string to gtk.gdk.Color."""
    color = gtk.gdk.color_parse(hex)
    return color
