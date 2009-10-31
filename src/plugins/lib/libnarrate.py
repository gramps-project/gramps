#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009  Brian G. Matherly
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
Narrator class for use by plugins.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.lib.date import Date
from gen.lib.person import Person
from gen.lib.eventroletype import EventRoleType
from gen.lib.eventtype import EventType
from gen.lib.familyreltype import FamilyRelType
from BasicUtils import name_displayer as _nd
import DateHandler
import Utils
from ReportBase import ReportUtils

#-------------------------------------------------------------------------
#
# Support functions
#
#-------------------------------------------------------------------------
def empty_notes(whatever):
    """
    Empty stab function for when endnotes are not needed
    """
    return ""

#------------------------------------------------------------------------
#
# Born strings
#
#------------------------------------------------------------------------

born_full_date_with_place = [
  {
    Person.UNKNOWN :  _("This person was born on %(birth_date)s in %(birth_place)s."), 
    Person.MALE :  _("He was born on %(birth_date)s in %(birth_place)s."), 
    Person.FEMALE : _("She was born on %(birth_date)s in %(birth_place)s."), 
  }, 
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born on %(birth_date)s in %(birth_place)s."), 
    Person.MALE : _("%(male_name)s was born on %(birth_date)s in %(birth_place)s."), 
    Person.FEMALE : _("%(female_name)s was born on %(birth_date)s in %(birth_place)s."), 
  },
  _("Born %(birth_date)s in %(birth_place)s."), 
]

born_modified_date_with_place = [
  {
    Person.UNKNOWN :  _("This person was born %(modified_date)s in %(birth_place)s."), 
    Person.MALE :  _("He was born %(modified_date)s in %(birth_place)s."), 
    Person.FEMALE : _("She was born %(modified_date)s in %(birth_place)s."), 
  }, 
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born %(modified_date)s in %(birth_place)s."), 
    Person.MALE : _("%(male_name)s was born %(modified_date)s in %(birth_place)s."), 
    Person.FEMALE : _("%(female_name)s was born %(modified_date)s in %(birth_place)s."), 
  },
  _("Born %(modified_date)s in %(birth_place)s."), 
]

born_full_date_no_place = [
  {
    Person.UNKNOWN : _("This person was born on %(birth_date)s."), 
    Person.MALE : _("He was born on %(birth_date)s."), 
    Person.FEMALE : _("She was born on %(birth_date)s."), 
  }, 
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born on %(birth_date)s."), 
    Person.MALE : _("%(male_name)s was born on %(birth_date)s."), 
    Person.FEMALE : _("%(female_name)s was born on %(birth_date)s."), 
  },
  _("Born %(birth_date)s."), 
]  

born_modified_date_no_place = [
  {
    Person.UNKNOWN : _("This person was born %(modified_date)s."), 
    Person.MALE : _("He was born %(modified_date)s."), 
    Person.FEMALE : _("She was born %(modified_date)s."), 
  }, 
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born %(modified_date)s."), 
    Person.MALE : _("%(male_name)s was born %(modified_date)s."), 
    Person.FEMALE : _("%(female_name)s was born %(modified_date)s."), 
  }, 
   _("Born %(modified_date)s."),
]  

born_partial_date_with_place = [
  {
    Person.UNKNOWN : _("This person was born in %(month_year)s in %(birth_place)s."), 
    Person.MALE : _("He was born in %(month_year)s in %(birth_place)s."), 
    Person.FEMALE : _("She was born in %(month_year)s in %(birth_place)s."), 
  }, 
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(month_year)s in %(birth_place)s."), 
    Person.MALE : _("%(male_name)s was born in %(month_year)s in %(birth_place)s."), 
    Person.FEMALE : _("%(female_name)s was born in %(month_year)s in %(birth_place)s."), 
  }, 
  _("Born %(month_year)s in %(birth_place)s."),
]  

born_partial_date_no_place = [
  {
    Person.UNKNOWN : _("This person was born in %(month_year)s."), 
    Person.MALE : _("He was born in %(month_year)s."), 
    Person.FEMALE : _("She was born in %(month_year)s."), 
  }, 
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(month_year)s."), 
    Person.MALE : _("%(male_name)s was born in %(month_year)s."), 
    Person.FEMALE : _("%(female_name)s was born in %(month_year)s."), 
  },
  _("Born %(month_year)s."),
]  

born_no_date_with_place = [
  {
    Person.UNKNOWN : _("This person was born in %(birth_place)s."), 
    Person.MALE : _("He was born in %(birth_place)s."), 
    Person.FEMALE : _("She was born in %(birth_place)s."), 
  }, 
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(birth_place)s."), 
    Person.MALE : _("%(male_name)s was born in %(birth_place)s."), 
    Person.FEMALE : _("%(female_name)s was born in %(birth_place)s."), 
  },
  _("Born in %(birth_place)s."),
]  

#------------------------------------------------------------------------
#
# Died strings
#
#------------------------------------------------------------------------

