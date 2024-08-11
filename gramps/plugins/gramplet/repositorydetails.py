# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
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

# -------------------------------------------------------------------------
#
# Gtk
#
# -------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository.GLib import markup_escape_text

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import UrlType
from gramps.gen.plug import Gramplet
from gramps.gen.const import COLON, GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


class RepositoryDetails(Gramplet):
    """
    Displays details for a repository.
    """

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.Box()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.name = Gtk.Label(halign=Gtk.Align.START)
        self.name.set_selectable(True)
        vbox.pack_start(self.name, fill=True, expand=False, padding=7)
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.grid.set_column_spacing(10)
        vbox.pack_start(self.grid, fill=True, expand=False, padding=0)
        self.top.pack_start(vbox, fill=True, expand=False, padding=10)
        self.top.show_all()
        return self.top

    def add_row(self, title, value):
        """
        Add a row to the table.
        """
        label = Gtk.Label(
            label=title + COLON, halign=Gtk.Align.END, valign=Gtk.Align.START
        )
        label.set_selectable(True)
        label.show()
        value = Gtk.Label(label=value, halign=Gtk.Align.START)
        value.set_selectable(True)
        value.show()
        self.grid.add(label)
        self.grid.attach_next_to(value, label, Gtk.PositionType.RIGHT, 1, 1)

    def clear_grid(self):
        """
        Remove all the rows from the grid.
        """
        list(map(self.grid.remove, self.grid.get_children()))

    def db_changed(self):
        self.connect(self.dbstate.db, "repository-update", self.update)
        self.connect_signal("Repository", self.update)

    def update_has_data(self):
        active_handle = self.get_active("Repository")
        if active_handle:
            repo = self.dbstate.db.get_repository_from_handle(active_handle)
            self.set_has_data(repo is not None)
        else:
            self.set_has_data(False)

    def main(self):
        self.display_empty()
        active_handle = self.get_active("Repository")
        if active_handle:
            repo = self.dbstate.db.get_repository_from_handle(active_handle)
            self.top.hide()
            if repo:
                self.display_repo(repo)
                self.set_has_data(True)
            else:
                self.set_has_data(False)
            self.top.show()
        else:
            self.set_has_data(False)

    def display_repo(self, repo):
        """
        Display details of the active repository.
        """
        self.name.set_markup(
            "<span size='large' weight='bold'>%s</span>"
            % markup_escape_text(repo.get_name(), -1)
        )

        self.clear_grid()
        address_list = repo.get_address_list()
        if len(address_list) > 0:
            self.display_address(address_list[0])
            self.display_separator()
            phone = address_list[0].get_phone()
            if phone:
                self.add_row(_("Phone"), phone)

        self.display_url(repo, UrlType(UrlType.EMAIL))
        self.display_url(repo, UrlType(UrlType.WEB_HOME))
        self.display_url(repo, UrlType(UrlType.WEB_SEARCH))
        self.display_url(repo, UrlType(UrlType.WEB_FTP))

    def display_address(self, address):
        """
        Display an address.
        """
        lines = [line for line in address.get_text_data_list()[:-1] if line]
        self.add_row(_("Address"), "\n".join(lines))

    def display_url(self, repo, url_type):
        """
        Display an url of the given url type.
        """
        for url in repo.get_url_list():
            if url.get_type() == url_type:
                self.add_row(str(url_type), url.get_path())

    def display_empty(self):
        """
        Display empty details when no repository is selected.
        """
        self.name.set_text("")
        self.clear_grid()

    def display_separator(self):
        """
        Display an empty row to separate groupd of entries.
        """
        label = Gtk.Label()
        label.set_markup("<span font='sans 4'> </span>")
        label.set_selectable(True)
        label.show()
        self.grid.add(label)
