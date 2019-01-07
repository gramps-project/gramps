#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
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
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ....utils.db import for_each_ancestor
from ._hascommonancestorwith import HasCommonAncestorWith
from ._matchesfilter import MatchesFilter

#-------------------------------------------------------------------------
#
# HasCommonAncestorWithFilterMatch
#
#-------------------------------------------------------------------------
class HasCommonAncestorWithFilterMatch(HasCommonAncestorWith):
    """Rule that checks for a person that has a common ancestor with
    someone matching a filter"""

    labels = [ _('Filter name:') ]
    name = _('People with a common ancestor with <filter> match')
    description = _("Matches people that have a common ancestor "
                    "with anybody matched by a filter")
    category = _("Ancestral filters")

    def __init__(self, list, use_regex=False):
        HasCommonAncestorWith.__init__(self, list, use_regex)
        self.ancestor_cache = {}

    def prepare(self, db, user):
        self.db = db
        # For each(!) person we keep track of who their ancestors
        # are, in a set(). So we only have to compute a person's
        # ancestor list once.
        # Start with filling the cache for root person (gramps_id in self.list[0])
        self.ancestor_cache = {}
        self.with_people = []
        self.filt = MatchesFilter(self.list)
        self.filt.requestprepare(db, user)
        if user:
            user.begin_progress(self.category,
                                _('Retrieving all sub-filter matches'),
                                db.get_number_of_people())
        for handle in db.iter_person_handles():
            person = db.get_person_from_handle(handle)
            if user:
                user.step_progress()
            if person and self.filt.apply(db, person):
                #store all people in the filter so as to compare later
                self.with_people.append(person.handle)
                #fill list of ancestor of person if not present yet
                if handle not in self.ancestor_cache:
                    self.add_ancs(db, person)
        if user:
            user.end_progress()

    def reset(self):
        self.filt.requestreset()
        self.ancestor_cache = {}
