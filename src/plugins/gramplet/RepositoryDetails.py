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

from gen.lib import UrlType
from gen.plug import Gramplet
from gui.widgets import LocationBox
from gen.ggettext import gettext as _
import gtk
import pango

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
        self.top = gtk.HBox()
        vbox = gtk.VBox()
        self.name = gtk.Label()
        self.name.set_alignment(0, 0)
        self.name.modify_font(pango.FontDescription('sans bold 12'))
        vbox.pack_start(self.name, fill=True, expand=False, padding=7)
        table = gtk.Table(4, 2)
        self.address = LocationBox()
        label = gtk.Label(_('Address') + ':')
        label.set_alignment(1, 0)
        table.attach(label, 0, 1, 0, 1, xoptions=gtk.FILL, xpadding=10)
        table.attach(self.address, 1, 2, 0, 1, xoptions=gtk.FILL)
        self.phone = self.make_row(table, 1, _('Phone'))
        self.email = self.make_row(table, 2, _('Email'))
        self.web = self.make_row(table, 3, _('Web'))
        vbox.pack_start(table, fill=True, expand=False)
        self.top.pack_start(vbox, fill=True, expand=False, padding=10)
        self.top.show_all()
        return self.top

    def make_row(self, table, row, title):
        """
        Make a row in a table.
        """
        label = gtk.Label(title + ':')
        label.set_alignment(1, 0)
        widget = gtk.Label()
        widget.set_alignment(0, 0)
        table.attach(label, 0, 1, row, row + 1, xoptions=gtk.FILL, xpadding=10)
        table.attach(widget, 1, 2, row, row + 1)
        return (label, widget)

    def db_changed(self):
        self.dbstate.db.connect('repository-update', self.update)
        self.connect_signal('Repository', self.update)
        self.update()

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
        address_list = repo.get_address_list()
        if len(address_list) > 0:
            self.address.set_location(address_list[0])
            self.phone[1].set_text(address_list[0].get_phone())
        else:
            self.address.set_location(None)
            self.phone[1].set_text('')

        self.email[1].set_text('')
        self.web[1].set_text('')
        for url in repo.get_url_list():
            if int(url.get_type()) == UrlType.EMAIL:
                self.email[1].set_text(url.get_path())
            if int(url.get_type()) == UrlType.WEB_HOME:
                self.web[1].set_text(url.get_path())

    def display_empty(self):
        """
        Display empty details when no repository is selected.
        """
        self.name.set_text('')
        self.address.set_location(None)
        self.phone[1].set_text('')
        self.email[1].set_text('')
        self.web[1].set_text('')
