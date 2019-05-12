#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011  Benny Malengier
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
# gen.filters.rules/Source/_MatchesRepositoryFilter.py

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .. import MatchesFilterBase

#-------------------------------------------------------------------------
# "Sources which reference a repository by selection"
#-------------------------------------------------------------------------
class MatchesRepositoryFilter(MatchesFilterBase):
    """Sources which reference the selected repository"""

    labels = [ _('Repository filter name:') ]
    name = _('Sources with repository reference matching the <repository filter>')
    description = _("Matches sources with a repository reference that match a certain\n"
                  "repository filter")
    category = _('General filters')

    # we want to have this filter show repository filters
    namespace = 'Repository'


    def prepare(self, db, user):
        MatchesFilterBase.prepare(self, db, user)
        self.MRF_filt = self.find_filter()

    def apply(self, db, object):
        if self.MRF_filt is None :
            return False

        repolist = [x.ref for x in object.get_reporef_list()]
        for repohandle in repolist:
            #check if repo in repository filter
            if self.MRF_filt.check(db, repohandle):
                return True
        return False
