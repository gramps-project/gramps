#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008       Stephane Charette
# Copyright (C) 2010       Jakim Friant
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

"Find unused objects and remove with the user's permission."

# -------------------------------------------------------------------------
#
# gtk modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gui.managedwindow import ManagedWindow
from gramps.gen.datehandler import displayer as _dd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.updatecallback import UpdateCallback
from gramps.gui.plug import tool
from gramps.gui.glade import Glade
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# runTool
#
# -------------------------------------------------------------------------
class RemoveUnused(tool.Tool, ManagedWindow, UpdateCallback):
    MARK_COL = 0
    OBJ_ID_COL = 1
    OBJ_NAME_COL = 2
    OBJ_TYPE_COL = 3
    OBJ_HANDLE_COL = 4

    BUSY_CURSOR = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.WATCH
    )

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.title = _("Unused Objects")

        tool.Tool.__init__(self, dbstate, options_class, name)

        if self.db.readonly:
            return

        ManagedWindow.__init__(self, uistate, [], self.__class__)
        UpdateCallback.__init__(self, self.uistate.pulse_progressbar)

        self.dbstate = dbstate
        self.uistate = uistate

        self.tables = {
            "events": {
                "get_func": self.db.get_event_from_handle,
                "remove": self.db.remove_event,
                "get_text": self.get_event_text,
                "editor": "EditEvent",
                "icon": "gramps-event",
                "name_ix": 4,
            },
            "sources": {
                "get_func": self.db.get_source_from_handle,
                "remove": self.db.remove_source,
                "get_text": None,
                "editor": "EditSource",
                "icon": "gramps-source",
                "name_ix": 2,
            },
            "citations": {
                "get_func": self.db.get_citation_from_handle,
                "remove": self.db.remove_citation,
                "get_text": None,
                "editor": "EditCitation",
                "icon": "gramps-citation",
                "name_ix": 3,
            },
            "places": {
                "get_func": self.db.get_place_from_handle,
                "remove": self.db.remove_place,
                "get_text": self.get_place_text,
                "editor": "EditPlace",
                "icon": "gramps-place",
                "name_ix": 2,
            },
            "media": {
                "get_func": self.db.get_media_from_handle,
                "remove": self.db.remove_media,
                "get_text": None,
                "editor": "EditMedia",
                "icon": "gramps-media",
                "name_ix": 4,
            },
            "repos": {
                "get_func": self.db.get_repository_from_handle,
                "remove": self.db.remove_repository,
                "get_text": None,
                "editor": "EditRepository",
                "icon": "gramps-repository",
                "name_ix": 3,
            },
            "notes": {
                "get_func": self.db.get_note_from_handle,
                "remove": self.db.remove_note,
                "get_text": self.get_note_text,
                "editor": "EditNote",
                "icon": "gramps-notes",
                "name_ix": 2,
            },
        }

        self.init_gui()

    def init_gui(self):
        self.top = Glade()
        window = self.top.toplevel
        self.set_window(window, self.top.get_object("title"), self.title)
        self.setup_configs("interface.removeunused", 400, 520)

        self.events_box = self.top.get_object("events_box")
        self.sources_box = self.top.get_object("sources_box")
        self.citations_box = self.top.get_object("citations_box")
        self.places_box = self.top.get_object("places_box")
        self.media_box = self.top.get_object("media_box")
        self.repos_box = self.top.get_object("repos_box")
        self.notes_box = self.top.get_object("notes_box")
        self.find_button = self.top.get_object("find_button")
        self.remove_button = self.top.get_object("remove_button")

        self.events_box.set_active(self.options.handler.options_dict["events"])
        self.sources_box.set_active(self.options.handler.options_dict["sources"])
        self.citations_box.set_active(self.options.handler.options_dict["citations"])
        self.places_box.set_active(self.options.handler.options_dict["places"])
        self.media_box.set_active(self.options.handler.options_dict["media"])
        self.repos_box.set_active(self.options.handler.options_dict["repos"])
        self.notes_box.set_active(self.options.handler.options_dict["notes"])

        self.warn_tree = self.top.get_object("warn_tree")
        self.warn_tree.connect("button_press_event", self.double_click)

        self.selection = self.warn_tree.get_selection()

        self.mark_button = self.top.get_object("mark_button")
        self.mark_button.connect("clicked", self.mark_clicked)

        self.unmark_button = self.top.get_object("unmark_button")
        self.unmark_button.connect("clicked", self.unmark_clicked)

        self.invert_button = self.top.get_object("invert_button")
        self.invert_button.connect("clicked", self.invert_clicked)

        self.real_model = Gtk.ListStore(
            GObject.TYPE_BOOLEAN,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
        )
        # a short term Gtk introspection means we need to try both ways:
        if hasattr(self.real_model, "sort_new_with_model"):
            self.sort_model = self.real_model.sort_new_with_model()
        else:
            self.sort_model = Gtk.TreeModelSort.new_with_model(self.real_model)
        self.warn_tree.set_model(self.sort_model)

        self.renderer = Gtk.CellRendererText()
        self.img_renderer = Gtk.CellRendererPixbuf()
        self.bool_renderer = Gtk.CellRendererToggle()
        self.bool_renderer.connect("toggled", self.selection_toggled)

        # Add mark column
        mark_column = Gtk.TreeViewColumn(
            _("Mark"), self.bool_renderer, active=RemoveUnused.MARK_COL
        )
        mark_column.set_sort_column_id(RemoveUnused.MARK_COL)
        self.warn_tree.append_column(mark_column)

        # Add image column
        img_column = Gtk.TreeViewColumn(None, self.img_renderer)
        img_column.set_cell_data_func(self.img_renderer, self.get_image)
        self.warn_tree.append_column(img_column)

        # Add column with object gramps_id
        id_column = Gtk.TreeViewColumn(
            _("ID"), self.renderer, text=RemoveUnused.OBJ_ID_COL
        )
        id_column.set_sort_column_id(RemoveUnused.OBJ_ID_COL)
        self.warn_tree.append_column(id_column)

        # Add column with object name
        name_column = Gtk.TreeViewColumn(
            _("Name"), self.renderer, text=RemoveUnused.OBJ_NAME_COL
        )
        name_column.set_sort_column_id(RemoveUnused.OBJ_NAME_COL)
        self.warn_tree.append_column(name_column)

        self.top.connect_signals(
            {
                "destroy_passed_object": self.close,
                "on_remove_button_clicked": self.do_remove,
                "on_find_button_clicked": self.find,
                "on_delete_event": self.close,
            }
        )

        self.dc_label = self.top.get_object("dc_label")

        self.sensitive_list = [
            self.warn_tree,
            self.mark_button,
            self.unmark_button,
            self.invert_button,
            self.dc_label,
            self.remove_button,
        ]

        for item in self.sensitive_list:
            item.set_sensitive(False)

        self.show()

    def build_menu_names(self, obj):
        return (self.title, None)

    def find(self, obj):
        self.options.handler.options_dict.update(
            events=self.events_box.get_active(),
            sources=self.sources_box.get_active(),
            citations=self.citations_box.get_active(),
            places=self.places_box.get_active(),
            media=self.media_box.get_active(),
            repos=self.repos_box.get_active(),
            notes=self.notes_box.get_active(),
        )

        for item in self.sensitive_list:
            item.set_sensitive(True)

        self.uistate.set_busy_cursor(True)
        self.uistate.progress.show()
        self.window.get_window().set_cursor(self.BUSY_CURSOR)

        self.real_model.clear()
        self.collect_unused()

        self.uistate.progress.hide()
        self.uistate.set_busy_cursor(False)
        self.window.get_window().set_cursor(None)
        self.reset()

        # Save options
        self.options.handler.save_options()

    def collect_unused(self):
        # Run through all requested tables and check all objects
        # for being referenced some place. If not, add_results on them.

        db = self.db
        tables = (
            ("events", db.get_event_cursor, db.get_number_of_events),
            ("sources", db.get_source_cursor, db.get_number_of_sources),
            ("citations", db.get_citation_cursor, db.get_number_of_citations),
            ("places", db.get_place_cursor, db.get_number_of_places),
            ("media", db.get_media_cursor, db.get_number_of_media),
            ("repos", db.get_repository_cursor, db.get_number_of_repositories),
            ("notes", db.get_note_cursor, db.get_number_of_notes),
        )

        # bug 7619 : don't select notes from to do list.
        # notes associated to the todo list doesn't have references.
        # get the todo list (from get_note_list method of the todo gramplet )
        all_notes = self.dbstate.db.get_note_handles()
        FilterClass = GenericFilterFactory("Note")
        filter1 = FilterClass()
        filter1.add_rule(rules.note.HasType(["To Do"]))
        todo_list = filter1.apply(self.dbstate.db, all_notes)
        filter2 = FilterClass()
        filter2.add_rule(rules.note.HasType(["Link"]))
        link_list = filter2.apply(self.dbstate.db, all_notes)

        for the_type, cursor_func, total_func in tables:
            if not self.options.handler.options_dict[the_type]:
                # This table was not requested. Skip it.
                continue

            with cursor_func() as cursor:
                self.set_total(total_func())
                fbh = db.find_backlink_handles
                for handle, data in cursor:
                    if not any(h for h in fbh(handle)):
                        if handle not in todo_list and handle not in link_list:
                            self.add_results((the_type, handle, data))
                    self.update()
            self.reset()

    def do_remove(self, obj):
        with DbTxn(_("Remove unused objects"), self.db, batch=False) as trans:
            self.db.disable_signals()

            for row_num in range(len(self.real_model) - 1, -1, -1):
                path = (row_num,)
                row = self.real_model[path]
                if not row[RemoveUnused.MARK_COL]:
                    continue

                the_type = row[RemoveUnused.OBJ_TYPE_COL]
                handle = row[RemoveUnused.OBJ_HANDLE_COL]
                remove_func = self.tables[the_type]["remove"]
                remove_func(handle, trans)

                self.real_model.remove(row.iter)

        self.db.enable_signals()
        self.db.request_rebuild()

    def selection_toggled(self, cell, path_string):
        sort_path = tuple(map(int, path_string.split(":")))
        real_path = self.sort_model.convert_path_to_child_path(Gtk.TreePath(sort_path))
        row = self.real_model[real_path]
        row[RemoveUnused.MARK_COL] = not row[RemoveUnused.MARK_COL]
        self.real_model.row_changed(real_path, row.iter)

    def mark_clicked(self, mark_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[RemoveUnused.MARK_COL] = True

    def unmark_clicked(self, unmark_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[RemoveUnused.MARK_COL] = False

    def invert_clicked(self, invert_button):
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            row[RemoveUnused.MARK_COL] = not row[RemoveUnused.MARK_COL]

    def double_click(self, obj, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            (model, node) = self.selection.get_selected()
            if not node:
                return
            sort_path = self.sort_model.get_path(node)
            real_path = self.sort_model.convert_path_to_child_path(sort_path)
            row = self.real_model[real_path]
            the_type = row[RemoveUnused.OBJ_TYPE_COL]
            handle = row[RemoveUnused.OBJ_HANDLE_COL]
            self.call_editor(the_type, handle)

    def call_editor(self, the_type, handle):
        try:
            obj = self.tables[the_type]["get_func"](handle)
            editor_str = "from gramps.gui.editors import %s as editor" % (
                self.tables[the_type]["editor"]
            )
            exec(editor_str, globals())
            editor(self.dbstate, self.uistate, [], obj)
        except WindowActiveError:
            pass

    def get_image(self, column, cell, model, iter, user_data=None):
        the_type = model.get_value(iter, RemoveUnused.OBJ_TYPE_COL)
        the_icon = self.tables[the_type]["icon"]
        cell.set_property("icon-name", the_icon)

    def add_results(self, results):
        (the_type, handle, data) = results
        gramps_id = data[1]

        # if we have a function that will return to us some type
        # of text summary, then we should use it; otherwise we'll
        # use the generic field index provided in the tables above
        if self.tables[the_type]["get_text"]:
            text = self.tables[the_type]["get_text"](the_type, handle, data)
        else:
            # grab the text field index we know about, and hope
            # it represents something useful to the user
            name_ix = self.tables[the_type]["name_ix"]
            text = data[name_ix]

        # insert a new row into the table
        self.real_model.append(row=[False, gramps_id, text, the_type, handle])

    def get_event_text(self, the_type, handle, data):
        """
        Come up with a short line of text that we can use as
        a summary to represent this event.
        """

        # get the event:
        event = self.tables[the_type]["get_func"](handle)

        # first check to see if the event has a descriptive name
        text = event.get_description()  # (this is rarely set for events)

        # if we don't have a description...
        if text == "":
            # ... then we merge together several fields

            # get the event type (marriage, birth, death, etc.)
            text = str(event.get_type())

            # see if there is a date
            date = _dd.display(event.get_date_object())
            if date != "":
                text += "; %s" % date

            # see if there is a place
            if event.get_place_handle():
                text += "; %s" % _pd.display_event(self.db, event)

        return text

    def get_note_text(self, the_type, handle, data):
        """
        We need just the first few words of a note as a summary.
        """
        # get the note object
        note = self.tables[the_type]["get_func"](handle)

        # get the note text; this ignores (discards) formatting
        text = note.get()

        # convert whitespace to a single space
        text = " ".join(text.split())

        # if the note is too long, truncate it
        if len(text) > 80:
            text = text[:80] + "..."

        return text

    def get_place_text(self, the_type, handle, data):
        """
        We need just the place name.
        """
        # get the place object
        place = self.tables[the_type]["get_func"](handle)

        # get the name
        text = place.get_name().get_value()

        return text


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class CheckOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)

        # Options specific for this report
        self.options_dict = {
            "events": 1,
            "sources": 1,
            "citations": 1,
            "places": 1,
            "media": 1,
            "repos": 1,
            "notes": 1,
        }
        self.options_help = {
            "events": (
                "=0/1",
                "Whether to use check for unused events",
                ["Do not check events", "Check events"],
                True,
            ),
            "sources": (
                "=0/1",
                "Whether to use check for unused sources",
                ["Do not check sources", "Check sources"],
                True,
            ),
            "citations": (
                "=0/1",
                "Whether to use check for unused citations",
                ["Do not check citations", "Check citations"],
                True,
            ),
            "places": (
                "=0/1",
                "Whether to use check for unused places",
                ["Do not check places", "Check places"],
                True,
            ),
            "media": (
                "=0/1",
                "Whether to use check for unused media",
                ["Do not check media", "Check media"],
                True,
            ),
            "repos": (
                "=0/1",
                "Whether to use check for unused repositories",
                ["Do not check repositories", "Check repositories"],
                True,
            ),
            "notes": (
                "=0/1",
                "Whether to use check for unused notes",
                ["Do not check notes", "Check notes"],
                True,
            ),
        }
