#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Name related utility functions
"""
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
from gen.display.name import displayer as name_displayer
from gen.ggettext import sgettext as _

#-------------------------------------------------------------------------
#
# Preset a name with a name of family member
#
#-------------------------------------------------------------------------

def preset_name(basepers, name, sibling=False):
    """Fill up name with all family common names of basepers. 
    If sibling=True, pa/matronymics are retained.
    """
    surnlist = []
    primname = basepers.get_primary_name()
    prim = False
    for surn in primname.get_surname_list():
        if (not sibling) and (surn.get_origintype().value in 
                        [gen.lib.NameOriginType.PATRONYMIC, 
                         gen.lib.NameOriginType.MATRONYMIC]):
            continue
        surnlist.append(gen.lib.Surname(source=surn))
        if surn.primary:
            prim=True
    if not surnlist:
        surnlist = [gen.lib.Surname()]
    name.set_surname_list(surnlist)
    if not prim:
        name.set_primary_surname(0)
    name.set_family_nick_name(primname.get_family_nick_name())
    name.set_group_as(primname.get_group_as())
    name.set_sort_as(primname.get_sort_as())

#-------------------------------------------------------------------------
#
# Short hand function to return either the person's name, or an empty
# string if the person is None
#
#-------------------------------------------------------------------------

def family_name(family, db, noname=_("unknown")):
    """Builds a name for the family from the parents names"""

    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    father = db.get_person_from_handle(father_handle)
    mother = db.get_person_from_handle(mother_handle)
    if father and mother:
        fname = name_displayer.display(father)
        mname = name_displayer.display(mother)
        name = _("%(father)s and %(mother)s") % {
                    "father" : fname, 
                    "mother" : mname}
    elif father:
        name = name_displayer.display(father)
    elif mother:
        name = name_displayer.display(mother)
    else:
        name = noname
    return name

def family_upper_name(family, db):
    """Builds a name for the family from the parents names"""
    father_handle = family.get_father_handle()
    mother_handle = family.get_mother_handle()
    father = db.get_person_from_handle(father_handle)
    mother = db.get_person_from_handle(mother_handle)
    if father and mother:
        fname = father.get_primary_name().get_upper_name()
        mname = mother.get_primary_name().get_upper_name()
        name = _("%(father)s and %(mother)s") % {
            'father' : fname, 
            'mother' : mname 
            }
    elif father:
        name = father.get_primary_name().get_upper_name()
    else:
        name = mother.get_primary_name().get_upper_name()
    return name
