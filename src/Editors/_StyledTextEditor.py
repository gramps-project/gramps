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
from Editors._StyledTextBuffer import (StyledTextBuffer, MATCH_START,
                                       MATCH_END, MATCH_FLAVOR, MATCH_STRING)
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
  <toolitem action="italic"/>  
  <toolitem action="bold"/>  
  <toolitem action="underline"/>
  <separator/>
  <toolitem action="font"/>
  <toolitem action="foreground"/>
  <toolitem action="background"/>
  <separator/>
  <toolitem action="clear"/>
</toolbar>
</ui>
'''

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
        gtk.TextView.__init__(self, self.textbuffer)

        self.match = None
        self.last_match = None
        self._init_url_match()
        self.url_match = None

        self.toolbar = self._create_toolbar()
        self.spellcheck = Spell(self)

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
        
        Handle shortcuts in the TextView.
        
        """
        return self.get_buffer().on_key_press_event(self, event)
    
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
        
        @returns: toolbar according to L{StyedTextBuffer} formatting
        capabilities.
        @returntype: gtk.Toolbar
        
        """
        uimanager = gtk.UIManager()
        uimanager.insert_action_group(self.textbuffer.format_action_group, 0)
        uimanager.add_ui_from_string(FORMAT_TOOLBAR)
        uimanager.ensure_update()
        
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