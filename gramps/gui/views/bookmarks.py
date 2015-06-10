#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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

"Handle bookmarks for the gramps interface."

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from io import StringIO

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
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ..display import display_help
from ..listmodel import ListModel
from gramps.gen.utils.db import navigation_label
from gramps.gen.const import URL_MANUAL_PAGE
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Navigation' % URL_MANUAL_PAGE
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
    
    def __init__(self, dbstate, uistate, callback=None):
        """
        Create the bookmark editor.

        bookmarks - list of People
        menu - parent menu to attach users
        callback - task to connect to the menu item as a callback
        """
        self.dbstate = dbstate
        self.uistate = uistate
        self.bookmarks = None
        self.update_bookmarks()
        self.active = DISABLED
        self.action_group = Gtk.ActionGroup(name='Bookmarks')
        self.connect_signals()
        self.dbstate.connect('database-changed', self.db_changed)

    def db_changed(self, data):
        """
        Reconnect the signals on a database changed.
        """
        self.connect_signals()
        self.update_bookmarks()

    def connect_signals(self):
        """
        Connect the person-delete signal
        """
        raise NotImplementedError

    def get_bookmarks(self):
        """
        Retrieve bookmarks from the database.
        """
        raise NotImplementedError

    def update_bookmarks(self):
        """
        Assign bookmarks 
        """
        self.bookmarks = self.get_bookmarks()

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
            self.action_group = Gtk.ActionGroup(name='Bookmarks')
            self.uistate.uimanager.ensure_update()
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
        self.top = Gtk.Dialog(title)
        self.top.set_default_size(400, 350)
        self.top.set_modal(True)
        self.top.set_transient_for(self.uistate.window)
        self.top.vbox.set_spacing(5)
        label = Gtk.Label(label='<span size="larger" weight="bold">%s</span>'
                          % _("Organize Bookmarks"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label, 0, 0, 5)
        box = Gtk.Box()
        self.top.vbox.pack_start(box, 1, 1, 5)
        
        name_titles = [(_('Name'), -1, 200), (_('ID'), -1, 50), ('', -1, 0)]
        self.namelist = Gtk.TreeView()
        self.namemodel = ListModel(self.namelist, name_titles)
        self.namemodel_cols = len(name_titles)

        slist = Gtk.ScrolledWindow()
        slist.add(self.namelist)
        slist.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box.pack_start(slist, 1, 1, 5)
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.START)
        bbox.set_spacing(6)
        up = Gtk.Button.new_with_mnemonic(_('_Up'))
        down = Gtk.Button.new_with_mnemonic(_('_Down'))
        delete = Gtk.Button.new_with_mnemonic(_('_Remove'))
        up.connect('clicked', self.up_clicked)
        down.connect('clicked', self.down_clicked)
        delete.connect('clicked', self.delete_clicked)
        self.top.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        self.top.add_button(_('_Help'), Gtk.ResponseType.HELP)
        self.top.connect('delete-event', self.close)
        bbox.add(up)
        bbox.add(down)
        bbox.add(delete)
        box.pack_start(bbox, 0, 0, 5)
        self.top.show_all()
    
    def close(self, widget, event):
        """Stop the bookmark organizer"""
        self.top.response(Gtk.ResponseType.CLOSE)

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
            if self.response == Gtk.ResponseType.HELP:
                self.help_clicked()
            elif self.response == Gtk.ResponseType.CLOSE:
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
        if self.namemodel.move_up(row):
            handle = self.bookmarks.pop(row)
            self.bookmarks.insert(row-1, handle)
            self.modified = True

    def down_clicked(self, obj):
        """Move the current selection down one row."""
        row = self.namemodel.get_selected_row()
        if self.namemodel.move_down(row):
            handle = self.bookmarks.pop(row)
            self.bookmarks.insert(row+1, handle)
            self.modified = True

    def help_clicked(self):
        """Display the relevant portion of GRAMPS manual."""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

class ListBookmarks(Bookmarks):

    def __init__(self, dbstate, uistate, change_active):
        self.change_active = change_active
        Bookmarks.__init__(self, dbstate, uistate)
    
    def callback(self, handle):
        return make_callback(handle, self.do_callback)

    def do_callback(self, handle):
        self.change_active(handle)

class PersonBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Person', handle)

    def connect_signals(self):
        self.dbstate.db.connect('person-delete', self.remove_handles)
        
    def get_bookmarks(self):
        return self.dbstate.db.get_bookmarks()
        
class FamilyBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Family', handle)

    def connect_signals(self):
        self.dbstate.db.connect('family-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_family_bookmarks()
        
class EventBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Event', handle)

    def connect_signals(self):
        self.dbstate.db.connect('event-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_event_bookmarks()
        
class SourceBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."

    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Source', handle)

    def connect_signals(self):
        self.dbstate.db.connect('source-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_source_bookmarks()
        
class CitationBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."

    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Citation', handle)

    # Override add from ListBookmarks, so that when self.bookmarks.add is called
    # from ListView.add_bookmark, it will not add a Source bookmark to a
    # Citation view.
    def add(self, handle):
        """Append the citation to the bottom of the bookmarks."""
        if self.dbstate.db.get_citation_from_handle(handle):
            ListBookmarks.add(self, handle)
        else:
            # Probably trying to bookmark a source when the navigation type is
            # citation. This can occur when in the Citation Tree View and we
            # bookmark a source.
            
            # FIXME: See http://www.gramps-project.org/bugs/view.php?id=6352 a
            # more comprehensive solution is needed in the long term. See also
            # change_active in CitatinTreeView
            from gramps.gui.dialog import WarningDialog
            WarningDialog(_("Cannot bookmark this reference"),
                          "Only Citations can be bookmarked in this view. "
                          "You are probably trying to bookmark a Source in the "
                          "Citation Tree View. In this view, only Citations "
                          "can be bookmarked. To bookmark a Source, switch to "
                          "the Source View",
                          parent=self.uistate.window)

    def connect_signals(self):
        self.dbstate.db.connect('citation-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_citation_bookmarks()
        
class MediaBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Media', handle)

    def connect_signals(self):
        self.dbstate.db.connect('media-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_media_bookmarks()
        
class RepoBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Repository', handle)

    def connect_signals(self):
        self.dbstate.db.connect('repository-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_repo_bookmarks()
        
class PlaceBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Place', handle)

    def connect_signals(self):
        self.dbstate.db.connect('place-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_place_bookmarks()
        
class NoteBookmarks(ListBookmarks) :
    "Handle the bookmarks interface for Gramps."
    
    def __init__(self, dbstate, uistate, change_active):
        ListBookmarks.__init__(self, dbstate, uistate, change_active)
        
    def make_label(self, handle):
        return navigation_label(self.dbstate.db, 'Note', handle)

    def connect_signals(self):
        self.dbstate.db.connect('note-delete', self.remove_handles)

    def get_bookmarks(self):
        return self.dbstate.db.get_note_bookmarks()
        
def make_callback(handle, function):
    """
    Build a unique call to the function with the associated handle.
    """
    return lambda x: function(handle)
