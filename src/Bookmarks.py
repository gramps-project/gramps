#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"Handle bookmarks for the gramps interface."

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------

from cStringIO import StringIO

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".Bookmarks")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import GrampsDisplay
from BasicUtils import name_displayer
import ListModel
import Utils
import const
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Navigation' % const.URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Bookmarks')

#-------------------------------------------------------------------------
#
# Bookmarks
#
#-------------------------------------------------------------------------

TOP = '''<ui><menubar name="MenuBar"><menu action="BookMenu">'''
BTM = '''</menu></menubar></ui>'''

DISABLED = -1

class Bookmarks :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, callback=None):
        """
        Create the bookmark editor.

        bookmarks - list of People
        menu - parent menu to attach users
        callback - task to connect to the menu item as a callback
        """
        self.dbstate = dbstate
        self.uistate = uistate
        self.bookmarks = bookmarks
        self.active = DISABLED
        self.action_group = gtk.ActionGroup('Bookmarks')
        self.connect_signals()
        self.dbstate.connect('database-changed', self.db_changed)

    def db_changed(self, data):
        """
        Reconnect the signals on a database changed.
        """
        self.connect_signals()

    def connect_signals(self):
        """
        Connect the person-delete signal
        """
        raise NotImplementedError

    def update_bookmarks(self, bookmarks):
        """
        Assign bookmarks 
        """
        self.bookmarks = bookmarks

    def display(self):
        """
        Redraw the display.
        """
        self.redraw()

    def undisplay(self):
        """
        Update the uimanager.
        """
        if self.active != DISABLED:
            self.uistate.uimanager.remove_ui(self.active)
            self.uistate.uimanager.remove_action_group(self.action_group)
            self.action_group = gtk.ActionGroup('Bookmarks')
            self.active = DISABLED

    def redraw_and_report_change(self):
        """Create the pulldown menu and set bookmarks to changed."""
        self.dbstate.db.report_bm_change()
        self.redraw()

    def redraw(self):
        """Create the pulldown menu."""
        text = StringIO()
        text.write(TOP)

        self.undisplay()

        actions = []
        count = 0

        if len(self.bookmarks.get()) > 0:
            text.write('<placeholder name="GoToBook">')
            for item in self.bookmarks.get():
                try:
                    label, obj = self.make_label(item)
                    func = self.callback(item)
                    action_id = "BM:%s" % item
                    actions.append((action_id, None, label, None, None, func))
                    text.write('<menuitem action="%s"/>' % action_id)
                    count += 1
                except AttributeError:
                    pass
            text.write('</placeholder>')
            
        text.write(BTM)
        self.action_group.add_actions(actions)
        self.uistate.uimanager.insert_action_group(self.action_group, 1)
        self.active = self.uistate.uimanager.add_ui_from_string(text.getvalue())
        self.uistate.uimanager.ensure_update()
        text.close()

    def make_label(self, handle):
        raise NotImplementedError

    def callback(self, handle):
        raise NotImplementedError

    def add(self, person_handle):
        """Append the person to the bottom of the bookmarks."""
        if person_handle not in self.bookmarks.get():
            self.bookmarks.append(person_handle)
            self.redraw_and_report_change()

    def remove_handles(self, handle_list):
        """
        Remove people from the list of bookmarked people.

        This function is for use *outside* the bookmark editor
        (removal when person is deleted or merged away).
        """

        modified = False
        for handle in handle_list:
            if handle in self.bookmarks.get():
                self.bookmarks.remove(handle)
                modified = True
        if modified:
            self.redraw_and_report_change()

    def draw_window(self):
        """Draw the bookmark dialog box."""
        title = _("%(title)s - Gramps") % {'title': _("Organize Bookmarks")}
        self.top = gtk.Dialog(title)
        self.top.set_default_size(400, 350)
        self.top.set_modal(True)
        self.top.set_transient_for(self.uistate.window)
        self.top.set_has_separator(False)
        self.top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % _("Organize Bookmarks"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label, 0, 0, 5)
        box = gtk.HBox()
        self.top.vbox.pack_start(box, 1, 1, 5)
        
        name_titles = [(_('Name'), -1, 200), (_('ID'), -1, 50), ('', -1, 0)]
        self.namelist = gtk.TreeView()
        self.namemodel = ListModel.ListModel(self.namelist, name_titles)
        self.namemodel_cols = len(name_titles)

        slist = gtk.ScrolledWindow()
        slist.add_with_viewport(self.namelist)
        slist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        box.pack_start(slist, 1, 1, 5)
        bbox = gtk.VButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_START)
        bbox.set_spacing(6)
        up = gtk.Button(stock=gtk.STOCK_GO_UP)
        down = gtk.Button(stock=gtk.STOCK_GO_DOWN)
        delete = gtk.Button(stock=gtk.STOCK_REMOVE)
        up.connect('clicked', self.up_clicked)
        down.connect('clicked', self.down_clicked)
        delete.connect('clicked', self.delete_clicked)
        self.top.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        self.top.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
        self.top.connect('delete-event', self.close)
        bbox.add(up)
        bbox.add(down)
        bbox.add(delete)
        box.pack_start(bbox, 0, 0, 5)
        self.top.show_all()
    
    def close(self, widget, event):
        """Stop the bookmark organizer"""
        self.top.response(gtk.RESPONSE_CLOSE)

    def edit(self):
        """
        Display the bookmark editor.

        The current bookmarked people are inserted into the namelist,
        attaching the person object to the corresponding row. The currently
        selected row is attached to the name list. This is either 0 if the
        list is not empty, or -1 if it is.
        """
        self.draw_window()
        for handle in self.bookmarks.get():
            name, obj = self.make_label(handle)
            if obj:
                gramps_id = obj.get_gramps_id()
                self.namemodel.add([name, gramps_id, handle])
        self.namemodel.connect_model()

        self.modified = False
        while True:
            self.response = self.top.run()
            if self.response == gtk.RESPONSE_HELP:
                self.help_clicked()
            elif self.response == gtk.RESPONSE_CLOSE:
                if self.modified:
                    self.redraw_and_report_change()
                self.top.destroy()
                break

    def delete_clicked(self, obj):
        """Remove the current selection from the list."""
        store, the_iter = self.namemodel.get_selected()
        if not the_iter:
            return
        row = self.namemodel.get_selected_row()
        self.bookmarks.pop(row)
        self.namemodel.remove(the_iter)
        self.modified = True
        if row > 0:
            row -= 1
        self.namemodel.select_row(row)

    def up_clicked(self, obj):
        """Move the current selection up one row."""
        row = self.namemodel.get_selected_row()
        if not row or row == -1:
            return
        store, the_iter = self.namemodel.get_selected()
        data = self.namemodel.get_data(the_iter, range(self.namemodel_cols))
        self.namemodel.remove(the_iter)
        self.namemodel.insert(row-1, data, None, 1)
        handle = self.bookmarks.pop(row)
        self.bookmarks.insert(row-1, handle)
        self.modified = True

    def down_clicked(self, obj):
        """Move the current selection down one row."""
        row = self.namemodel.get_selected_row()
        if row + 1 >= self.namemodel.count or row == -1:
            return
        store, the_iter = self.namemodel.get_selected()
        data = self.namemodel.get_data(the_iter, range(self.namemodel_cols))
        self.namemodel.remove(the_iter)
        self.namemodel.insert(row+1, data, None, 1)
        handle = self.bookmarks.pop(row)
        self.bookmarks.insert(row+1, handle)
        self.modified = True

    def help_clicked(self):
        """Display the relevant portion of GRAMPS manual."""
        GrampsDisplay.help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

