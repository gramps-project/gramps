#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009       Nick Hall
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

"""
Provide the base classes for GRAMPS' DataView classes
"""

#----------------------------------------------------------------
#
# python modules
#
#----------------------------------------------------------------
import logging

_LOG = logging.getLogger('.navigationview')

#----------------------------------------------------------------
#
# gtk
#
#----------------------------------------------------------------
import gtk

#----------------------------------------------------------------
#
# GRAMPS 
#
#----------------------------------------------------------------
from gui.views.pageview import PageView

from TransUtils import sgettext as _

NAVIGATION_NONE = -1
NAVIGATION_PERSON = 0
NAVIGATION_FAMILY = 1
NAVIGATION_EVENT = 2
NAVIGATION_PLACE = 3
NAVIGATION_SOURCE = 4
NAVIGATION_REPOSITORY = 5
NAVIGATION_MEDIA = 6
NAVIGATION_NOTE = 7

#------------------------------------------------------------------------------
#
# NavigationView
#
#------------------------------------------------------------------------------
class NavigationView(PageView):
    """
    The NavigationView class is the base class for all Data Views that require
    navigation functionalilty. Views that need bookmarks and forward/backward
    should derive from this class.
    """
    
    def __init__(self, title, state, uistate, bookmarks, bm_type):
        PageView.__init__(self, title, state, uistate)
        self.bookmarks = bm_type(self.dbstate, self.uistate, bookmarks,
                                 self.goto_handle)

        self.fwd_action = None
        self.back_action = None
        self.book_action = None
        self.other_action = None
        self.key_active_changed = None

    def define_actions(self):
        """
        Define menu actions.
        """
        self.bookmark_actions()
        self.navigation_actions()
        
    def disable_action_group(self):
        """
        Normally, this would not be overridden from the base class. However, 
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.disable_action_group(self)
        
        self.fwd_action.set_visible(False)
        self.back_action.set_visible(False)

    def enable_action_group(self, obj):
        """
        Normally, this would not be overridden from the base class. However, 
        in this case, we have additional action groups that need to be
        handled correctly.
        """
        PageView.enable_action_group(self, obj)
        
        self.fwd_action.set_visible(True)
        self.back_action.set_visible(True)
        hobj = self.uistate.phistory
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

    def change_page(self):
        """
        Called when the page changes.
        """
        hobj = self.uistate.phistory
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())
        self.other_action.set_sensitive(not self.dbstate.db.readonly)
        
    def set_active(self):
        """
        Called when the page becomes active (displayed).
        """
        PageView.set_active(self)
        self.bookmarks.display()
        self.key_active_changed = self.dbstate.connect('active-changed', 
                                                       self.goto_active)
        self.goto_active(None)

    def set_inactive(self):
        """
        Called when the page becomes inactive (not displayed).
        """
        if self.active:
            PageView.set_inactive(self)
            self.bookmarks.undisplay()
            self.dbstate.disconnect(self.key_active_changed)

    def goto_active(self, active_handle):
        """
        Callback (and usable function) that selects the active person
        in the display tree.
        """
        if self.dbstate.active:
            self.handle_history(self.dbstate.active.handle)

        # active object for each navigation type
        if self.navigation_type() == NAVIGATION_PERSON:
            if self.dbstate.active:
                self.goto_handle(self.dbstate.active.handle)
         
    def change_active(self, handle):
        """
        Changes the active object.
        """
        self.dbstate.set_active(self.navigation_type(), handle)

    def goto_handle(self, handle):
        """
        Needs to be implemented by classes derived from this.
        Used to move to the given handle.
        """
        raise NotImplementedError

    ####################################################################
    # BOOKMARKS
    ####################################################################
    def add_bookmark(self, obj):
        """
        Add a bookmark to the list.
        """
        from BasicUtils import name_displayer
        
        if self.dbstate.active:
            self.bookmarks.add(self.dbstate.active.get_handle())
            name = name_displayer.display(self.dbstate.active)
            self.uistate.push_message(self.dbstate, 
                                      _("%s has been bookmarked") % name)
        else:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _("Could Not Set a Bookmark"), 
                _("A bookmark could not be set because "
                  "no one was selected."))

    def edit_bookmarks(self, obj):
        """
        Call the bookmark editor.
        """
        self.bookmarks.edit()

    def bookmark_actions(self):
        """
        Define the bookmark menu actions.
        """
        self.book_action = gtk.ActionGroup(self.title + '/Bookmark')
        self.book_action.add_actions([
            ('AddBook', 'gramps-bookmark-new', _('_Add Bookmark'), 
             '<control>d', None, self.add_bookmark), 
            ('EditBook', 'gramps-bookmark-edit', 
             _("%(title)s...") % {'title': _("Organize Bookmarks")}, 
             '<shift><control>b', None, 
             self.edit_bookmarks), 
            ])

        self._add_action_group(self.book_action)

    ####################################################################
    # NAVIGATION
    ####################################################################
    def navigation_actions(self):
        """
        Define the navigation menu actions.
        """
        # add the Forward action group to handle the Forward button
        self.fwd_action = gtk.ActionGroup(self.title + '/Forward')
        self.fwd_action.add_actions([
            ('Forward', gtk.STOCK_GO_FORWARD, _("_Forward"), 
             "<ALT>Right", _("Go to the next person in the history"), 
             self.fwd_clicked)
            ])

        # add the Backward action group to handle the Forward button
        self.back_action = gtk.ActionGroup(self.title + '/Backward')
        self.back_action.add_actions([
            ('Back', gtk.STOCK_GO_BACK, _("_Back"), 
             "<ALT>Left", _("Go to the previous person in the history"), 
             self.back_clicked)
            ])

        self._add_action('HomePerson', gtk.STOCK_HOME, _("_Home"), 
                         accel="<Alt>Home", 
                         tip=_("Go to the default person"), callback=self.home)

        self.other_action = gtk.ActionGroup(self.title + '/PersonOther')
        self.other_action.add_actions([
                ('SetActive', gtk.STOCK_HOME, _("Set _Home Person"), None, 
                 None, self.set_default_person), 
                ])

        self._add_action_group(self.back_action)
        self._add_action_group(self.fwd_action)
        self._add_action_group(self.other_action)

    def set_default_person(self, obj):
        """
        Set the default person.
        """
        active = self.dbstate.active
        if active:
            self.dbstate.db.set_default_person_handle(active.get_handle())

    def home(self, obj):
        """
        Move to the default person.
        """
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.dbstate.change_active_person(defperson)

    def jump(self):
        """
        A dialog to move to a Gramps ID entered by the user.
        """
        dialog = gtk.Dialog(_('Jump to by Gramps ID'), None, 
                            gtk.DIALOG_NO_SEPARATOR)
        dialog.set_border_width(12)
        label = gtk.Label('<span weight="bold" size="larger">%s</span>' % 
                          _('Jump to by Gramps ID'))
        label.set_use_markup(True)
        dialog.vbox.add(label)
        dialog.vbox.set_spacing(10)
        dialog.vbox.set_border_width(12)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("%s: " % _('ID')), False)
        text = gtk.Entry()
        text.set_activates_default(True)
        hbox.pack_start(text, False)
        dialog.vbox.pack_start(hbox, False)
        dialog.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                           gtk.STOCK_JUMP_TO, gtk.RESPONSE_OK)
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.vbox.show_all()
        
        if dialog.run() == gtk.RESPONSE_OK:
            gid = text.get_text()
            handle = self.get_handle_from_gramps_id(gid)
            if handle is not None:
                if self.navigation_type() == NAVIGATION_PERSON:
                    self.change_active(handle)

                self.goto_handle(handle)
            else:
                self.uistate.push_message(
                    self.dbstate, 
                    _("Error: %s is not a valid Gramps ID") % gid)
        dialog.destroy()

    def get_handle_from_gramps_id(self, gid):
        """
        Get an object handle from its Gramps ID.
        Needs to be implemented by the inheriting class.
        """
        pass

    def fwd_clicked(self, obj):
        """
        Move forward one object in the history.
        """
        hobj = self.uistate.phistory
        hobj.lock = True
        if not hobj.at_end():
            try:
                handle = hobj.forward()
                self.dbstate.change_active_handle(handle)
                self.uistate.modify_statusbar(self.dbstate)
                hobj.mhistory.append(hobj.history[hobj.index])
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

    def back_clicked(self, obj):
        """
        Move backward one object in the history.
        """
        hobj = self.uistate.phistory
        hobj.lock = True
        if not hobj.at_front():
            try:
                handle = hobj.back()
                self.active = self.dbstate.db.get_person_from_handle(handle)
                self.uistate.modify_statusbar(self.dbstate)
                self.dbstate.change_active_handle(handle)
                hobj.mhistory.append(hobj.history[hobj.index])
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
        It will push the person at the end of the history if that person is
        not present person
        """
        hobj = self.uistate.phistory
        if handle and not hobj.lock and not (handle == hobj.present()):
            hobj.push(handle)
            self.fwd_action.set_sensitive(not hobj.at_end())
            self.back_action.set_sensitive(not hobj.at_front())
            
    ####################################################################
    # Template functions
    ####################################################################
    def get_bookmarks(self):
        """
        Template function to get bookmarks.
        We could implement this here based on navigation_type()
        """
        raise NotImplementedError
        
    def edit(self, obj):
        """
        Template function to allow the editing of the selected object
        """
        raise NotImplementedError

    def remove(self, handle):
        """
        Template function to allow the removal of an object by its handle
        """
        raise NotImplementedError

    def add(self, obj):
        """
        Template function to allow the adding of a new object
        """
        raise NotImplementedError

    def remove_object_from_handle(self, handle):
        """
        Template function to allow the removal of an object by its handle
        """
        raise NotImplementedError

    def build_tree(self):
        """
        Rebuilds the current display. This must be overridden by the derived
        class.
        """
        raise NotImplementedError

    def build_widget(self):
        """
        Builds the container widget for the interface. Must be overridden by the
        the base class. Returns a gtk container widget.
        """
        raise NotImplementedError
        
