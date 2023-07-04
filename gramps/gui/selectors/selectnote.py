#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009       Gary Burton
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

"""Handling of selection dialog for selecting notes
"""

#-------------------------------------------------------------------------
#
# Python Modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from ..views.treemodels import NoteModel
from .baseselector import BaseSelector
from gramps.gen.const import URL_MANUAL_SECT1

NOTE_DATE = None

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# SelectNote
#
#-------------------------------------------------------------------------
class SelectNote(BaseSelector):
    """ Class that handles the selection of a note
    """

    namespace = 'Note'

    def __init__(self, dbstate, uistate, track=[], title=None, filter=None,
                 skip=set(), show_search_bar=False, default=None):

        # SelectNote may have a title passed to it which should be used
        # instead of the default defined for get_window_title()
        if title is not None:
            self.title = title

        history = uistate.get_history(self.namespace).mru
        active_handle = uistate.get_active(self.namespace)

        # see gui.plug._guioptions

        from gramps.gen.filters import GenericFilterFactory, rules

        # Baseselector? rules.note.IsBookmarked?
        # Create a filter for the note selector.
        sfilter = GenericFilterFactory(self.namespace)()
        sfilter.set_logical_op('or')
        #sfilter.add_rule(rules.note.IsBookmarked([]))

        # Add recent notes.
        for handle in history:
            recent = dbstate.db.get_note_from_handle(handle)
            gid = recent.get_gramps_id()
            sfilter.add_rule(rules.note.HasIdOf([gid]))

        # Add bookmarked notes.
        for handle in dbstate.db.get_note_bookmarks().get():
            marked = dbstate.db.get_note_from_handle(handle)
            gid = marked.get_gramps_id()
            sfilter.add_rule(rules.note.HasIdOf([gid]))

        if active_handle:
            BaseSelector.__init__(self, dbstate, uistate, track, sfilter,
                                  skip, show_search_bar, active_handle)
        else:
            BaseSelector.__init__(self, dbstate, uistate, track, sfilter,
                                  skip, show_search_bar)

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.setup_configs('interface.note-sel', 600, 450)
        SWITCH = self.switch.get_state()

    def get_window_title(self):
        return _("Select Note")

    def get_model_class(self):
        return NoteModel

    def get_column_titles(self):
        return [
            (_('Preview'), 350, BaseSelector.TEXT, 0),
            (_('ID'),      75,  BaseSelector.TEXT, 1),
            (_('Type'),    100, BaseSelector.TEXT, 2),
            (_('Tags'),    100, BaseSelector.TEXT, 4),
            #(_('Last Change'), 150, BaseSelector.TEXT, 5),
            ]

    def get_from_handle_func(self):
        return self.db.get_note_from_handle

    WIKI_HELP_PAGE = URL_MANUAL_SECT1
    WIKI_HELP_SEC = _('Select_Note_selector', 'manual')
