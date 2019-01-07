#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011  Benny Malengier
# Copyright (C) 2011  Tim G L Lyons
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
# Standard Python modules
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".citation")
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
    """Citations which have a source which references the selected repository"""

    labels = [ _('Repository filter name:') ]
    name = _('Citations with a source with a repository reference '
                    'matching the <repository filter>')
    description = _("Matches citations with sources with a repository "
                    "reference that match a certain repository filter")
    category = _('General filters')

    # we want to have this filter show repository filters
    namespace = 'Repository'


    def prepare(self, db, user):
        MatchesFilterBase.prepare(self, db, user)
        self.MRF_filt = self.find_filter()

    def apply(self, db, object):
        if self.MRF_filt is None :
            return False

        source_handle = object.source_handle
        source = db.get_source_from_handle(source_handle)
        repolist = [x.ref for x in source.get_reporef_list()]
        for repohandle in repolist:
            #check if repo in repository filter
            if self.MRF_filt.check(db, repohandle):
                return True
        return False
