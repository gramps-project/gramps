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

NAVIGATION_NONE   = -1
NAVIGATION_PERSON = 0


class PageView:
    
    def __init__(self,title,dbstate,uistate):
        self.title = title
        self.dbstate = dbstate
        self.uistate = uistate
        self.action_list = []
        self.action_toggle_list = []
        self.action_group = None
        self.additional_action_groups = []
        self.additional_uis = []
        self.widget = None
        self.ui = '<ui></ui>'
        self.dbstate.connect('no-database',self.disable_action_group)
        self.dbstate.connect('database-changed',self.enable_action_group)

    def navigation_type(self):
        return NAVIGATION_NONE
    
    def ui_definition(self):
        return self.ui

    def additional_ui_definitions(self):
        return self.additional_uis

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

    def change_page(self):
        pass
    
class PersonNavView(PageView):
    def __init__(self,title,dbstate,uistate):
        PageView.__init__(self,title,dbstate,uistate)

    def navigation_type(self):
        return NAVIGATION_PERSON

    def define_actions(self):
        # add the Forward action group to handle the Forward button

        self.fwd_action = gtk.ActionGroup(self.title + '/Forward')
        self.fwd_action.add_actions([
            ('Forward',gtk.STOCK_GO_FORWARD,"_Forward", None, None, self.fwd_clicked)
            ])

        # add the Backward action group to handle the Forward button
        self.back_action = gtk.ActionGroup(self.title + '/Backward')
        self.back_action.add_actions([
            ('Back',gtk.STOCK_GO_BACK,"_Back", None, None, self.back_clicked)
            ])

        self.add_action_group(self.back_action)
        self.add_action_group(self.fwd_action)

    def disable_action_group(self):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.disable_action_group(self)
        
        self.fwd_action.set_visible(False)
        self.back_action.set_visible(False)

    def enable_action_group(self,obj):
        """
        Normally, this would not be overridden from the base class. However,
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.enable_action_group(self,obj)
        
        self.fwd_action.set_visible(True)
        self.back_action.set_visible(True)
        hobj = self.uistate.phistory
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

    def home(self,obj):
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.dbstate.change_active_person(defperson)

    def fwd_clicked(self,obj,step=1):
        hobj = self.uistate.phistory
        hobj.lock = True
        if not hobj.at_end():
            try:
                handle = hobj.forward()
                self.dbstate.active = self.dbstate.db.get_person_from_handle(handle)
                self.uistate.modify_statusbar()
                self.dbstate.change_active_handle(handle)
                hobj.mhistory.append(hobj.history[hobj.index])
                #self.redraw_histmenu()
                self.fwd_action.set_sensitive(not hobj.at_end())
                self.back_action.set_sensitive(True)
            except:
                hobj.clear()
                self.fwd_action.set_sensitive(False)
                self.back_action.set_sensitive(False)
        else:
            self.fwd_action.set_sensitive(False)
            self.back_action.set_sensitive(True)
        hobj.lock = False

    def back_clicked(self,obj,step=1):
        hobj = self.uistate.phistory
        hobj.lock = True
        if not hobj.at_front():
            try:
                handle = hobj.back()
                self.active = self.dbstate.db.get_person_from_handle(handle)
                self.uistate.modify_statusbar()
                self.dbstate.change_active_handle(handle)
                hobj.mhistory.append(hobj.history[hobj.index])
#                self.redraw_histmenu()
                self.back_action.set_sensitive(not hobj.at_front())
                self.fwd_action.set_sensitive(True)
            except:
                hobj.clear()
                self.fwd_action.set_sensitive(False)
                self.back_action.set_sensitive(False)
        else:
            self.back_action.set_sensitive(False)
            self.fwd_action.set_sensitive(True)
        hobj.lock = False
        
    def handle_history(self, handle):
        """
        Updates the person history information
        """
        hobj = self.uistate.phistory
        if handle and not hobj.lock:
            hobj.push(handle)
            #self.redraw_histmenu()
            self.fwd_action.set_sensitive(not hobj.at_end())
            self.back_action.set_sensitive(not hobj.at_front())

    def change_page(self):
        hobj = self.uistate.phistory
        print hobj.at_end(), hobj.at_front()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())