died_full_date_with_place = [
  { Person.UNKNOWN : [
    _("This person died on %(death_date)s in %(death_place)s."), 
    _("This person died on %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("This person died on %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("This person died on %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("He died on %(death_date)s in %(death_place)s."), 
    _("He died on %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("He died on %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("He died on %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("She died on %(death_date)s in %(death_place)s."), 
    _("She died on %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("She died on %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("She died on %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
  }, 
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s."), 
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("%(male_name)s died on %(death_date)s in %(death_place)s."), 
    _("%(male_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("%(male_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("%(male_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("%(female_name)s died on %(death_date)s in %(death_place)s."), 
    _("%(female_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("%(female_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("%(female_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
  },
  [
  _("Died %(death_date)s in %(death_place)s."),
  _("Died %(death_date)s in %(death_place)s (age %(age)d years)."),
  _("Died %(death_date)s in %(death_place)s (age %(age)d months)."),
  _("Died %(death_date)s in %(death_place)s (age %(age)d days)."),
  ], 
]

died_modified_date_with_place = [
  { Person.UNKNOWN : [
    _("This person died %(death_date)s in %(death_place)s."), 
    _("This person died %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("This person died %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("This person died %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("He died %(death_date)s in %(death_place)s."), 
    _("He died %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("He died %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("He died %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("She died %(death_date)s in %(death_place)s."), 
    _("She died %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("She died %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("She died %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
  }, 
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s."), 
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("%(male_name)s died %(death_date)s in %(death_place)s."), 
    _("%(male_name)s died %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("%(male_name)s died %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("%(male_name)s died %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("%(female_name)s died %(death_date)s in %(death_place)s."), 
    _("%(female_name)s died %(death_date)s in %(death_place)s at the age of %(age)d years."), 
    _("%(female_name)s died %(death_date)s in %(death_place)s at the age of %(age)d months."), 
    _("%(female_name)s died %(death_date)s in %(death_place)s at the age of %(age)d days."), 
    ], 
  },
  [
  _("Died %(death_date)s in %(death_place)s."),
  _("Died %(death_date)s in %(death_place)s (age %(age)d years)."),
  _("Died %(death_date)s in %(death_place)s (age %(age)d months)."),
  _("Died %(death_date)s in %(death_place)s (age %(age)d days)."),
  ], 
]

died_full_date_no_place = [
  { Person.UNKNOWN : [
    _("This person died on %(death_date)s."), 
    _("This person died on %(death_date)s at the age of %(age)d years."), 
    _("This person died on %(death_date)s at the age of %(age)d months."), 
    _("This person died on %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("He died on %(death_date)s."), 
    _("He died on %(death_date)s at the age of %(age)d years."), 
    _("He died on %(death_date)s at the age of %(age)d months."), 
    _("He died on %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("She died on %(death_date)s."), 
    _("She died on %(death_date)s at the age of %(age)d years."), 
    _("She died on %(death_date)s at the age of %(age)d months."), 
    _("She died on %(death_date)s at the age of %(age)d days."), 
    ], 
  }, 
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died on %(death_date)s."), 
    _("%(unknown_gender_name)s died on %(death_date)s at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died on %(death_date)s at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died on %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("%(male_name)s died on %(death_date)s."), 
    _("%(male_name)s died on %(death_date)s at the age of %(age)d years."), 
    _("%(male_name)s died on %(death_date)s at the age of %(age)d months."), 
    _("%(male_name)s died on %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("%(female_name)s died on %(death_date)s."), 
    _("%(female_name)s died on %(death_date)s at the age of %(age)d years."), 
    _("%(female_name)s died on %(death_date)s at the age of %(age)d months."), 
    _("%(female_name)s died on %(death_date)s at the age of %(age)d days."), 
    ], 
  },
  [
  _("Died %(death_date)s."),
  _("Died %(death_date)s (age %(age)d years)."),
  _("Died %(death_date)s (age %(age)d months)."),
  _("Died %(death_date)s (age %(age)d days)."),
  ], 
]  

died_modified_date_no_place = [
  { Person.UNKNOWN : [
    _("This person died %(death_date)s."), 
    _("This person died %(death_date)s at the age of %(age)d years."), 
    _("This person died %(death_date)s at the age of %(age)d months."), 
    _("This person died %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("He died %(death_date)s."), 
    _("He died %(death_date)s at the age of %(age)d years."), 
    _("He died %(death_date)s at the age of %(age)d months."), 
    _("He died %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("She died %(death_date)s."), 
    _("She died %(death_date)s at the age of %(age)d years."), 
    _("She died %(death_date)s at the age of %(age)d months."), 
    _("She died %(death_date)s at the age of %(age)d days."), 
    ], 
  }, 
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died %(death_date)s."), 
    _("%(unknown_gender_name)s died %(death_date)s at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died %(death_date)s at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("%(male_name)s died %(death_date)s."), 
    _("%(male_name)s died %(death_date)s at the age of %(age)d years."), 
    _("%(male_name)s died %(death_date)s at the age of %(age)d months."), 
    _("%(male_name)s died %(death_date)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("%(female_name)s died %(death_date)s."), 
    _("%(female_name)s died %(death_date)s at the age of %(age)d years."), 
    _("%(female_name)s died %(death_date)s at the age of %(age)d months."), 
    _("%(female_name)s died %(death_date)s at the age of %(age)d days."), 
    ], 
  },
  [
  _("Died %(death_date)s."),
  _("Died %(death_date)s (age %(age)d years)."),
  _("Died %(death_date)s (age %(age)d months)."),
  _("Died %(death_date)s (age %(age)d days)."),
  ], 
]  

died_partial_date_with_place = [
  { Person.UNKNOWN : [
    _("This person died in %(month_year)s in %(death_place)s."), 
    _("This person died in %(month_year)s in %(death_place)s at the age of %(age)d years."), 
    _("This person died in %(month_year)s in %(death_place)s at the age of %(age)d months."), 
    _("This person died in %(month_year)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("He died in %(month_year)s in %(death_place)s."), 
    _("He died in %(month_year)s in %(death_place)s at the age of %(age)d years."), 
    _("He died in %(month_year)s in %(death_place)s at the age of %(age)d months."), 
    _("He died in %(month_year)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("She died in %(month_year)s in %(death_place)s."), 
    _("She died in %(month_year)s in %(death_place)s at the age of %(age)d years."), 
    _("She died in %(month_year)s in %(death_place)s at the age of %(age)d months."), 
    _("She died in %(month_year)s in %(death_place)s at the age of %(age)d days."), 
    ]
  }, 
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s."), 
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("%(male_name)s died in %(month_year)s in %(death_place)s."), 
    _("%(male_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d years."), 
    _("%(male_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d months."), 
    _("%(male_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("%(female_name)s died in %(month_year)s in %(death_place)s."), 
    _("%(female_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d years."), 
    _("%(female_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d months."), 
    _("%(female_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d days."), 
    ], 
  },
  [
  _("Died %(month_year)s in %(death_place)s."),
  _("Died %(month_year)s in %(death_place)s (age %(age)d years)."),
  _("Died %(month_year)s in %(death_place)s (age %(age)d months)."),
  _("Died %(month_year)s in %(death_place)s (age %(age)d days)."),
  ], 
]  

died_partial_date_no_place = [
  { Person.UNKNOWN : [
    _("This person died in %(month_year)s."), 
    _("This person died in %(month_year)s at the age of %(age)d years."), 
    _("This person died in %(month_year)s at the age of %(age)d months."), 
    _("This person died in %(month_year)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("He died in %(month_year)s."), 
    _("He died in %(month_year)s at the age of %(age)d years."), 
    _("He died in %(month_year)s at the age of %(age)d months."), 
    _("He died in %(month_year)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("She died in %(month_year)s."), 
    _("She died in %(month_year)s at the age of %(age)d years."), 
    _("She died in %(month_year)s at the age of %(age)d months."), 
    _("She died in %(month_year)s at the age of %(age)d days."), 
    ], 
  }, 
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(month_year)s."), 
    _("%(unknown_gender_name)s died in %(month_year)s at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died in %(month_year)s at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died in %(month_year)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("%(male_name)s died in %(month_year)s."), 
    _("%(male_name)s died in %(month_year)s at the age of %(age)d years."), 
    _("%(male_name)s died in %(month_year)s at the age of %(age)d months."), 
    _("%(male_name)s died in %(month_year)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("%(female_name)s died in %(month_year)s."), 
    _("%(female_name)s died in %(month_year)s at the age of %(age)d years."), 
    _("%(female_name)s died in %(month_year)s at the age of %(age)d months."), 
    _("%(female_name)s died in %(month_year)s at the age of %(age)d days."), 
    ], 
  },
  [
  _("Died %(month_year)s."),
  _("Died %(month_year)s (age %(age)d years)."),
  _("Died %(month_year)s (age %(age)d months)."),
  _("Died %(month_year)s (age %(age)d days)."),
  ],
]  

died_no_date_with_place = [
  {
    Person.UNKNOWN : [
    _("This person died in %(death_place)s."), 
    _("This person died in %(death_place)s at the age of %(age)d years."), 
    _("This person died in %(death_place)s at the age of %(age)d months."), 
    _("This person died in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("He died in %(death_place)s."), 
    _("He died in %(death_place)s at the age of %(age)d years."), 
    _("He died in %(death_place)s at the age of %(age)d months."), 
    _("He died in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("She died in %(death_place)s."), 
    _("She died in %(death_place)s at the age of %(age)d years."), 
    _("She died in %(death_place)s at the age of %(age)d months."), 
    _("She died in %(death_place)s at the age of %(age)d days."), 
    ], 
  }, 
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(death_place)s."), 
    _("%(unknown_gender_name)s died in %(death_place)s at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died in %(death_place)s at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    _("%(male_name)s died in %(death_place)s."), 
    _("%(male_name)s died in %(death_place)s at the age of %(age)d years."), 
    _("%(male_name)s died in %(death_place)s at the age of %(age)d months."), 
    _("%(male_name)s died in %(death_place)s at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    _("%(female_name)s died in %(death_place)s."), 
    _("%(female_name)s died in %(death_place)s at the age of %(age)d years."), 
    _("%(female_name)s died in %(death_place)s at the age of %(age)d months."), 
    _("%(female_name)s died in %(death_place)s at the age of %(age)d days."), 
    ], 
  },
  [
  _("Died in %(death_place)s."),
  _("Died in %(death_place)s (age %(age)d years)."),
  _("Died in %(death_place)s (age %(age)d months)."),
  _("Died in %(death_place)s (age %(age)d days)."),
  ],
]  

died_no_date_no_place = [
  { Person.UNKNOWN : [
    "", 
    _("This person died at the age of %(age)d years."), 
    _("This person died at the age of %(age)d months."), 
    _("This person died at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    "", 
    _("He died at the age of %(age)d years."), 
    _("He died at the age of %(age)d months."), 
    _("He died at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    "", 
    _("She died at the age of %(age)d years."), 
    _("She died at the age of %(age)d months."), 
    _("She died at the age of %(age)d days."), 
    ], 
  }, 
  { Person.UNKNOWN : [
    "", 
    _("%(unknown_gender_name)s died at the age of %(age)d years."), 
    _("%(unknown_gender_name)s died at the age of %(age)d months."), 
    _("%(unknown_gender_name)s died at the age of %(age)d days."), 
    ], 
    Person.MALE : [
    "", 
    _("%(male_name)s died at the age of %(age)d years."), 
    _("%(male_name)s died at the age of %(age)d months."), 
    _("%(male_name)s died at the age of %(age)d days."), 
    ], 
    Person.FEMALE : [
    "", 
    _("%(female_name)s died at the age of %(age)d years."), 
    _("%(female_name)s died at the age of %(age)d months."), 
    _("%(female_name)s died at the age of %(age)d days."), 
    ], 
  },
  [
  "",
  _("Died (age %(age)d years)."),
  _("Died (age %(age)d months)."),
  _("Died (age %(age)d days)."),
  ], 
]


#------------------------------------------------------------------------
#
# Buried strings
#
#------------------------------------------------------------------------

buried_full_date_place = {
    Person.MALE: [
    _("%(male_name)s was buried on %(burial_date)s in %(burial_place)s%(endnotes)s."), 
    _("He was buried on %(burial_date)s in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was buried on %(burial_date)s in %(burial_place)s%(endnotes)s."), 
    _("She was buried on %(burial_date)s in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried on %(burial_date)s in %(burial_place)s%(endnotes)s."), 
    _("This person was buried on %(burial_date)s in %(burial_place)s%(endnotes)s."), 
    ], 
    'succinct' : _("Buried %(burial_date)s in %(burial_place)s%(endnotes)s."),
    }

buried_full_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was buried on %(burial_date)s%(endnotes)s."), 
    _("He was buried on %(burial_date)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was buried on %(burial_date)s%(endnotes)s."), 
    _("She was buried on %(burial_date)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried on %(burial_date)s%(endnotes)s."), 
    _("This person was buried on %(burial_date)s%(endnotes)s."), 
    ], 
    'succinct' : _("Buried %(burial_date)s%(endnotes)s."),
    }

buried_partial_date_place = {
    Person.MALE: [
    _("%(male_name)s was buried in %(month_year)s in %(burial_place)s%(endnotes)s."), 
    _("He was buried in %(month_year)s in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was buried in %(month_year)s in %(burial_place)s%(endnotes)s."), 
    _("She was buried in %(month_year)s in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried in %(month_year)s in %(burial_place)s%(endnotes)s."), 
    _("This person was buried in %(month_year)s in %(burial_place)s%(endnotes)s."), 
    ], 
    'succinct' : _("Buried %(month_year)s in %(burial_place)s%(endnotes)s."),
    }

buried_partial_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was buried in %(month_year)s%(endnotes)s."), 
    _("He was buried in %(month_year)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was buried in %(month_year)s%(endnotes)s."), 
    _("She was buried in %(month_year)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried in %(month_year)s%(endnotes)s."), 
    _("This person was buried in %(month_year)s%(endnotes)s."), 
    ], 
    'succinct' : _("Buried %(month_year)s%(endnotes)s."),
    }

buried_modified_date_place = {
    Person.MALE: [
    _("%(male_name)s was buried %(modified_date)s in %(burial_place)s%(endnotes)s."), 
    _("He was buried %(modified_date)s in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was buried %(modified_date)s in %(burial_place)s%(endnotes)s."), 
    _("She was buried %(modified_date)s in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried %(modified_date)s in %(burial_place)s%(endnotes)s."), 
    _("This person was buried %(modified_date)s in %(burial_place)s%(endnotes)s."), 
    ], 
    'succinct' : _("Buried %(modified_date)s in %(burial_place)s%(endnotes)s."),
    }

buried_modified_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was buried %(modified_date)s%(endnotes)s."), 
    _("He was buried %(modified_date)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was buried %(modified_date)s%(endnotes)s."), 
    _("She was buried %(modified_date)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried %(modified_date)s%(endnotes)s."), 
    _("This person was buried %(modified_date)s%(endnotes)s."), 
    ], 
    'succinct' : _("Buried %(modified_date)s%(endnotes)s."),
    }

buried_no_date_place = {
    Person.MALE    : [
    _("%(male_name)s was buried in %(burial_place)s%(endnotes)s."), 
    _("He was buried in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE  : [
    _("%(female_name)s was buried in %(burial_place)s%(endnotes)s."), 
    _("She was buried in %(burial_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was buried in %(burial_place)s%(endnotes)s."), 
    _("This person was buried in %(burial_place)s%(endnotes)s."), 
    ], 
    'succinct' : _("Buried in %(burial_place)s%(endnotes)s."),
    }

buried_no_date_no_place = {
    Person.MALE    : [
    _("%(male_name)s was buried%(endnotes)s."), 
    _("He was buried%(endnotes)s."), 
    ], 
    Person.FEMALE  : [
    _("%(female_name)s was buried%(endnotes)s."), 
    _("She was buried%(endnotes)s."), 
    ], 
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was buried%(endnotes)s."), 
    _("This person was buried%(endnotes)s."), 
    ],
    'succinct' : _("Buried%(endnotes)s."),
 
   }
#------------------------------------------------------------------------
#
# Baptised strings
#
#------------------------------------------------------------------------

baptised_full_date_place = {
    Person.MALE: [
    _("%(male_name)s was baptised on %(baptism_date)s in %(baptism_place)s%(endnotes)s."), 
    _("He was baptised on %(baptism_date)s in %(baptism_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was baptised on %(baptism_date)s in %(baptism_place)s%(endnotes)s."), 
    _("She was baptised on %(baptism_date)s in %(baptism_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [ 
    _("%(unknown_gender_name)s was baptised on %(baptism_date)s in %(baptism_place)s%(endnotes)s."), 
    _("This person was baptised on %(baptism_date)s in %(baptism_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Baptised %(baptism_date)s in %(baptism_place)s%(endnotes)s."), 
    }

baptised_full_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was baptised on %(baptism_date)s%(endnotes)s."), 
    _("He was baptised on %(baptism_date)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was baptised on %(baptism_date)s%(endnotes)s."), 
    _("She was baptised on %(baptism_date)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptised on %(baptism_date)s%(endnotes)s."), 
    _("This person was baptised on %(baptism_date)s%(endnotes)s."), 
    ],
    'succinct' : _("Baptised %(baptism_date)s%(endnotes)s.") 
    }

baptised_partial_date_place = {
    Person.MALE: [
    _("%(male_name)s was baptised in %(month_year)s in %(baptism_place)s%(endnotes)s."), 
    _("He was baptised in %(month_year)s in %(baptism_place)s%(endnotes)s."), 
    ], 
Person.FEMALE: [
    _("%(female_name)s was baptised in %(month_year)s in %(baptism_place)s%(endnotes)s."), 
    _("She was baptised in %(month_year)s in %(baptism_place)s%(endnotes)s."), 
    ], 
Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptised in %(month_year)s in %(baptism_place)s%(endnotes)s."), 
    _("This person was baptised in %(month_year)s in %(baptism_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Baptised %(month_year)s in %(baptism_place)s%(endnotes)s."), 
    }

baptised_partial_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was baptised in %(month_year)s%(endnotes)s."), 
    _("He was baptised in %(month_year)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was baptised in %(month_year)s%(endnotes)s."), 
    _("She was baptised in %(month_year)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptised in %(month_year)s%(endnotes)s."), 
    _("This person was baptised in %(month_year)s%(endnotes)s."), 
    ],
    'succinct' : _("Baptised %(month_year)s%(endnotes)s."), 
    }

baptised_modified_date_place = {
    Person.MALE: [
    _("%(male_name)s was baptised %(modified_date)s in %(baptism_place)s%(endnotes)s."), 
    _("He was baptised %(modified_date)s in %(baptism_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was baptised %(modified_date)s in %(baptism_place)s%(endnotes)s."), 
    _("She was baptised %(modified_date)s in %(baptism_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptised %(modified_date)s in %(baptism_place)s%(endnotes)s."), 
    _("This person was baptised %(modified_date)s in %(baptism_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Baptised %(modified_date)s in %(baptism_place)s%(endnotes)s."), 
    }

baptised_modified_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was baptised %(modified_date)s%(endnotes)s."), 
    _("He was baptised %(modified_date)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was baptised %(modified_date)s%(endnotes)s."), 
    _("She was baptised %(modified_date)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptised %(modified_date)s%(endnotes)s."), 
    _("This person was baptised %(modified_date)s%(endnotes)s."), 
    ],
    'succinct' : _("Baptised %(modified_date)s%(endnotes)s."), 
    }

baptised_no_date_place = {
    Person.MALE    : [
    _("%(male_name)s was baptised in %(baptism_place)s%(endnotes)s."), 
    _("He was baptised in %(baptism_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE  : [
    _("%(female_name)s was baptised in %(baptism_place)s%(endnotes)s."), 
    _("She was baptised in %(baptism_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was baptised in %(baptism_place)s%(endnotes)s."), 
    _("This person was baptised in %(baptism_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Baptised in %(baptism_place)s%(endnotes)s."), 
    }

baptised_no_date_no_place = {
    Person.MALE    : [
    _("%(male_name)s was baptised%(endnotes)s."), 
    _("He was baptised%(endnotes)s."), 
    ], 
    Person.FEMALE  : [
    _("%(female_name)s was baptised%(endnotes)s."), 
    _("She was baptised%(endnotes)s."), 
    ], 
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was baptised%(endnotes)s."), 
    _("This person was baptised%(endnotes)s."), 
    ],
    'succinct' : _("Baptised%(endnotes)s."),
    }

#------------------------------------------------------------------------
#
# Christened strings
#
#------------------------------------------------------------------------

christened_full_date_place = {
    Person.MALE: [
    _("%(male_name)s was christened on %(christening_date)s in %(christening_place)s%(endnotes)s."), 
    _("He was christened on %(christening_date)s in %(christening_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was christened on %(christening_date)s in %(christening_place)s%(endnotes)s."), 
    _("She was christened on %(christening_date)s in %(christening_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [ 
    _("%(unknown_gender_name)s was christened on %(christening_date)s in %(christening_place)s%(endnotes)s."), 
    _("This person was christened on %(christening_date)s in %(christening_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Christened %(christening_date)s in %(christening_place)s%(endnotes)s."), 
    }

christened_full_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was christened on %(christening_date)s%(endnotes)s."), 
    _("He was christened on %(christening_date)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was christened on %(christening_date)s%(endnotes)s."), 
    _("She was christened on %(christening_date)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was christened on %(christening_date)s%(endnotes)s."), 
    _("This person was christened on %(christening_date)s%(endnotes)s."), 
    ],
    'succinct' : _("Christened %(christening_date)s%(endnotes)s.") 
    }

christened_partial_date_place = {
    Person.MALE: [
    _("%(male_name)s was christened in %(month_year)s in %(christening_place)s%(endnotes)s."), 
    _("He was christened in %(month_year)s in %(christening_place)s%(endnotes)s."), 
    ], 
Person.FEMALE: [
    _("%(female_name)s was christened in %(month_year)s in %(christening_place)s%(endnotes)s."), 
    _("She was christened in %(month_year)s in %(christening_place)s%(endnotes)s."), 
    ], 
Person.UNKNOWN: [
    _("%(unknown_gender_name)s was christened in %(month_year)s in %(christening_place)s%(endnotes)s."), 
    _("This person was christened in %(month_year)s in %(christening_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Christened %(month_year)s in %(christening_place)s%(endnotes)s."), 
    }

christened_partial_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was christened in %(month_year)s%(endnotes)s."), 
    _("He was christened in %(month_year)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was christened in %(month_year)s%(endnotes)s."), 
    _("She was christened in %(month_year)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was christened in %(month_year)s%(endnotes)s."), 
    _("This person was christened in %(month_year)s%(endnotes)s."), 
    ],
    'succinct' : _("Christened %(month_year)s%(endnotes)s."), 
    }

christened_modified_date_place = {
    Person.MALE: [
    _("%(male_name)s was christened %(modified_date)s in %(christening_place)s%(endnotes)s."), 
    _("He was christened %(modified_date)s in %(christening_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was christened %(modified_date)s in %(christening_place)s%(endnotes)s."), 
    _("She was christened %(modified_date)s in %(christening_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was christened %(modified_date)s in %(christening_place)s%(endnotes)s."), 
    _("This person was christened %(modified_date)s in %(christening_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Christened %(modified_date)s in %(christening_place)s%(endnotes)s."), 
    }

christened_modified_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was christened %(modified_date)s%(endnotes)s."), 
    _("He was christened %(modified_date)s%(endnotes)s."), 
    ], 
    Person.FEMALE: [
    _("%(female_name)s was christened %(modified_date)s%(endnotes)s."), 
    _("She was christened %(modified_date)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was christened %(modified_date)s%(endnotes)s."), 
    _("This person was christened %(modified_date)s%(endnotes)s."), 
    ],
    'succinct' : _("Christened %(modified_date)s%(endnotes)s."), 
    }

christened_no_date_place = {
    Person.MALE    : [
    _("%(male_name)s was christened in %(christening_place)s%(endnotes)s."), 
    _("He was christened in %(christening_place)s%(endnotes)s."), 
    ], 
    Person.FEMALE  : [
    _("%(female_name)s was christened in %(christening_place)s%(endnotes)s."), 
    _("She was christened in %(christening_place)s%(endnotes)s."), 
    ], 
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was christened in %(christening_place)s%(endnotes)s."), 
    _("This person was christened in %(christening_place)s%(endnotes)s."), 
    ],
    'succinct' : _("Christened in %(christening_place)s%(endnotes)s."), 
    }

christened_no_date_no_place = {
    Person.MALE    : [
    _("%(male_name)s was christened%(endnotes)s."), 
    _("He was christened%(endnotes)s."), 
    ], 
    Person.FEMALE  : [
    _("%(female_name)s was christened%(endnotes)s."), 
    _("She was christened%(endnotes)s."), 
    ], 
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was christened%(endnotes)s."), 
    _("This person was christened%(endnotes)s."), 
    ],
    'succinct' : _("Christened%(endnotes)s."),
    }

#-------------------------------------------------------------------------
#
#  child to parent relationships
#
#-------------------------------------------------------------------------

child_father_mother = {
    Person.UNKNOWN: [
      [
        _("This person is the child of %(father)s and %(mother)s."), 
        _("This person was the child of %(father)s and %(mother)s."), 
      ], 
      [
        _("%(male_name)s is the child of %(father)s and %(mother)s."), 
        _("%(male_name)s was the child of %(father)s and %(mother)s."), 
      ],
      _("Child of %(father)s and %(mother)s."), 
    ], 
    Person.MALE : [
      [
        _("He is the son of %(father)s and %(mother)s."), 
        _("He was the son of %(father)s and %(mother)s."), 
      ], 
      [
        _("%(male_name)s is the son of %(father)s and %(mother)s."), 
        _("%(male_name)s was the son of %(father)s and %(mother)s."), 
      ],
      _("Son of %(father)s and %(mother)s."),
    ], 
    Person.FEMALE : [
     [
        _("She is the daughter of %(father)s and %(mother)s."), 
        _("She was the daughter of %(father)s and %(mother)s."), 
     ], 
     [
        _("%(female_name)s is the daughter of %(father)s and %(mother)s."), 
        _("%(female_name)s was the daughter of %(father)s and %(mother)s."), 
     ],
     _("Daughter of %(father)s and %(mother)s."), 
    ]
}

child_father = {
    Person.UNKNOWN : [
      [
        _("This person is the child of %(father)s."), 
        _("This person was the child of %(father)s."), 
      ], 
      [
        _("%(male_name)s is the child of %(father)s."), 
        _("%(male_name)s was the child of %(father)s."), 
      ],
      _("Child of %(father)s."), 
    ], 
    Person.MALE : [
      [
        _("He is the son of %(father)s."), 
        _("He was the son of %(father)s."), 
      ], 
      [
        _("%(male_name)s is the son of %(father)s."), 
        _("%(male_name)s was the son of %(father)s."), 
      ],
      _("Son of %(father)s."), 
    ], 
    Person.FEMALE : [
      [
        _("She is the daughter of %(father)s."), 
        _("She was the daughter of %(father)s."), 
      ],  
      [
        _("%(female_name)s is the daughter of %(father)s."), 
        _("%(female_name)s was the daughter of %(father)s."), 
      ],
      _("Daughter of %(father)s."), 
    ], 
}

child_mother = {
    Person.UNKNOWN : [
      [
        _("This person is the child of %(mother)s."), 
        _("This person was the child of %(mother)s."), 
      ], 
      [
        _("%(male_name)s is the child of %(mother)s."), 
        _("%(male_name)s was the child of %(mother)s."), 
      ],
      _("Child of %(mother)s."), 
    ], 
    Person.MALE : [
      [
        _("He is the son of %(mother)s."), 
        _("He was the son of %(mother)s."), 
      ], 
      [
        _("%(male_name)s is the son of %(mother)s."), 
        _("%(male_name)s was the son of %(mother)s."), 
      ],
      _("Son of %(mother)s."), 
    ], 
    Person.FEMALE : [
      [
        _("She is the daughter of %(mother)s."), 
        _("She was the daughter of %(mother)s."), 
      ], 
      [
        _("%(female_name)s is the daughter of %(mother)s."), 
        _("%(female_name)s was the daughter of %(mother)s."), 
      ],
      _("Daughter of %(mother)s."), 
   ], 
}

#------------------------------------------------------------------------
#
# Marriage strings - Relationship type MARRIED
#
#------------------------------------------------------------------------

marriage_first_date_place = {
    Person.UNKNOWN : [
        _('This person married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('This person married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('This person married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('He married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('He married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('She married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('She married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ],
    'succinct' : [
        _('Married %(spouse)s %(partial_date)s in %(place)s%(endnotes)s.'),
        _('Married %(spouse)s %(full_date)s in %(place)s%(endnotes)s.'),
        _('Married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ], 
    }

marriage_also_date_place = {
    Person.UNKNOWN : [
        _('This person also married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('This person also married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('This person also married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He also married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('He also married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('He also married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She also married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('She also married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('She also married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ],
    'succinct' : [
        _('Also married %(spouse)s %(partial_date)s in %(place)s%(endnotes)s.'),
        _('Also married %(spouse)s %(full_date)s in %(place)s%(endnotes)s.'),
        _('Also married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],       
    }

marriage_first_date = {
    Person.UNKNOWN : [
        _('This person married %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('This person married %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('This person married %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He married %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('He married %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('He married %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She married %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('She married %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('She married %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ],
    'succinct' : [
        _('Married %(spouse)s %(partial_date)s%(endnotes)s.'),
        _('Married %(spouse)s %(full_date)s%(endnotes)s.'),
        _('Married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],       
    }

marriage_also_date = {
    Person.UNKNOWN : [
        _('This person also married %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('This person also married %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('This person also married %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He also married %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('He also married %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('He also married %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She also married %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('She also married %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('She also married %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ],
    'succinct' : [
        _('Also married %(spouse)s %(partial_date)s%(endnotes)s.'),
        _('Also married %(spouse)s %(full_date)s%(endnotes)s.'),
        _('Also married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],       
    }

marriage_first_place = {
    Person.UNKNOWN : _('This person married %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.MALE : _('He married %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.FEMALE : _('She married %(spouse)s in %(place)s%(endnotes)s.'),
    'succinct' : _('Married %(spouse)s in %(place)s%(endnotes)s.'), 
    }

marriage_also_place = {
    Person.UNKNOWN : _('This person also married %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.MALE : _('He also married %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.FEMALE : _('She also married %(spouse)s in %(place)s%(endnotes)s.'),
    'succinct' : _('Also married %(spouse)s in %(place)s%(endnotes)s.'), 
    }

marriage_first_only = {
    Person.UNKNOWN : _('This person married %(spouse)s%(endnotes)s.'), 
    Person.MALE : _('He married %(spouse)s%(endnotes)s.'), 
    Person.FEMALE : _('She married %(spouse)s%(endnotes)s.'),
    'succinct' : _('Married %(spouse)s%(endnotes)s.'), 
    }

marriage_also_only = {
    Person.UNKNOWN : _('This person also married %(spouse)s%(endnotes)s.'), 
    Person.MALE : _('He also married %(spouse)s%(endnotes)s.'), 
    Person.FEMALE : _('She also married %(spouse)s%(endnotes)s.'),
    'succinct' : _('Also married %(spouse)s%(endnotes)s.'), 
    }

#------------------------------------------------------------------------
#
# Marriage strings - Relationship type UNMARRIED
#
#------------------------------------------------------------------------

unmarried_first_date_place = {
    Person.UNKNOWN : [
        _('This person had an unmarried relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('This person had an unmarried relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('This person had an unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He had an unmarried relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('He had an unmarried relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('He had an unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She had an unmarried relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('She had an unmarried relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('She had an unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Unmarried relationship with %(spouse)s %(partial_date)s in %(place)s%(endnotes)s.'),
        _('Unmarried relationship with %(spouse)s %(full_date)s in %(place)s%(endnotes)s.'),
        _('Unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],  
    }

unmarried_also_date_place = {
    Person.UNKNOWN : [
        _('This person also had an unmarried relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('This person also had an unmarried relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('This person also had an unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He also had an unmarried relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('He also had an unmarried relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('He also had an unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She also had an unmarried relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('She also had an unmarried relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('She also had an unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Unmarried relationship with %(spouse)s %(partial_date)s in %(place)s%(endnotes)s.'),
        _('Unmarried relationship with %(spouse)s %(full_date)s in %(place)s%(endnotes)s.'),
        _('Unmarried relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ], 
    }

unmarried_first_date = {
    Person.UNKNOWN : [
        _('This person had an unmarried relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('This person had an unmarried relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('This person had an unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He had an unmarried relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('He had an unmarried relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('He had an unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She had an unmarried relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('She had an unmarried relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('She had an unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Unmarried relationship with %(spouse)s %(partial_date)s%(endnotes)s.'),
        _('Unmarried relationship with %(spouse)s %(full_date)s%(endnotes)s.'),
        _('Unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],       
    }

unmarried_also_date = {
    Person.UNKNOWN : [
        _('This person also had an unmarried relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('This person also had an unmarried relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('This person also had an unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He also had an unmarried relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('He also had an unmarried relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('He also had an unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She also had an unmarried relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('She also had an unmarried relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('She also had an unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Also unmarried relationship with %(spouse)s %(partial_date)s%(endnotes)s.'),
        _('Also unmarried relationship with %(spouse)s %(full_date)s%(endnotes)s.'),
        _('Also unmarried relationship with %(spouse)s %(modified_date)s%(endnotes)s.'),
      ], 
    }

unmarried_first_place = {
    Person.UNKNOWN : _('This person had an unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.MALE : _('He had an unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.FEMALE : _('She had an unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    'succinct' : _('Unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    }

unmarried_also_place = {
    Person.UNKNOWN : _('This person also had an unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.MALE : _('He also had an unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.FEMALE : _('She also had an unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    'succinct' : _('Unmarried relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    }

unmarried_first_only = {
    Person.UNKNOWN : _('This person had an unmarried relationship with %(spouse)s%(endnotes)s.'), 
    Person.MALE : _('He had an unmarried relationship with %(spouse)s%(endnotes)s.'), 
    Person.FEMALE : _('She had an unmarried relationship with %(spouse)s%(endnotes)s.'),
    'succinct' : _('Unmarried relationship with %(spouse)s%(endnotes)s.'),  
    }

unmarried_also_only = {
    Person.UNKNOWN : _('This person also had an unmarried relationship with %(spouse)s%(endnotes)s.'), 
    Person.MALE : _('He also had an unmarried relationship with %(spouse)s%(endnotes)s.'), 
    Person.FEMALE : _('She also had an unmarried relationship with %(spouse)s%(endnotes)s.'), 
    'succinct' : _('Unmarried relationship with %(spouse)s%(endnotes)s.'), 
    }

#------------------------------------------------------------------------
#
# Marriage strings - Relationship type other than MARRIED or UNMARRIED
#                    i.e. CIVIL UNION or CUSTOM
#
#------------------------------------------------------------------------

relationship_first_date_place = {
    Person.UNKNOWN : [
        _('This person had a relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('This person had a relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('This person had a relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He had a relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('He had a relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('He had a relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She had a relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('She had a relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('She had a relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Relationship with %(spouse)s %(partial_date)s in %(place)s%(endnotes)s.'),
        _('Relationship with %(spouse)s %(full_date)s in %(place)s%(endnotes)s.'),
        _('Relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],       
    }

relationship_also_date_place = {
    Person.UNKNOWN : [
        _('This person also had a relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('This person also had a relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('This person also had a relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He also had a relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('He also had a relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('He also had a relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She also had a relationship with %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'), 
        _('She also had a relationship with %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'), 
        _('She also had a relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Also relationship with %(spouse)s %(partial_date)s in %(place)s%(endnotes)s.'),
        _('Also relationship with %(spouse)s %(full_date)s in %(place)s%(endnotes)s.'),
        _('Also relationship with %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ], 
    }

relationship_first_date = {
    Person.UNKNOWN : [
        _('This person had a relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('This person had a relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('This person had a relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He had a relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('He had a relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('He had a relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She had a relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('She had a relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('She had a relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Relationship with %(spouse)s %(partial_date)s%(endnotes)s.'),
        _('Relationship with %(spouse)s %(full_date)s%(endnotes)s.'),
        _('Relationship with %(spouse)s %(modified_date)s%(endnotes)s.'),
      ], 
    }

relationship_also_date = {
    Person.UNKNOWN : [
        _('This person also had a relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('This person also had a relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('This person also had a relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.MALE : [
        _('He also had a relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('He also had a relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('He also had a relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ], 
    Person.FEMALE : [
        _('She also had a relationship with %(spouse)s in %(partial_date)s%(endnotes)s.'), 
        _('She also had a relationship with %(spouse)s on %(full_date)s%(endnotes)s.'), 
        _('She also had a relationship with %(spouse)s %(modified_date)s%(endnotes)s.'), 
      ],
      'succinct' : [
        _('Also relationship with %(spouse)s %(partial_date)s%(endnotes)s.'),
        _('Also relationship with %(spouse)s %(full_date)s%(endnotes)s.'),
        _('Also relationship with %(spouse)s %(modified_date)s%(endnotes)s.'),
      ], 
    }

relationship_first_place = {
    Person.UNKNOWN : _('This person had a relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.MALE : _('He had a relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.FEMALE : _('She had a relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    'succinct' : _('Relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    }

relationship_also_place = {
    Person.UNKNOWN : _('This person also had a relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.MALE : _('He also had a relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    Person.FEMALE : _('She also had a relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    'succinct' : _('Also relationship with %(spouse)s in %(place)s%(endnotes)s.'), 
    }

relationship_first_only = {
    Person.UNKNOWN : _('This person had a relationship with %(spouse)s%(endnotes)s.'), 
    Person.MALE : _('He had a relationship with %(spouse)s%(endnotes)s.'), 
    Person.FEMALE : _('She had a relationship with %(spouse)s%(endnotes)s.'),
    'succinct' : _('Relationship with %(spouse)s%(endnotes)s.'),  
    }

relationship_also_only = {
    Person.UNKNOWN : _('This person also had a relationship with %(spouse)s%(endnotes)s.'), 
    Person.MALE : _('He also had a relationship with %(spouse)s%(endnotes)s.'), 
    Person.FEMALE : _('She also had a relationship with %(spouse)s%(endnotes)s.'), 
    'succinct' : _('Also relationship with %(spouse)s%(endnotes)s.'), 
    }


#------------------------------------------------------------------------
#
# Narrator
#
#------------------------------------------------------------------------
class Narrator(object):
    """ 
    Narrator is a class which provides narration text.
    """

    def __init__(self, dbase, verbose=True, empty_date="", empty_place=""):
        """ 
        Initialize the narrator class.
        """ 
        self.__db = dbase
        self.__verbose = verbose
        self.__empty_date = empty_date
        self.__empty_place = empty_place

    def born_str(self, person, person_name=None ):
        """ 
        Check birth record.
        Statement formats name precedes this
            was born on Date.
            was born on Date in Place.
            was born in Month_Year.
            was born in Month_Year in Place.
            was born in Place.
            ''
        """
    
        name_index = 1
        if person_name is None:
            person_name = _nd.display(person)
        elif person_name == 0:
            name_index = 0
    
        text = ""
        
        bplace = self.__empty_place
        bdate = self.__empty_date
        bdate_full = False
        bdate_mod = False
    
        birth_ref = person.get_birth_ref()
        if birth_ref and birth_ref.ref:
            birth = self.__db.get_event_from_handle(birth_ref.ref)
            if birth:
                bdate = DateHandler.get_date(birth)
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    place = self.__db.get_place_from_handle(bplace_handle)
                    bplace = place.get_title()
                bdate_obj = birth.get_date_object()
                bdate_full = bdate_obj and bdate_obj.get_day_valid()
                bdate_mod = bdate_obj and \
                            bdate_obj.get_modifier() != Date.MOD_NONE
    
        value_map = {
            'name'                : person_name, 
            'male_name'           : person_name, 
            'unknown_gender_name' : person_name, 
            'female_name'         : person_name, 
            'birth_date'          : bdate, 
            'birth_place'         : bplace, 
            'month_year'          : bdate, 
            'modified_date'       : bdate, 
            }
    
        gender = person.get_gender()
    
        if bdate:
            if bdate_mod:
                if bplace and self.__verbose:
                    text = born_modified_date_with_place[name_index][gender] % value_map
                elif bplace:
                    text = born_modified_date_with_place[2] % value_map
                elif self.__verbose:
                    text = born_modified_date_no_place[name_index][gender] % value_map
                else:
                    text = born_modified_date_no_place[2] % value_map
            elif bdate_full:
                if bplace and self.__verbose:
                    text = born_full_date_with_place[name_index][gender] % value_map
                elif bplace:
                    text = born_full_date_with_place[2] % value_map
                elif self.__verbose:
                    text = born_full_date_no_place[name_index][gender] % value_map
                else:
                    text = born_full_date_no_place[2] % value_map
            else:
                if bplace and self.__verbose:
                    text = born_partial_date_with_place[name_index][gender] % value_map
                elif bplace:
                    text = born_partial_date_with_place[2] % value_map
                elif self.__verbose:
                    text = born_partial_date_no_place[name_index][gender] % value_map
                else:
                    text = born_partial_date_no_place[2] % value_map
        else:
            if bplace and self.__verbose:
                text = born_no_date_with_place[name_index][gender] % value_map
            elif bplace:
                text = born_no_date_with_place[2] % value_map
            else:
                text = ""
        if text:
            text = text + " "
        return text

    #-------------------------------------------------------------------------
    #
    # died_str
    #
    #-------------------------------------------------------------------------
    def died_str(self, person, person_name=None, span=None):
        """
        Write obit sentence.
            FIRSTNAME died on Date
            FIRSTNAME died on Date at the age of N Years
            FIRSTNAME died on Date at the age of N Months
            FIRSTNAME died on Date at the age of N Days
            FIRSTNAME died on Date in Place
            FIRSTNAME died on Date in Place at the age of N Years
            FIRSTNAME died on Date in Place at the age of N Months
            FIRSTNAME died on Date in Place at the age of N Days
            FIRSTNAME died in Month_Year
            FIRSTNAME died in Month_Year at the age of N Years
            FIRSTNAME died in Month_Year at the age of N Months
            FIRSTNAME died in Month_Year at the age of N Days
            FIRSTNAME died in Month_Year in Place
            FIRSTNAME died in Month_Year in Place at the age of N Years
            FIRSTNAME died in Month_Year in Place at the age of N Months
            FIRSTNAME died in Month_Year in Place at the age of N Days
            FIRSTNAME died in Place
            FIRSTNAME died in Place at the age of N Years
            FIRSTNAME died in Place at the age of N Months
            FIRSTNAME died in Place at the age of N Days
            FIRSTNAME died
            FIRSTNAME died at the age of N Years
            FIRSTNAME died at the age of N Months
            FIRSTNAME died at the age of N Days
        """
    
        name_index = 1
        if person_name is None:
            person_name = _nd.display(person)
        elif person_name == 0:
            name_index = 0
    
        text = ""
    
        dplace = self.__empty_place
        ddate = self.__empty_date
        ddate_full = False
        ddate_mod = False

    
        death_ref = person.get_death_ref()
        if death_ref and death_ref.ref:
            death = self.__db.get_event_from_handle(death_ref.ref)
            if death:
                ddate = DateHandler.get_date(death)
                dplace_handle = death.get_place_handle()
                if dplace_handle:
                    place = self.__db.get_place_from_handle(dplace_handle)
                    dplace = place.get_title()
                ddate_obj = death.get_date_object()
                ddate_full = ddate_obj and ddate_obj.get_day_valid()
                ddate_mod = ddate_obj and \
                            ddate_obj.get_modifier() != Date.MOD_NONE
    
        # TODO: fixme to let date format itself
        if span and span.is_valid():
            YEARS  = 1
            MONTHS = 2
            DAYS   = 3
            if span[0] != 0:
                age = span[0]
                age_units = YEARS
            elif span[1] != 0:
                age = span[1]
                age_units = MONTHS
            elif span[2] != 0:
                age = span[2]
                age_units = DAYS
            else:
                age = 0
                age_units = 0
        else:
            age = 0
            age_units = 0
        # end of todo ----------------------------
    
        value_map = {
            'name'                : person_name, 
            'unknown_gender_name' : person_name, 
            'male_name'           : person_name, 
            'female_name'         : person_name, 
            'death_date'          : ddate, 
            'modified_date'       : ddate, 
            'death_place'         : dplace, 
            'age'                 : age, 
            'month_year'          : ddate, 
            }
    
        gender = person.get_gender()
    
        if ddate:
            if ddate_mod:
                if dplace and self.__verbose:
                    text = died_modified_date_with_place[name_index][gender][age_units] % value_map
                elif dplace:
                    text = died_modified_date_with_place[2][age_units] % value_map
                elif self.__verbose:
                    text = died_modified_date_no_place[name_index][gender][age_units] % value_map
                else:
                    text = died_modified_date_no_place[2][age_units] % value_map
            elif ddate_full:
                if dplace and self.__verbose:
                    text = died_full_date_with_place[name_index][gender][age_units] % value_map
                elif dplace:
                    text = died_full_date_with_place[2][age_units] % value_map
                elif self.__verbose:
                    text = died_full_date_no_place[name_index][gender][age_units] % value_map
                else:
                    text = died_full_date_no_place[2][age_units] % value_map
            else:
                if dplace and self.__verbose:
                    text = died_partial_date_with_place[name_index][gender][age_units] % value_map
                elif dplace:
                    text = died_partial_date_with_place[2][age_units] % value_map
                elif self.__verbose:
                    text = died_partial_date_no_place[name_index][gender][age_units] % value_map
                else:
                    text = died_partial_date_no_place[2][age_units] % value_map
        else:
            if dplace and self.__verbose:
                text = died_no_date_with_place[name_index][gender][age_units] % value_map
            elif dplace:
                text = died_no_date_with_place[2][age_units] % value_map
            elif self.__verbose:
                text = died_no_date_no_place[name_index][gender][age_units] % value_map
            else:
                text = died_no_date_no_place[2][age_units] % value_map
        if text:
            text = text + " "
        return text
    
    #-------------------------------------------------------------------------
    #
    # buried_str
    #
    #-------------------------------------------------------------------------
    def buried_str(self, person, person_name=None, endnotes=None):
        """ 
        Check burial record.
        Statement formats name precedes this
            was buried on Date.
            was buried on Date in Place.
            was buried in Month_Year.
            was buried in Month_Year in Place.
            was buried in Place.
            ''
        """
    
        if not endnotes:
            endnotes = empty_notes
    
        name_index = 0
        if person_name is None:
            person_name = _nd.display(person)
        elif person_name == 0:
            name_index = 1
    
        gender = person.get_gender()
            
        text = ""
        
        bplace = self.__empty_place
        bdate = self.__empty_date
        bdate_full = False
        bdate_mod = False
        
        burial = None
        for event_ref in person.get_event_ref_list():
            event = self.__db.get_event_from_handle(event_ref.ref)
            if event and event.type.value == EventType.BURIAL \
                and event_ref.role.value == EventRoleType.PRIMARY:
                burial = event
                break
    
        if burial:
            bdate = DateHandler.get_date(burial)
            bplace_handle = burial.get_place_handle()
            if bplace_handle:
                place = self.__db.get_place_from_handle(bplace_handle)
                bplace = place.get_title()
            bdate_obj = burial.get_date_object()
            bdate_full = bdate_obj and bdate_obj.get_day_valid()
            bdate_mod = bdate_obj and bdate_obj.get_modifier() != Date.MOD_NONE
        else:
            return text
    
        values = {
            'unknown_gender_name' : person_name, 
            'male_name'           : person_name, 
            'name'                : person_name, 
            'female_name'         : person_name, 
            'burial_date'         : bdate, 
            'burial_place'        : bplace, 
            'month_year'          : bdate, 
            'modified_date'       : bdate,
            'endnotes'            : endnotes(event), 
            }
    
        if bdate and bdate_mod and self.__verbose:
            if bplace: #male, date, place
                text = buried_modified_date_place[gender][name_index] % values
            else:      #male, date, no place
                text = buried_modified_date_no_place[gender][name_index] % values
        elif bdate and bdate_mod:
            if bplace: #male, date, place
                text = buried_modified_date_place['succinct'] % values
            else:      #male, date, no place
                text = buried_modified_date_no_place['succinct'] % values
        elif bdate and bdate_full and self.__verbose:
            if bplace: #male, date, place
                text = buried_full_date_place[gender][name_index] % values
            else:      #male, date, no place
                text = buried_full_date_no_place[gender][name_index] % values
        elif bdate and bdate_full:
            if bplace: #male, date, place
                text = buried_full_date_place['succinct'] % values
            else:      #male, date, no place
                text = buried_full_date_no_place['succinct'] % values
        elif bdate and self.__verbose:
            if bplace: #male, month_year, place
                text = buried_partial_date_place[gender][name_index] % values
            else:      #male, month_year, no place
                text = buried_partial_date_no_place[gender][name_index] % values
        elif bdate:
            if bplace: #male, month_year, place
                text = buried_partial_date_place['succinct'] % values
            else:      #male, month_year, no place
                text = buried_partial_date_no_place['succinct'] % values
        elif bplace and self.__verbose:   #male, no date, place
            text = buried_no_date_place[gender][name_index] % values
        elif bplace:   #male, no date, place
            text = buried_no_date_place['succinct'] % values
        elif self.__verbose:
            text = buried_no_date_no_place[gender][name_index] % values
        else:          #male, no date, no place
            text = buried_no_date_no_place['succinct'] % values
            
        if text:
            text = text + " "
        return text
    
    #-------------------------------------------------------------------------
    #
    # baptised_str
    #
    #-------------------------------------------------------------------------
    def baptised_str(self, person, person_name=None, endnotes=None):
        """ 
        Check baptism record.
        Statement formats name precedes this
            was baptised on Date.
            was baptised on Date in Place.
            was baptised in Month_Year.
            was baptised in Month_Year in Place.
            was baptised in Place.
            ''
        """
    
        if not endnotes:
            endnotes = empty_notes
    
        name_index = 0
        if person_name is None:
            person_name = _nd.display(person)
        elif person_name == 0:
            name_index = 1
    
        gender = person.get_gender()
        
        text = ""
    
        bplace = self.__empty_place
        bdate = self.__empty_date
        bdate_full = False
        bdate_mod = False
    
        baptism = None
        for event_ref in person.get_event_ref_list():
            event = self.__db.get_event_from_handle(event_ref.ref)
            if event and event.type.value == EventType.BAPTISM \
                and event_ref.role.value == EventRoleType.PRIMARY:
                baptism = event
                break
    
        if baptism:
            bdate = DateHandler.get_date(baptism)
            bplace_handle = baptism.get_place_handle()
            if bplace_handle:
                place = self.__db.get_place_from_handle(bplace_handle)
                bplace = place.get_title()
            bdate_obj = baptism.get_date_object()
            bdate_full = bdate_obj and bdate_obj.get_day_valid()
            bdate_mod = bdate_obj and bdate_obj.get_modifier() != Date.MOD_NONE
        else:
            return text
    
        values = {
            'unknown_gender_name' : person_name, 
            'male_name'           : person_name, 
            'name'                : person_name, 
            'female_name'         : person_name, 
            'baptism_date'        : bdate, 
            'baptism_place'       : bplace, 
            'month_year'          : bdate, 
            'modified_date'       : bdate,
            'endnotes'            : endnotes(event), 
            }
    
        if bdate and bdate_mod and self.__verbose:
            if bplace: #male, date, place
                text = baptised_modified_date_place[gender][name_index] % values
            else:      #male, date, no place
                text = baptised_modified_date_no_place[gender][name_index] % values
        elif bdate and bdate_mod:
            if bplace: #male, date, place
                text = baptised_modified_date_place['succinct'] % values
            else:      #male, date, no place
                text = baptised_modified_date_no_place['succinct'] % values
        elif bdate and bdate_full and self.__verbose:
            if bplace: #male, date, place
                text = baptised_full_date_place[gender][name_index] % values
            else:      #male, date, no place
                text = baptised_full_date_no_place[gender][name_index] % values
        elif bdate and bdate_full:
            if bplace: #male, date, place
                text = baptised_full_date_place['succinct'] % values
            else:      #male, date, no place
                text = baptised_full_date_no_place['succinct'] % values
        elif bdate and self.__verbose:
            if bplace: #male, month_year, place
                text = baptised_partial_date_place[gender][name_index] % values
            else:      #male, month_year, no place
                text = baptised_partial_date_no_place[gender][name_index] % values
        elif bdate:
            if bplace: #male, month_year, place
                text = baptised_partial_date_place['succinct'] % values
            else:      #male, month_year, no place
                text = baptised_partial_date_no_place['succinct'] % values
        elif bplace and self.__verbose:   #male, no date, place
            text = baptised_no_date_place[gender][name_index] % values
        elif bplace:   #male, no date, place
            text = baptised_no_date_place['succinct'] % values
        elif self.__verbose:
            text = baptised_no_date_no_place[gender][name_index] % values
        else:          #male, no date, no place
            text = baptised_no_date_no_place['succinct'] % values
            
        if text:
            text = text + " "
        return text
    
    #-------------------------------------------------------------------------
    #
    # christened_str
    #
    #-------------------------------------------------------------------------
    def christened_str(self, person, person_name=None, endnotes=None):
        """ 
        Check christening record.
        Statement formats name precedes this
            was christened on Date.
            was christened on Date in Place.
            was christened in Month_Year.
            was christened in Month_Year in Place.
            was christened in Place.
            ''
        """
    
        if not endnotes:
            endnotes = empty_notes
    
        name_index = 0
        if person_name is None:
            person_name = _nd.display(person)
        elif person_name == 0:
            name_index = 1
    
        gender = person.get_gender()
        
        text = ""
    
        cplace = self.__empty_place
        cdate = self.__empty_date
        cdate_full = False
        cdate_mod = False
    
        christening = None
        for event_ref in person.get_event_ref_list():
            event = self.__db.get_event_from_handle(event_ref.ref)
            if event and event.type.value == EventType.CHRISTEN \
                and event_ref.role.value == EventRoleType.PRIMARY:
                christening = event
                break
    
        if christening:
            cdate = DateHandler.get_date(christening)
            cplace_handle = christening.get_place_handle()
            if cplace_handle:
                place = self.__db.get_place_from_handle(cplace_handle)
                cplace = place.get_title()
            cdate_obj = christening.get_date_object()
            cdate_full = cdate_obj and cdate_obj.get_day_valid()
            cdate_mod = cdate_obj and cdate_obj.get_modifier() != Date.MOD_NONE
        else:
            return text
    
        values = {
            'unknown_gender_name' : person_name, 
            'male_name'           : person_name, 
            'name'                : person_name, 
            'female_name'         : person_name, 
            'christening_date'    : cdate, 
            'christening_place'   : cplace, 
            'month_year'          : cdate, 
            'modified_date'       : cdate,
            'endnotes'            : endnotes(event), 
            }
    
        if cdate and cdate_mod and self.__verbose:
            if cplace: #male, date, place
                text = christened_modified_date_place[gender][name_index] % values
            else:      #male, date, no place
                text = christened_modified_date_no_place[gender][name_index] % values
        elif cdate and cdate_mod:
            if cplace: #male, date, place
                text = christened_modified_date_place['succinct'] % values
            else:      #male, date, no place
                text = christened_modified_date_no_place['succinct'] % values
        elif cdate and cdate_full and self.__verbose:
            if cplace: #male, date, place
                text = christened_full_date_place[gender][name_index] % values
            else:      #male, date, no place
                text = christened_full_date_no_place[gender][name_index] % values
        elif cdate and cdate_full:
            if cplace: #male, date, place
                text = christened_full_date_place['succinct'] % values
            else:      #male, date, no place
                text = christened_full_date_no_place['succinct'] % values
        elif cdate and self.__verbose:
            if cplace: #male, month_year, place
                text = christened_partial_date_place[gender][name_index] % values
            else:      #male, month_year, no place
                text = christened_partial_date_no_place[gender][name_index] % values
        elif cdate:
            if cplace: #male, month_year, place
                text = christened_partial_date_place['succinct'] % values
            else:      #male, month_year, no place
                text = christened_partial_date_no_place['succinct'] % values
        elif cplace and self.__verbose:   #male, no date, place
            text = christened_no_date_place[gender][name_index] % values
        elif cplace:   #male, no date, place
            text = christened_no_date_place['succinct'] % values
        elif self.__verbose:
            text = christened_no_date_no_place[gender][name_index] % values
        else:          #male, no date, no place
            text = christened_no_date_no_place['succinct'] % values
            
        if text:
            text = text + " "
        return text

    def married_str(self, person, family, endnotes=None, is_first=True):
        """
        Composes a string describing marriage of a person. Missing information 
        will be omitted without loss of readability. Optional references may be 
        added to birth and death events.
        
        @param database: GRAMPS database to which the Person object belongs
        @type database: GrampsDbBase
        @param person: Person instance whose marriage is discussed
        @type person: Person
        @param family: Family instance of the "marriage" being discussed
        @param endnotes: Function to use for reference composition. If None
        then references will not be added
        @type endnotes: function
        @returns: A composed string
        @rtype: unicode
        """
    
        spouse_handle = ReportUtils.find_spouse(person, family)
        spouse = self.__db.get_person_from_handle(spouse_handle)
        event = ReportUtils.find_marriage(self.__db, family)
    
        # not all families have a spouse.
        if not spouse:
            return u""
    
        if not endnotes:
            endnotes = empty_notes
    
        date = self.__empty_date
        place = self.__empty_place
        spouse_name = _nd.display(spouse)
    
        if event:
            mdate = DateHandler.get_date(event)
            if mdate:
                date = mdate
            place_handle = event.get_place_handle()
            if place_handle:
                place_obj = self.__db.get_place_from_handle(place_handle)
                place = place_obj.get_title()
        relationship = family.get_relationship()
    
        values = {
            'spouse'        : spouse_name, 
            'endnotes'      : endnotes(event), 
            'full_date'     : date, 
            'modified_date' : date, 
            'partial_date'  : date, 
            'place'         : place, 
            }
    
        if event:
            dobj = event.get_date_object()
        
            if dobj.get_modifier() != Date.MOD_NONE:
                date_full = 2
            elif dobj and dobj.get_day_valid():
                date_full = 1
            else:
                date_full = 0
            
        gender = person.get_gender()
    
        # This would be much simpler, excepting for translation considerations
        # Currently support FamilyRelType's:
        #     MARRIED     : civil and/or religious
        #     UNMARRIED
        #     CIVIL UNION : described as a relationship
        #     UNKNOWN     : also described as a relationship
        #     CUSTOM      : also described as a relationship
        #
        # In the future, there may be a need to distinguish between 
        # CIVIL UNION, UNKNOWN and CUSTOM relationship types
        # CUSTOM will be difficult as user can supply any arbitrary string to 
        # describe type
    
        if is_first:
            if event and date and place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date_place[gender][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date_place[gender][date_full] % values
                else:
                    text = relationship_first_date_place[gender][date_full] % values
            elif event and date and place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date_place['succinct'][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date_place['succinct'][date_full] % values
                else:
                    text = relationship_first_date_place['succinct'][date_full] % values                
            elif event and date and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date[gender][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date[gender][date_full] % values
                else:
                    text = relationship_first_date[gender][date_full] % values
            elif event and date:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date['succinct'][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date['succinct'][date_full] % values
                else:
                    text = relationship_first_date['succinct'][date_full] % values
            elif event and place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_place[gender] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_place[gender] % values
                else:
                    text = relationship_first_place[gender] % values
            elif event and place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_place['succinct'] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_place['succinct'] % values
                else:
                    text = relationship_first_place['succinct'] % values
            elif self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_only[gender] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_only[gender] % values
                else:
                    text = relationship_first_only[gender] % values                            
            else:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_only['succinct'] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_only['succinct'] % values
                else:
                    text = relationship_first_only['succinct'] % values
        else:
            if event and date and place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date_place[gender][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date_place[gender][date_full] % values
                else:
                    text = relationship_also_date_place[gender][date_full] % values
            if event and date and place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date_place['succinct'][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date_place['succinct'][date_full] % values
                else:
                    text = relationship_also_date_place['succinct'][date_full] % values
            elif event and date and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date[gender][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date[gender][date_full] % values
                else:
                    text = relationship_also_date[gender][date_full] % values
            elif event and date:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date['succinct'][date_full] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date['succinct'][date_full] % values
                else:
                    text = relationship_also_date['succinct'][date_full] % values
            elif event and place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_place[gender] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_place[gender] % values
                else:
                    text = relationship_also_place[gender] % values
            elif event and place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_place['succinct'] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_place['succinct'] % values
                else:
                    text = relationship_also_place['succinct'] % values
            elif self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_only[gender] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_only[gender] % values
                else:
                    text = relationship_also_only[gender] % values
            else:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_only['succinct'] % values
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_only['succinct'] % values
                else:
                    text = relationship_also_only['succinct'] % values
    
        if text:
            text = text + " "
        return text

    def child_str(self, person, father_name="", mother_name="", person_name=0):
        """
        Composes a string describing person being a child.
        
        The string is composed in the following form:
            'He/She is/was the son/daughter of father_name and mother_name'
        Missing information will be omitted without loss of readability.
        
        @param person_gender: Person.MALE, Person.FEMALE, or Person.UNKNOWN
        @type person: Person.MALE, Person.FEMALE, or Person.UNKNOWN~
        @param father_name: String to use for father's name
        @type father_name: unicode
        @param mother_name: String to use for mother's name
        @type mother_name: unicode
        @param dead: Whether the person discussed is dead or not
        @type dead: bool
        @returns: A composed string
        @rtype: unicode
        """
    
        values = {
            'father'              : father_name, 
            'mother'              : mother_name, 
            'male_name'           : person_name, 
            'name'                : person_name, 
            'female_name'         : person_name, 
            'unknown_gender_name' : person_name, 
            }
        
        dead = not Utils.probably_alive(person, self.__db)
    
        if person_name == 0:
            index = 0
        else:
            index = 1
    
        gender = person.get_gender()
    
        text = ""
        if mother_name and father_name and self.__verbose:
            text = child_father_mother[gender][index][dead] % values
        elif mother_name and father_name:
            text = child_father_mother[gender][2] % values
        elif mother_name and self.__verbose:
            text = child_mother[gender][index][dead] % values
        elif mother_name:
            text = child_mother[gender][2] % values
        elif father_name and self.__verbose:
            text = child_father[gender][index][dead] % values
        elif father_name:
            text = child_father[gender][2] % values
        if text:
            text = text + " "
        return text