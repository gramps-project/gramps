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

        self.set_window(
            gtk.Dialog("",uistate.window,
                       gtk.DIALOG_DESTROY_WITH_PARENT,
                       (gtk.STOCK_UNDO,gtk.RESPONSE_REJECT,
                        gtk.STOCK_REDO,gtk.RESPONSE_ACCEPT,
                        gtk.STOCK_CLEAR,gtk.RESPONSE_APPLY,
                        gtk.STOCK_CLOSE,gtk.RESPONSE_CLOSE,
                        )
                       ),
            None, self.title)
        self.window.set_size_request(600,400)
        self.window.connect('response', self._response)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.list = gtk.TreeView()
        self.model = gtk.ListStore(str, str)
        self.selection = self.list.get_selection()

        self.list.set_model(self.model)
        self.list.set_rules_hint(True)
        self.list.append_column(
            gtk.TreeViewColumn(_('Original time'), gtk.CellRendererText(),
                               text=0))
        self.list.append_column(
            gtk.TreeViewColumn(_('Modification'), gtk.CellRendererText(),
                               text=1))

        scrolled_window.add(self.list)
        self.window.vbox.add(scrolled_window)
        self.window.show_all()

        self._build_model()

        self.db.connect('database-changed',self.clear)
        self.selection.connect('changed',self._move)

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
        self.update()
        if self.db.undo_callback:
            self.db.undo_callback(None)
        if self.db.redo_callback:
            self.db.redo_callback(None)

    def _move(self,obj,steps=-1):
        self._update_ui()

    def _update_ui(self):
        pass

    def _build_model(self):
        self.model.clear()
        # Get the not-None portion of transaction list
        translist = [item for item in self.db.translist if item]
        translist.reverse()
        for transaction in translist:
            time_text = time.ctime(transaction.timestamp)
            mod_text = transaction.get_description()
            self.model.append(row=[time_text,mod_text])
        if self.db.undoindex < 0:
            self.selection.unselect_all()
        else:
            path = (self.db.undoindex,)
            self.selection.select_path(path)
        
    def update(self):
        self._build_model()
        self._update_ui()
