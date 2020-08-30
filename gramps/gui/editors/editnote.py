#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2011       Tim G L Lyons
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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".gui.editors.EditNote")

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.config import config
from .editprimary import EditPrimary
from .displaytabs import GrampsTab, NoteBackRefList
from ..widgets import (MonitoredDataType, MonitoredCheckbox,
                         MonitoredEntry, PrivacyButton, MonitoredTagList)
from gramps.gen.lib import Note
from gramps.gen.db import DbTxn
from ..dialog import ErrorDialog
from ..glade import Glade
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _('Editing_information_about_notes', 'manual')

#-------------------------------------------------------------------------
#
# NoteTab
#
#-------------------------------------------------------------------------

class NoteTab(GrampsTab):
    """
    This class provides the tabpage of the note
    """

    def __init__(self, dbstate, uistate, track, name, widget):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: L{DbState.DbState}
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: L{DisplayState.DisplayState}
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        @param widget: widget to be shown in the tab
        @type widget: gtk widget
        """
        GrampsTab.__init__(self, dbstate, uistate, track, name)
        eventbox = Gtk.EventBox()
        eventbox.add(widget)
        self.pack_start(eventbox, True, True, 0)
        self._set_label(show_image=False)
        eventbox.connect('key_press_event', self.key_pressed)
        self.show_all()

    def is_empty(self):
        """
        Override base class
        """
        return False

#-------------------------------------------------------------------------
#
# EditNote
#
#-------------------------------------------------------------------------

class EditNote(EditPrimary):
    def __init__(self, dbstate, uistate, track, note, callback=None,
                 callertitle = None, extratype = None):
        """Create an EditNote window. Associate a note with the window.

        @param callertitle: Text passed by calling object to add to title
        @type callertitle: str
        @param extratype: Extra L{NoteType} values to add to the default types.
        They are removed from the ignorelist of L{NoteType}.
        @type extratype: list of int

        """
        self.callertitle = callertitle
        self.extratype = extratype
        EditPrimary.__init__(self, dbstate, uistate, track, note,
                             dbstate.db.get_note_from_handle,
                             dbstate.db.get_note_from_gramps_id, callback)

    def empty_object(self):
        """Return an empty Note object for comparison for changes.

        It is used by the base class L{EditPrimary}.

        """
        empty_note = Note();
        if self.extratype:
            empty_note.set_type(self.extratype[0])
        return empty_note

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
        and the glade interface. It is called by the base class L{EditPrimary},
        and overridden here.

        """
        self.top = Glade()

        win = self.top.toplevel
        self.set_window(win, None, self.get_menu_title())
        self.setup_configs('interface.note', 700, 500)

        vboxnote = self.top.get_object('vbox131')
        notebook = self.top.get_object('note_notebook')
        #recreate start page as GrampsTab
        notebook.remove_page(0)
        self.ntab = NoteTab(self.dbstate, self.uistate, self.track,
                              _('_Note'), vboxnote)
        self.track_ref_for_deletion("ntab")

        self.build_interface()

    def _setup_fields(self):
        """Get control widgets and attach them to Note's attributes."""
        self.type_selector = MonitoredDataType(
            self.top.get_object('type'),
            self.obj.set_type,
            self.obj.get_type,
            self.db.readonly,
            custom_values=self.get_custom_notetypes(),
            ignore_values=self.obj.get_type().get_ignore_list(self.extratype))

        self.check = MonitoredCheckbox(
            self.obj,
            self.top.get_object('format'),
            self.obj.set_format,
            self.obj.get_format,
            readonly = self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_object('id'),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)

        self.tags = MonitoredTagList(
            self.top.get_object("tag_label"),
            self.top.get_object("tag_button"),
            self.obj.set_tag_list,
            self.obj.get_tag_list,
            self.db,
            self.uistate, self.track,
            self.db.readonly)

        self.priv = PrivacyButton(
            self.top.get_object("private"),
            self.obj, self.db.readonly)

    def _connect_signals(self):
        """Connects any signals that need to be connected.

        Called by the init routine of the base class L{EditPrimary}.

        """
        self.define_ok_button(self.top.get_object('ok'), self.save)
        self.define_cancel_button(self.top.get_object('cancel'))
        self.define_help_button(self.top.get_object('help'),
                WIKI_HELP_PAGE, WIKI_HELP_SEC)

    def _connect_db_signals(self):
        """
        Connect any signals that need to be connected.
        Called by the init routine of the base class (_EditPrimary).
        """
        self._add_db_signal('note-rebuild', self._do_close)
        self._add_db_signal('note-delete', self.check_for_close)

    def _create_tabbed_pages(self):
        """Create the notebook tabs and inserts them into the main window."""
        notebook = self.top.get_object("note_notebook")

        self._add_tab(notebook, self.ntab)

        handles = self.dbstate.db.find_backlink_handles(self.obj.handle)
        self.rlist = NoteBackRefList(self.dbstate,
                                     self.uistate,
                                     self.track,
                                     handles)
        self.backref_tab = self._add_tab(notebook, self.rlist)
        self.track_ref_for_deletion("rlist")
        self.track_ref_for_deletion("backref_tab")

        self._setup_notebook_tabs(notebook)

    def build_interface(self):
        self.texteditor = self.top.get_object('texteditor')
        self.texteditor.set_editable(not self.dbstate.db.readonly)
        self.texteditor.set_wrap_mode(Gtk.WrapMode.WORD)

        # create a formatting toolbar
        if not self.dbstate.db.readonly:
            vbox = self.top.get_object('container')
            toolbar, self.action_group = self.texteditor.create_toolbar(
                self.uistate.uimanager, self.window)
            vbox.pack_start(toolbar, False, False, 0)
            self.texteditor.set_transient_parent(self.window)

        # setup initial values for textview and textbuffer
        if self.obj:
            self.empty = False
            with self.texteditor.undo_disabled():
                self.texteditor.set_text(self.obj.get_styledtext())
            # Reset the undoable buffer:
            self.texteditor.reset()
            _LOG.debug("Initial Note: %s" % str(self.texteditor.get_text()))
        else:
            self.empty = True

    def build_menu_names(self, person):
        """
        Provide the information needed by the base class to define the
        window management menu entries.
        """
        return (_('Edit Note'), self.get_menu_title())

    def _post_init(self):
        self.texteditor.grab_focus()

    def update_note(self):
        """Update the Note object with current value."""
        if self.obj:
            text = self.texteditor.get_text()
            self.obj.set_styledtext(text)
            _LOG.debug(str(text))

    def close(self, *obj):
        """Called when cancel button clicked."""
        self.update_note()
        super().close()

    def save(self, *obj):
        """Save the data."""
        self.ok_button.set_sensitive(False)

        self.update_note()

        if self.object_is_empty():
            ErrorDialog(_("Cannot save note"),
                        _("No data exists for this note. Please "
                          "enter data or cancel the edit."),
                        parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        (uses_dupe_id, id) = self._uses_duplicate_id()
        if uses_dupe_id:
            msg1 = _("Cannot save note. ID already exists.")
            msg2 = _("You have attempted to use the existing Gramps ID with "
                         "value %(id)s. This value is already used. Please "
                         "enter a different ID or leave "
                         "blank to get the next available ID value.") % {
                         'id' : id }
            ErrorDialog(msg1, msg2, parent=self.window)
            self.ok_button.set_sensitive(True)
            return

        if not self.obj.handle:
            with DbTxn(_("Add Note"),
                       self.db) as trans:
                self.db.add_note(self.obj, trans)
        else:
            if self.data_has_changed():
                with DbTxn(_("Edit Note"),
                           self.db) as trans:
                    if not self.obj.get_gramps_id():
                        self.obj.set_gramps_id(self.db.find_next_note_gramps_id())
                    self.db.commit_note(self.obj, trans)

        self._do_close()
        if self.callback:
            self.callback(self.obj.get_handle())

class DeleteNoteQuery:
    def __init__(self, dbstate, uistate, note, the_lists):
        self.note = note
        self.db = dbstate.db
        self.uistate = uistate
        self.the_lists = the_lists

    def query_response(self):
        with DbTxn(_("Delete Note (%s)") % self.note.get_gramps_id(),
                   self.db) as trans:
            self.db.disable_signals()

            (person_list, family_list, event_list, place_list, source_list,
             citation_list, media_list, repo_list) = self.the_lists

            note_handle = self.note.get_handle()

            for handle in person_list:
                person = self.db.get_person_from_handle(handle)
                if person:
                    person.remove_note(note_handle)
                    self.db.commit_person(person, trans)

            for handle in family_list:
                family = self.db.get_family_from_handle(handle)
                if family:
                    family.remove_note(note_handle)
                    self.db.commit_family(family, trans)

            for handle in event_list:
                event = self.db.get_event_from_handle(handle)
                if event:
                    event.remove_note(note_handle)
                    self.db.commit_event(event, trans)

            for handle in place_list:
                place = self.db.get_place_from_handle(handle)
                if place:
                    place.remove_note(note_handle)
                    self.db.commit_place(place, trans)

            for handle in source_list:
                source = self.db.get_source_from_handle(handle)
                if source:
                    source.remove_note(note_handle)
                    self.db.commit_source(source, trans)

            for handle in citation_list:
                citation = self.db.get_citation_from_handle(handle)
                if citation:
                    citation.remove_note(note_handle)
                    self.db.commit_citation(citation, trans)

            for handle in media_list:
                media = self.db.get_media_from_handle(handle)
                if media:
                    media.remove_note(note_handle)
                    self.db.commit_media(media, trans)

            for handle in repo_list:
                repo = self.db.get_repository_from_handle(handle)
                if repo:
                    repo.remove_note(note_handle)
                    self.db.commit_repository(repo, trans)

            self.db.enable_signals()
            self.db.remove_note(note_handle, trans)
