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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import gen.lib
from gui.dbguielement import DbGUIElement
from gui.selectors import SelectorFactory
import Errors
from DdTargets import DdTargets
from _RepoRefModel import RepoRefModel
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# RepoEmbedList
#
#-------------------------------------------------------------------------
class RepoEmbedList(EmbeddedList, DbGUIElement):

    _HANDLE_COL = 4
    _DND_TYPE = DdTargets.REPOREF
    _DND_EXTRA = DdTargets.REPO_LINK
        
    _MSG = {
        'add'   : _('Create and add a new repository'),
        'del'   : _('Remove the existing repository'),
        'edit'  : _('Edit the selected repository'),
        'share' : _('Add an existing repository'),
        'up'    : _('Move the selected repository upwards'),
        'down'  : _('Move the selected repository downwards'),
        }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('ID'),     0, 75, 0, -1), 
        (_('Title'),  1, 200, 0, -1), 
        (_('Call Number'), 2, 125, 0, -1), 
        (_('Type'),   3, 100, 0, -1), 
        ]
    
    def __init__(self, dbstate, uistate, track, obj):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track, 
                              _('_Repositories'), RepoRefModel, 
                              share_button=True, move_buttons=True)
        DbGUIElement.__init__(self, dbstate.db)
        self.callman.register_handles({'repository': [rref.ref for rref 
                                                          in self.obj]})
 
    def _connect_db_signals(self):
        """
        Implement base class DbGUIElement method
        """
        #note: repository-rebuild closes the editors, so no need to connect
        self.callman.register_callbacks(
           {'repository-delete': self.repo_delete,  # delete a repo we track
            'repository-update': self.repo_update,  # change a repo we track
           })
        self.callman.connect_all(keys=['repository'])

    def get_icon_name(self):
        return 'gramps-repository'

    def get_data(self):
        return self.obj

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2), (1, 3))

    def handle_extra_type(self, objtype, obj):
        try:
            from Editors import EditRepoRef
            
            ref = gen.lib.RepoRef()
            repo = self.dbstate.db.get_repository_from_handle(obj)
            EditRepoRef(
                self.dbstate, self.uistate, self.track, 
                repo, ref, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def add_button_clicked(self, obj):
        ref = gen.lib.RepoRef()
        repo = gen.lib.Repository()
        try:
            from Editors import EditRepoRef
            
            EditRepoRef(
                self.dbstate, self.uistate, self.track, 
                repo, ref, self.add_callback)
        except Errors.WindowActiveError:
            pass

    def share_button_clicked(self, obj):
        SelectRepository = SelectorFactory('Repository')

        sel = SelectRepository(
            self.dbstate,
            self.uistate,
            self.track)
        
        repo = sel.run()
        if repo:
            try:
                from Editors import EditRepoRef
                
                ref = gen.lib.RepoRef()
                EditRepoRef(self.dbstate,
                              self.uistate,
                              self.track, 
                              repo,
                              ref,
                              self.add_callback)
                
            except Errors.WindowActiveError:
                pass

    def add_callback(self, value):
        value[0].ref = value[1].handle
        self.get_data().append(value[0])
        self.callman.register_handles({'repository': [value[1].handle]})
        self.changed = True
        self.rebuild()

    def edit_button_clicked(self, obj):
        ref = self.get_selected()
        if ref:
            repo = self.dbstate.db.get_repository_from_handle(ref.ref)
            try:
                from Editors import EditRepoRef
                
                EditRepoRef(
                    self.dbstate, self.uistate, self.track, repo, 
                    ref, self.edit_callback)
            except Errors.WindowActiveError:
                from QuestionDialog import WarningDialog
                WarningDialog(
                    _("Cannot edit this reference"),
                    _("This repository reference cannot be edited at this "
                      "time. Either the associated repository is already "
                      "being edited or another repository reference that is "
                      "associated with the same repository is being edited."
                      "\n\nTo edit this repository reference, you need to "
                      "close the repository.")
                    )


    def edit_callback(self, name):
        self.changed = True
        self.rebuild()

    def repo_delete(self, del_repo_handle_list):
        """
        Outside of this tab repo objects have been deleted. Check if tab
        and object must be changed.
        Note: delete of object will cause reference on database to be removed,
              so this method need not do this
        """
        rebuild = False
        ref_handles = [rref.ref for rref in self.obj]
        for handle in del_repo_handle_list :
            while 1:
                pos = None
                try :
                    pos = ref_handles.index(handle)
                except ValueError :
                    break
            
                if pos is not None:
                    #oeps, we need to remove this reference, and rebuild tab
                    del self.obj[pos]
                    del ref_handles[pos]
                    rebuild = True
        if rebuild:
            self.rebuild()

    def repo_update(self, upd_repo_handle_list):
        """
        Outside of this tab repo objects have been changed. Check if tab
        and object must be changed.
        """
        ref_handles = [rref.ref for rref in self.obj]
        for handle in upd_repo_handle_list :
            if handle in ref_handles:
                self.rebuild()
                break
