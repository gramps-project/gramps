#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
from pango import WEIGHT_BOLD, STYLE_ITALIC, UNDERLINE_SINGLE

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import const
import Spell
import Config
import GrampsDisplay
import MarkupText
from _EditPrimary import EditPrimary
from GrampsWidgets import *
from RelLib import Note

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
USERCHARS = "-A-Za-z0-9"
PASSCHARS = "-A-Za-z0-9,?;.:/!%$^*&~\"#'"
HOSTCHARS = "-A-Za-z0-9"
PATHCHARS = "-A-Za-z0-9_$.+!*(),;:@&=?/~#%"
#SCHEME = "(news:|telnet:|nntp:|file:/|https?:|ftps?:|webcal:)"
SCHEME = "(file:/|https?:|ftps?:|webcal:)"
USER = "[" + USERCHARS + "]+(:[" + PASSCHARS + "]+)?"
URLPATH = "/[" + PATHCHARS + "]*[^]'.}>) \t\r\n,\\\"]"

(GENERAL, HTTP, MAIL) = range(3)

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------
class EditNote(EditPrimary):
    hand_cursor = gtk.gdk.Cursor(gtk.gdk.HAND2)
    regular_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)

    def __init__(self, state, uistate, track, note, callback=None
                     , callertitle = None, extratype = None):
        """Create an EditNote window. Associate a note with the window.
        
        @param callertitle: a text passed by calling object to add to title 
        @type callertitle: str
        @param extratype: extra NoteType values to add to the default types 
            They are removed from the ignorelist of NoteType.
        @type extratype: list of int
        """
        self.callertitle = callertitle
        self.extratype = extratype
        EditPrimary.__init__(self, state, uistate, track, note, 
                             state.db.get_note_from_handle, callback)

    def empty_object(self):
        """Return an empty Note object for comparison for changes.
        
        It is used by the base class (EditPrimary).
        
        """
        return Note()

    def get_menu_title(self):
        if self.obj.get_handle():
            if self.callertitle :
                title = _('Note: %(id)s - %(context)s') % {
                                        'id'      : self.obj.get_gramps_id(),
                                        'context' : self.callertitle
                                        }
            else :
                title = _('Note: %s') % self.obj.get_gramps_id()
        else:
            if self.callertitle :
                title = _('New Note - %(context)s') % {
                                        'context' : self.callertitle
                                        }
            else :
                title = _('New Note')  
            
        return title
    
    def get_custom_notetypes(self):
        return self.dbstate.db.get_note_types()

    def _local_init(self):
        """Local initialization function.
        
        Perform basic initialization, including setting up widgets
        and the glade interface. It is called by the base class (EditPrimary),
        and overridden here.
        
        """
        self.top = gtk.glade.XML(const.GLADE_FILE, "edit_note", "gramps")
        win = self.top.get_widget("edit_note")
        self.set_window(win, None, self.get_menu_title())

        width = Config.get(Config.NOTE_WIDTH)
        height = Config.get(Config.NOTE_HEIGHT)
        self.window.set_default_size(width, height)

        settings = gtk.settings_get_default()
        self.show_unicode = settings.get_property('gtk-show-unicode-menu')
        settings.set_property('gtk-show-unicode-menu', False)
        
        self.build_interface()
        
    def _setup_fields(self):
        """Get control widgets and attached them to Note's attributes."""
        self.type_selector = MonitoredDataType(
            self.top.get_widget('type'),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            custom_values=self.get_custom_notetypes(),
            ignore_values=self.obj.get_type().get_ignore_list(self.extratype))

        self.check = MonitoredCheckbox(
            self.obj,
            self.top.get_widget('format'),
            self.obj.set_format,
            self.obj.get_format,
            on_toggle = self.flow_changed,
            readonly = self.db.readonly)
        
        self.gid = MonitoredEntry(
            self.top.get_widget('id'),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        self.marker = MonitoredDataType(
            self.top.get_widget('marker'), 
            self.obj.set_marker, 
            self.obj.get_marker, 
            self.db.readonly,
            self.db.get_marker_types())

        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj, self.db.readonly)
        
    def _connect_signals(self):
        """Connects any signals that need to be connected.
        
        Called by the init routine of the base class (_EditPrimary).
        
        """
        self.define_ok_button(self.top.get_widget('ok'),self.save)
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'), '')
        
    def build_interface(self):
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

        buffer = MarkupText.MarkupBuffer()
        buffer.create_tag('hyperlink',
                          underline=UNDERLINE_SINGLE,
                          foreground='blue')
        buffer.match_add("(www|ftp)[" + HOSTCHARS + "]*\\.[" + HOSTCHARS +
                         ".]+" + "(:[0-9]+)?(" + URLPATH + ")?/?", HTTP)
        buffer.match_add("(mailto:)?[a-z0-9][a-z0-9.-]*@[a-z0-9][a-z0-9-]*"
                         "(\\.[a-z0-9][a-z0-9-]*)+", MAIL)
        buffer.match_add(SCHEME + "//(" + USER + "@)?[" + HOSTCHARS + ".]+" +
                             "(:[0-9]+)?(" + URLPATH + ")?/?", GENERAL)
        self.match = None
        self.last_match = None

        self.text = self.top.get_widget('text')
        self.text.set_editable(not self.dbstate.db.readonly)
        self.text.set_buffer(buffer)
        self.text.connect('key-press-event',
                          self.on_textview_key_press_event)
        self.text.connect('insert-at-cursor',
                          self.on_textview_insert_at_cursor)
        self.text.connect('delete-from-cursor',
                          self.on_textview_delete_from_cursor)
        self.text.connect('paste-clipboard',
                          self.on_textview_paste_clipboard)
        self.text.connect('motion-notify-event',
                          self.on_textview_motion_notify_event)
        self.text.connect('button-press-event',
                          self.on_textview_button_press_event)
        self.text.connect('populate-popup',
                          self.on_textview_populate_popup)
        
        # setup spell checking interface
        spellcheck = Spell.Spell(self.text)
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        cell = gtk.CellRendererText()
        lang_selector = self.top.get_widget('spell')
        lang_selector.set_model(liststore)
        lang_selector.pack_start(cell, True)
        lang_selector.add_attribute(cell, 'text', 0)
        act_lang = spellcheck.get_active_language()
        idx = 0
        for lang in spellcheck.get_all_languages():
            lang_selector.append_text(lang)
            if lang == act_lang:
                act_idx = idx
            idx = idx + 1
        lang_selector.set_active(act_idx)
        lang_selector.connect('changed', self.on_spell_change, spellcheck)
        #lang_selector.set_sensitive(Config.get(Config.SPELLCHECK))

        # create a formatting toolbar
        if not self.dbstate.db.readonly:
            uimanager = gtk.UIManager()
            uimanager.insert_action_group(buffer.format_action_group, 0)
            uimanager.add_ui_from_string(FORMAT_TOOLBAR)
            uimanager.ensure_update()

            toolbar = uimanager.get_widget('/ToolBar')      
            toolbar.set_style(gtk.TOOLBAR_ICONS)
            vbox = self.top.get_widget('container')
            vbox.pack_start(toolbar)
                
        # setup initial values for textview and buffer
        if self.obj:
            self.empty = False
            self.flow_changed(self.obj.get_format())
            buffer.set_text(self.obj.get(markup=True))
            log.debug("Initial Note: %s" % buffer.get_text())
        else:
            self.empty = True
            
    def build_menu_names(self, person):
        """
        Provides the information needed by the base class to define the
        window management menu entries.
        """
        return (_('Edit Note'), self.get_menu_title())

    def on_textview_key_press_event(self, textview, event):
        """Handle shortcuts in the TextView."""
        return textview.get_buffer().on_key_press_event(textview, event)
    
    def on_textview_insert_at_cursor(self, textview, string):
        log.debug("Textview insert '%s'" % string)
        
    def on_textview_delete_from_cursor(self, textview, type, count):
        log.debug("Textview delete type %d count %d" % (type, count))
        
    def on_textview_paste_clipboard(self, textview):
        log.debug("Textview paste clipboard")
    
    def on_textview_motion_notify_event(self, textview, event):
        window = textview.get_window(gtk.TEXT_WINDOW_TEXT)
        x, y = textview.window_to_buffer_coords(gtk.TEXT_WINDOW_WIDGET,
                                                int(event.x), int(event.y))
        iter = textview.get_iter_at_location(x, y)
        buffer = textview.get_buffer()
        self.match = buffer.match_check(iter.get_offset())
        
        if self.match != self.last_match:
            start, end = buffer.get_bounds()
            buffer.remove_tag_by_name('hyperlink', start, end)
            if self.match:
                start_offset = self.match[MarkupText.MATCH_START]
                end_offset = self.match[MarkupText.MATCH_END]
                
                start = buffer.get_iter_at_offset(start_offset)
                end = buffer.get_iter_at_offset(end_offset)

                buffer.apply_tag_by_name('hyperlink', start, end)
                window.set_cursor(self.hand_cursor)
            else:
                window.set_cursor(self.regular_cursor)

        self.last_match = self.match
        
        textview.window.get_pointer()
        return False

    def on_textview_button_press_event(self, textview, event):
        if ((event.type == gtk.gdk.BUTTON_PRESS) and
            (event.button == 1) and
            (event.state and gtk.gdk.CONTROL_MASK) and
            (self.match)):
            
            flavor = self.match[MarkupText.MATCH_FLAVOR]
            url = self.match[MarkupText.MATCH_STRING]
            self.open_url_cb(None, url, flavor)
            
        return False
        
    def on_textview_populate_popup(self, textview, menu):
        """Insert extra menuitems according to matched pattern."""
        if self.match:
            flavor = self.match[MarkupText.MATCH_FLAVOR]
            url = self.match[MarkupText.MATCH_STRING]
            
            if flavor == MAIL:
                open_menu = gtk.MenuItem(_('_Send Mail To...'))
                copy_menu = gtk.MenuItem(_('Copy _E-mail Address'))
            else:
                open_menu = gtk.MenuItem(_('_Open Link'))
                copy_menu = gtk.MenuItem(_('Copy _Link Address'))

            copy_menu.connect('activate', self.copy_url_cb, url, flavor)
            copy_menu.show()
            menu.prepend(copy_menu)
            
            open_menu.connect('activate', self.open_url_cb, url, flavor)
            open_menu.show()
            menu.prepend(open_menu)

    def on_spell_change(self, combobox, spell):
        """Set spell checker language according to user selection."""
        lang = combobox.get_active_text()
        spell.set_active_language(lang)
        
    def open_url_cb(self, menuitem, url, flavor):
        if not url:
            return
        
        if flavor == HTTP:
            url = 'http:' + url
        elif flavor == MAIL:
            if not url.startswith('mailto:'):
                url = 'mailto:' + url
        elif flavor == GENERAL:
            pass
        else:
            return
        
        GrampsDisplay.url(url)
    
    def copy_url_cb(self, menuitem, url, flavor):
        """Copy url to both useful selections."""
        clipboard = gtk.Clipboard(selection="CLIPBOARD")
        clipboard.set_text(url)
        
        clipboard = gtk.Clipboard(selection="PRIMARY")
        clipboard.set_text(url)
    
    def update_note(self):
        """Update the Note object with current value."""
        if self.obj:
            buffer = self.text.get_buffer()
            (start, stop) = buffer.get_bounds()
            text = buffer.get_text(start, stop)
            self.obj.set(text)
            log.debug(text)

    def flow_changed(self, active):
        if active:
            self.text.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self.text.set_wrap_mode(gtk.WRAP_WORD)

    def save(self, *obj):
        """Save the data."""
        trans = self.db.transaction_begin()

        self.update_note()

        if self.obj.get_handle():
            self.db.commit_note(self.obj,trans)
        else:
            self.db.add_note(self.obj,trans)
        self.db.transaction_commit(trans, _("Edit Note"))
        
        if self.callback:
            self.callback(self.obj.get_handle())
        self.close()

    def _cleanup_on_exit(self):
        (width, height) = self.window.get_size()
        Config.set(Config.NOTE_WIDTH, width)
        Config.set(Config.NOTE_HEIGHT, height)
        Config.sync()

        settings = gtk.settings_get_default()
        settings.set_property('gtk-show-unicode-menu', self.show_unicode)


