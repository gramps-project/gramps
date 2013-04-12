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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

from gramps.gen.lib import UrlType
from gramps.gen.plug import Gramplet
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gi.repository import Gtk
from gi.repository import Pango

class RepositoryDetails(Gramplet):
    """
    Displays details for a repository.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.HBox()
        vbox = Gtk.VBox()
        self.name = Gtk.Label()
        self.name.set_alignment(0, 0)
        self.name.modify_font(Pango.FontDescription('sans bold 12'))
        vbox.pack_start(self.name, fill=True, expand=False, padding=7)
        self.table = Gtk.Table(1, 2)
        vbox.pack_start(self.table, fill=True, expand=False, padding=0)
        self.top.pack_start(vbox, fill=True, expand=False, padding=10)
        self.top.show_all()
        return self.top

    def add_row(self, title, value):
        """
        Add a row to the table.
        """
        label = Gtk.Label(label=title + ':')
        label.set_alignment(1, 0)
        label.show()
        value = Gtk.Label(label=value)
        value.set_alignment(0, 0)
        value.show()
        rows = self.table.get_property('n-rows')
        rows += 1
        self.table.resize(rows, 2)
        self.table.attach(label, 0, 1, rows, rows + 1, 
	                  xoptions=Gtk.AttachOptions.FILL, xpadding=10)
        self.table.attach(value, 1, 2, rows, rows + 1)
        
    def clear_table(self):
        """
        Remove all the rows from the table.
        """
        list(map(self.table.remove, self.table.get_children()))
        self.table.resize(1, 2)

    def db_changed(self):
        self.dbstate.db.connect('repository-update', self.update)
        self.connect_signal('Repository', self.update)

    def update_has_data(self): 
        active_handle = self.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        self.set_has_data(active_person is not None)

    def main(self):
        active_handle = self.get_active('Repository')
        repo = self.dbstate.db.get_repository_from_handle(active_handle)
        self.top.hide()
        if repo:
            self.display_repo(repo)
            self.set_has_data(True)
        else:
            self.display_empty()
            self.set_has_data(False)
        self.top.show()

    def display_repo(self, repo):
        """
        Display details of the active repository.
        """
        self.name.set_text(repo.get_name())

        self.clear_table()
        address_list = repo.get_address_list()
        if len(address_list) > 0:
            self.display_address(address_list[0])
            self.display_separator()
            phone = address_list[0].get_phone()
            if phone:
                self.add_row(_('Phone'), phone)

        self.display_url(repo, UrlType(UrlType.EMAIL))
        self.display_url(repo, UrlType(UrlType.WEB_HOME))
        self.display_url(repo, UrlType(UrlType.WEB_SEARCH))
        self.display_url(repo, UrlType(UrlType.WEB_FTP))

    def display_address(self, address):
        """
        Display an address.
        """
        lines = [line for line in address.get_text_data_list()[:-1] if line]
        self.add_row(_('Address'), '\n'.join(lines))

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
        self.name.set_text('')
        self.clear_table()

    def display_separator(self):
        """
        Display an empty row to separate groupd of entries.
        """
        label = Gtk.Label(label='')
        label.modify_font(Pango.FontDescription('sans 4'))
        label.show()
        rows = self.table.get_property('n-rows')
        rows += 1
        self.table.resize(rows, 2)
        self.table.attach(label, 0, 1, rows, rows + 1, 
	                  xoptions=Gtk.AttachOptions.FILL)
