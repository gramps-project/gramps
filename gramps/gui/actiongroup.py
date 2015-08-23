#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015      Nick Hall
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

"""
A replacement ActionGroup that correctly loads named icons from an icon theme.
"""

from gi.repository import Gtk

class ActionGroup(Gtk.ActionGroup):

    def add_actions(self, action_list, **kwargs):
        Gtk.ActionGroup.add_actions(self, action_list, **kwargs)
        self.fix_icon_name(action_list)

    def add_toggle_actions(self, action_list, **kwargs):
        Gtk.ActionGroup.add_toggle_actions(self, action_list, **kwargs)
        self.fix_icon_name(action_list)

    def add_radio_actions(self, action_list, **kwargs):
        Gtk.ActionGroup.add_radio_actions(self, action_list, **kwargs)
        self.fix_icon_name(action_list)

    def fix_icon_name(self, action_list):
        for action_tuple in action_list:
            if action_tuple[1]:
                action = self.get_action(action_tuple[0])
                action.set_icon_name(action_tuple[1])
