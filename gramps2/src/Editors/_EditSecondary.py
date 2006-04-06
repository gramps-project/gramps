#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

from gettext import gettext as _

import ManagedWindow
import Config
import GrampsDisplay
import Utils

class EditSecondary(ManagedWindow.ManagedWindow):

    def __init__(self, state, uistate, track, obj, callback=None):
        """Creates an edit window.  Associates a person with the window."""

        self.obj = obj
        self.dbstate = state
        self.uistate = uistate
        self.db = state.db
        self.callback = callback
        self.signal_keys = []

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, obj)

        self._local_init()

        self._create_tabbed_pages()
        self._setup_fields()
        self._connect_signals()
        self.show()
        self._post_init()

    def _local_init(self):
        """
        Derived class should do any pre-window initalization in this task.
        """
        pass

    def _post_init(self):
        """
        Derived class should do any post-window initalization in this task.
        """
        pass

    def _add_db_signal(self, name, callback):
        self.signal_keys.append(self.db.connect(name,callback))
        
    def _connect_signals(self):
        pass

    def _setup_fields(self):
        pass

    def _create_tabbed_pages(self):
        pass

    def build_window_key(self,obj):
        return id(obj)
        
    def _add_tab(self,notebook,page):
        notebook.insert_page(page)
        notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def _cleanup_on_exit(self):
        pass

    def define_ok_button(self,button,function):
        button.connect('clicked',function)
        button.set_sensitive(not self.db.readonly)

    def define_top_level(self,window,title,text):
        self.window = window
        self.window.connect('delete-event',self.delete_event)
        Utils.set_titles(window,title,text)
        
    def define_cancel_button(self,button):
        button.connect('clicked',self.delete_event)

    def define_help_button(self,button,tag):
        button.connect('clicked', lambda x: GrampsDisplay.help(tag))

    def close_window(self,*obj):
        for key in self.signal_keys:
            self.db.disconnect(key)
        self._cleanup_on_exit()
        self.close()

    def delete_event(self,*obj):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        self.close_window()

