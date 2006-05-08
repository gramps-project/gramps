#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modiy
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

# $Id: ScratchPad.py 6485 2006-04-28 16:56:19Z rshura $

# Written by Alex Roitman

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import time
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from QuestionDialog import QuestionDialog
import ManagedWindow

#-------------------------------------------------------------------------
#
# UndoHistory class
#
#-------------------------------------------------------------------------
class UndoHistory(ManagedWindow.ManagedWindow):
    """
    The UndoHistory provides a list view with all the editing
    steps available for undo/redo. Selecting a line in the list
    will revert/advance to the appropriate step in editing history.
    """
    
    def __init__(self, dbstate, uistate):

        self.title = _("Undo History")
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)
        self.db = dbstate.db
        self.dbstate = dbstate

        window = gtk.Dialog("",uistate.window,
                            gtk.DIALOG_DESTROY_WITH_PARENT,None)

        self.undo_button = window.add_button(gtk.STOCK_UNDO,
                                             gtk.RESPONSE_REJECT)
        self.redo_button = window.add_button(gtk.STOCK_REDO,
                                             gtk.RESPONSE_ACCEPT)
        self.clear_button = window.add_button(gtk.STOCK_CLEAR,
                                              gtk.RESPONSE_APPLY)
        self.close_button = window.add_button(gtk.STOCK_CLOSE,
                                              gtk.RESPONSE_CLOSE)
     
        self.set_window(window, None, self.title)
        self.window.set_size_request(400,200)
        self.window.connect('response', self._response)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.tree = gtk.TreeView()
        self.model = gtk.ListStore(str, str)
        self.selection = self.tree.get_selection()

        self.tree.set_model(self.model)
        self.tree.set_rules_hint(True)
        self.tree.append_column(
            gtk.TreeViewColumn(_('Original time'), gtk.CellRendererText(),
                               text=0))
        self.tree.append_column(
            gtk.TreeViewColumn(_('Action'), gtk.CellRendererText(),
                               text=1))

        scrolled_window.add(self.tree)
        self.window.vbox.add(scrolled_window)
        self.window.show_all()

        self._build_model()
        self._update_ui()
        
        self.db_change_key = dbstate.connect('database-changed',self._close)
        self.selection.connect('changed',self._selection_changed)
        self.show()

    def _close(self,obj):
        self.dbstate.disconnect(self.db_change_key)
        self.close()

    def _selection_changed(self,obj):
        (model,node) = self.selection.get_selected()
        if node:
            path = self.model.get_path(node)
            self._move(path[0]-self.db.undoindex-1)

    def _response(self,obj,response_id):
        if response_id == gtk.RESPONSE_CLOSE:
            self.close()
        elif response_id == gtk.RESPONSE_REJECT:
            self._move(-1)
        elif response_id == gtk.RESPONSE_ACCEPT:
            self._move(1)
        elif response_id == gtk.RESPONSE_APPLY:
            self._clear_clicked()

    def build_menu_names(self,obj):
        return (self.title,None)

    def _clear_clicked(self,obj=None):
        QuestionDialog(_("Delete confirmation"),
                       _("Are you sure you want to clear the Undo history?"),
                       _("Clear"),
                       self.clear,
                       self.window)

    def clear(self):
        self.db.undoindex = -1
        self.db.translist = [None] * len(self.db.translist)
        self.db.abort_possible = False
        self.update()
        if self.db.undo_callback:
            self.db.undo_callback(None)
        if self.db.redo_callback:
            self.db.redo_callback(None)

    def _move(self,steps=-1):
        if steps == 0 :
            return
        elif steps < 0:
            func = self.db.undo
        elif steps > 0:
            func = self.db.redo

        for step in range(abs(steps)):
            func(False)
        self.update()

    def _update_ui(self):
        self.undo_button.set_sensitive(self.db.undo_available())
        self.redo_button.set_sensitive(self.db.redo_available())
        self.clear_button.set_sensitive(
            self.db.undo_available() or self.db.redo_available() )

    def _build_model(self):
        self.model.clear()

        if self.db.abort_possible:
            mod_text = _('Database opened')
        else:
            mod_text = _('History cleared')
        time_text = time.ctime(self.db.undo_history_timestamp)
        self.model.append(row=[time_text,mod_text])

        # Get the not-None portion of transaction list
        translist = [item for item in self.db.translist if item]
        for transaction in translist:
            time_text = time.ctime(transaction.timestamp)
            mod_text = transaction.get_description()
            self.model.append(row=[time_text,mod_text])
        path = (self.db.undoindex+1,)
        self.selection.select_path(path)

    def update(self):
        self._build_model()
        self._update_ui()
