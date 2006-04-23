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
import DateHandler
import NameDisplay
import Config
import GrampsDisplay
from QuestionDialog import SaveDialog

class EditPrimary(ManagedWindow.ManagedWindow):

    def __init__(self, state, uistate, track, obj, get_from_handle, callback=None):
        """Creates an edit window.  Associates a person with the window."""

        self.dp  = DateHandler.parser
        self.dd  = DateHandler.displayer
        self.nd  = NameDisplay.displayer
        self.obj = obj
        self.dbstate = state
        self.uistate = uistate
        self.db = state.db
        self.callback = callback
        self.signal_keys = []
        self.get_from_handle = get_from_handle

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
        if obj and obj.get_handle():
            return obj.get_handle()
        else:
            return id(self)
        
    def _add_tab(self,notebook,page):
        notebook.insert_page(page)
        notebook.set_tab_label(page,page.get_tab_widget())
        return page

    def _cleanup_on_exit(self):
        pass

    def object_is_empty(self):
        return cmp(self.obj.serialize()[1:],
                   self.empty_object().serialize()[1:]) == 0

    def define_ok_button(self,button,function):
        button.connect('clicked',function)
        button.set_sensitive(not self.db.readonly)

    def define_cancel_button(self,button):
        button.connect('clicked',self.close)

    def define_help_button(self,button,tag):
        button.connect('clicked', lambda x: GrampsDisplay.help(tag))

    def _do_close(self,*obj):
        for key in self.signal_keys:
            self.db.disconnect(key)
        self._cleanup_on_exit()
        ManagedWindow.ManagedWindow.close(self)

    def close(self,*obj):
        """If the data has changed, give the user a chance to cancel
        the close window"""
        if not Config.get_dont_ask() and self.data_has_changed():
            SaveDialog(
                _('Save Changes?'),
                _('If you close without saving, the changes you '
                  'have made will be lost'),
                self._do_close,
                self.save)
            return True
        else:
            self._do_close()
            return False

    def empty_object(self):
        return None

    def data_has_changed(self):

        if self.db.readonly:
            return False
        elif self.obj.handle:
            orig = self.get_from_handle(self.obj.handle)
            if orig:
                cmp_obj = orig
            else:
                cmp_obj = self.empty_object()
            return cmp(cmp_obj.serialize()[1:],
                       self.obj.serialize()[1:]) != 0
        else:
            cmp_obj = self.empty_object()
            return cmp(cmp_obj.serialize()[1:],
                       self.obj.serialize()[1:]) != 0

    def save(self,*obj):
        pass
