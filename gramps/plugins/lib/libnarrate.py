# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Vlada Perić <vlada.peric@gmail.com>
# Copyright (C) 2011       Matt Keenan <matt.keenan@gmail.com>
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013-2014  Paul Franklin
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
Narrator class for use by plugins.
"""

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.lib.date import Date
from gramps.gen.lib.person import Person
from gramps.gen.lib.eventroletype import EventRoleType
from gramps.gen.lib.eventtype import EventType
from gramps.gen.lib.familyreltype import FamilyRelType
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.utils.alive import probably_alive
from gramps.gen.plug.report import utils
from gramps.gen.const import GRAMPS_LOCALE as glocale

#-------------------------------------------------------------------------
#
# Private constants
#
#-------------------------------------------------------------------------
# In string arrays, the first strings should include the name, the second
# strings should not include the name.
_NAME_INDEX_INCLUDE_NAME = 0
_NAME_INDEX_EXCLUDE_NAME = 1

# In string arrays, the first strings should not include age.
# The following strings should include year, month and day units.
# And support format with precision (see gen/lib/date.py).
_AGE_INDEX_NO_AGE = 0
_AGE_INDEX = 1

#-------------------------------------------------------------------------
#
# Private functions
#
#-------------------------------------------------------------------------
def _get_empty_endnote_numbers(obj):
    """
    Empty stab function for when endnotes are not needed
    """
    return ""

# avoid normal translation!
# enable deferred translations
# (these days this is done elsewhere as _T_ but it was done here first)
##from gramps.gen.const import GRAMPS_LOCALE as glocale
##_ = glocale.translation.gettext
def _(message): return message

#------------------------------------------------------------------------
#
# Born strings
#
#------------------------------------------------------------------------
born_full_date_with_place = [
 {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born on %(birth_date)s in %(birth_place)s."),
    Person.MALE : _("%(male_name)s was born on %(birth_date)s in %(birth_place)s."),
    Person.FEMALE : _("%(female_name)s was born on %(birth_date)s in %(birth_place)s."),
  },
  {
    Person.UNKNOWN :  _("This person was born on %(birth_date)s in %(birth_place)s."),
    Person.MALE :  _("He was born on %(birth_date)s in %(birth_place)s."),
    Person.FEMALE : _("She was born on %(birth_date)s in %(birth_place)s."),
  },
  _("Born %(birth_date)s in %(birth_place)s."),
]

born_modified_date_with_place = [
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born %(modified_date)s in %(birth_place)s."),
    Person.MALE : _("%(male_name)s was born %(modified_date)s in %(birth_place)s."),
    Person.FEMALE : _("%(female_name)s was born %(modified_date)s in %(birth_place)s."),
  },
  {
    Person.UNKNOWN :  _("This person was born %(modified_date)s in %(birth_place)s."),
    Person.MALE :  _("He was born %(modified_date)s in %(birth_place)s."),
    Person.FEMALE : _("She was born %(modified_date)s in %(birth_place)s."),
  },
  _("Born %(modified_date)s in %(birth_place)s."),
]

born_full_date_no_place = [
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born on %(birth_date)s."),
    Person.MALE : _("%(male_name)s was born on %(birth_date)s."),
    Person.FEMALE : _("%(female_name)s was born on %(birth_date)s."),
  },
  {
    Person.UNKNOWN : _("This person was born on %(birth_date)s."),
    Person.MALE : _("He was born on %(birth_date)s."),
    Person.FEMALE : _("She was born on %(birth_date)s."),
  },
  _("Born %(birth_date)s."),
]

born_modified_date_no_place = [
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born %(modified_date)s."),
    Person.MALE : _("%(male_name)s was born %(modified_date)s."),
    Person.FEMALE : _("%(female_name)s was born %(modified_date)s."),
  },
  {
    Person.UNKNOWN : _("This person was born %(modified_date)s."),
    Person.MALE : _("He was born %(modified_date)s."),
    Person.FEMALE : _("She was born %(modified_date)s."),
  },
   _("Born %(modified_date)s."),
]

born_partial_date_with_place = [
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(month_year)s in %(birth_place)s."),
    Person.MALE : _("%(male_name)s was born in %(month_year)s in %(birth_place)s."),
    Person.FEMALE : _("%(female_name)s was born in %(month_year)s in %(birth_place)s."),
  },
  {
    Person.UNKNOWN : _("This person was born in %(month_year)s in %(birth_place)s."),
    Person.MALE : _("He was born in %(month_year)s in %(birth_place)s."),
    Person.FEMALE : _("She was born in %(month_year)s in %(birth_place)s."),
  },
  _("Born %(month_year)s in %(birth_place)s."),
]

born_partial_date_no_place = [
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(month_year)s."),
    Person.MALE : _("%(male_name)s was born in %(month_year)s."),
    Person.FEMALE : _("%(female_name)s was born in %(month_year)s."),
  },
  {
    Person.UNKNOWN : _("This person was born in %(month_year)s."),
    Person.MALE : _("He was born in %(month_year)s."),
    Person.FEMALE : _("She was born in %(month_year)s."),
  },
  _("Born %(month_year)s."),
]

born_no_date_with_place = [
  {
    Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(birth_place)s."),
    Person.MALE : _("%(male_name)s was born in %(birth_place)s."),
    Person.FEMALE : _("%(female_name)s was born in %(birth_place)s."),
  },
  {
    Person.UNKNOWN : _("This person was born in %(birth_place)s."),
    Person.MALE : _("He was born in %(birth_place)s."),
    Person.FEMALE : _("She was born in %(birth_place)s."),
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
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s."),
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("%(male_name)s died on %(death_date)s in %(death_place)s."),
    _("%(male_name)s died on %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("%(female_name)s died on %(death_date)s in %(death_place)s."),
    _("%(female_name)s died on %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
  },
  { Person.UNKNOWN : [
    _("This person died on %(death_date)s in %(death_place)s."),
    _("This person died on %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("He died on %(death_date)s in %(death_place)s."),
    _("He died on %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("She died on %(death_date)s in %(death_place)s."),
    _("She died on %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
  },
  [
  _("Died %(death_date)s in %(death_place)s."),
  _("Died %(death_date)s in %(death_place)s (%(age)s)."),
  ],
]

died_modified_date_with_place = [
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s."),
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("%(male_name)s died %(death_date)s in %(death_place)s."),
    _("%(male_name)s died %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("%(female_name)s died %(death_date)s in %(death_place)s."),
    _("%(female_name)s died %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
  },
  { Person.UNKNOWN : [
    _("This person died %(death_date)s in %(death_place)s."),
    _("This person died %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("He died %(death_date)s in %(death_place)s."),
    _("He died %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("She died %(death_date)s in %(death_place)s."),
    _("She died %(death_date)s in %(death_place)s at the age of %(age)s."),
    ],
  },
  [
  _("Died %(death_date)s in %(death_place)s."),
  _("Died %(death_date)s in %(death_place)s (%(age)s)."),
  ],
]

died_full_date_no_place = [
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died on %(death_date)s."),
    _("%(unknown_gender_name)s died on %(death_date)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("%(male_name)s died on %(death_date)s."),
    _("%(male_name)s died on %(death_date)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("%(female_name)s died on %(death_date)s."),
    _("%(female_name)s died on %(death_date)s at the age of %(age)s."),
    ],
  },
  { Person.UNKNOWN : [
    _("This person died on %(death_date)s."),
    _("This person died on %(death_date)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("He died on %(death_date)s."),
    _("He died on %(death_date)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("She died on %(death_date)s."),
    _("She died on %(death_date)s at the age of %(age)s."),
    ],
  },
  [
  _("Died %(death_date)s."),
  _("Died %(death_date)s (%(age)s)."),
  ],
]

died_modified_date_no_place = [
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died %(death_date)s."),
    _("%(unknown_gender_name)s died %(death_date)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("%(male_name)s died %(death_date)s."),
    _("%(male_name)s died %(death_date)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("%(female_name)s died %(death_date)s."),
    _("%(female_name)s died %(death_date)s at the age of %(age)s."),
    ],
  },
  { Person.UNKNOWN : [
    _("This person died %(death_date)s."),
    _("This person died %(death_date)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("He died %(death_date)s."),
    _("He died %(death_date)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("She died %(death_date)s."),
    _("She died %(death_date)s at the age of %(age)s."),
    ],
  },
  [
  _("Died %(death_date)s."),
  _("Died %(death_date)s (%(age)s)."),
  ],
]

died_partial_date_with_place = [
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s."),
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("%(male_name)s died in %(month_year)s in %(death_place)s."),
    _("%(male_name)s died in %(month_year)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("%(female_name)s died in %(month_year)s in %(death_place)s."),
    _("%(female_name)s died in %(month_year)s in %(death_place)s at the age of %(age)s."),
    ],
  },
  { Person.UNKNOWN : [
    _("This person died in %(month_year)s in %(death_place)s."),
    _("This person died in %(month_year)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("He died in %(month_year)s in %(death_place)s."),
    _("He died in %(month_year)s in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("She died in %(month_year)s in %(death_place)s."),
    _("She died in %(month_year)s in %(death_place)s at the age of %(age)s."),
    ]
  },
  [
  _("Died %(month_year)s in %(death_place)s."),
  _("Died %(month_year)s in %(death_place)s (%(age)s)."),
  ],
]

died_partial_date_no_place = [
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(month_year)s."),
    _("%(unknown_gender_name)s died in %(month_year)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("%(male_name)s died in %(month_year)s."),
    _("%(male_name)s died in %(month_year)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("%(female_name)s died in %(month_year)s."),
    _("%(female_name)s died in %(month_year)s at the age of %(age)s."),
    ],
  },
  { Person.UNKNOWN : [
    _("This person died in %(month_year)s."),
    _("This person died in %(month_year)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("He died in %(month_year)s."),
    _("He died in %(month_year)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("She died in %(month_year)s."),
    _("She died in %(month_year)s at the age of %(age)s."),
    ],
  },
  [
  _("Died %(month_year)s."),
  _("Died %(month_year)s (%(age)s)."),
  ],
]

died_no_date_with_place = [
  { Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(death_place)s."),
    _("%(unknown_gender_name)s died in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("%(male_name)s died in %(death_place)s."),
    _("%(male_name)s died in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("%(female_name)s died in %(death_place)s."),
    _("%(female_name)s died in %(death_place)s at the age of %(age)s."),
    ],
  },
  {
    Person.UNKNOWN : [
    _("This person died in %(death_place)s."),
    _("This person died in %(death_place)s at the age of %(age)s."),
    ],
    Person.MALE : [
    _("He died in %(death_place)s."),
    _("He died in %(death_place)s at the age of %(age)s."),
    ],
    Person.FEMALE : [
    _("She died in %(death_place)s."),
    _("She died in %(death_place)s at the age of %(age)s."),
    ],
  },
  [
  _("Died in %(death_place)s."),
  _("Died in %(death_place)s (%(age)s)."),
  ],
]

died_no_date_no_place = [
  { Person.UNKNOWN : [
    "",
    _("%(unknown_gender_name)s died at the age of %(age)s."),
    ],
    Person.MALE : [
    "",
    _("%(male_name)s died at the age of %(age)s."),
    ],
    Person.FEMALE : [
    "",
    _("%(female_name)s died at the age of %(age)s."),
    ],
  },
  { Person.UNKNOWN : [
    "",
    _("This person died at the age of %(age)s."),
    ],
    Person.MALE : [
    "",
    _("He died at the age of %(age)s."),
    ],
    Person.FEMALE : [
    "",
    _("She died at the age of %(age)s."),
    ],
  },
  [
  "",
  _("Died (%(age)s)."),
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
# Baptized strings
#
#------------------------------------------------------------------------
baptised_full_date_place = {
    Person.MALE: [
    _("%(male_name)s was baptized on %(baptism_date)s in %(baptism_place)s%(endnotes)s."),
    _("He was baptized on %(baptism_date)s in %(baptism_place)s%(endnotes)s."),
    ],
    Person.FEMALE: [
    _("%(female_name)s was baptized on %(baptism_date)s in %(baptism_place)s%(endnotes)s."),
    _("She was baptized on %(baptism_date)s in %(baptism_place)s%(endnotes)s."),
    ],
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptized on %(baptism_date)s in %(baptism_place)s%(endnotes)s."),
    _("This person was baptized on %(baptism_date)s in %(baptism_place)s%(endnotes)s."),
    ],
    'succinct' : _("Baptized %(baptism_date)s in %(baptism_place)s%(endnotes)s."),
    }

baptised_full_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was baptized on %(baptism_date)s%(endnotes)s."),
    _("He was baptized on %(baptism_date)s%(endnotes)s."),
    ],
    Person.FEMALE: [
    _("%(female_name)s was baptized on %(baptism_date)s%(endnotes)s."),
    _("She was baptized on %(baptism_date)s%(endnotes)s."),
    ],
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptized on %(baptism_date)s%(endnotes)s."),
    _("This person was baptized on %(baptism_date)s%(endnotes)s."),
    ],
    'succinct' : _("Baptized %(baptism_date)s%(endnotes)s.")
    }

baptised_partial_date_place = {
    Person.MALE: [
    _("%(male_name)s was baptized in %(month_year)s in %(baptism_place)s%(endnotes)s."),
    _("He was baptized in %(month_year)s in %(baptism_place)s%(endnotes)s."),
    ],
Person.FEMALE: [
    _("%(female_name)s was baptized in %(month_year)s in %(baptism_place)s%(endnotes)s."),
    _("She was baptized in %(month_year)s in %(baptism_place)s%(endnotes)s."),
    ],
Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptized in %(month_year)s in %(baptism_place)s%(endnotes)s."),
    _("This person was baptized in %(month_year)s in %(baptism_place)s%(endnotes)s."),
    ],
    'succinct' : _("Baptized %(month_year)s in %(baptism_place)s%(endnotes)s."),
    }

baptised_partial_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was baptized in %(month_year)s%(endnotes)s."),
    _("He was baptized in %(month_year)s%(endnotes)s."),
    ],
    Person.FEMALE: [
    _("%(female_name)s was baptized in %(month_year)s%(endnotes)s."),
    _("She was baptized in %(month_year)s%(endnotes)s."),
    ],
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptized in %(month_year)s%(endnotes)s."),
    _("This person was baptized in %(month_year)s%(endnotes)s."),
    ],
    'succinct' : _("Baptized %(month_year)s%(endnotes)s."),
    }

baptised_modified_date_place = {
    Person.MALE: [
    _("%(male_name)s was baptized %(modified_date)s in %(baptism_place)s%(endnotes)s."),
    _("He was baptized %(modified_date)s in %(baptism_place)s%(endnotes)s."),
    ],
    Person.FEMALE: [
    _("%(female_name)s was baptized %(modified_date)s in %(baptism_place)s%(endnotes)s."),
    _("She was baptized %(modified_date)s in %(baptism_place)s%(endnotes)s."),
    ],
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptized %(modified_date)s in %(baptism_place)s%(endnotes)s."),
    _("This person was baptized %(modified_date)s in %(baptism_place)s%(endnotes)s."),
    ],
    'succinct' : _("Baptized %(modified_date)s in %(baptism_place)s%(endnotes)s."),
    }

baptised_modified_date_no_place = {
    Person.MALE: [
    _("%(male_name)s was baptized %(modified_date)s%(endnotes)s."),
    _("He was baptized %(modified_date)s%(endnotes)s."),
    ],
    Person.FEMALE: [
    _("%(female_name)s was baptized %(modified_date)s%(endnotes)s."),
    _("She was baptized %(modified_date)s%(endnotes)s."),
    ],
    Person.UNKNOWN: [
    _("%(unknown_gender_name)s was baptized %(modified_date)s%(endnotes)s."),
    _("This person was baptized %(modified_date)s%(endnotes)s."),
    ],
    'succinct' : _("Baptized %(modified_date)s%(endnotes)s."),
    }

baptised_no_date_place = {
    Person.MALE    : [
    _("%(male_name)s was baptized in %(baptism_place)s%(endnotes)s."),
    _("He was baptized in %(baptism_place)s%(endnotes)s."),
    ],
    Person.FEMALE  : [
    _("%(female_name)s was baptized in %(baptism_place)s%(endnotes)s."),
    _("She was baptized in %(baptism_place)s%(endnotes)s."),
    ],
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was baptized in %(baptism_place)s%(endnotes)s."),
    _("This person was baptized in %(baptism_place)s%(endnotes)s."),
    ],
    'succinct' : _("Baptized in %(baptism_place)s%(endnotes)s."),
    }

baptised_no_date_no_place = {
    Person.MALE    : [
    _("%(male_name)s was baptized%(endnotes)s."),
    _("He was baptized%(endnotes)s."),
    ],
    Person.FEMALE  : [
    _("%(female_name)s was baptized%(endnotes)s."),
    _("She was baptized%(endnotes)s."),
    ],
    Person.UNKNOWN : [
    _("%(unknown_gender_name)s was baptized%(endnotes)s."),
    _("This person was baptized%(endnotes)s."),
    ],
    'succinct' : _("Baptized%(endnotes)s."),
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
        _("%(male_name)s is the child of %(father)s and %(mother)s."),
        _("%(male_name)s was the child of %(father)s and %(mother)s."),
      ],
      [
        _("This person is the child of %(father)s and %(mother)s."),
        _("This person was the child of %(father)s and %(mother)s."),
      ],
      _("Child of %(father)s and %(mother)s."),
    ],
    Person.MALE : [
      [
        _("%(male_name)s is the son of %(father)s and %(mother)s."),
        _("%(male_name)s was the son of %(father)s and %(mother)s."),
      ],
      [
        _("He is the son of %(father)s and %(mother)s."),
        _("He was the son of %(father)s and %(mother)s."),
      ],
      _("Son of %(father)s and %(mother)s."),
    ],
    Person.FEMALE : [
     [
        _("%(female_name)s is the daughter of %(father)s and %(mother)s."),
        _("%(female_name)s was the daughter of %(father)s and %(mother)s."),
     ],
     [
        _("She is the daughter of %(father)s and %(mother)s."),
        _("She was the daughter of %(father)s and %(mother)s."),
     ],
     _("Daughter of %(father)s and %(mother)s."),
    ]
}

child_father = {
    Person.UNKNOWN : [
      [
        _("%(male_name)s is the child of %(father)s."),
        _("%(male_name)s was the child of %(father)s."),
      ],
      [
        _("This person is the child of %(father)s."),
        _("This person was the child of %(father)s."),
      ],
      _("Child of %(father)s."),
    ],
    Person.MALE : [
      [
        _("%(male_name)s is the son of %(father)s."),
        _("%(male_name)s was the son of %(father)s."),
      ],
      [
        _("He is the son of %(father)s."),
        _("He was the son of %(father)s."),
      ],
      _("Son of %(father)s."),
    ],
    Person.FEMALE : [
      [
        _("%(female_name)s is the daughter of %(father)s."),
        _("%(female_name)s was the daughter of %(father)s."),
      ],
      [
        _("She is the daughter of %(father)s."),
        _("She was the daughter of %(father)s."),
      ],
      _("Daughter of %(father)s."),
    ],
}

child_mother = {
    Person.UNKNOWN : [
      [
        _("%(male_name)s is the child of %(mother)s."),
        _("%(male_name)s was the child of %(mother)s."),
      ],
      [
        _("This person is the child of %(mother)s."),
        _("This person was the child of %(mother)s."),
      ],
      _("Child of %(mother)s."),
    ],
    Person.MALE : [
      [
        _("%(male_name)s is the son of %(mother)s."),
        _("%(male_name)s was the son of %(mother)s."),
      ],
      [
        _("He is the son of %(mother)s."),
        _("He was the son of %(mother)s."),
      ],
      _("Son of %(mother)s."),
    ],
    Person.FEMALE : [
      [
        _("%(female_name)s is the daughter of %(mother)s."),
        _("%(female_name)s was the daughter of %(mother)s."),
      ],
      [
        _("She is the daughter of %(mother)s."),
        _("She was the daughter of %(mother)s."),
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
class Narrator:
    """
    Narrator is a class which provides narration text.
    """

    def __init__(self, dbase, verbose=True,
                 use_call_name=False, use_fulldate=False,
                 empty_date="", empty_place="", place_format=-1,
                 nlocale=glocale,
                 get_endnote_numbers=_get_empty_endnote_numbers):
        """
        Initialize the narrator class.

        If nlocale is passed in (a GrampsLocale), then
        the translated values will be returned instead.

        :param dbase: The database that contains the data to be narrated.
        :type dbase: :class:`~gen.db.base,DbBase`
        :param verbose: Specifies whether complete sentences should be used.
        :type verbose: bool
        :param use_call_name: Specifies whether a person's call name should be
            used for the first name.
        :type use_call_name: bool
        :param empty_date: String to use when a date is not known.
        :type empty_date: str
        :param empty_place: String to use when a place is not known.
        :type empty_place: str
        :param get_endnote_numbers: A callable to use for getting a string
            representing endnote numbers.
            The function takes a :class:`~gen.lib.CitationBase` instance.
            A typical return value from get_endnote_numbers() would be "2a" and
            would represent a reference to an endnote in a document.
        :type get_endnote_numbers:
            callable( :class:`~gen.lib.CitationBase` )
        :param nlocale: allow deferred translation of dates and strings
        :type nlocale: a GrampsLocale instance
        :param place_format: allow display of places in any place format
        :type place_format: int
        """
        self.__db = dbase
        self.__verbose = verbose
        self.__use_call = use_call_name
        self.__use_fulldate = use_fulldate
        self.__empty_date = empty_date
        self.__empty_place = empty_place
        self.__get_endnote_numbers = get_endnote_numbers
        self.__person = None
        self.__first_name = ""
        self.__first_name_used = False

        self.__translate_text = nlocale.translation.gettext
        self.__get_date = nlocale.get_date
        self._locale = nlocale
        self._place_format = place_format

    def set_subject(self, person):
        """
        Start a new story about this person. The person's first name will be
        used in the first sentence. A pronoun will be used as the subject for
        each subsequent sentence.
        :param person: The person to be the subject of the story.
        :type person: :class:`~gen.lib.person,Person`
        """
        self.__person = person

        if self.__use_call and person.get_primary_name().get_call_name():
            self.__first_name = person.get_primary_name().get_call_name()
        else:
            self.__first_name = person.get_primary_name().get_first_name()

        if self.__first_name:
            self.__first_name_used = False # use their name the first time
        else:
            self.__first_name_used = True # but use a pronoun if no name

    def get_born_string(self):
        """
        Get a string narrating the birth of the subject.
        Example sentences:
            Person was born on Date.
            Person was born on Date in Place.
            Person was born in Place.
            ''

        :returns: A sentence about the subject's birth.
        :rtype: unicode
        """
        if not self.__first_name_used:
            name_index = _NAME_INDEX_INCLUDE_NAME
            self.__first_name_used = True
        else:
            name_index = _NAME_INDEX_EXCLUDE_NAME

        text = ""

        bplace = self.__empty_place
        bdate = self.__empty_date
        birth_event = None
        bdate_full = False
        bdate_mod = False

        birth_ref = self.__person.get_birth_ref()
        if birth_ref and birth_ref.ref:
            birth_event = self.__db.get_event_from_handle(birth_ref.ref)
            if birth_event:
                if self.__use_fulldate :
                    bdate = self.__get_date(birth_event.get_date_object())
                else:
                    bdate = birth_event.get_date_object().get_year()
                bplace_handle = birth_event.get_place_handle()
                if bplace_handle:
                    place = self.__db.get_place_from_handle(bplace_handle)
                    bplace = _pd.display_event(self.__db, birth_event,
                                               fmt=self._place_format)
                bdate_obj = birth_event.get_date_object()
                bdate_full = bdate_obj and bdate_obj.get_day_valid()
                bdate_mod = bdate_obj and \
                            bdate_obj.get_modifier() != Date.MOD_NONE

        value_map = {
            'name'                : self.__first_name,
            'male_name'           : self.__first_name,
            'unknown_gender_name' : self.__first_name,
            'female_name'         : self.__first_name,
            'birth_date'          : bdate,
            'birth_place'         : bplace,
            'month_year'          : bdate,
            'modified_date'       : bdate,
            }

        gender = self.__person.get_gender()

        if bdate:
            if bdate_mod:
                if bplace and self.__verbose:
                    text = born_modified_date_with_place[name_index][gender]
                elif bplace:
                    text = born_modified_date_with_place[2]
                elif self.__verbose:
                    text = born_modified_date_no_place[name_index][gender]
                else:
                    text = born_modified_date_no_place[2]
            elif bdate_full:
                if bplace and self.__verbose:
                    text = born_full_date_with_place[name_index][gender]
                elif bplace:
                    text = born_full_date_with_place[2]
                elif self.__verbose:
                    text = born_full_date_no_place[name_index][gender]
                else:
                    text = born_full_date_no_place[2]
            else:
                if bplace and self.__verbose:
                    text = born_partial_date_with_place[name_index][gender]
                elif bplace:
                    text = born_partial_date_with_place[2]
                elif self.__verbose:
                    text = born_partial_date_no_place[name_index][gender]
                else:
                    text = born_partial_date_no_place[2]
        else:
            if bplace and self.__verbose:
                text = born_no_date_with_place[name_index][gender]
            elif bplace:
                text = born_no_date_with_place[2]
            else:
                text = ""

        if text:
            text = self.__translate_text(text) % value_map

            if birth_event:
                text = text.rstrip(". ")
                text = text + self.__get_endnote_numbers(birth_event) + ". "

            text = text + " "

        return text

    def get_died_string(self, include_age=False):
        """
        Get a string narrating the death of the subject.
        Example sentences:
            Person died on Date
            Person died on Date at the age of 'age'
            Person died on Date in Place
            Person died on Date in Place at the age of 'age'
            Person died in Place
            Person died in Place at the age of 'age'
            Person died
            ''
        where 'age' string is an advanced age calculation.

        :returns: A sentence about the subject's death.
        :rtype: unicode
        """

        if not self.__first_name_used:
            name_index = _NAME_INDEX_INCLUDE_NAME
            self.__first_name_used = True
        else:
            name_index = _NAME_INDEX_EXCLUDE_NAME

        text = ""

        dplace = self.__empty_place
        ddate = self.__empty_date
        death_event = None
        ddate_full = False
        ddate_mod = False

        death_ref = self.__person.get_death_ref()
        if death_ref and death_ref.ref:
            death_event = self.__db.get_event_from_handle(death_ref.ref)
            if death_event:
                if self.__use_fulldate :
                    ddate = self.__get_date(death_event.get_date_object())
                else:
                    ddate = death_event.get_date_object().get_year()
                dplace_handle = death_event.get_place_handle()
                if dplace_handle:
                    place = self.__db.get_place_from_handle(dplace_handle)
                    dplace = _pd.display_event(self.__db, death_event,
                                               fmt=self._place_format)
                ddate_obj = death_event.get_date_object()
                ddate_full = ddate_obj and ddate_obj.get_day_valid()
                ddate_mod = ddate_obj and \
                            ddate_obj.get_modifier() != Date.MOD_NONE

        if include_age:
            age, age_index = self.__get_age_at_death()
        else:
            age = 0
            age_index = _AGE_INDEX_NO_AGE

        value_map = {
            'name'                : self.__first_name,
            'unknown_gender_name' : self.__first_name,
            'male_name'           : self.__first_name,
            'female_name'         : self.__first_name,
            'death_date'          : ddate,
            'modified_date'       : ddate,
            'death_place'         : dplace,
            'age'                 : age,
            'month_year'          : ddate,
            }

        gender = self.__person.get_gender()

        if ddate and ddate_mod:
            if dplace and self.__verbose:
                text = died_modified_date_with_place[name_index][gender][age_index]
            elif dplace:
                text = died_modified_date_with_place[2][age_index]
            elif self.__verbose:
                text = died_modified_date_no_place[name_index][gender][age_index]
            else:
                text = died_modified_date_no_place[2][age_index]
        elif ddate and ddate_full:
            if dplace and self.__verbose:
                text = died_full_date_with_place[name_index][gender][age_index]
            elif dplace:
                text = died_full_date_with_place[2][age_index]
            elif self.__verbose:
                text = died_full_date_no_place[name_index][gender][age_index]
            else:
                text = died_full_date_no_place[2][age_index]
        elif ddate:
            if dplace and self.__verbose:
                text = died_partial_date_with_place[name_index][gender][age_index]
            elif dplace:
                text = died_partial_date_with_place[2][age_index]
            elif self.__verbose:
                text = died_partial_date_no_place[name_index][gender][age_index]
            else:
                text = died_partial_date_no_place[2][age_index]
        elif dplace and self.__verbose:
            text = died_no_date_with_place[name_index][gender][age_index]
        elif dplace:
            text = died_no_date_with_place[2][age_index]
        elif self.__verbose:
            text = died_no_date_no_place[name_index][gender][age_index]
        else:
            text = died_no_date_no_place[2][age_index]

        if text:
            text = self.__translate_text(text) % value_map

            if death_event:
                text = text.rstrip(". ")
                text = text + self.__get_endnote_numbers(death_event) + ". "

            text = text + " "

        return text

    def get_buried_string(self):
        """
        Get a string narrating the burial of the subject.
        Example sentences:
            Person was  buried on Date.
            Person was  buried on Date in Place.
            Person was  buried in Month_Year.
            Person was  buried in Month_Year in Place.
            Person was  buried in Place.
            ''

        :returns: A sentence about the subject's burial.
        :rtype: unicode
        """

        if not self.__first_name_used:
            name_index = _NAME_INDEX_INCLUDE_NAME
            self.__first_name_used = True
        else:
            name_index = _NAME_INDEX_EXCLUDE_NAME

        gender = self.__person.get_gender()

        text = ""

        bplace = self.__empty_place
        bdate = self.__empty_date
        bdate_full = False
        bdate_mod = False

        burial = None
        for event_ref in self.__person.get_event_ref_list():
            event = self.__db.get_event_from_handle(event_ref.ref)
            if event and event.type.value == EventType.BURIAL \
                     and event_ref.role.value == EventRoleType.PRIMARY:
                burial = event
                break

        if burial:
            if self.__use_fulldate :
                bdate = self.__get_date(burial.get_date_object())
            else:
                bdate = burial.get_date_object().get_year()
            bplace_handle = burial.get_place_handle()
            if bplace_handle:
                place = self.__db.get_place_from_handle(bplace_handle)
                bplace = _pd.display_event(self.__db, burial,
                                           fmt=self._place_format)
            bdate_obj = burial.get_date_object()
            bdate_full = bdate_obj and bdate_obj.get_day_valid()
            bdate_mod = bdate_obj and bdate_obj.get_modifier() != Date.MOD_NONE
        else:
            return text

        value_map = {
            'unknown_gender_name' : self.__first_name,
            'male_name'           : self.__first_name,
            'name'                : self.__first_name,
            'female_name'         : self.__first_name,
            'burial_date'         : bdate,
            'burial_place'        : bplace,
            'month_year'          : bdate,
            'modified_date'       : bdate,
            'endnotes'            : self.__get_endnote_numbers(event),
            }

        if bdate and bdate_mod and self.__verbose:
            if bplace: #male, date, place
                text = buried_modified_date_place[gender][name_index]
            else:      #male, date, no place
                text = buried_modified_date_no_place[gender][name_index]
        elif bdate and bdate_mod:
            if bplace: #male, date, place
                text = buried_modified_date_place['succinct']
            else:      #male, date, no place
                text = buried_modified_date_no_place['succinct']
        elif bdate and bdate_full and self.__verbose:
            if bplace: #male, date, place
                text = buried_full_date_place[gender][name_index]
            else:      #male, date, no place
                text = buried_full_date_no_place[gender][name_index]
        elif bdate and bdate_full:
            if bplace: #male, date, place
                text = buried_full_date_place['succinct']
            else:      #male, date, no place
                text = buried_full_date_no_place['succinct']
        elif bdate and self.__verbose:
            if bplace: #male, month_year, place
                text = buried_partial_date_place[gender][name_index]
            else:      #male, month_year, no place
                text = buried_partial_date_no_place[gender][name_index]
        elif bdate:
            if bplace: #male, month_year, place
                text = buried_partial_date_place['succinct']
            else:      #male, month_year, no place
                text = buried_partial_date_no_place['succinct']
        elif bplace and self.__verbose:   #male, no date, place
            text = buried_no_date_place[gender][name_index]
        elif bplace:   #male, no date, place
            text = buried_no_date_place['succinct']
        elif self.__verbose:
            text = buried_no_date_no_place[gender][name_index]
        else:          #male, no date, no place
            text = buried_no_date_no_place['succinct']

        if text:
            text = self.__translate_text(text) % value_map
            text = text + " "

        return text

    def get_baptised_string(self):
        """
        Get a string narrating the baptism of the subject.
        Example sentences:
            Person was baptized on Date.
            Person was baptized on Date in Place.
            Person was baptized in Month_Year.
            Person was baptized in Month_Year in Place.
            Person was baptized in Place.
            ''

        :returns: A sentence about the subject's baptism.
        :rtype: unicode
        """

        if not self.__first_name_used:
            name_index = _NAME_INDEX_INCLUDE_NAME
            self.__first_name_used = True
        else:
            name_index = _NAME_INDEX_EXCLUDE_NAME

        gender = self.__person.get_gender()

        text = ""

        bplace = self.__empty_place
        bdate = self.__empty_date
        bdate_full = False
        bdate_mod = False

        baptism = None
        for event_ref in self.__person.get_event_ref_list():
            event = self.__db.get_event_from_handle(event_ref.ref)
            if event and event.type.value == EventType.BAPTISM \
                and event_ref.role.value == EventRoleType.PRIMARY:
                baptism = event
                break

        if baptism:
            if self.__use_fulldate :
                bdate = self.__get_date(baptism.get_date_object())
            else:
                bdate = baptism.get_date_object().get_year()
            bplace_handle = baptism.get_place_handle()
            if bplace_handle:
                place = self.__db.get_place_from_handle(bplace_handle)
                bplace = _pd.display_event(self.__db, baptism,
                                           fmt=self._place_format)
            bdate_obj = baptism.get_date_object()
            bdate_full = bdate_obj and bdate_obj.get_day_valid()
            bdate_mod = bdate_obj and bdate_obj.get_modifier() != Date.MOD_NONE
        else:
            return text

        value_map = {
            'unknown_gender_name' : self.__first_name,
            'male_name'           : self.__first_name,
            'name'                : self.__first_name,
            'female_name'         : self.__first_name,
            'baptism_date'        : bdate,
            'baptism_place'       : bplace,
            'month_year'          : bdate,
            'modified_date'       : bdate,
            'endnotes'            : self.__get_endnote_numbers(event),
            }

        if bdate and bdate_mod and self.__verbose:
            if bplace: #male, date, place
                text = baptised_modified_date_place[gender][name_index]
            else:      #male, date, no place
                text = baptised_modified_date_no_place[gender][name_index]
        elif bdate and bdate_mod:
            if bplace: #male, date, place
                text = baptised_modified_date_place['succinct']
            else:      #male, date, no place
                text = baptised_modified_date_no_place['succinct']
        elif bdate and bdate_full and self.__verbose:
            if bplace: #male, date, place
                text = baptised_full_date_place[gender][name_index]
            else:      #male, date, no place
                text = baptised_full_date_no_place[gender][name_index]
        elif bdate and bdate_full:
            if bplace: #male, date, place
                text = baptised_full_date_place['succinct']
            else:      #male, date, no place
                text = baptised_full_date_no_place['succinct']
        elif bdate and self.__verbose:
            if bplace: #male, month_year, place
                text = baptised_partial_date_place[gender][name_index]
            else:      #male, month_year, no place
                text = baptised_partial_date_no_place[gender][name_index]
        elif bdate:
            if bplace: #male, month_year, place
                text = baptised_partial_date_place['succinct']
            else:      #male, month_year, no place
                text = baptised_partial_date_no_place['succinct']
        elif bplace and self.__verbose:   #male, no date, place
            text = baptised_no_date_place[gender][name_index]
        elif bplace:   #male, no date, place
            text = baptised_no_date_place['succinct']
        elif self.__verbose:
            text = baptised_no_date_no_place[gender][name_index]
        else:          #male, no date, no place
            text = baptised_no_date_no_place['succinct']

        if text:
            text = self.__translate_text(text) % value_map
            text = text + " "

        return text

    def get_christened_string(self):
        """
        Get a string narrating the christening of the subject.
        Example sentences:
            Person was christened on Date.
            Person was christened on Date in Place.
            Person was christened in Month_Year.
            Person was christened in Month_Year in Place.
            Person was christened in Place.
            ''

        :returns: A sentence about the subject's christening.
        :rtype: unicode
        """

        if not self.__first_name_used:
            name_index = _NAME_INDEX_INCLUDE_NAME
            self.__first_name_used = True
        else:
            name_index = _NAME_INDEX_EXCLUDE_NAME

        gender = self.__person.get_gender()

        text = ""

        cplace = self.__empty_place
        cdate = self.__empty_date
        cdate_full = False
        cdate_mod = False

        christening = None
        for event_ref in self.__person.get_event_ref_list():
            event = self.__db.get_event_from_handle(event_ref.ref)
            if event and event.type.value == EventType.CHRISTEN \
                and event_ref.role.value == EventRoleType.PRIMARY:
                christening = event
                break

        if christening:
             if self.__use_fulldate :
                cdate = self.__get_date(christening.get_date_object())
             else:
                cdate = christening.get_date_object().get_year()
             cplace_handle = christening.get_place_handle()
             if cplace_handle:
                place = self.__db.get_place_from_handle(cplace_handle)
                cplace = _pd.display_event(self.__db, christening,
                                           fmt=self._place_format)
             cdate_obj = christening.get_date_object()
             cdate_full = cdate_obj and cdate_obj.get_day_valid()
             cdate_mod = cdate_obj and cdate_obj.get_modifier() != Date.MOD_NONE
        else:
            return text

        value_map = {
            'unknown_gender_name' : self.__first_name,
            'male_name'           : self.__first_name,
            'name'                : self.__first_name,
            'female_name'         : self.__first_name,
            'christening_date'    : cdate,
            'christening_place'   : cplace,
            'month_year'          : cdate,
            'modified_date'       : cdate,
            'endnotes'            : self.__get_endnote_numbers(event),
            }

        if cdate and cdate_mod and self.__verbose:
            if cplace: #male, date, place
                text = christened_modified_date_place[gender][name_index]
            else:      #male, date, no place
                text = christened_modified_date_no_place[gender][name_index]
        elif cdate and cdate_mod:
            if cplace: #male, date, place
                text = christened_modified_date_place['succinct']
            else:      #male, date, no place
                text = christened_modified_date_no_place['succinct']
        elif cdate and cdate_full and self.__verbose:
            if cplace: #male, date, place
                text = christened_full_date_place[gender][name_index]
            else:      #male, date, no place
                text = christened_full_date_no_place[gender][name_index]
        elif cdate and cdate_full:
            if cplace: #male, date, place
                text = christened_full_date_place['succinct']
            else:      #male, date, no place
                text = christened_full_date_no_place['succinct']
        elif cdate and self.__verbose:
            if cplace: #male, month_year, place
                text = christened_partial_date_place[gender][name_index]
            else:      #male, month_year, no place
                text = christened_partial_date_no_place[gender][name_index]
        elif cdate:
            if cplace: #male, month_year, place
                text = christened_partial_date_place['succinct']
            else:      #male, month_year, no place
                text = christened_partial_date_no_place['succinct']
        elif cplace and self.__verbose:   #male, no date, place
            text = christened_no_date_place[gender][name_index]
        elif cplace:   #male, no date, place
            text = christened_no_date_place['succinct']
        elif self.__verbose:
            text = christened_no_date_no_place[gender][name_index]
        else:          #male, no date, no place
            text = christened_no_date_no_place['succinct']

        if text:
            text = self.__translate_text(text) % value_map
            text = text + " "

        return text

    def get_married_string(self, family, is_first=True, name_display=None):
        """
        Get a string narrating the marriage of the subject.
        Example sentences:
            Person was married to Spouse on Date.
            Person was married to Spouse.
            Person was also married to Spouse on Date.
            Person was also married to Spouse.
            ""

        :param family: The family that contains the Spouse for this marriage.
        :type family: :class:`~gen.lib.family,Family`
        :param is_first: Indicates whether this sentence represents the first
            marriage. If it is not the first marriage, the sentence will
            include "also".
        :type is_first: bool
        :param name_display: An object to be used for displaying names
        :type name_display: :class:`~gen.display.name,NameDisplay`
        :returns: A sentence about the subject's marriage.
        :rtype: unicode
        """


        date = self.__empty_date
        place = self.__empty_place

        spouse_name = None
        spouse_handle = utils.find_spouse(self.__person, family)
        if spouse_handle:
            spouse = self.__db.get_person_from_handle(spouse_handle)
            if spouse:
                if not name_display:
                    spouse_name = _nd.display(spouse)
                else:
                    spouse_name = name_display.display(spouse)
        if not spouse_name:
            spouse_name = self.__translate_text("Unknown") # not: _("Unknown")

        event = utils.find_marriage(self.__db, family)
        if event:
            if self.__use_fulldate :
                mdate = self.__get_date(event.get_date_object())
            else:
                mdate = event.get_date_object().get_year()
            if mdate:
                date = mdate
            place_handle = event.get_place_handle()
            if place_handle:
                place_obj = self.__db.get_place_from_handle(place_handle)
                place = _pd.display_event(self.__db, event,
                                          fmt=self._place_format)
        relationship = family.get_relationship()

        value_map = {
            'spouse'        : spouse_name,
            'endnotes'      : self.__get_endnote_numbers(event),
            'full_date'     : date,
            'modified_date' : date,
            'partial_date'  : date,
            'place'         : place,
            }

        date_full = 0

        if event:
            dobj = event.get_date_object()

            if dobj.get_modifier() != Date.MOD_NONE:
                date_full = 2
            elif dobj and dobj.get_day_valid():
                date_full = 1

        gender = self.__person.get_gender()

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
            if date and place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date_place[gender][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date_place[gender][date_full]
                else:
                    text = relationship_first_date_place[gender][date_full]
            elif date and place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date_place['succinct'][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date_place['succinct'][date_full]
                else:
                    text = relationship_first_date_place['succinct'][date_full]
            elif date and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date[gender][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date[gender][date_full]
                else:
                    text = relationship_first_date[gender][date_full]
            elif date:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_date['succinct'][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_date['succinct'][date_full]
                else:
                    text = relationship_first_date['succinct'][date_full]
            elif place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_place[gender]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_place[gender]
                else:
                    text = relationship_first_place[gender]
            elif place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_place['succinct']
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_place['succinct']
                else:
                    text = relationship_first_place['succinct']
            elif self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_only[gender]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_only[gender]
                else:
                    text = relationship_first_only[gender]
            else:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_first_only['succinct']
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_first_only['succinct']
                else:
                    text = relationship_first_only['succinct']
        else:
            if date and place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date_place[gender][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date_place[gender][date_full]
                else:
                    text = relationship_also_date_place[gender][date_full]
            elif date and place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date_place['succinct'][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date_place['succinct'][date_full]
                else:
                    text = relationship_also_date_place['succinct'][date_full]
            elif date and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date[gender][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date[gender][date_full]
                else:
                    text = relationship_also_date[gender][date_full]
            elif date:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_date['succinct'][date_full]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_date['succinct'][date_full]
                else:
                    text = relationship_also_date['succinct'][date_full]
            elif place and self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_place[gender]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_place[gender]
                else:
                    text = relationship_also_place[gender]
            elif place:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_place['succinct']
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_place['succinct']
                else:
                    text = relationship_also_place['succinct']
            elif self.__verbose:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_only[gender]
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_only[gender]
                else:
                    text = relationship_also_only[gender]
            else:
                if relationship == FamilyRelType.MARRIED:
                    text = marriage_also_only['succinct']
                elif relationship == FamilyRelType.UNMARRIED:
                    text = unmarried_also_only['succinct']
                else:
                    text = relationship_also_only['succinct']

        if text:
            text = self.__translate_text(text) % value_map
            text = text + " "
        return text

    def get_child_string(self, father_name="", mother_name=""):
        """
        Get a string narrating the relationship to the parents of the subject.
        Missing information will be omitted without loss of readability.
        Example sentences:
            Person was the son of father_name and mother_name.
            Person was the daughter of father_name and mother_name.
            ""

        :param father_name: The name of the Subjects' father.
        :type father_name: unicode
        :param mother_name: The name of the Subjects' mother.
        :type mother_name: unicode
        :returns: A sentence about the subject's parents.
        :rtype: unicode
        """

        value_map = {
            'father'              : father_name,
            'mother'              : mother_name,
            'male_name'           : self.__first_name,
            'name'                : self.__first_name,
            'female_name'         : self.__first_name,
            'unknown_gender_name' : self.__first_name,
            }

        dead = not probably_alive(self.__person, self.__db)

        if not self.__first_name_used:
            index = _NAME_INDEX_INCLUDE_NAME
            self.__first_name_used = True
        else:
            index = _NAME_INDEX_EXCLUDE_NAME

        gender = self.__person.get_gender()

        text = ""
        if mother_name and father_name and self.__verbose:
            text = child_father_mother[gender][index][dead]
        elif mother_name and father_name:
            text = child_father_mother[gender][2]
        elif mother_name and self.__verbose:
            text = child_mother[gender][index][dead]
        elif mother_name:
            text = child_mother[gender][2]
        elif father_name and self.__verbose:
            text = child_father[gender][index][dead]
        elif father_name:
            text = child_father[gender][2]

        if text:
            text = self.__translate_text(text) % value_map
            text = text + " "

        return text

    def __get_age_at_death(self):
        """
        Calculate the age the person died.

        Returns a tuple representing (age, age_index).
        """
        birth_ref = self.__person.get_birth_ref()
        if birth_ref:
            birth_event = self.__db.get_event_from_handle(birth_ref.ref)
            birth = birth_event.get_date_object()
            birth_year_valid = birth.get_year_valid()
        else:
            birth_year_valid = False
        death_ref = self.__person.get_death_ref()
        if death_ref:
            death_event = self.__db.get_event_from_handle(death_ref.ref)
            death = death_event.get_date_object()
            death_year_valid = death.get_year_valid()
        else:
            death_year_valid = False

        # without at least a year for each event no age can be calculated
        if birth_year_valid and death_year_valid:
            span = death - birth
            if span and span.is_valid():
                if span:
                    age = span.get_repr(dlocale=self._locale)
                    age_index = _AGE_INDEX
                else:
                    age = 0
                    age_index = _AGE_INDEX_NO_AGE
            else:
                age = 0
                age_index = _AGE_INDEX_NO_AGE
        else:
            age = 0
            age_index = _AGE_INDEX_NO_AGE

        return age, age_index
