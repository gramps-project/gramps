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

# $Id: notetab.py 14091 2010-01-18 04:42:17Z pez4brian $

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
import Errors
import gen.lib
from gui.dbguielement import DbGUIElement
from gui.selectors import SelectorFactory
from citationrefmodel import CitationRefModel
from embeddedlist import EmbeddedList
from DdTargets import DdTargets
from gen.lib.refbase import RefBase

#-------------------------------------------------------------------------
#
# CitationEmbedList
#
#-------------------------------------------------------------------------
class CitationEmbedList(EmbeddedList, DbGUIElement):
    """
    Citation List display tab for edit dialogs. 
    
    Derives from the EmbeddedList class.
    """

    _HANDLE_COL = 4  # Column number from CitationRefModel
    _DND_TYPE = DdTargets.NOTE_LINK

    _MSG = {
        'add'   : _('Create and add a new citation'),
        'del'   : _('Remove the existing citation'),
        'edit'  : _('Edit the selected citation'),
        'share' : _('Add an existing citation'),
        'up'    : _('Move the selected citation upwards'),
        'down'  : _('Move the selected citation downwards'),
    }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Title'),  0, 200, 0, -1), 
        (_('Author'), 1, 125, 0, -1), 
        (_('Page'),   2, 100, 0, -1), 
        (_('ID'),     3, 75, 0, -1), 
    ]

    def __init__(self, dbstate, uistate, track, data, callertitle=None):
        self.data = data
        self.callertitle = callertitle
        EmbeddedList.__init__(self, dbstate, uistate, track, _("_Citations"),
                              CitationRefModel, share_button=True, 
                              move_buttons=True)
        DbGUIElement.__init__(self, dbstate.db)
        self.callman.register_handles({'citation': self.data})

    def _connect_db_signals(self):
        """
        Implement base class DbGUIElement method
        """
        #citation: citation-rebuild closes the editors, so no need to connect to it
        self.callman.register_callbacks(
           {'citation-delete': self.citation_delete,  # delete a citation we track
            'citation-update': self.citation_update,  # change a citation we track
           })
        self.callman.connect_all(keys=['citation'])

    def get_icon_name(self):
        """
        Return the stock-id icon name associated with the display tab
        """
        return 'gramps-citations'
        
    def get_data(self):
        """
        Return the data associated with display tab
        """
        return self.data

    def column_order(self):
        """
        Return the column order of the columns in the display tab.
        """
        return ((1, 0), (1, 1), (1, 2), (1, 3))

    def add_button_clicked(self, obj):
        """
        Create a new Citation instance and call the EditCitation editor with the new 
        citation. 
        
        Called when the Add button is clicked. 
        If the window already exists (Errors.WindowActiveError), we ignore it. 
        This prevents the dialog from coming up twice on the same object.
        """
        citation = gen.lib.Citation()
        try:
            from gui.editors import EditCitation
            EditCitation(self.dbstate, self.uistate, self.track,
                         gen.lib.Citation(), gen.lib.Source(),
                         self.add_callback, self.callertitle)
        except Errors.WindowActiveError:
            pass

    def add_callback(self, value):
        """
        Called to update the screen when a new citation is added
        """
        self.get_data().append(value)
        self.callman.register_handles({'citation': [value]})
        self.changed = True
        self.rebuild()

    def share_button_clicked(self, obj):
        SelectCitation = SelectorFactory('Citation')

        sel = SelectCitation(self.dbstate, self.uistate, self.track)
        citation = sel.run()
        LOG.debug("selected citation: %s" % citation)
        if citation:
            try:
                source = self.dbstate.db.get_source_from_handle(citation.ref)
                from gui.editors import EditCitation
                EditCitation(self.dbstate, self.uistate, self.track, 
                              citation,  source, self.add_callback, 
                              self.callertitle)
            except Errors.WindowActiveError:
                from QuestionDialog import WarningDialog
                WarningDialog(_("Cannot share this reference"),
                              self.__blocked_text())
    
    def edit_button_clicked(self, obj):
        """
        Get the selected Citation instance and call the EditCitation editor with the 
        citation. 
        
        Called when the Edit button is clicked. 
        If the window already exists (Errors.WindowActiveError), we ignore it. 
        This prevents the dialog from coming up twice on the same object.
        """
        handle = self.get_selected()
        LOG.debug('selected handle %s' % handle)
        if handle:
            citation = self.dbstate.db.get_citation_from_handle(handle)
            LOG.debug("selected citation: %s" % citation)
            source = self.dbstate.db.get_source_from_handle(citation.ref)
            try:
                from gui.editors import EditCitation
                EditCitation(self.dbstate, self.uistate, self.track, citation,
                        source, callertitle = self.callertitle)
            except Errors.WindowActiveError:
                pass
    
    def citation_delete(self, del_citation_handle_list):
        """
        Outside of this tab citation objects have been deleted. Check if tab
        and object must be changed.
        Note: delete of object will cause reference on database to be removed,
            so this method need not do this
        """
        rebuild = False
        for handle in del_citation_handle_list :
            while self.data.count(handle) > 0:
                self.data.remove(handle)
                rebuild = True
        if rebuild:
            self.rebuild()
                
    def citation_update(self, upd_citation_handle_list):
        """
        Outside of this tab citation objects have been updated. Check if tab
        and object must be updated.
        """
        for handle in upd_citation_handle_list :
            if handle in self.data:
                self.rebuild()
                break

# FIXME: Are these functions needed for citations?
#    def get_editor(self):
#        pass
#
#    def get_user_values(self):
#        return []
