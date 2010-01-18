#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Nick Hall
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
from gen.ggettext import sgettext as _
from Utils import navigation_label

DISABLED = -1
MRU_SIZE = 10

MRU_TOP = [
    '<ui>'
    '<menubar name="MenuBar">'
    '<menu action="GoMenu">'
    '<placeholder name="CommonHistory">'
    ]

MRU_BTM = [
    '</placeholder>'
    '</menu>'
    '</menubar>'
    '</ui>'
    ]
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
    
    def __init__(self, title, state, uistate, bookmarks, bm_type, nav_group):
        PageView.__init__(self, title, state, uistate)
        self.bookmarks = bm_type(self.dbstate, self.uistate, bookmarks,
                                 self.goto_handle)

        self.fwd_action = None
        self.back_action = None
        self.book_action = None
        self.other_action = None
        self.active_signal = None
        self.mru_signal = None
        self.nav_group = nav_group
        self.mru_active = DISABLED

        self.uistate.register(self.navigation_type(), self.nav_group)

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
        hobj = self.get_history()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

    def change_page(self):
        """
        Called when the page changes.
        """
        hobj = self.get_history()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())
        self.other_action.set_sensitive(not self.dbstate.db.readonly)
        self.uistate.modify_statusbar(self.dbstate)

    def set_active(self):
        """
        Called when the page becomes active (displayed).
        """
        PageView.set_active(self)
        self.bookmarks.display()
        
        hobj = self.get_history()
        self.active_signal = hobj.connect('active-changed', self.goto_active)
        self.mru_signal = hobj.connect('mru-changed', self.update_mru_menu)
        self.update_mru_menu(hobj.mru)
            
        self.goto_active(None)

    def set_inactive(self):
        """
        Called when the page becomes inactive (not displayed).
        """
        if self.active:
            PageView.set_inactive(self)
            self.bookmarks.undisplay()
            hobj = self.get_history()
            hobj.disconnect(self.active_signal)
            hobj.disconnect(self.mru_signal)
            self.mru_disable()

    def navigation_group(self):
        """
        Return the navigation group.
        """
        return self.nav_group
        
    def get_history(self):
        """
        Return the history object.
        """
        return self.uistate.get_history(self.navigation_type(),
                                        self.navigation_group())

    def goto_active(self, active_handle):
        """
        Callback (and usable function) that selects the active person
        in the display tree.
        """
        active_handle = self.uistate.get_active(self.navigation_type(),
                                                self.navigation_group())
        if active_handle:
            self.goto_handle(active_handle)
            
        hobj = self.get_history()
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(not hobj.at_front())

    def get_active(self):
        """
        Return the handle of the active object.
        """
        hobj = self.uistate.get_history(self.navigation_type(),
                                        self.navigation_group())
        return hobj.present()
        
    def change_active(self, handle):
        """
        Changes the active object.
        """
        hobj = self.get_history()
        if handle and not hobj.lock and not (handle == hobj.present()):
            hobj.push(handle)            

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
        from gen.display.name import displayer as name_displayer

        active_handle = self.uistate.get_active('Person')
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        if active_person:
            self.bookmarks.add(active_handle)
            name = name_displayer.display(active_person)
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
        active = self.uistate.get_active('Person')
        if active:
            self.dbstate.db.set_default_person_handle(active)

    def home(self, obj):
        """
        Move to the default person.
        """
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.change_active(defperson.get_handle())

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
        hobj = self.get_history()
        hobj.lock = True
        if not hobj.at_end():
            hobj.forward()
            self.uistate.modify_statusbar(self.dbstate)
        self.fwd_action.set_sensitive(not hobj.at_end())
        self.back_action.set_sensitive(True)
        hobj.lock = False

    def back_clicked(self, obj):
        """
        Move backward one object in the history.
        """
        hobj = self.get_history()
        hobj.lock = True
        if not hobj.at_front():
            hobj.back()
            self.uistate.modify_statusbar(self.dbstate)
        self.back_action.set_sensitive(not hobj.at_front())
        self.fwd_action.set_sensitive(True)
        hobj.lock = False
        
    ####################################################################
    # MRU functions
    ####################################################################
    
    def mru_disable(self):
        """
        Remove the UI and action groups for the MRU list.
        """
        if self.mru_active != DISABLED:
            self.uistate.uimanager.remove_ui(self.mru_active)
            self.uistate.uimanager.remove_action_group(self.mru_action)
            self.mru_active = DISABLED

    def mru_enable(self):
        """
        Enables the UI and action groups for the MRU list.
        """
        if self.mru_active == DISABLED:
            self.uistate.uimanager.insert_action_group(self.mru_action, 1)
            self.mru_active = self.uistate.uimanager.add_ui_from_string(self.mru_ui)
            self.uistate.uimanager.ensure_update()

    def update_mru_menu(self, items):
        """
        Builds the UI and action group for the MRU list.
        """
        self.mru_disable()
        nav_type = self.navigation_type()
        hobj = self.get_history()
        menu_len = min(len(items) - 1, MRU_SIZE)
        
        entry = '<menuitem action="%s%02d"/>'
        data = [entry % (nav_type, index) for index in range(0, menu_len)]
        self.mru_ui = "".join(MRU_TOP) + "".join(data) + "".join(MRU_BTM)
        
        mitems = items[-MRU_SIZE - 1:-1] # Ignore current handle
        mitems.reverse()
        data = []
        for index, handle in enumerate(mitems):
            name, obj = navigation_label(self.dbstate.db, nav_type, handle)
            data.append(('%s%02d'%(nav_type, index), None,  name,
                         "<alt>%d" % index, None,
                         make_callback(hobj.push, handle)))
 
        self.mru_action = gtk.ActionGroup(nav_type)
        self.mru_action.add_actions(data)
        self.mru_enable()

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
        
def make_callback(func, handle):
    """
    Generates a callback function based off the passed arguments
    """
    return lambda x: func(handle)
