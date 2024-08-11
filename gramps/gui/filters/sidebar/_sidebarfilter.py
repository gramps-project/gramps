#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
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

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from bisect import insort_left
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

from ... import widgets
from ...dbguielement import DbGUIElement
from gramps.gen.config import config
from ...utils import no_match_primary_mask

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")


class SidebarFilter(DbGUIElement):
    _FILTER_WIDTH = -1
    _FILTER_ELLIPSIZE = Pango.EllipsizeMode.END

    def __init__(self, dbstate, uistate, namespace):
        self.signal_map = {
            "tag-add": self._tag_add,
            "tag-delete": self._tag_delete,
            "tag-update": self._tag_update,
            "tag-rebuild": self._tag_rebuild,
        }
        DbGUIElement.__init__(self, dbstate.db)

        self.position = 1
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.grid = Gtk.Grid()
        self.vbox.pack_start(self.grid, False, False, 0)
        self.grid.set_border_width(6)
        self.grid.set_row_spacing(6)
        self.grid.set_column_spacing(6)
        self.apply_btn = Gtk.Button.new_with_mnemonic(_("_Find"))
        self.apply_btn.set_tooltip_text(
            _("This updates the view with the current filter parameters.")
        )
        self.clear_btn = Gtk.Button()
        self.clear_btn.set_tooltip_text(
            _(
                "This resets the filter parameters to empty state.  The 'Find' "
                "button should be used to actually update the view to its "
                "defaults."
            )
        )

        self._init_interface()
        uistate.connect("filters-changed", self.on_filters_changed)
        dbstate.connect("database-changed", self._db_changed)
        self.uistate = uistate
        self.dbstate = dbstate
        self.namespace = namespace
        self.__tag_list = []
        self._tag_rebuild()

    def _init_interface(self):
        self.create_widget()

        self.apply_btn.connect("clicked", self.clicked)

        hbox = Gtk.Box()
        hbox.show()
        image = Gtk.Image()
        image.set_from_icon_name("edit-undo", Gtk.IconSize.BUTTON)
        image.show()
        label = Gtk.Label(label=_("Reset"))
        label.show()
        hbox.pack_start(image, False, False, 0)
        hbox.pack_start(label, False, True, 0)
        hbox.set_spacing(4)

        self.clear_btn.add(hbox)
        self.clear_btn.connect("clicked", self.clear)

        hbox = Gtk.ButtonBox()
        hbox.set_layout(Gtk.ButtonBoxStyle.START)
        hbox.set_spacing(6)
        hbox.set_border_width(12)
        hbox.add(self.apply_btn)
        hbox.add(self.clear_btn)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 0)
        self.vbox.show()

    def get_widget(self):
        return self.vbox

    def create_widget(self):
        pass

    def clear(self, obj):
        pass

    def clicked(self, obj):
        self.uistate.set_busy_cursor(True)
        self.clicked_func()
        self.uistate.set_busy_cursor(False)

    def clicked_func(self):
        pass

    def get_filter(self):
        pass

    def add_regex_entry(self, widget):
        hbox = Gtk.Box()
        hbox.pack_start(widget, False, False, 12)
        widget.connect("toggled", self.regex_selection)
        self.vbox.pack_start(hbox, False, False, 0)

    def add_regex_case(self, widget):
        hbox = Gtk.Box()
        hbox.pack_start(widget, False, False, 12)
        self.vbox.pack_start(hbox, False, False, 0)
        self.regex_selection()

    def regex_selection(self, widget=None):
        if self.sensitive_regex:
            if widget and widget.get_active():
                self.sensitive_regex.set_sensitive(True)
            else:
                self.sensitive_regex.set_active(False)
                self.sensitive_regex.set_sensitive(False)

    def add_text_entry(self, name, widget, tooltip=None):
        self.add_entry(name, widget)
        widget.connect("key-press-event", self.key_press)
        if tooltip:
            widget.set_tooltip_text(tooltip)

    def key_press(self, obj, event):
        if no_match_primary_mask(event.get_state()):
            if event.keyval in (_RETURN, _KP_ENTER):
                self.clicked(obj)
        return False

    def add_heading(self, heading):
        label = Gtk.Label()
        label.set_text("<b>%s</b>" % heading)
        label.set_use_markup(True)
        label.set_halign(Gtk.Align.START)
        self.grid.attach(label, 1, self.position, 1, 1)
        self.position += 1

    def add_entry(self, name, widget):
        if name:
            self.grid.attach(widgets.BasicLabel(name), 1, self.position, 1, 1)
        widget.set_hexpand(True)
        self.grid.attach(widget, 2, self.position, 2, 1)
        self.position += 1

    def on_filters_changed(self, namespace):
        """
        Called when filters are changed.
        """
        pass

    def _db_changed(self, db):
        """
        Called when the database is changed.
        """
        self._change_db(db)
        self.on_db_changed(db)
        self._tag_rebuild()

    def on_db_changed(self, db):
        """
        Called when the database is changed.
        """
        pass

    def _connect_db_signals(self):
        """
        Connect database signals defined in the signal map.
        """
        for sig in self.signal_map:
            self.callman.add_db_signal(sig, self.signal_map[sig])

    def _tag_add(self, handle_list):
        """
        Called when tags are added.
        """
        for handle in handle_list:
            tag = self.dbstate.db.get_tag_from_handle(handle)
            insort_left(self.__tag_list, (tag.get_name(), handle))
        self.on_tags_changed([item[0] for item in self.__tag_list])

    def _tag_update(self, handle_list):
        """
        Called when tags are updated.
        """
        for handle in handle_list:
            item = [item for item in self.__tag_list if item[1] == handle][0]
            self.__tag_list.remove(item)
            tag = self.dbstate.db.get_tag_from_handle(handle)
            insort_left(self.__tag_list, (tag.get_name(), handle))
        self.on_tags_changed([item[0] for item in self.__tag_list])

    def _tag_delete(self, handle_list):
        """
        Called when tags are deleted.
        """
        self.__tag_list = [
            item for item in self.__tag_list if item[1] not in handle_list
        ]
        self.on_tags_changed([item[0] for item in self.__tag_list])

    def _tag_rebuild(self):
        """
        Called when the tag list needs to be rebuilt.
        """
        self.__tag_list = []
        if self.dbstate.is_open():
            for handle in self.dbstate.db.get_tag_handles(sort_handles=True):
                tag = self.dbstate.db.get_tag_from_handle(handle)
                self.__tag_list.append((tag.get_name(), handle))
        self.on_tags_changed([item[0] for item in self.__tag_list])

    def on_tags_changed(self, tag_list):
        """
        Called when tags are changed.
        """
        pass

    def add_filter_entry(self, text, widget):
        """
        Adds the text and widget to GUI, with an Edit button.
        """
        hbox = Gtk.Box()
        hbox.pack_start(widget, True, True, 0)
        hbox.pack_start(
            widgets.SimpleButton("gtk-edit", self.edit_filter), False, False, 0
        )
        self.add_entry(text, hbox)

    def edit_filter(self, obj):
        """
        Callback which invokes the EditFilter dialog. Will create new
        filter if called if none is selected.
        """
        from ...editors import EditFilter
        from gramps.gen.filters import FilterList, GenericFilterFactory
        from gramps.gen.const import CUSTOM_FILTERS

        the_filter = None
        filterdb = FilterList(CUSTOM_FILTERS)
        filterdb.load()
        if self.generic.get_active() != 0:
            model = self.generic.get_model()
            node = self.generic.get_active_iter()
            if node:
                sel_filter = model.get_value(node, 1)
                # the_filter needs to be a particular object for editor
                for filt in filterdb.get_filters(self.namespace):
                    if filt.get_name() == sel_filter.get_name():
                        the_filter = filt
        else:
            the_filter = GenericFilterFactory(self.namespace)()
        if the_filter:
            EditFilter(
                self.namespace,
                self.dbstate,
                self.uistate,
                [],
                the_filter,
                filterdb,
                selection_callback=self.edit_filter_save,
            )

    def edit_filter_save(self, filterdb, filter_name):
        """
        If a filter changed, save them all. Reloads, and sets name.
        Takes the filter database, and the filter name edited.
        """
        from gramps.gen.filters import reload_custom_filters

        filterdb.save()
        reload_custom_filters()
        self.uistate.emit("filters-changed", (self.namespace,))
        self.set_filters_to_name(filter_name)

    def set_filters_to_name(self, filter_name):
        """
        Resets the Filter combobox to the edited/saved filter.
        """
        liststore = self.generic.get_model()
        iter = liststore.get_iter_first()
        while iter:
            filter = liststore.get_value(iter, 1)
            if filter and filter.name == filter_name:
                self.generic.set_active_iter(iter)
                break
            iter = liststore.iter_next(iter)
