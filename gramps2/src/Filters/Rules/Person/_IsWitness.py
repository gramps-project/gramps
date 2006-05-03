#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
# "Witnesses"
#-------------------------------------------------------------------------
class IsWitness(Rule):
    """Witnesses"""

    labels      = [_('Personal event:'), _('Family event:')]
    name        = _('Witnesses')
    description = _("Matches people who are witnesses in any event")
    category    = _('Event filters')

    def prepare(self,db):
        self.db = db
        self.map = []
        self.build_witness_list()

    def reset(self):
        self.map = []
        
    def apply(self,db,person):
        return person.handle in self.map

    def build_witness_list(self):
        for person_handle in self.db.get_person_handles():
            p = self.db.get_person_from_handle(person_handle)
            self.get_witness_of_events(self.list[0],
                                       p.get_event_ref_list()+
                                       [p.get_birth_ref(),
                                        p.get_death_ref()]
                                       )

        for family_handle in self.db.get_family_handles():
            f = self.db.get_family_from_handle(family_handle)
            self.get_witness_of_events(self.list[1],f.get_event_ref_list())

    def get_witness_of_events(self, event_type, event_list):
        if not event_list:
            return
        for event_ref in event_list:
            if event_ref:
                event = self.db.get_event_from_handle(event_ref.ref)
                if event_type and not event.get_name() == event_type:
                    continue
                wlist = event.get_witness_list()
                if wlist:
                    for w in wlist:
                        if w.get_type() == 1:
                            self.map.append(w.get_value())
