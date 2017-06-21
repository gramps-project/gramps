#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2017       Alois Poettker
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
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

from .backrefmodel import BackRefModel
from .backreflist import BackRefList

from ...dialog import QuestionDialog
from ...widgets import SimpleButton

class EventBackRefList(BackRefList):

    def __init__(self, dbstate, uistate, track, obj, option=None, callback=None):
        """"""
        self.dbase = dbstate.db
        self.uistate = uistate
        self.option = option

        BackRefList.__init__(self, dbstate, uistate, track, obj, BackRefModel,
                             callback=callback)

    def get_icon_name(self):
        return 'gramps-event'

    def _cleanup_local_connects(self):
        """
        Method overrides '_cleanup_local_connects' from BackRefList.py
        """
        # if not self.changed:   # Temp. disabled
        self.model.disconnect(self.connectid)

    def _create_buttons(self, share_button=False, move_button=False,
                        jump_button=False, top_label=None):
        """
        Create a button box consisting of several button(s): Edit, (Delete).
        This button box is then appended hbox (self).
        Method overrides create_buttons from BackRefList.py
        """
        self.add_btn, self.del_btn = None, None
        self.edit_btn = SimpleButton('gtk-edit', self.edit_button_clicked)
        self.edit_btn.set_tooltip_text(_('Edit reference'))
        if self.option and self.option['del_btn']:
            self.del_btn = SimpleButton('list-remove', self.delete_button_clicked)
            self.del_btn.set_tooltip_text(_('Delete reference'))

        hbox = Gtk.Box()
        hbox.set_spacing(6)
        hbox.pack_start(self.edit_btn, False, True, 0)
        if self.del_btn:
            hbox.pack_start(self.del_btn, False, True, 0)
        hbox.show_all()
        self.pack_start(hbox, False, True, 0)

        self.track_ref_for_deletion("edit_btn")
        self.track_ref_for_deletion("add_btn")
        self.track_ref_for_deletion("del_btn")

    def _selection_changed(self, obj=None):
        """
        Method overrides '_selection_changed' from BackRefList.py
        """
        if self.dirty_selection:
            return

        self._set_label()
        if self.get_selected():
            self.edit_btn.set_sensitive(True)
            if self.del_btn:
                self.del_btn.set_sensitive(True)
        else:
            self.edit_btn.set_sensitive(False)
            if self.del_btn:
                self.del_btn.set_sensitive(False)

    def get_data(self):
        """
        Method overrides 'get_data' from BackRefList.py
        """
        if self.option and self.option['del_btn']:
            result_list = self.option['ref_call']()
        else:
            result_list = self.obj

        return result_list

    def delete_button_clicked(self, obj):
        """"""
        (reftype, ref) = self.find_node()
        self.option['ref_call'](ref)

        # with reference deleting self.connectid handler is lost,
        # therefore we don't need a disconnect anymore
        self.changed = True
        self.rebuild()
