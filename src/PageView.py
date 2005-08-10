#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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

import gtk

class PageView:
    
    def __init__(self,title,state):
        self.title = title
        self.state = state
        self.action_list = []
        self.action_toggle_list = []
        self.action_group = None
        self.additional_action_groups = []
        self.widget = None
        self.ui = ""
        self.state.connect('no-database',self.disable_action_group)
        self.state.connect('database-changed',self.enable_action_group)

    def disable_action_group(self):
        if self.action_group:
            self.action_group.set_visible(False)

    def enable_action_group(self,obj):
        if self.action_group:
            self.action_group.set_visible(True)

    def get_stock(self):
        try:
            return gtk.STOCK_MEDIA_MISSING
        except AttributeError:
            return gtk.STOCK_MISSING_IMAGE
        
    def get_ui(self):
        return self.ui

    def get_title(self):
        return self.title

    def get_display(self):
        if not self.widget:
            self.widget = self.build_widget()
        return self.widget

    def build_widget(self):
        assert False

    def define_actions(self):
        assert False

    def _build_action_group(self):
        self.action_group = gtk.ActionGroup(self.title)
        if len(self.action_list) > 0:
            self.action_group.add_actions(self.action_list)
        if len(self.action_toggle_list) > 0:
            self.action_group.add_toggle_actions(self.action_toggle_list)

    def add_action(self, name, stock_icon, label, accel=None, tip=None, callback=None):
        self.action_list.append((name,stock_icon,label,accel,tip,callback))

    def add_toggle_action(self, name, stock_icon, label, accel=None, tip=None, callback=None):
        self.action_toggle_list.append((name,stock_icon,label,accel,tip,callback))

    def get_actions(self):
        if not self.action_group:
            self.define_actions()
            self._build_action_group()
        return [self.action_group] + self.additional_action_groups

    def add_action_group(self,group):
        self.additional_action_groups.append(group)
