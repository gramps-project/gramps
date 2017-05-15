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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".citation")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject, GLib

#-------------------------------------------------------------------------
#
# Gramps classes
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Citation, Source
from ...dbguielement import DbGUIElement
from ...selectors import SelectorFactory
from .citationrefmodel import CitationRefModel
from .embeddedlist import EmbeddedList, TEXT_COL, MARKUP_COL, ICON_COL
from ...ddtargets import DdTargets

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

    _HANDLE_COL = 5  # Column number from CitationRefModel
    _DND_TYPE = DdTargets.CITATION_LINK
    _DND_EXTRA = DdTargets.SOURCE_LINK

    _MSG = {
        'add'   : _('Create and add a new citation and new source'),
        'del'   : _('Remove the existing citation'),
        'edit'  : _('Edit the selected citation'),
        'share' : _('Add an existing citation or source'),
        'up'    : _('Move the selected citation upwards'),
        'down'  : _('Move the selected citation downwards'),
    }

    #index = column in model. Value =
    #  (name, sortcol in model, width, markup/text, weigth_col
    _column_names = [
        (_('Title'),   0, 200, TEXT_COL, -1, None),
        (_('Author'),  1, 125, TEXT_COL, -1, None),
        (_('Page'),    2, 100, TEXT_COL, -1, None),
        (_('ID'),      3,  75, TEXT_COL, -1, None),
        (_('Private'), 4,  30, ICON_COL, -1, 'gramps-lock')
    ]

    def __init__(self, dbstate, uistate, track, data, callertitle=None):
        self.data = data
        self.callertitle = callertitle
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _("_Source Citations"), CitationRefModel,
                              share_button=True, move_buttons=True)
        DbGUIElement.__init__(self, dbstate.db)
        self.callman.register_handles({'citation': self.data})

    def _connect_db_signals(self):
        """
        Implement base class DbGUIElement method
        """
        #citation: citation-rebuild closes the editors, so no need to connect
        # to it
        self.callman.register_callbacks(
           {'citation-delete': self.citation_delete,
            'citation-update': self.citation_update,
           })
        self.callman.connect_all(keys=['citation'])

    def get_icon_name(self):
        """
        Return the stock-id icon name associated with the display tab
        """
        return 'gramps-source'

    def get_data(self):
        """
        Return the data associated with display tab
        """
        return self.data

    def column_order(self):
        """
        Return the column order of the columns in the display tab.
        """
        return ((1, 4), (1, 0), (1, 1), (1, 2), (1, 3))

    def add_button_clicked(self, obj):
        """
        Create a new Citation instance and call the EditCitation editor with
        the new citation.

        Called when the Add button is clicked.
        If the window already exists (WindowActiveError), we ignore it.
        This prevents the dialog from coming up twice on the same object.
        """
        try:
            from .. import EditCitation
            EditCitation(self.dbstate, self.uistate, self.track,
                         Citation(), Source(),
                         self.add_callback, self.callertitle)
        except WindowActiveError:
            pass

    def add_callback(self, value):
        """
        Called to update the screen when a new citation is added
        """
        data = self.get_data()
        data.append(value)
        self.callman.register_handles({'citation': [value]})
        self.changed = True
        self.rebuild()
        GLib.idle_add(self.tree.scroll_to_cell, len(data) - 1)

    def share_button_clicked(self, obj):
        SelectCitation = SelectorFactory('Citation')

        sel = SelectCitation(self.dbstate, self.uistate, self.track)
        object = sel.run()
        LOG.debug("selected object: %s" % object)
        # the object returned should either be a Source or a Citation
        if object:
            if isinstance(object, Source):
                try:
                    from .. import EditCitation
                    EditCitation(self.dbstate, self.uistate, self.track,
                                 Citation(), object,
                                 callback=self.add_callback,
                                 callertitle=self.callertitle)
                except WindowActiveError:
                    from ...dialog import WarningDialog
                    WarningDialog(_("Cannot share this reference"),
                                  self.__blocked_text(),
                                  parent=self.uistate.window)
            elif isinstance(object, Citation):
                try:
                    from .. import EditCitation
                    EditCitation(self.dbstate, self.uistate, self.track,
                                 object, callback=self.add_callback,
                                 callertitle=self.callertitle)
                except WindowActiveError:
                    from ...dialog import WarningDialog
                    WarningDialog(_("Cannot share this reference"),
                                  self.__blocked_text(),
                                  parent=self.uistate.window)
            else:
                raise ValueError("selection must be either source or citation")

    def __blocked_text(self):
        """
        Return the common text used when citation cannot be edited
        """
        return _("This citation cannot be created at this time. "
                    "Either the associated Source object is already being "
                    "edited, or another citation associated with the same "
                    "source is being edited.\n\nTo edit this "
                    "citation, you need to close the object.")

    def edit_button_clicked(self, obj):
        """
        Get the selected Citation instance and call the EditCitation editor
        with the citation.

        Called when the Edit button is clicked.
        If the window already exists (WindowActiveError), we ignore it.
        This prevents the dialog from coming up twice on the same object.
        """
        handle = self.get_selected()
        if handle:
            citation = self.dbstate.db.get_citation_from_handle(handle)
            try:
                from .. import EditCitation
                EditCitation(self.dbstate, self.uistate, self.track, citation,
                             callertitle = self.callertitle)
            except WindowActiveError:
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

    def _handle_drag(self, row, handle):
        """
        A CITATION_LINK has been dragged
        """
        if handle:
            object = self.dbstate.db.get_citation_from_handle(handle)
            if isinstance(object, Citation):
                try:
                    from .. import EditCitation
                    EditCitation(self.dbstate, self.uistate, self.track,
                                 object, callback=self.add_callback,
                                 callertitle=self.callertitle)
                except WindowActiveError:
                    from ...dialog import WarningDialog
                    WarningDialog(_("Cannot share this reference"),
                                  self.__blocked_text(),
                                  parent=self.uistate.window)
            else:
                raise ValueError("selection must be either source or citation")

    def handle_extra_type(self, objtype, handle):
        """
        A SOURCE_LINK object has been dragged
        """
        if handle:
            object = self.dbstate.db.get_source_from_handle(handle)
            if isinstance(object, Source):
                try:
                    from .. import EditCitation
                    EditCitation(self.dbstate, self.uistate, self.track,
                                 Citation(), object,
                                 callback=self.add_callback,
                                 callertitle=self.callertitle)
                except WindowActiveError:
                    from ...dialog import WarningDialog
                    WarningDialog(_("Cannot share this reference"),
                                  self.__blocked_text(),
                                  parent=self.uistate.window)
            else:
                raise ValueError("selection must be either source or citation")
