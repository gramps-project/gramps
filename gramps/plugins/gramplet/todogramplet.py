# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2013       Nick Hall
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
# Gtk modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gui.widgets.styledtexteditor import StyledTextEditor
from gramps.gui.widgets import SimpleButton
from gramps.gen.lib import StyledText, Note, NoteType
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.utils.db import navigation_label
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class ToDoGramplet(Gramplet):
    """
    Displays all the To Do notes in the database.
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
        self.left = SimpleButton('go-previous', self.left_clicked)
        self.left.set_tooltip_text(_('Previous To Do note'))
        self.left.set_sensitive(False)
        hbox.pack_start(self.left, False, False, 0)
        self.right = SimpleButton('go-next', self.right_clicked)
        self.right.set_tooltip_text(_('Next To Do note'))
        self.right.set_sensitive(False)
        hbox.pack_start(self.right, False, False, 0)
        self.edit = SimpleButton('gtk-edit', self.edit_clicked)
        self.edit.set_tooltip_text(_('Edit the selected To Do note'))
        self.edit.set_sensitive(False)
        hbox.pack_start(self.edit, False, False, 0)
        self.new = SimpleButton('document-new', self.new_clicked)
        self.new.set_tooltip_text(_('Add a new To Do note'))
        hbox.pack_start(self.new, False, False, 0)
        self.page = Gtk.Label()
        hbox.pack_end(self.page, False, False, 10)

        self.title = Gtk.Label(halign=Gtk.Align.START)
        self.title.set_line_wrap(True)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                  Gtk.PolicyType.AUTOMATIC)
        self.texteditor = StyledTextEditor()
        self.texteditor.set_editable(False)
        self.texteditor.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolledwindow.add(self.texteditor)

        top.pack_start(hbox, False, False, 0)
        top.pack_start(self.title, False, False, 4)
        top.pack_start(scrolledwindow, True, True, 0)
        top.show_all()
        return top

    def main(self):
        self.get_notes()

    def get_note_list(self):
        """
        Get a list of all To Do notes.
        """
        all_notes = self.dbstate.db.get_note_handles()
        FilterClass = GenericFilterFactory('Note')
        filter = FilterClass()
        filter.add_rule(rules.note.HasType(["To Do"]))
        note_list = filter.apply(self.dbstate.db, all_notes)
        return note_list

    def get_notes(self):
        """
        Display all the To Do notes.
        """
        self.left.set_sensitive(False)
        self.right.set_sensitive(False)
        self.edit.set_sensitive(False)
        self.texteditor.set_text(StyledText())
        self.note_list = self.get_note_list()
        self.page.set_text('')
        self.title.set_text('')
        if len(self.note_list) > 0:
            self.set_has_data(True)
            self.edit.set_sensitive(True)
            if len(self.note_list) > 1:
                self.right.set_sensitive(True)
            self.current = 0
            self.display_note()
        else:
            self.set_has_data(False)

    def clear_text(self):
        self.left.set_sensitive(False)
        self.right.set_sensitive(False)
        self.edit.set_sensitive(False)
        self.texteditor.set_text(StyledText())
        self.page.set_text('')
        self.title.set_text('')
        self.current = 0

    def display_note(self):
        """
        Display the current note.
        """
        note_handle = self.note_list[self.current]
        note = self.dbstate.db.get_note_from_handle(note_handle)
        obj = [x for x in self.dbstate.db.find_backlink_handles(note_handle)]
        if obj:
            name, obj = navigation_label(self.dbstate.db, obj[0][0], obj[0][1])
            self.title.set_text(name)
        else:
            self.title.set_text(_("Unattached"))
        self.texteditor.set_text(note.get_styledtext())
        self.page.set_text(_('%(current)d of %(total)d') %
                           {'current': self.current + 1,
                            'total': len(self.note_list)})

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

    def get_has_data(self):
        """
        Return True if the gramplet has data, else return False.
        """
        if self.get_note_list():
            return True
        return False

    def edit_clicked(self, obj):
        """
        Edit current To Do note.
        """
        from gramps.gui.editors import EditNote
        note_handle = self.note_list[self.current]
        note = self.dbstate.db.get_note_from_handle(note_handle)
        try:
            EditNote(self.gui.dbstate, self.gui.uistate, [], note)
        except AttributeError:
            pass

    def new_clicked(self, obj):
        """
        Create a new To Do note.
        """
        from gramps.gui.editors import EditNote
        note = Note()
        note.set_type(NoteType.TODO)
        try:
            EditNote(self.gui.dbstate, self.gui.uistate, [], note)
        except AttributeError:
            pass

    def update_has_data(self):
        self.set_has_data(self.get_has_data())

    def db_changed(self):
        self.connect(self.dbstate.db, 'note-add', self.update)
        self.connect(self.dbstate.db, 'note-delete', self.update)
        self.connect(self.dbstate.db, 'note-update', self.update)