class ListBookmarks(Bookmarks):

    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        self.goto_handle = goto_handle
        Bookmarks.__init__(self, dbstate, uistate, bookmarks)
    
    def callback(self, handle):
        return make_callback(handle, self.do_callback)

    def do_callback(self, handle):
        self.goto_handle(handle)

class PersonBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Person', handle)

    def connect_signals(self):
        self.dbstate.db.connect('person-delete', self.remove_handles)
        
class FamilyBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Family', handle)

    def connect_signals(self):
        self.dbstate.db.connect('family-delete', self.remove_handles)

class EventBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Event', handle)

    def connect_signals(self):
        self.dbstate.db.connect('event-delete', self.remove_handles)

class SourceBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Source', handle)

    def connect_signals(self):
        self.dbstate.db.connect('source-delete', self.remove_handles)

class MediaBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Media', handle)

    def connect_signals(self):
        self.dbstate.db.connect('media-delete', self.remove_handles)

class RepoBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Repository', handle)

    def connect_signals(self):
        self.dbstate.db.connect('repository-delete', self.remove_handles)

class PlaceBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Place', handle)

    def connect_signals(self):
        self.dbstate.db.connect('place-delete', self.remove_handles)

class NoteBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, bookmarks, goto_handle):
        ListBookmarks.__init__(self, dbstate, uistate, bookmarks,
                               goto_handle)
        
    def make_label(self, handle):
        return Utils.navigation_label(self.dbstate.db, 'Note', handle)

    def connect_signals(self):
        self.dbstate.db.connect('note-delete', self.remove_handles)

def make_callback(handle, function):
    """
    Build a unique call to the function with the associated handle.
    """
    return lambda x: function(handle)
