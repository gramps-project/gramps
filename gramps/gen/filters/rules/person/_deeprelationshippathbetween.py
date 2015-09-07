#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Robert Ham <rah@bash.sh>
# Copyright (C) 2011 Adam Stein <adam@csh.rit.edu>
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
from .. import Rule
from . import MatchesFilter

#-------------------------------------------------------------------------
#
# DeepRelationshipPathBetween
#
#-------------------------------------------------------------------------

def filter_database(db, progress, filter_name):
    """Returns a list of person handles"""

    filt = MatchesFilter([filter_name])
    progress.set_header(_('Preparing sub-filter'))
    filt.requestprepare(db)

    progress.set_header(_('Retrieving all sub-filter matches'))
    matches = []
    for handle in db.iter_person_handles():
        person = db.get_person_from_handle(handle)
        if filt.apply(db, person):
            matches.append(handle)
        progress.step()

    filt.requestreset()

    return matches


def get_family_handle_people(db, exclude_handle, family_handle):
    people = set()

    family = db.get_family_from_handle(family_handle)

    def possibly_add_handle(h):
        if h != None and h != exclude_handle:
            people.add(db.get_person_from_handle(h))

    possibly_add_handle(family.get_father_handle())
    possibly_add_handle(family.get_mother_handle())

    for child_ref in family.get_child_ref_list():
        if child_ref:
            possibly_add_handle(child_ref.get_reference_handle())

    return people

def get_person_family_people(db, person, person_handle):
    people = set()

    def add_family_handle_list(list):
        for family_handle in list:
            people.update(get_family_handle_people(db, person_handle, family_handle))

    add_family_handle_list(person.get_family_handle_list())
    add_family_handle_list(person.get_parent_family_handle_list())

    return people

def find_deep_relations(db, progress, person, path, seen, target_people):
    if len(target_people) < 1:
        return []

    handle = person.get_handle()
    if handle in seen:
        return []
    seen.append(handle)

    return_paths = []
    person_path = path + [handle]

    if handle in target_people:
        return_paths += [person_path]
        target_people.remove(handle)

    family_people = get_person_family_people(db, person, handle)
    for family_person in family_people:
        return_paths += find_deep_relations(db, progress, family_person, person_path, seen, target_people)
        if progress: progress.step()

    return return_paths

class DeepRelationshipPathBetween(Rule):
    """Checks if there is any familial connection between a person and a
       filter match by searching over all connections."""

    labels      = [ _('ID:'), _('Filter name:') ]
    name        = _("Relationship path between <person> and people matching <filter>")
    category    = _('Relationship filters')
    description = _("Searches over the database starting from a specified person and"
                    " returns everyone between that person and a set of target people specified"
                    " with a filter.  This produces a set of relationship paths (including"
                    " by marriage) between the specified person and the target people."
                    "  Each path is not necessarily the shortest path.")

    def prepare(self, db):
        # FIXME: this should user the User class
        from gramps.gui.utils import ProgressMeter
        root_person_id = self.list[0]
        root_person = db.get_person_from_gramps_id(root_person_id)

        progress = ProgressMeter(_('Finding relationship paths'))
        progress.set_pass(header=_('Evaluating people'), mode=ProgressMeter.MODE_ACTIVITY)

        filter_name = self.list[1]
        target_people = filter_database(db, progress, filter_name)

        paths = find_deep_relations(db, progress, root_person, [], [], target_people)

        progress.close()
        progress = None

        self.__matches = set()
        list(map(self.__matches.update, paths))

    def reset(self):
        self.__matches = set()

    def apply(self, db, person):
        return person.get_handle() in self.__matches
