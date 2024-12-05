# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
# Copyright (C) 2011 Tim G L Lyons
# Copyright (C) 2020 Matthias Kemmer
# Copyright (C) 2024-2025 Steve Youngs
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

# ------------------------------------------------------------------------
#
# Gtk
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.editors import EditNote
from gramps.gui.widgets.styledtexteditor import StyledTextEditor
from gramps.gui.widgets import SimpleButton
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import StyledText
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class Notes(Gramplet):
    """
    Displays the notes for an object.
    """

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        hbox = Gtk.Box()
        self.left = SimpleButton("go-previous", self.left_clicked)
        self.left.set_sensitive(False)
        hbox.pack_start(self.left, False, False, 0)
        self.right = SimpleButton("go-next", self.right_clicked)
        self.right.set_sensitive(False)
        hbox.pack_start(self.right, False, False, 0)
        self.edit = SimpleButton("gtk-edit", self.edit_clicked)
        self.edit.set_sensitive(False)
        hbox.pack_start(self.edit, False, False, 0)
        self.page = Gtk.Label()
        self.page.set_halign(Gtk.Align.START)
        hbox.pack_start(self.page, True, True, 10)
        self.ntype = Gtk.Label()
        hbox.pack_start(self.ntype, False, False, 10)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.texteditor = StyledTextEditor()
        self.texteditor.set_editable(False)
        self.texteditor.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolledwindow.add(self.texteditor)

        top.pack_start(hbox, False, False, 0)
        top.pack_start(scrolledwindow, True, True, 0)
        top.show_all()
        return top

    def clear_text(self):
        self.left.set_sensitive(False)
        self.right.set_sensitive(False)
        self.edit.set_sensitive(False)
        self.texteditor.set_text(StyledText())
        self.page.set_text("")
        self.current = 0

    def display_note(self):
        """
        Display the current note.
        """
        note_handle = self.note_list[self.current]
        note = self.dbstate.db.get_note_from_handle(note_handle)
        self.texteditor.set_text(note.get_styledtext())
        self.ntype.set_text(str(note.get_type()))
        self.page.set_text(
            _("%(current)d of %(total)d")
            % {"current": self.current + 1, "total": len(self.note_list)}
        )

    def left_clicked(self, button):
        """
        Display the previous note.
        """
        if self.current > 0:
            self.current -= 1
            self.right.set_sensitive(True)
            if self.current == 0:
                self.left.set_sensitive(False)
            self.display_note()

    def right_clicked(self, button):
        """
        Display the next note.
        """
        if self.current < len(self.note_list) - 1:
            self.current += 1
            self.left.set_sensitive(True)
            if self.current == len(self.note_list) - 1:
                self.right.set_sensitive(False)
            self.display_note()

    def edit_clicked(self, button):
        pass

    def get_has_data(self, obj):
        """
        Return True if the gramplet has data, else return False.
        """
        if obj is None:
            return False
        if obj.get_note_list():
            return True
        return False


class NotesOf(Notes):
    def init(self, object_class):
        super().init()
        self.object_class = object_class

    def db_changed(self):
        self.connect(
            self.dbstate.db, "%s-update" % self.object_class.lower(), self.update
        )
        self.connect(
            self.dbstate.db, "%s-delete" % self.object_class.lower(), self.update
        )
        self.connect(self.dbstate.db, "note-add", self.update)
        self.connect(self.dbstate.db, "note-update", self.update)
        self.connect(self.dbstate.db, "note-delete", self.update)

    def active_changed(self, handle):
        self.update()
        self.connect_signal(self.object_class, self.update)

    def get_notes(self, obj):
        """
        Get the note list for the current object.
        """
        self.left.set_sensitive(False)
        self.right.set_sensitive(False)
        self.texteditor.set_text(StyledText())
        self.note_list = obj.get_note_list()
        self.page.set_text("")
        self.ntype.set_text("")
        self.edit.set_sensitive(len(self.note_list) > 0)
        if len(self.note_list) > 0:
            self.set_has_data(True)
            if len(self.note_list) > 1:
                self.right.set_sensitive(True)
            self.current = 0
            self.display_note()
        else:
            self.set_has_data(False)

    def update_has_data(self):
        active_handle = self.get_active(self.object_class)
        if active_handle:
            active = self.dbstate.db.method("get_%s_from_handle", self.object_class)(
                active_handle
            )
            self.set_has_data(self.get_has_data(active))
        else:
            self.set_has_data(False)

    def edit_clicked(self, button):
        """
        Get the selected Note instance and call the EditNote editor with the
        note.

        Called when the Edit button is clicked.
        If the window already exists (WindowActiveError), we ignore it.
        This prevents the dialog from coming up twice on the same object.
        """
        note_handle = self.note_list[self.current]
        note = self.dbstate.db.get_note_from_handle(note_handle)
        try:
            EditNote(self.gui.dbstate, self.gui.uistate, [], note)
        except WindowActiveError:
            pass

    def main(self):
        self.clear_text()
        active_handle = self.get_active(self.object_class)
        if active_handle:
            active = self.dbstate.db.method("get_%s_from_handle", self.object_class)(
                active_handle
            )
            if active:
                self.get_notes(active)
            else:
                self.set_has_data(False)
        else:
            self.set_has_data(False)


class PersonNotes(NotesOf):
    """
    Displays the notes for a person.
    """

    def init(self):
        super().init("Person")

    def db_changed(self):
        self.connect(self.dbstate.db, "person-update", self.update)
        # superclass will call active_changed if the active Person changes
        self.connect(self.dbstate.db, "note-add", self.update)
        self.connect(self.dbstate.db, "note-update", self.update)
        self.connect(self.dbstate.db, "note-delete", self.update)

    def active_changed(self, handle):
        self.update()


class EventNotes(NotesOf):
    """
    Displays the notes for an event.
    """

    def init(self):
        super().init("Event")


class FamilyNotes(NotesOf):
    """
    Displays the notes for a family.
    """

    def init(self):
        super().init("Family")


class PlaceNotes(NotesOf):
    """
    Displays the notes for a place.
    """

    def init(self):
        super().init("Place")


class SourceNotes(NotesOf):
    """
    Displays the notes for a source.
    """

    def init(self):
        super().init("Source")


class CitationNotes(NotesOf):
    """
    Displays the notes for a Citation.
    """

    def init(self):
        super().init("Citation")


class RepositoryNotes(NotesOf):
    """
    Displays the notes for a repository.
    """

    def init(self):
        super().init("Repository")


class MediaNotes(NotesOf):
    """
    Displays the notes for a media object.
    """

    def init(self):
        super().init("Media")


class NoteNotes(Notes):
    """
    Display a single note in NoteView.
    """

    def db_changed(self):
        self.connect(self.dbstate.db, "note-update", self.update)
        self.connect(self.dbstate.db, "note-delete", self.update)
        self.connect_signal("Note", self.update)

    def edit_clicked(self, button):
        """
        Get the selected Note instance and call the EditNote editor with the
        note.

        Called when the Edit button is clicked.
        If the window already exists (WindowActiveError), we ignore it.
        This prevents the dialog from coming up twice on the same object.
        """
        active_handle = self.get_active("Note")
        note = self.dbstate.db.get_note_from_handle(active_handle)
        try:
            EditNote(self.gui.dbstate, self.gui.uistate, [], note)
        except WindowActiveError:
            pass

    def main(self):
        self.clear_text()
        active_handle = self.get_active("Note")
        if active_handle:
            active = self.dbstate.db.get_note_from_handle(active_handle)
            if active:
                self.edit.set_sensitive(True)
                self.texteditor.set_text(active.get_styledtext())
