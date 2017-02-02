#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017
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

"""
Utilities to get labels for parents
"""
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib.person import Person
from gramps.gen.relationship import get_relationship_calculator

# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value):
    """ enable deferred translations (see Python docs 22.1.3.4) """
    return value

#-------------------------------------------------------------------------
#
# get labels for parents
#
#-------------------------------------------------------------------------
def parents(db, family, xlocale):
    """
    Get the label for parent
    """
    if family.get_father_handle(): #[0]
        father = db.get_person_from_handle(family.get_father_handle())
        if family.get_mother_handle():
            mother = db.get_person_from_handle(family.get_mother_handle())
        else:
            if father.gender == Person.FEMALE:
                return [_T_("Woman"), _T_("Person")]
            else:
                return [_T_("Man"), _T_("Person")]
    else:
        if family.get_mother_handle(): #[1]
            mother = db.get_person_from_handle(family.get_mother_handle())
            if mother.gender == Person.MALE:
                return [_T_("Person"), _T_("Man")]
        else:
            return [_T_("Person"), _T_("Person")]

    # need it for above strings and as fallback
    rel_father = _("Man")
    rel_mother = _("Woman")

    if len(family.get_child_ref_list()) > 0:
        rel_father = _T_("Father")
        rel_mother = _T_("Mother")
        if father.gender == Person.FEMALE:
            rel_father = rel_mother
        if mother.gender == Person.MALE:
            rel_mother = _T_("Father") # if both parents switched
    else:
        if family.get_father_handle() and family.get_mother_handle():
            rc = get_relationship_calculator(True, xlocale)
            rel_father = rc.get_one_relationship(db, mother, father, olocale=xlocale)
            rel_mother = rc.get_one_relationship(db, father, mother, olocale=xlocale)
        if xlocale.lang[0:2] == "fr":
            rel_father = rel_father.split()[-1]
            rel_mother = rel_mother.split()[-1]
        if xlocale.lang[0:2] not in ("ar", "he", "jp", "zh"):
            rel_father = rel_father.capitalize()
            rel_mother = rel_mother.capitalize()

    return [rel_father, rel_mother]
