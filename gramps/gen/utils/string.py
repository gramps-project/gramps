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
String mappings for constants
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..lib import Person, Citation, FamilyRelType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Integer to String mappings for constants
#
#-------------------------------------------------------------------------
gender = {
    Person.MALE    : _("male"), 
    Person.FEMALE  : _("female"), 
    Person.UNKNOWN : _("gender|unknown"), 
    }

def format_gender( type):
    return gender.get(type[0], _("Invalid"))

confidence = {
    Citation.CONF_VERY_HIGH : _("Very High"), 
    Citation.CONF_HIGH      : _("High"), 
    Citation.CONF_NORMAL    : _("Normal"), 
    Citation.CONF_LOW       : _("Low"), 
    Citation.CONF_VERY_LOW  : _("Very Low"), 
   }

family_rel_descriptions = {
    FamilyRelType.MARRIED     : _("A legal or common-law relationship "
                                         "between a husband and wife"), 
    FamilyRelType.UNMARRIED   : _("No legal or common-law relationship "
                                         "between man and woman"), 
    FamilyRelType.CIVIL_UNION : _("An established relationship between "
                                         "members of the same sex"), 
    FamilyRelType.UNKNOWN     : _("Unknown relationship between a man "
                                         "and woman"), 
    FamilyRelType.CUSTOM      : _("An unspecified relationship between "
                                         "a man and woman"), 
    }

data_recover_msg = _('The data can only be recovered by Undo operation '
            'or by quitting with abandoning changes.')
