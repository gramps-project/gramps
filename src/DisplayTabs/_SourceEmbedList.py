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
from _SourceRefModel import SourceRefModel
from _EmbeddedList import EmbeddedList

#-------------------------------------------------------------------------
#
# SourceEmbedList
#
#-------------------------------------------------------------------------
class SourceEmbedList(EmbeddedList, DbGUIElement):

    _HANDLE_COL = 4
    _DND_TYPE = DdTargets.SOURCEREF
    _DND_EXTRA = DdTargets.SOURCE_LINK
        
    _MSG = {
        'add'   : _('Create and add a new source'),
        'del'   : _('Remove the existing source'),
        'edit'  : _('Edit the selected source'),
        'share' : _('Add an existing source'),
        'up'    : _('Move the selected source upwards'),
        'down'  : _('Move the selected source downwards'),
        }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('ID'),     0, 75, 0, -1), 
        (_('Title'),  1, 200, 0, -1), 
        (_('Author'), 2, 125, 0, -1), 
        (_('Page'),   3, 100, 0, -1), 
        ]
    
    def __init__(self, dbstate, uistate, track, obj):
        self.obj = obj
        EmbeddedList.__init__(self, dbstate, uistate, track, _('_Sources'), 
                              SourceRefModel, share_button=True, 
                              move_buttons=True)
        DbGUIElement.__init__(self, dbstate.db)
        self.callman.register_handles({'source': [sref.ref for sref 
                                        in self.obj.get_source_references()]})

    def _connect_db_signals(self):
        """
        Implement base class DbGUIElement method
        """
        #note: source-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
           {'source-delete': self.source_delete,  # delete a source we track
            'source-update': self.source_update,  # change a source we track
           })
        self.callman.connect_all(keys=['source'])

    def get_icon_name(self):
        return 'gramps-source'

    def get_data(self):
        return self.obj.get_source_references()

    def column_order(self):
        return ((1, 0), (1, 1), (1, 2), (1, 3))

    def add_button_clicked(self, obj):
        try:
            from Editors import EditSourceRef
            
            sref = gen.lib.SourceRef()
            src = gen.lib.Source()
            EditSourceRef(
                self.dbstate,
                self.uistate,
                self.track, 
                src,
                sref,
                self.object_added)
        except Errors.WindowActiveError:
            pass

    def share_button_clicked(self, obj):
        SelectSource = SelectorFactory('Source')

        sel = SelectSource(self.dbstate,self.uistate,self.track)
        src = sel.run()
        if src:
            try:
                from Editors import EditSourceRef
                
                ref = gen.lib.SourceRef()
                EditSourceRef(self.dbstate,
                              self.uistate,
                              self.track, 
                              src,
                              ref,
                              self.object_added)
                
            except Errors.WindowActiveError:
                pass

    def edit_button_clicked(self, obj):
        sref = self.get_selected()
        if sref:
            src = self.dbstate.db.get_source_from_handle(sref.ref)

            try:
                from Editors import EditSourceRef
                
                EditSourceRef(self.dbstate, self.uistate, self.track, 
                              src, sref, self.object_edited)
            except Errors.WindowActiveError:
                from QuestionDialog import WarningDialog
                WarningDialog(
                    _("Cannot edit this reference"),
                    _("This source reference cannot be edited at this time. "
                      "Either the associated source is already being edited "
                      "or another source reference that is associated with "
                      "the same source is being edited.\n\nTo edit this "
                      "source reference, you need to close the source.")
                    )

    def object_added(self, reference, primary):
        """
        Callback from sourceref editor after adding a new reference (to a new
        or an existing source).
        Note that if it was to an existing source already present in the 
        sourcelist, then the source-update signal will also cause a rebuild 
        at that time.
        """
        reference.ref = primary.handle
        self.get_data().append(reference)
        self.callman.register_handles({'source': [primary.handle]})
        self.changed = True
        self.rebuild()

    def object_edited(self, refererence, primary):
        """
        Callback from sourceref editor. If the source changes itself, also
        the source-change signal will cause a rebuild. 
        This could be solved in the source editor if it only calls this 
        method in the case the sourceref part only changes.
        """
        self.changed = True
        self.rebuild()

    def handle_extra_type(self, objtype, obj):
        sref = gen.lib.SourceRef()
        src = self.dbstate.db.get_source_from_handle(obj)
        try:
            from Editors import EditSourceRef
            
            EditSourceRef(self.dbstate, self.uistate, self.track, 
                          src, sref, self.object_added)
        except Errors.WindowActiveError:
            pass

    def source_delete(self, del_src_handle_list):
        """
        Outside of this tab source objects have been deleted. Check if tab
        and object must be changed.
        Note: delete of object will cause reference on database to be removed,
              so this method need not do this
        """
        rebuild = False
        sourceref_list = self.get_data()
        ref_handles = [sref.ref for sref in sourceref_list]
        for handle in del_src_handle_list :
            while 1:
                pos = None
                try :
                    pos = ref_handles.index(handle)
                except ValueError :
                    break
            
                if pos is not None:
                    #oeps, we need to remove this reference, and rebuild tab
                    del sourceref_list[pos]
                    del ref_handles[pos]
                    rebuild = True
        if rebuild:
            self.rebuild()

    def source_update(self, upd_src_handle_list):
        """
        Outside of this tab media objects have been changed. Check if tab
        and object must be changed.
        """
        ref_handles = [sref.ref for sref in self.get_data()]
        for handle in upd_src_handle_list :
            if handle in ref_handles:
                self.rebuild()
                break
