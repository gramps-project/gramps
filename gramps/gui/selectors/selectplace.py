#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Nick Hall
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
# internationalization
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from ..views.treemodels.placemodel import PlaceTreeModel
from .baseselector import BaseSelector
from .selectorexceptions import SelectorException
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# SelectPlace
#
#-------------------------------------------------------------------------
class Filter(object):

    def __init__(self, db):

        self.db = db

    def match(self, handle, db):

        value = self.db.get_raw_place_data(handle)
        if value[8][0] == "4":
            return value[2] == Gtk.TextIter.forward_search()

class SelectPlace(BaseSelector):
    
    namespace = 'Place'

    def __init__(self, dbstate, uistate, track=[], title=None, filter=None,
                 skip=set(), show_search_bar=False, default=None, expand=True):

        # Need purge the skip list, else it will only work the first time
        if len(skip) != 0:
            skip = []

        history = uistate.get_history(self.namespace).mru
        active_handle = uistate.get_active(self.namespace)

        # tests, Filter(dbstate.db)

        for handle in dbstate.db.get_place_handles():
            #print(dbstate.db.get_raw_place_data(handle)[2], dbstate.db.get_raw_place_data(handle)[8][0])
            skip.append(handle)

        for handle in dbstate.db.get_place_bookmarks().get():
            skip.remove(handle)

        for handle in history:
            if handle in skip:
                skip.remove(handle)

        # extra test
        # to check navigation, active and history
        if active_handle and (active_handle in skip):
            try:
                skip.remove(active_handle)
            except ValueError:
                pass
                #raise SelectorException("Attempt to remove "
                                #"active place record "
                                #"place handle = %s" % (active_handle,))
        # enclosed places
        for link in dbstate.db.find_backlink_handles(
                active_handle, include_classes=['Place']):
            if link[1] in skip:
                skip.remove(link[1])

        BaseSelector.__init__(self, dbstate, uistate, track, None,
                            [x for x in skip], True, active_handle, True)

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.setup_configs('interface.place-sel', 600, 450)
        SWITCH = self.switch.get_state() # nothing set yet

    def get_window_title(self):
        return _("Select Place")

    def get_model_class(self):
        return PlaceTreeModel
    
    def exact_search(self):
        """
        Returns a tuple indicating columns requiring an exact search
        """
        return (0,)

    def get_column_titles(self):
        return [
            (_('Name'),  200, BaseSelector.TEXT, 0),
            (_('ID'),    75,  BaseSelector.TEXT, 1),
            (_('Type'),  100, BaseSelector.TEXT, 3),
            (_('Title'), 300, BaseSelector.TEXT, 2),
            (_('Last Change'), 150, BaseSelector.TEXT, 9),
            ]

    def get_from_handle_func(self):
        return self.db.get_place_from_handle

    def setup_filter(self):
        """Build the default filters and add them to the filter menu.
        This overrides the baseselector method because we use the hidden
        COL_SEARCH (11) that has alt names as well as primary name for name
        searching"""
        cols = [(pair[3],
                 pair[1] if pair[1] else 11,
                 pair[0] in self.exact_search())
                for pair in self.column_order() if pair[0]
                ]
        self.search_bar.setup_filter(cols)

    WIKI_HELP_PAGE = URL_MANUAL_SECT2
    WIKI_HELP_SEC = _('Select_Place_selector', 'manual')