class DeleteNoteQuery:
    def __init__(self, dbstate, uistate, note, the_lists):
        self.note = note
        self.db = dbstate.db
        self.uistate = uistate
        self.the_lists = the_lists

    def query_response(self):
        trans = self.db.transaction_begin()
        self.db.disable_signals()
        
        (person_list, family_list, event_list, place_list, source_list,
         media_list, repo_list) = self.the_lists

        note_handle = self.note.get_handle()

        for handle in person_list:
            person = self.db.get_person_from_handle(handle)
            person.remove_note(note_handle)
            self.db.commit_person(person,trans)

        for handle in family_list:
            family = self.db.get_family_from_handle(handle)
            family.remove_note(note_handle)
            self.db.commit_family(family,trans)

        for handle in event_list:
            event = self.db.get_event_from_handle(handle)
            event.remove_note(note_handle)
            self.db.commit_event(event,trans)

        for handle in place_list:
            place = self.db.get_place_from_handle(handle)
            place.remove_note(note_handle)
            self.db.commit_place(place,trans)

        for handle in source_list:
            source = self.db.get_source_from_handle(handle)
            source.remove_note(note_handle)
            self.db.commit_source(source,trans)

        for handle in media_list:
            media = self.db.get_object_from_handle(handle)
            media.remove_note(note_handle)
            self.db.commit_media_object(media,trans)

        for handle in repo_list:
            repo = self.db.get_repository_from_handle(handle)
            repo.remove_note(note_handle)
            self.db.commit_repository(repo,trans)

        self.db.enable_signals()
        self.db.remove_note(note_handle, trans)
        self.db.transaction_commit(
            trans,_("Delete Note (%s)") % self.note.get_gramps_id())
