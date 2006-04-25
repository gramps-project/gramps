#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"Handle bookmarks for the gramps interface"

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
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
import NameDisplay
import ListModel

#-------------------------------------------------------------------------
#
# Bookmarks
#
#-------------------------------------------------------------------------

_top = '''<ui><menubar name="MenuBar"><menu action="BookMenu"><menu action="GoToBook">'''
_btm = '''</menu></menu></menubar></ui>'''

DISABLED = -1

class Bookmarks :
    "Handle the bookmarks interface for Gramps"
    
    def __init__(self,dbstate,uistate,bookmarks):
        """
        Creates a the bookmark editor.

        bookmarks - list of People
        menu - parent menu to attach users
        callback - task to connect to the menu item as a callback
        """
        self.dbstate = dbstate
        self.uistate = uistate
        self.bookmarks = bookmarks
        self.active = DISABLED
        self.action_group = gtk.ActionGroup('Bookmarks')
        self.redraw()

    def redraw(self):
        """Create the pulldown menu"""
        f = StringIO()
        f.write(_top)

        count = 0
        if self.active != DISABLED:
            self.uistate.uimanager.remove_ui(self.active)
            self.uistate.uimanager.remove_action_group(self.action_group)
            self.active = DISABLED
            
        actions = []
        for item in self.bookmarks:
            person = self.dbstate.db.get_person_from_handle(item)
            name = NameDisplay.displayer.display(person)
            action_id = "BM:%s" % item
            f.write('<menuitem action="%s"/>' % action_id)
            label = "%s [%s]" % (name,person.gramps_id)
            func = make_callback(item,self.dbstate.change_active_handle)
            actions.append((action_id,None,label,None,None,func))
            count +=1
        f.write(_btm)
        self.action_group.add_actions(actions)
        self.uistate.uimanager.insert_action_group(self.action_group,1)
        self.active = self.uistate.uimanager.add_ui_from_string(f.getvalue())
        f.close()

    def add(self,person_handle):
        """appends the person to the bottom of the bookmarks"""
        if person_handle not in self.bookmarks:
            self.bookmarks.append(person_handle)
            self.redraw()

    def remove_people(self,person_handle_list):
        """
        Removes people from the list of bookmarked people.

        This function is for use *outside* the bookmark editor
        (removal when person is deleted or merged away).
        """
        modified = False
        for person_handle in person_handle_list:
            if person_handle in self.bookmarks:
                self.bookmarks.remove(person_handle)
                modified = True
        if modified:
            self.redraw()

    def draw_window(self):
        """Draws the bookmark dialog box"""
        title = "%s - GRAMPS" % _("Edit Bookmarks")
        self.top = gtk.Dialog(title)
        self.top.set_default_size(400,350)
        self.top.set_has_separator(False)
        self.top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % _("Edit Bookmarks"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label,0,0,5)
        box = gtk.HBox()
        self.top.vbox.pack_start(box,1,1,5)
        
        name_titles = [(_('Name'),-1,200),(_('ID'),-1,50),('',-1,0)]
        self.namelist = gtk.TreeView()
        self.namemodel = ListModel.ListModel(self.namelist,name_titles)
        self.namemodel_cols = len(name_titles)

        slist = gtk.ScrolledWindow()
        slist.add_with_viewport(self.namelist)
        slist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        box.pack_start(slist,1,1,5)
        bbox = gtk.VButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_START)
        bbox.set_spacing(6)
        up = gtk.Button(stock=gtk.STOCK_GO_UP)
        down = gtk.Button(stock=gtk.STOCK_GO_DOWN)
        delete = gtk.Button(stock=gtk.STOCK_REMOVE)
        up.connect('clicked', self.up_clicked)
        down.connect('clicked',self.down_clicked)
        delete.connect('clicked',self.delete_clicked)
        self.top.add_button(gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE)
        self.top.add_button(gtk.STOCK_HELP,gtk.RESPONSE_HELP)
        bbox.add(up)
        bbox.add(down)
        bbox.add(delete)
        box.pack_start(bbox,0,0,5)
        self.top.show_all()
        
    def edit(self):
        """
        display the bookmark editor.

        The current bookmarked people are inserted into the namelist,
        attaching the person object to the corresponding row. The currently
        selected row is attached to the name list. This is either 0 if the
        list is not empty, or -1 if it is.
        """
        self.draw_window()
        for person_handle in self.bookmarks:
            person = self.dbstate.db.get_person_from_handle(person_handle)
            if person:
                name = NameDisplay.displayer.display(person)
                gramps_id = person.get_gramps_id()
                self.namemodel.add([name,gramps_id,person_handle])
        self.namemodel.connect_model()

        self.modified = False
        self.response = self.top.run()
        if self.response == gtk.RESPONSE_HELP:
            self.help_clicked()
        if self.modified:
            self.redraw()
        self.top.destroy()

    def delete_clicked(self,obj):
        """Removes the current selection from the list"""
        store,the_iter = self.namemodel.get_selected()
        if not the_iter:
            return
        row = self.namemodel.get_selected_row()
        self.bookmarks.pop(row)
        self.namemodel.remove(the_iter)
        self.modified = True

    def up_clicked(self,obj):
        """Moves the current selection up one row"""
        row = self.namemodel.get_selected_row()
        if not row or row == -1:
            return
        store,the_iter = self.namemodel.get_selected()
        data = self.namemodel.get_data(the_iter,range(self.namemodel_cols))
        self.namemodel.remove(the_iter)
        self.namemodel.insert(row-1,data,None,1)
        handle = self.bookmarks.pop(row)
        self.bookmarks.insert(row-1,handle)
        self.modified = True

    def down_clicked(self,obj):
        """Moves the current selection down one row"""
        row = self.namemodel.get_selected_row()
        if row + 1 >= self.namemodel.count or row == -1:
            return
        store,the_iter = self.namemodel.get_selected()
        data = self.namemodel.get_data(the_iter,range(self.namemodel_cols))
        self.namemodel.remove(the_iter)
        self.namemodel.insert(row+1,data,None,1)
        handle = self.bookmarks.pop(row)
        self.bookmarks.insert(row+1,handle)
        self.modified = True

    def help_clicked(self):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('gramps-nav')
        self.response = self.top.run()

def make_callback(n,f):
    return lambda x: f(n)
