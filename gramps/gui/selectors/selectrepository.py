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
from ..views.treemodels import RepositoryModel
from .baseselector import BaseSelector
from gramps.gen.const import URL_MANUAL_SECT2

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# SelectRepository
#
#-------------------------------------------------------------------------
class SelectRepository(BaseSelector):
    
    namespace = 'Repository'

    def __init__(self, dbstate, uistate, track=[], title=None, filter=None,
                 skip=set(), show_search_bar=False, default=None):

        # SelectRepository may have a title passed to it which should be used
        # instead of the default defined for get_window_title()
        if title is not None:
            self.title = title

        history = uistate.get_history(self.namespace).mru
        active_handle = uistate.get_active(self.namespace)

        # see gui.plug._guioptions

        from gramps.gen.filters import GenericFilterFactory, rules

        # Baseselector? rules.repository.IsBookmarked?
        # Create a filter for the repository selector.
        sfilter = GenericFilterFactory(self.namespace)()
        sfilter.set_logical_op('or')
        #sfilter.add_rule(rules.repository.IsBookmarked([]))

        # Add recent repositories.
        for handle in history:
            recent = dbstate.db.get_repository_from_handle(handle)
            gid = recent.get_gramps_id()
            sfilter.add_rule(rules.repository.HasIdOf([gid]))

        # Add bookmarked repositories.
        for handle in dbstate.db.get_repo_bookmarks().get():
            marked = dbstate.db.get_repository_from_handle(handle)
            gid = marked.get_gramps_id()
            sfilter.add_rule(rules.repository.HasIdOf([gid]))

        BaseSelector.__init__(self, dbstate, uistate, track, sfilter,
                              skip, show_search_bar, active_handle)

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.setup_configs('interface.repo-sel', 600, 450)
        SWITCH = self.switch.get_state()

    def get_window_title(self):
        return _("Select Repository")

    def get_model_class(self):
        return RepositoryModel

    def get_column_titles(self):
        return [
            (_('Title'), 350, BaseSelector.TEXT, 0),
            (_('ID'),     75, BaseSelector.TEXT, 1),
            #(_('Last Change'), 150, BaseSelector.TEXT, 14),
            ]

    def get_from_handle_func(self):
        return self.db.get_repository_from_handle

    WIKI_HELP_PAGE = URL_MANUAL_SECT2
    WIKI_HELP_SEC = _('Select_Repository_selector', 'manual')
