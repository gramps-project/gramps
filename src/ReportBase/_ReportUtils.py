#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
#
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
A collection of utilities to aid in the generation of reports.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import time
import os
from gettext import gettext as _
import cStringIO

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import DateHandler
import RelLib
from BasicUtils.NameDisplay import displayer as _nd
from QuestionDialog import WarningDialog
import BaseDoc

#------------------------------------------------------------------------
#
# Born strings
#
#------------------------------------------------------------------------

born_full_date_with_place = [
  {
    RelLib.Person.UNKNOWN :  _("This person was born on %(birth_date)s in %(birth_place)s."),
    RelLib.Person.MALE :  _("He was born on %(birth_date)s in %(birth_place)s."),
    RelLib.Person.FEMALE : _("She was born on %(birth_date)s in %(birth_place)s."),
  },
  {
    RelLib.Person.UNKNOWN : _("%(unknown_gender_name)s was born on %(birth_date)s in %(birth_place)s."),
    RelLib.Person.MALE : _("%(male_name)s was born on %(birth_date)s in %(birth_place)s."),
    RelLib.Person.FEMALE : _("%(female_name)s was born on %(birth_date)s in %(birth_place)s."),
  },
]

born_modified_date_with_place = [
  {
    RelLib.Person.UNKNOWN :  _("This person was born %(modified_date)s in %(birth_place)s."),
    RelLib.Person.MALE :  _("He was born %(modified_date)s in %(birth_place)s."),
    RelLib.Person.FEMALE : _("She was born %(modified_date)s in %(birth_place)s."),
  },
  {
    RelLib.Person.UNKNOWN : _("%(unknown_gender_name)s was born %(modified_date)s in %(birth_place)s."),
    RelLib.Person.MALE : _("%(male_name)s was born %(modified_date)s in %(birth_place)s."),
    RelLib.Person.FEMALE : _("%(female_name)s was born %(modified_date)s in %(birth_place)s."),
  },
]

born_full_date_no_place = [
  {
    RelLib.Person.UNKNOWN : _("This person was born on %(birth_date)s."),
    RelLib.Person.MALE : _("He was born on %(birth_date)s."),
    RelLib.Person.FEMALE : _("She was born on %(birth_date)s."),
  },
  {
    RelLib.Person.UNKNOWN : _("%(unknown_gender_name)s was born on %(birth_date)s."),
    RelLib.Person.MALE : _("%(male_name)s was born on %(birth_date)s."),
    RelLib.Person.FEMALE : _("%(female_name)s was born on %(birth_date)s."),
  },
]  

born_modified_date_no_place = [
  {
    RelLib.Person.UNKNOWN : _("This person was born %(modified_date)s."),
    RelLib.Person.MALE : _("He was born %(modified_date)s."),
    RelLib.Person.FEMALE : _("She was born %(modified_date)s."),
  },
  {
    RelLib.Person.UNKNOWN : _("%(unknown_gender_name)s was born %(modified_date)s."),
    RelLib.Person.MALE : _("%(male_name)s was born %(modified_date)s."),
    RelLib.Person.FEMALE : _("%(female_name)s was born %(modified_date)s."),
  },
]  

born_partial_date_with_place = [
  {
    RelLib.Person.UNKNOWN : _("This person was born in %(month_year)s in %(birth_place)s."),
    RelLib.Person.MALE : _("He was born in %(month_year)s in %(birth_place)s."),
    RelLib.Person.FEMALE : _("She was born in %(month_year)s in %(birth_place)s."),
  },
  {
    RelLib.Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(month_year)s in %(birth_place)s."),
    RelLib.Person.MALE : _("%(male_name)s was born in %(month_year)s in %(birth_place)s."),
    RelLib.Person.FEMALE : _("%(female_name)s was born in %(month_year)s in %(birth_place)s."),
  },
]  

born_partial_date_no_place = [
  {
    RelLib.Person.UNKNOWN : _("This person was born in %(month_year)s."),
    RelLib.Person.MALE : _("He was born in %(month_year)s."),
    RelLib.Person.FEMALE : _("She was born in %(month_year)s."),
  },
  {
    RelLib.Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(month_year)s."),
    RelLib.Person.MALE : _("%(male_name)s was born in %(month_year)s."),
    RelLib.Person.FEMALE : _("%(female_name)s was born in %(month_year)s."),
  }
]  

born_no_date_with_place = [
  {
    RelLib.Person.UNKNOWN : _("This person was born in %(birth_place)s."),
    RelLib.Person.MALE : _("He was born in %(birth_place)s."),
    RelLib.Person.FEMALE : _("She was born in %(birth_place)s."),
  },
  {
    RelLib.Person.UNKNOWN : _("%(unknown_gender_name)s was born in %(birth_place)s."),
    RelLib.Person.MALE : _("%(male_name)s was born in %(birth_place)s."),
    RelLib.Person.FEMALE : _("%(female_name)s was born in %(birth_place)s."),
  }
]  

#------------------------------------------------------------------------
#
# Died strings
#
#------------------------------------------------------------------------

died_full_date_with_place = [
  { RelLib.Person.UNKNOWN : [
    _("This person died on %(death_date)s in %(death_place)s."),
    _("This person died on %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("This person died on %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("This person died on %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("He died on %(death_date)s in %(death_place)s."),
    _("He died on %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("He died on %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("He died on %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("She died on %(death_date)s in %(death_place)s."),
    _("She died on %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("She died on %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("She died on %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
  },
  { RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s."),
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("%(unknown_gender_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("%(male_name)s died on %(death_date)s in %(death_place)s."),
    _("%(male_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("%(male_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("%(male_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("%(female_name)s died on %(death_date)s in %(death_place)s."),
    _("%(female_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("%(female_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("%(female_name)s died on %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
  },
]

died_modified_date_with_place = [
  { RelLib.Person.UNKNOWN : [
    _("This person died %(death_date)s in %(death_place)s."),
    _("This person died %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("This person died %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("This person died %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("He died %(death_date)s in %(death_place)s."),
    _("He died %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("He died %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("He died %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("She died %(death_date)s in %(death_place)s."),
    _("She died %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("She died %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("She died %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
  },
  { RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s."),
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("%(unknown_gender_name)s died %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("%(male_name)s died %(death_date)s in %(death_place)s."),
    _("%(male_name)s died %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("%(male_name)s died %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("%(male_name)s died %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("%(female_name)s died %(death_date)s in %(death_place)s."),
    _("%(female_name)s died %(death_date)s in %(death_place)s at the age of %(age)d years."),
    _("%(female_name)s died %(death_date)s in %(death_place)s at the age of %(age)d months."),
    _("%(female_name)s died %(death_date)s in %(death_place)s at the age of %(age)d days."),
    ],
  },
]

died_full_date_no_place = [
  { RelLib.Person.UNKNOWN : [
    _("This person died on %(death_date)s."),
    _("This person died on %(death_date)s at the age of %(age)d years."),
    _("This person died on %(death_date)s at the age of %(age)d months."),
    _("This person died on %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("He died on %(death_date)s."),
    _("He died on %(death_date)s at the age of %(age)d years."),
    _("He died on %(death_date)s at the age of %(age)d months."),
    _("He died on %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("She died on %(death_date)s."),
    _("She died on %(death_date)s at the age of %(age)d years."),
    _("She died on %(death_date)s at the age of %(age)d months."),
    _("She died on %(death_date)s at the age of %(age)d days."),
    ],
  },
  { RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s died on %(death_date)s."),
    _("%(unknown_gender_name)s died on %(death_date)s at the age of %(age)d years."),
    _("%(unknown_gender_name)s died on %(death_date)s at the age of %(age)d months."),
    _("%(unknown_gender_name)s died on %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("%(male_name)s died on %(death_date)s."),
    _("%(male_name)s died on %(death_date)s at the age of %(age)d years."),
    _("%(male_name)s died on %(death_date)s at the age of %(age)d months."),
    _("%(male_name)s died on %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("%(female_name)s died on %(death_date)s."),
    _("%(female_name)s died on %(death_date)s at the age of %(age)d years."),
    _("%(female_name)s died on %(death_date)s at the age of %(age)d months."),
    _("%(female_name)s died on %(death_date)s at the age of %(age)d days."),
    ],
  },
]  

died_modified_date_no_place = [
  { RelLib.Person.UNKNOWN : [
    _("This person died %(death_date)s."),
    _("This person died %(death_date)s at the age of %(age)d years."),
    _("This person died %(death_date)s at the age of %(age)d months."),
    _("This person died %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("He died %(death_date)s."),
    _("He died %(death_date)s at the age of %(age)d years."),
    _("He died %(death_date)s at the age of %(age)d months."),
    _("He died %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("She died %(death_date)s."),
    _("She died %(death_date)s at the age of %(age)d years."),
    _("She died %(death_date)s at the age of %(age)d months."),
    _("She died %(death_date)s at the age of %(age)d days."),
    ],
  },
  { RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s died %(death_date)s."),
    _("%(unknown_gender_name)s died %(death_date)s at the age of %(age)d years."),
    _("%(unknown_gender_name)s died %(death_date)s at the age of %(age)d months."),
    _("%(unknown_gender_name)s died %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("%(male_name)s died %(death_date)s."),
    _("%(male_name)s died %(death_date)s at the age of %(age)d years."),
    _("%(male_name)s died %(death_date)s at the age of %(age)d months."),
    _("%(male_name)s died %(death_date)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("%(female_name)s died %(death_date)s."),
    _("%(female_name)s died %(death_date)s at the age of %(age)d years."),
    _("%(female_name)s died %(death_date)s at the age of %(age)d months."),
    _("%(female_name)s died %(death_date)s at the age of %(age)d days."),
    ],
  },
]  

died_partial_date_with_place = [
  { RelLib.Person.UNKNOWN : [
    _("This person died in %(month_year)s in %(death_place)s."),
    _("This person died in %(month_year)s in %(death_place)s at the age of %(age)d years."),
    _("This person died in %(month_year)s in %(death_place)s at the age of %(age)d months."),
    _("This person died in %(month_year)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("He died in %(month_year)s in %(death_place)s."),
    _("He died in %(month_year)s in %(death_place)s at the age of %(age)d years."),
    _("He died in %(month_year)s in %(death_place)s at the age of %(age)d months."),
    _("He died in %(month_year)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("She died in %(month_year)s in %(death_place)s."),
    _("She died in %(month_year)s in %(death_place)s at the age of %(age)d years."),
    _("She died in %(month_year)s in %(death_place)s at the age of %(age)d months."),
    _("She died in %(month_year)s in %(death_place)s at the age of %(age)d days."),
    ]
  },
  { RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s."),
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d years."),
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d months."),
    _("%(unknown_gender_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("%(male_name)s died in %(month_year)s in %(death_place)s."),
    _("%(male_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d years."),
    _("%(male_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d months."),
    _("%(male_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("%(female_name)s died in %(month_year)s in %(death_place)s."),
    _("%(female_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d years."),
    _("%(female_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d months."),
    _("%(female_name)s died in %(month_year)s in %(death_place)s at the age of %(age)d days."),
    ],
  },
]  

died_partial_date_no_place = [
  { RelLib.Person.UNKNOWN : [
    _("This person died in %(month_year)s."),
    _("This person died in %(month_year)s at the age of %(age)d years."),
    _("This person died in %(month_year)s at the age of %(age)d months."),
    _("This person died in %(month_year)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("He died in %(month_year)s."),
    _("He died in %(month_year)s at the age of %(age)d years."),
    _("He died in %(month_year)s at the age of %(age)d months."),
    _("He died in %(month_year)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("She died in %(month_year)s."),
    _("She died in %(month_year)s at the age of %(age)d years."),
    _("She died in %(month_year)s at the age of %(age)d months."),
    _("She died in %(month_year)s at the age of %(age)d days."),
    ],
  },
  { RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(month_year)s."),
    _("%(unknown_gender_name)s died in %(month_year)s at the age of %(age)d years."),
    _("%(unknown_gender_name)s died in %(month_year)s at the age of %(age)d months."),
    _("%(unknown_gender_name)s died in %(month_year)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("%(male_name)s died in %(month_year)s."),
    _("%(male_name)s died in %(month_year)s at the age of %(age)d years."),
    _("%(male_name)s died in %(month_year)s at the age of %(age)d months."),
    _("%(male_name)s died in %(month_year)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("%(female_name)s died in %(month_year)s."),
    _("%(female_name)s died in %(month_year)s at the age of %(age)d years."),
    _("%(female_name)s died in %(month_year)s at the age of %(age)d months."),
    _("%(female_name)s died in %(month_year)s at the age of %(age)d days."),
    ],
  }
]  

died_no_date_with_place = [
  {
    RelLib.Person.UNKNOWN : [
    _("This person died in %(death_place)s."),
    _("This person died in %(death_place)s at the age of %(age)d years."),
    _("This person died in %(death_place)s at the age of %(age)d months."),
    _("This person died in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("He died in %(death_place)s."),
    _("He died in %(death_place)s at the age of %(age)d years."),
    _("He died in %(death_place)s at the age of %(age)d months."),
    _("He died in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("She died in %(death_place)s."),
    _("She died in %(death_place)s at the age of %(age)d years."),
    _("She died in %(death_place)s at the age of %(age)d months."),
    _("She died in %(death_place)s at the age of %(age)d days."),
    ],
  },
  { RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s died in %(death_place)s."),
    _("%(unknown_gender_name)s died in %(death_place)s at the age of %(age)d years."),
    _("%(unknown_gender_name)s died in %(death_place)s at the age of %(age)d months."),
    _("%(unknown_gender_name)s died in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    _("%(male_name)s died in %(death_place)s."),
    _("%(male_name)s died in %(death_place)s at the age of %(age)d years."),
    _("%(male_name)s died in %(death_place)s at the age of %(age)d months."),
    _("%(male_name)s died in %(death_place)s at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    _("%(female_name)s died in %(death_place)s."),
    _("%(female_name)s died in %(death_place)s at the age of %(age)d years."),
    _("%(female_name)s died in %(death_place)s at the age of %(age)d months."),
    _("%(female_name)s died in %(death_place)s at the age of %(age)d days."),
    ],
  }
]  

died_no_date_no_place = [
  { RelLib.Person.UNKNOWN : [
    "",
    _("This person died at the age of %(age)d years."),
    _("This person died at the age of %(age)d months."),
    _("This person died at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    "",
    _("He died at the age of %(age)d years."),
    _("He died at the age of %(age)d months."),
    _("He died at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    "",
    _("She died at the age of %(age)d years."),
    _("She died at the age of %(age)d months."),
    _("She died at the age of %(age)d days."),
    ],
  },
  { RelLib.Person.UNKNOWN : [
    "",
    _("%(unknown_gender_name)s died at the age of %(age)d years."),
    _("%(unknown_gender_name)s died at the age of %(age)d months."),
    _("%(unknown_gender_name)s died at the age of %(age)d days."),
    ],
    RelLib.Person.MALE : [
    "",
    _("%(male_name)s died at the age of %(age)d years."),
    _("%(male_name)s died at the age of %(age)d months."),
    _("%(male_name)s died at the age of %(age)d days."),
    ],
    RelLib.Person.FEMALE : [
    "",
    _("%(female_name)s died at the age of %(age)d years."),
    _("%(female_name)s died at the age of %(age)d months."),
    _("%(female_name)s died at the age of %(age)d days."),
    ],
  },
]

#------------------------------------------------------------------------
#
# Buried strings
#
#------------------------------------------------------------------------

buried_full_date_place = {
    RelLib.Person.MALE: [
    _("%(male_name)s was buried on %(burial_date)s in %(burial_place)s."),
    _("He was buried on %(burial_date)s in %(burial_place)s."),
    ],
    RelLib.Person.FEMALE: [
    _("%(female_name)s was buried on %(burial_date)s in %(burial_place)s."),
    _("She was buried on %(burial_date)s in %(burial_place)s."),
    ],
    RelLib.Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried on %(burial_date)s in %(burial_place)s."),
    _("This person was buried on %(burial_date)s in %(burial_place)s."),
    ],
    }

buried_full_date_no_place = {
    RelLib.Person.MALE: [
    _("%(male_name)s was buried on %(burial_date)s."),
    _("He was buried on %(burial_date)s."),
    ],
    RelLib.Person.FEMALE: [
    _("%(female_name)s was buried on %(burial_date)s."),
    _("She was buried on %(burial_date)s."),
    ],
    RelLib.Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried on %(burial_date)s."),
    _("This person was buried on %(burial_date)s."),
    ],
    }

buried_partial_date_place = {
    RelLib.Person.MALE: [
    _("%(male_name)s was buried in %(month_year)s in %(burial_place)s."),
    _("He was buried in %(month_year)s in %(burial_place)s."),
    ],
    RelLib.Person.FEMALE: [
    _("%(female_name)s was buried in %(month_year)s in %(burial_place)s."),
    _("She was buried in %(month_year)s in %(burial_place)s."),
    ],
    RelLib.Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried in %(month_year)s in %(burial_place)s."),
    _("This person was buried in %(month_year)s in %(burial_place)s."),
    ],
    }

buried_partial_date_no_place = {
    RelLib.Person.MALE: [
    _("%(male_name)s was buried in %(month_year)s."),
    _("He was buried in %(month_year)s."),
    ],
    RelLib.Person.FEMALE: [
    _("%(female_name)s was buried in %(month_year)s."),
    _("She was buried in %(month_year)s."),
    ],
    RelLib.Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried in %(month_year)s."),
    _("This person was buried in %(month_year)s."),
    ],
    }

buried_modified_date_place = {
    RelLib.Person.MALE: [
    _("%(male_name)s was buried %(modified_date)s in %(burial_place)s."),
    _("He was buried %(modified_date)s in %(burial_place)s."),
    ],
    RelLib.Person.FEMALE: [
    _("%(female_name)s was buried %(modified_date)s in %(burial_place)s."),
    _("She was buried %(modified_date)s in %(burial_place)s."),
    ],
    RelLib.Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried %(modified_date)s in %(burial_place)s."),
    _("This person was buried %(modified_date)s in %(burial_place)s."),
    ],
    }

buried_modified_date_no_place = {
    RelLib.Person.MALE: [
    _("%(male_name)s was buried %(modified_date)s."),
    _("He was buried %(modified_date)s."),
    ],
    RelLib.Person.FEMALE: [
    _("%(female_name)s was buried %(modified_date)s."),
    _("She was buried %(modified_date)s."),
    ],
    RelLib.Person.UNKNOWN: [
    _("%(unknown_gender_name)s was buried %(modified_date)s."),
    _("This person was buried %(modified_date)s."),
    ],
    }

buried_no_date_place = {
    RelLib.Person.MALE    : [
    _("%(male_name)s was buried in %(burial_place)s."),
    _("He was buried in %(burial_place)s."),
    ],
    RelLib.Person.FEMALE  : [
    _("%(female_name)s was buried in %(burial_place)s."),
    _("She was buried in %(burial_place)s."),
    ],
    RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s was buried in %(burial_place)s."),
    _("This person was buried in %(burial_place)s."),
    ],
    }

buried_no_date_no_place = {
    RelLib.Person.MALE    : [
    _("%(male_name)s was buried."),
    _("He was buried."),
    ],
    RelLib.Person.FEMALE  : [
    _("%(female_name)s was buried."),
    _("She was buried."),
    ],
    RelLib.Person.UNKNOWN : [
    _("%(unknown_gender_name)s was buried."),
    _("This person was buried."),
    ]
    }

#------------------------------------------------------------------------
#
# Marriage strings
#
#------------------------------------------------------------------------

marriage_first_date_place = {
    RelLib.Person.UNKNOWN : [
        _('This person married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'),
        _('This person married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'),
        _('This person married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],
    RelLib.Person.MALE : [
        _('He married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'),
        _('He married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'),
        _('He married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],
    RelLib.Person.FEMALE : [
        _('She married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'),
        _('She married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'),
        _('She married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],
    }

marriage_also_date_place = {
    RelLib.Person.UNKNOWN : [
        _('This person also married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'),
        _('This person also married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'),
        _('This person also married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],
    RelLib.Person.MALE : [
        _('He also married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'),
        _('He also married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'),
        _('He also married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],
    RelLib.Person.FEMALE : [
        _('She also married %(spouse)s in %(partial_date)s in %(place)s%(endnotes)s.'),
        _('She also married %(spouse)s on %(full_date)s in %(place)s%(endnotes)s.'),
        _('She also married %(spouse)s %(modified_date)s in %(place)s%(endnotes)s.'),
      ],
    }

marriage_first_date = {
    RelLib.Person.UNKNOWN : [
        _('This person married %(spouse)s in %(partial_date)s%(endnotes)s.'),
        _('This person married %(spouse)s on %(full_date)s%(endnotes)s.'),
        _('This person married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],
    RelLib.Person.MALE : [
        _('He married %(spouse)s in %(partial_date)s%(endnotes)s.'),
        _('He married %(spouse)s on %(full_date)s%(endnotes)s.'),
        _('He married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],
    RelLib.Person.FEMALE : [
        _('She married %(spouse)s in %(partial_date)s%(endnotes)s.'),
        _('She married %(spouse)s on %(full_date)s%(endnotes)s.'),
        _('She married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],
    }

marriage_also_date = {
    RelLib.Person.UNKNOWN : [
        _('This person also married %(spouse)s in %(partial_date)s%(endnotes)s.'),
        _('This person also married %(spouse)s on %(full_date)s%(endnotes)s.'),
        _('This person also married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],
    RelLib.Person.MALE : [
        _('He also married %(spouse)s in %(partial_date)s%(endnotes)s.'),
        _('He also married %(spouse)s on %(full_date)s%(endnotes)s.'),
        _('He also married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],
    RelLib.Person.FEMALE : [
        _('She also married %(spouse)s in %(partial_date)s%(endnotes)s.'),
        _('She also married %(spouse)s on %(full_date)s%(endnotes)s.'),
        _('She also married %(spouse)s %(modified_date)s%(endnotes)s.'),
      ],
    }

marriage_first_place = {
    RelLib.Person.UNKNOWN : _('This person married %(spouse)s in %(place)s%(endnotes)s.'),
    RelLib.Person.MALE : _('He married %(spouse)s in %(place)s%(endnotes)s.'),
    RelLib.Person.FEMALE : _('She married %(spouse)s in %(place)s%(endnotes)s.'),
    }

marriage_also_place = {
    RelLib.Person.UNKNOWN : _('This person also married %(spouse)s in %(place)s%(endnotes)s.'),
    RelLib.Person.MALE : _('He also married %(spouse)s in %(place)s%(endnotes)s.'),
    RelLib.Person.FEMALE : _('She also married %(spouse)s in %(place)s%(endnotes)s.'),
    }

marriage_first_only = {
    RelLib.Person.UNKNOWN : _('This person married %(spouse)s%(endnotes)s.'),
    RelLib.Person.MALE : _('He married %(spouse)s%(endnotes)s.'),
    RelLib.Person.FEMALE : _('She married %(spouse)s%(endnotes)s.'),
    }

marriage_also_only = {
    RelLib.Person.UNKNOWN : _('This person also married %(spouse)s%(endnotes)s.'),
    RelLib.Person.MALE : _('He also married %(spouse)s%(endnotes)s.'),
    RelLib.Person.FEMALE : _('She also married %(spouse)s%(endnotes)s.'),
    }

#-------------------------------------------------------------------------
#
#  child to parent relationships
#
#-------------------------------------------------------------------------

child_father_mother = {
    RelLib.Person.UNKNOWN: [
      [
        _("This person is the child of %(father)s and %(mother)s."),
        _("This person was the child of %(father)s and %(mother)s."),
      ],
      [
        _("%(male_name)s is the child of %(father)s and %(mother)s."),
        _("%(male_name)s was the child of %(father)s and %(mother)s."),
      ],
    ],
    RelLib.Person.MALE : [
      [
        _("He is the son of %(father)s and %(mother)s."),
        _("He was the son of %(father)s and %(mother)s."),
      ],
      [
        _("%(male_name)s is the son of %(father)s and %(mother)s."),
        _("%(male_name)s was the son of %(father)s and %(mother)s."),
      ]
    ],
    RelLib.Person.FEMALE : [
     [
        _("She is the daughter of %(father)s and %(mother)s."),
        _("She was the daughter of %(father)s and %(mother)s."),
     ],
     [
        _("%(female_name)s is the daughter of %(father)s and %(mother)s."),
        _("%(female_name)s was the daughter of %(father)s and %(mother)s."),
     ],
    ]
}

child_father = {
    RelLib.Person.UNKNOWN : [
      [
        _("This person is the child of %(father)s."),
        _("This person was the child of %(father)s."),
      ],
      [
        _("%(male_name)s is the child of %(father)s."),
        _("%(male_name)s was the child of %(father)s."),
      ],
    ],
    RelLib.Person.MALE : [
      [
        _("He is the son of %(father)s."),
        _("He was the son of %(father)s."),
      ],
      [
        _("%(male_name)s is the son of %(father)s."),
        _("%(male_name)s was the son of %(father)s."),
      ],
    ],
    RelLib.Person.FEMALE : [
      [
        _("She is the daughter of %(father)s."),
        _("She was the daughter of %(father)s."),
      ],  
      [
        _("%(female_name)s is the daughter of %(father)s."),
        _("%(female_name)s was the daughter of %(father)s."),
      ],
    ],
}

child_mother = {
    RelLib.Person.UNKNOWN : [
      [
        _("This person is the child of %(mother)s."),
        _("This person was the child of %(mother)s."),
      ],
      [
        _("%(male_name)s is the child of %(mother)s."),
        _("%(male_name)s was the child of %(mother)s."),
      ],
    ],
    RelLib.Person.MALE : [
      [
        _("He is the son of %(mother)s."),
        _("He was the son of %(mother)s."),
      ],
      [
        _("%(male_name)s is the son of %(mother)s."),
        _("%(male_name)s was the son of %(mother)s."),
      ],
    ],
    RelLib.Person.FEMALE : [
      [
        _("She is the daughter of %(mother)s."),
        _("She was the daughter of %(mother)s."),
      ],
      [
        _("%(female_name)s is the daughter of %(mother)s."),
        _("%(female_name)s was the daughter of %(mother)s."),
      ],
   ],
}

#-------------------------------------------------------------------------
#
# relationship types
#
#-------------------------------------------------------------------------
_rtype = {
    RelLib.FamilyRelType.UNMARRIED     : _("unmarried"),
    RelLib.FamilyRelType.CIVIL_UNION   : _("civil union"),
    RelLib.FamilyRelType.UNKNOWN       : _("Unknown"),
    RelLib.FamilyRelType.CUSTOM        : _("Other"),
    }
   
#-------------------------------------------------------------------------
#
#  Convert points to cm and back
#
#-------------------------------------------------------------------------
def pt2cm(pt):
    """
    Converts points to centimeters. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param pt: points
    @type pt: float or int
    @returns: equivalent units in centimeters
    @rtype: float
    """
    return pt/28.3465

def cm2pt(cm):
    """
    Converts centimeters to points. Fonts are typically specified in points,
    but the BaseDoc classes use centimeters.

    @param cm: centimeters
    @type cm: float or int
    @returns: equivalent units in points
    @rtype: float
    """
    return cm*28.3465

def rgb_color(color):
    """
    Converts color value from 0-255 integer range into 0-1 float range.

    @param color: list or tuple of integer values for red, green, and blue
    @type color: int
    @returns: (r,g,b) tuple of floating point color values
    @rtype: 3-tuple
    """
    r = float(color[0])/255.0
    g = float(color[1])/255.0
    b = float(color[2])/255.0
    return (r,g,b)

def draw_wedge(doc,  style,  centerx,  centery,  radius,  start_angle, 
               end_angle,  short_radius=0):
    from math import pi, cos, sin
    
    while end_angle < start_angle:
        end_angle += 360

    p = []
    
    degreestoradians = pi / 180.0
    radiansdelta = degreestoradians / 2
    sangle = start_angle * degreestoradians
    eangle = end_angle * degreestoradians
    while eangle < sangle:
        eangle = eangle + 2 * pi
    angle = sangle

    if short_radius == 0:
        if (end_angle - start_angle) != 360:
            p.append((centerx, centery))
    else:
        origx = (centerx + cos(angle) * short_radius)
        origy = (centery + sin(angle) * short_radius)
        p.append((origx, origy))
        
    while angle < eangle:
        x = centerx + cos(angle) * radius
        y = centery + sin(angle) * radius
        p.append((x, y))
        angle = angle + radiansdelta
    x = centerx + cos(eangle) * radius
    y = centery + sin(eangle) * radius
    p.append((x, y))

    if short_radius:
        x = centerx + cos(eangle) * short_radius
        y = centery + sin(eangle) * short_radius
        p.append((x, y))

        angle = eangle
        while angle >= sangle:
            x = centerx + cos(angle) * short_radius
            y = centery + sin(angle) * short_radius
            p.append((x, y))
            angle = angle - radiansdelta
    doc.draw_path(style, p)

    delta = (eangle - sangle) / 2.0
    rad = short_radius + (radius - short_radius) / 2.0

    return ( (centerx + cos(sangle + delta) * rad),
             (centery + sin(sangle + delta) * rad))


def draw_pie_chart(doc, center_x, center_y, radius, data, start=0):
    """
    Draws a pie chart in the specified document. The data passed is plotted as
    a pie chart. The data should consist of the actual data. Percentages of
    each slice are determined by the routine.

    @param doc: Document to which the pie chart should be added
    @type doc: BaseDoc derived class
    @param center_x: x coordinate in centimeters where the center of the pie
       chart should be. 0 is the left hand edge of the document.
    @type center_x: float
    @param center_y: y coordinate in centimeters where the center of the pie
       chart should be. 0 is the top edge of the document
    @type center_y: float
    @param radius: radius of the pie chart. The pie charts width and height
       will be twice this value.
    @type radius: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    @param start: starting point in degrees, where the default of 0 indicates
       a start point extending from the center to right in a horizontal line.
    @type start: float
    """

    total = 0.0
    for item in data:
        total += item[1]

    for item in data:
        incr = 360.0*(item[1]/total)
        draw_wedge(doc,item[0], center_x, center_y, radius, start, start + incr)
        start += incr

def draw_legend(doc, start_x, start_y, data, title, label_style):
    """
    Draws a legend for a graph in the specified document. The data passed is
    used to define the legend.  First item style is used for the optional
    Legend title.

    @param doc: Document to which the legend chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand corner
        of the legend is placed. 0 is the left hand edge of the document.
    @type start_x: float
    @param start_y: y coordinate in centimeters where the top of the legend
        should be. 0 is the top edge of the document
    @type start_y: float
    @param data: List of tuples containing the data to be used to create the
       legend. In order to be compatible with the graph plots, the first and
       third values of the tuple used. The format is (graphics_format, value,
       legend_description).
    @type data: list
    """
    if title:
        gstyle = doc.get_draw_style(label_style)
        pstyle = gstyle.get_paragraph_style()
        size = pt2cm(doc.get_style(pstyle).get_font().get_size())
        doc.draw_text(label_style, title, start_x + (3*size), start_y - (size*0.25))
        start_y += size * 1.3
    
    for (format, size, legend) in data:
        gstyle = doc.get_draw_style(format)
        pstyle = gstyle.get_paragraph_style()
        size = pt2cm(doc.get_style(pstyle).get_font().get_size())
        doc.draw_box(format, "", start_x, start_y, (2*size), size)
        doc.draw_text(label_style, legend, start_x + (3*size), start_y - (size*0.25))
        start_y += size * 1.3
        
def draw_vertical_bar_graph(doc, format, start_x, start_y, height, width, data):
    """
    Draws a vertical bar chart in the specified document. The data passed 
    should consist of the actual data. The bars are scaled appropriately by
    the routine.

    @param doc: Document to which the bar chart should be added
    @type doc: BaseDoc derived class
    @param start_x: x coordinate in centimeters where the left hand side of the
       chart should be. 0 is the left hand edge of the document.
    @type start_x: float
    @param start_y: y coordinate in centimeters where the top of the chart
    should be. 0 is the top edge of the document
    @type start_y: float
    @param height: height of the graph in centimeters
    @type height: float
    @param width: width of the graph in centimeters
    @type width: float
    @param data: List of tuples containing the data to be plotted. The values
       are (graphics_format, value), where graphics_format is a BaseDoc
       GraphicsStyle, and value is a floating point number. Any other items in
       the tuple are ignored. This allows you to share the same data list with
       the L{draw_legend} function.
    @type data: list
    """
    doc.draw_line(format,start_x,start_y+height,start_x,start_y)
    doc.draw_line(format,start_x,start_y+height,start_x+width,start_y+height)

    largest = 0.0
    for item in data:
        largest = max(item[1],largest)

    scale = float(height)/float(largest)
    units = len(data)
    box_width = (float(width) / (units*3.0+1.0))*2
    box_height = float(height)
    bottom = float(start_y)+float(height)

    start = 0.5*box_width + start_x
    for index in range(units):
        size = float(data[index][1]) * scale
        doc.draw_box(data[index][0],"",start,bottom-size,box_width,box_height)
        start += box_width * 1.5


_t = time.localtime(time.time())
_TODAY = DateHandler.parser.parse("%04d-%02d-%02d" % (_t[0],_t[1],_t[2]))

def estimate_age(db, person, end_handle=None, start_handle=None, today=_TODAY):
    """
    Estimates the age of a person based off the birth and death
    dates of the person. A tuple containing the estimated upper
    and lower bounds of the person's age is returned. If either
    the birth or death date is missing, a (-1,-1) is returned.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: Person object to calculate the age of
    @type person: Person
    @param end_handle: Determines the event handle that determines
       the upper limit of the age. If None, the death event is used
    @type end_handle: str
    @param start_handle: Determines the event handle that determines
       the lower limit of the event. If None, the birth event is
       used
    @type start_handle: str
    @returns: tuple containing the lower and upper bounds of the
       person's age, or (-1,-1) if it could not be determined.
    @rtype: tuple
    """

    bhandle = None
    if start_handle:
        bhandle = start_handle
    else:
        bref = person.get_birth_ref()
        if bref:
            bhandle = bref.get_reference_handle()

    dhandle = None
    if end_handle:
        dhandle = end_handle
    else:
        dref = person.get_death_ref()
        if dref:
            dhandle = dref.get_reference_handle()

    # if either of the events is not defined, return an error message
    if not bhandle:
        return (-1,-1)

    bdata = db.get_event_from_handle(bhandle).get_date_object()
    if dhandle:
        ddata = db.get_event_from_handle(dhandle).get_date_object()
    else:
        if today != None:
            ddata = today
        else:
            return (-1,-1)

    # if the date is not valid, return an error message
    if not bdata.get_valid() or not ddata.get_valid():
        return (-1,-1)

    # if a year is not valid, return an error message
    if not bdata.get_year_valid() or not ddata.get_year_valid():
        return (-1,-1)

    bstart = bdata.get_start_date()
    bstop  = bdata.get_stop_date()

    dstart = ddata.get_start_date()
    dstop  = ddata.get_stop_date()

    def _calc_diff(low,high):
        if (low[1],low[0]) > (high[1],high[0]):
            return high[2] - low[2] - 1
        else:
            return high[2] - low[2]

    if bstop == RelLib.Date.EMPTY and dstop == RelLib.Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        age = (lower, lower)
    elif bstop == RelLib.Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        upper = _calc_diff(bstart,dstop)
        age = (lower,upper)
    elif dstop == RelLib.Date.EMPTY:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstart)
        age = (lower,upper)
    else:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstop)
        age = (lower,upper)
    return age

def estimate_age_on_date(db, person, ddata=_TODAY):
    """
    This will be replaced with something similar to probably_alive
    """
    bhandle = None
    bref = person.get_birth_ref()
    if bref:
        bhandle = bref.get_reference_handle()
    if not bhandle:
        return (-1,-1)
    bdata = db.get_event_from_handle(bhandle).get_date_object()
    # if the date is not valid, return an error message
    if not bdata.get_valid() or not ddata.get_valid():
        return (-1,-1)
    # if a year is not valid, return an error message
    if not bdata.get_year_valid() or not ddata.get_year_valid():
        return (-1,-1)
    bstart = bdata.get_start_date()
    bstop  = bdata.get_stop_date()
    dstart = ddata.get_start_date()
    dstop  = ddata.get_stop_date()
    def _calc_diff(low,high):
        if (low[1],low[0]) > (high[1],high[0]):
            return high[2] - low[2] - 1
        else:
            return high[2] - low[2]
    if bstop == RelLib.Date.EMPTY and dstop == RelLib.Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        age = [lower, lower]
    elif bstop == RelLib.Date.EMPTY:
        lower = _calc_diff(bstart,dstart)
        upper = _calc_diff(bstart,dstop)
        age = [lower,upper]
    elif dstop == RelLib.Date.EMPTY:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstart)
        age = [lower,upper]
    else:
        lower = _calc_diff(bstop,dstart)
        upper = _calc_diff(bstart,dstop)
        age = [lower,upper]
    if age[0] < 0 and age[1] < 0:
        age = (-1, -1)
    elif age[0] > 120 and age[1] > 120:
        age = (-1, -1)
    return age

def sanitize_list(obj_list,exclude_private):
    """
    Removes private objects from the list.

    @param obj_list: objects that have a privacy flag
    @type obj_list: list
    @param exclude_private: indicates if objects marked private
    are eliminated from the list
    @type exclude_private: bool
    @returns: objects that match the privacy request
    @rtype: list
    """
    if exclude_private:
        return [obj for obj in obj_list if not obj.private]
    else:
        return obj_list

def sanitize_media_ref_list(db, media_ref_list, exclude_private):
    """
    Removes private references and references to private objects
    from the list.

    @param db: GRAMPS database to which the references belongs
    @type db: GrampsDbBase
    @param ref_list: references to objects that have a privacy flag
    @type ref_list: list
    @param exclude_private: indicates if objects marked private
    are eliminated from the list
    @type exclude_private: bool
    @returns: references to objects that match the privacy request
    @rtype: list
    """
    if exclude_private == True:
        new_list = []
        for media_ref in media_ref_list:
            if media_ref.get_privacy() == False:
                handle = media_ref.get_reference_handle()
                media_object = db.get_object_from_handle(handle)
                if media_object.get_privacy() == False:
                    new_list.append(media_ref)
        return new_list
    else:
        return media_ref_list

def sanitize_person(db,person):
    """
    Creates a new Person instance based off the passed Person
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: source Person object that will be copied with
    privacy records removed
    @type person: Person
    @returns: 'cleansed' Person object
    @rtype: Person
    """
    new_person = RelLib.Person()

    # copy gender
    new_person.set_gender(person.get_gender())
    new_person.set_gramps_id(person.get_gramps_id())
    new_person.set_handle(person.get_handle())
    
    # copy names if not private
    name = person.get_primary_name()
    if name.get_privacy() or person.get_privacy():
        name = RelLib.Name()
        name.set_surname(_('Private'))

    new_person.set_primary_name(name)
    # copy Family reference list
    for handle in person.get_family_handle_list():
        new_person.add_family_handle(handle)

    # copy Family reference list
    for item in person.get_parent_family_handle_list():
        new_person.add_parent_family_handle(item)

    if person.get_privacy():
        return new_person

    for name in person.get_alternate_names():
        if not name.get_privacy():
            new_person.add_alternate_name(name)

    # set complete flag
    new_person.set_marker(person.get_marker())

    # copy event list
    for event_ref in person.get_event_ref_list():
        if event_ref and event_ref.get_privacy() == False:
            event = db.get_event_from_handle(event_ref.ref)
            if not event.get_privacy():
                new_person.add_event_ref(event_ref)

    # Copy birth and death after event list to maintain the order.
    # copy birth event
    event_ref = person.get_birth_ref()
    if event_ref and event_ref.get_privacy() == False:
        event = db.get_event_from_handle(event_ref.ref)
        if not event.get_privacy():
            new_person.set_birth_ref(event_ref)

    # copy death event
    event_ref = person.get_death_ref()
    if event_ref and event_ref.get_privacy() == False:
        event = db.get_event_from_handle(event_ref.ref)
        if not event.get_privacy():
            new_person.set_death_ref(event_ref)

    # copy address list
    for address in person.get_address_list():
        if not address.get_privacy():
            new_person.add_address(RelLib.Address(address))

    # copy attribute list
    for attribute in person.get_attribute_list():
        if not attribute.get_privacy():
            new_person.add_attribute(RelLib.Attribute(attribute))

    # copy source references
    for ref in person.get_source_references():
        if not ref.get_privacy():
            handle = ref.get_reference_handle()
            source = db.get_source_from_handle(handle)
            if source.get_privacy() == False:
                new_person.add_source_reference(RelLib.SourceRef(ref))

    # copy URL list
    for url in person.get_url_list():
        if not url.get_privacy():
            new_person.add_url(url)

    # copy Media reference list
    clean_list = sanitize_media_ref_list(db,person.get_media_list(),True)
    for ref in clean_list:
        new_person.add_media_reference(RelLib.MediaRef(ref))

    # LDS ordinances
    for lds_ord in person.get_lds_ord_list():
        lds_type = lds_ord.get_type()
        if lds_type == RelLib.LdsOrd.BAPTISM           or       \
           lds_type == RelLib.LdsOrd.ENDOWMENT         or       \
           lds_type == RelLib.LdsOrd.SEAL_TO_PARENTS   or       \
           lds_type == RelLib.LdsOrd.SEAL_TO_SPOUSE             :
               new_person.add_lds_ord( lds_ord )

    new_person.set_note_list(person.get_note_list())
    
    return new_person

def dont_restrict(db,person):
    return person

def restrict_with_names(db,person):
    return restrict_person(db,person,False)

def restrict_no_names(db,person):
    return restrict_person(db,person,True)

def restrict_person(db,person,no_names=False):
    """
    Creates a new Person instance based off the passed Person
    instance. The returned instance has all private records
    removed from it.
    
    @param db: GRAMPS database to which the Person object belongs
    @type db: GrampsDbBase
    @param person: source Person object that will be copied with
    privacy records removed
    @type person: Person
    @returns: 'cleansed' Person object
    @rtype: Person
    """
    new_person = RelLib.Person()

    # copy gender
    new_person.set_gender(person.get_gender())
    new_person.set_gramps_id(person.get_gramps_id())
    new_person.set_handle(person.get_handle())
    
    # copy names if not private
    if no_names:
        name = RelLib.Name()
        name.set_surname(_('Private'))
    else:
        name = person.get_primary_name()
        name.set_source_reference_list([])

    new_person.set_primary_name(name)

    # copy Family reference list
    for handle in person.get_family_handle_list():
        new_person.add_family_handle(handle)

    # copy Family reference list
    for item in person.get_parent_family_handle_list():
        new_person.add_parent_family_handle(item[0],item[1],item[2])

    return new_person

#-------------------------------------------------------------------------
#
#  Roman numbers
#
#-------------------------------------------------------------------------
def roman(num):
    """ Integer to Roman numeral converter for 0 < num < 4000 """
    if type(num) != int:
        return "?"
    if not 0 < num < 4000:
        return "?"
    vals = (1000, 900, 500, 400, 100,  90,  50,  40,  10,   9,   5,   4,   1)
    nums = ( 'M','CM', 'D','CD', 'C','XC', 'L','XL', 'X','IX', 'V','IV', 'I')
    retval = ""
    for i in range(len(vals)):
        amount  = int(num / vals[i])
        retval += nums[i] * amount
        num    -= vals[i] * amount
    return retval

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
def place_name(db,place_handle):
    if place_handle:
        place = db.get_place_from_handle(place_handle).get_title()
    else:
        place = ""
    return place
    
#-------------------------------------------------------------------------
#
# Functions commonly used in reports
#
#-------------------------------------------------------------------------
def insert_image(database, doc, photo, w_cm=4.0, h_cm=4.0):
    """
    Insert pictures of a person into the document.
    """

    object_handle = photo.get_reference_handle()
    media_object = database.get_object_from_handle(object_handle)
    mime_type = media_object.get_mime_type()
    if mime_type and mime_type.startswith("image"):
        filename = media_object.get_path()
        if os.path.exists(filename):
            doc.add_media_object(filename,"right",w_cm,h_cm)
        else:
            WarningDialog(_("Could not add photo to page"),
                          "%s: %s" % (filename, _('File does not exist')))

#-------------------------------------------------------------------------
#
# Strings commonly used in reports
#
#-------------------------------------------------------------------------
def empty_notes(whatever):
    # Empty stab function for when endnotes are not needed
    return ""

def get_birth_death_strings(database,person,empty_date="",empty_place=""):
    """
    Returns strings for dates and places of birth and death.
    """

    bplace = dplace = empty_place
    bdate = ddate = empty_date
    bdate_full = ddate_full = False
    bdate_mod = False
    ddate_mod = False

    birth_ref = person.get_birth_ref()
    if birth_ref and birth_ref.ref:
        birth = database.get_event_from_handle(birth_ref.ref)
        if birth:
            bdate = DateHandler.get_date(birth)
            bplace_handle = birth.get_place_handle()
            if bplace_handle:
                bplace = database.get_place_from_handle(bplace_handle).get_title()
            bdate_obj = birth.get_date_object()
            bdate_full = bdate_obj and bdate_obj.get_day_valid()
            bdate_mod = bdate_obj and bdate_obj.get_modifier() != RelLib.Date.MOD_NONE

    death_ref = person.get_death_ref()
    if death_ref and death_ref.ref:
        death = database.get_event_from_handle(death_ref.ref)
        if death:
            ddate = DateHandler.get_date(death)
            dplace_handle = death.get_place_handle()
            if dplace_handle:
                dplace = database.get_place_from_handle(dplace_handle).get_title()
            ddate_obj = death.get_date_object()
            ddate_full = ddate_obj and ddate_obj.get_day_valid()
            ddate_mod = ddate_obj and ddate_obj.get_modifier() != RelLib.Date.MOD_NONE

    return (bdate,bplace,bdate_full,bdate_mod,ddate,dplace,ddate_full,ddate_mod)

def born_died_str(database,person,endnotes=None,name_object=None,person_name=None):
    """
    Composes a string describing birth and death of a person.
    Missing information will be omitted without loss of readability.
    Optional references may be added to birth and death events.
    Optional Name object may be used to override a person's Name instance.
    Optional string may be used to override the string representation of a name.
    
    @param database: GRAMPS database to which the Person object belongs
    @type database: GrampsDbBase
    @param person: Person instance for which the string has to be composed
    @type person: Person
    @param endnotes: Function to use for reference composition. If None
    then references will not be added
    @type endnotes: function
    @param name_object: Name instance for which the phrase is composed. If None
    then the regular primary name of the person will be used
    @type name_object: Name
    @param person_name: String to override the person's name. If None then the
    regular primary name string will be used
    @type person_name: unicode
    @returns: A composed string
    @rtype: unicode
    """

    if not endnotes:
        endnotes = empty_notes

    if not name_object:
        name_object = person.get_primary_name()

    if person_name == None:
        person_name = _nd.display_name(name_object)
    elif person_name == 0:
        if person.get_gender() == RelLib.Person.MALE:
            person_name = _('He')
        else:
            person_name = _('She')

    bdate,bplace,bdate_full,bdate_mod,ddate,dplace,ddate_full,ddate_mod = \
                            get_birth_death_strings(database,person)

    birth = None
    birth_ref = person.get_birth_ref()
    if birth_ref:
        birth = database.get_event_from_handle(birth_ref.ref)

    death = None
    death_ref = person.get_death_ref()
    if death_ref:
        death = database.get_event_from_handle(death_ref.ref)

    values = {
        'unknown_gender_name' : person_name,
        'name'                : person_name,
        'male_name'           : person_name,
        'female_name'         : person_name,
        'endnotes'            : endnotes(name_object),
        'birth_date'          : bdate,
        'birth_place'         : bplace,
        'birth_endnotes'      : endnotes(birth),
        'death_date'          : ddate,
        'death_place'         : dplace,
        'death_endnotes'      : endnotes(death),
        }

    if person.get_gender() == RelLib.Person.MALE:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % values
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s.") % values
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s.") % values
            else:
                if ddate:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s "
                            "died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(male_name)s%(endnotes)s "
                            "died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(male_name)s%(endnotes)s.") % values
    else:
        if bdate:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % values
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born %(birth_date)s%(birth_endnotes)s.") % values
        else:
            if bplace:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s, "
                            "and died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "was born in %(birth_place)s%(birth_endnotes)s.") % values
            else:
                if ddate:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s "
                            "died %(death_date)s%(death_endnotes)s.") % values
                else:
                    if dplace:
                        text = _("%(female_name)s%(endnotes)s "
                            "died in %(death_place)s%(death_endnotes)s.") % values
                    else:
                        text = _("%(female_name)s%(endnotes)s.") % values
    if text:
        text = text + " "
    return text

#-------------------------------------------------------------------------
#
# married_str
#
#-------------------------------------------------------------------------
def married_str(database,person,spouse,event,endnotes=None,
                empty_date="",empty_place="",is_first=True):
    """
    Composes a string describing marriage of a person. Missing information will
    be omitted without loss of readability. Optional references may be added to
    birth and death events.
    
    @param database: GRAMPS database to which the Person object belongs
    @type database: GrampsDbBase
    @param person: Person instance whose marriage is discussed
    @type person: Person
    @param spouse: Person instance to use as a spouse
    @type spouse: Person
    @param event: Event instance of marriage 
    @type event: Event
    @param endnotes: Function to use for reference composition. If None
    then references will not be added
    @type endnotes: function
    @returns: A composed string
    @rtype: unicode
    """

    # not all families have a spouse.
    if not spouse:
        return u""

    if not endnotes:
        endnotes = empty_notes

    date = empty_date
    place = empty_place
    spouse_name = _nd.display(spouse)

    mdate = DateHandler.get_date(event)
    if mdate:
        date = mdate
    place_handle = event.get_place_handle()
    if place_handle:
        place = database.get_place_from_handle(place_handle).get_title()

    values = {
        'spouse'        : spouse_name,
        'endnotes'      : endnotes(event),
        'full_date'     : date,
        'modified_date' : date,
        'partial_date'  : date,
        'place'         : place,
        }

    dobj = event.get_date_object()
    
    if dobj.get_modifier() != RelLib.Date.MOD_NONE:
        date_full = 2
    elif dobj and dobj.get_day_valid():
        date_full = 1
    else:
        date_full = 0
        
    gender = person.get_gender()

    if is_first:
        if date and place:
            text = marriage_first_date_place[gender][date_full] % values
        elif date:
            text = marriage_first_date[gender][date_full] % values
        elif place:
            text = marriage_first_place[gender] % values
        else:
            text = marriage_first_only[gender] % values
    else:
        if date and place:
            text = marriage_also_date_place[gender][date_full] % values
        elif date:
            text = marriage_also_date[gender][date_full] % values
        elif place:
            text = marriage_also_place[gender] % values
        else:
            text = marriage_also_only[gender] % values

    if text:
        text = text + " "
    return text

#-------------------------------------------------------------------------
#
# relationship types
#
#-------------------------------------------------------------------------
def married_rel_str(database,person,family,is_first=True):
    """
    Composes a string describing marriage of a person. Missing information will
    be omitted without loss of readability. Optional references may be added to
    birth and death events.
    
    @param database: GRAMPS database to which the Person object belongs
    @type database: GrampsDbBase
    @param person: Person instance whose marriage is discussed
    @type person: Person
    @param family: Family instance whose marriage is discussed
    @type family: Family
    @param is_first: Indicates if this is a first marriage
    @type is_first: bool
    @returns: A composed string
    @rtype: unicode
    """
    spouse_handle = find_spouse(person,family)
    spouse = database.get_person_from_handle(spouse_handle)

    # not all families have a spouse.
    if not spouse_handle or not spouse:
        return u""

    values = {
        'spouse' :_nd.display(spouse)
        }
    
    relationship = family.get_relationship()
    
    if is_first:
        if relationship == RelLib.FamilyRelType.MARRIED:
            if person.get_gender() == RelLib.Person.MALE:
                text = _('He married %(spouse)s.') % values
            elif person.get_gender() == RelLib.Person.FEMALE:
                text = _('She married %(spouse)s.') % values
            else:
                text = _('This person married %(spouse)s.') % values
        elif relationship == RelLib.FamilyRelType.UNMARRIED:
            if person.get_gender() == RelLib.Person.MALE:
                text = _('He had an unmarried relationship with %(spouse)s.') % values
            elif person.get_gender() == RelLib.Person.FEMALE:
                text = _('This person had an unmarried relationship with %(spouse)s.') % values
            else:
                text = _('She had an unmarried relationship with %(spouse)s.') % values
        else:
            if person.get_gender() == RelLib.Person.MALE:
                text = _('He had relationship with %(spouse)s.') % values
            elif person.get_gender() == RelLib.Person.FEMALE:
                text = _('She had relationship with %(spouse)s.') % values
            else:
                text = _('This person had relationship with %(spouse)s.') % values
    else:
        if relationship == RelLib.FamilyRelType.MARRIED:
            if person.get_gender() == RelLib.Person.MALE:
                text = _('He also married %(spouse)s.') % values
            elif person.get_gender() == RelLib.Person.FEMALE:
                text = _('She also married %(spouse)s.') % values
            else:
                text = _('This person also married %(spouse)s.') % values
        elif relationship == RelLib.FamilyRelType.UNMARRIED:
            if person.get_gender() == RelLib.Person.MALE:
                text = _('He had an unmarried relationship with %(spouse)s.') % values
            elif person.get_gender() == RelLib.Person.FEMALE:
                text = _('She had an unmarried relationship with %(spouse)s.') % values
            else:
                text = _('This person had an unmarried relationship with %(spouse)s.') % values
        else:
            if person.get_gender() == RelLib.Person.MALE:
                text = _('He also had relationship with %(spouse)s.') % values
            elif person.get_gender() == RelLib.Person.FEMALE:
                text = _('She also had relationship with %(spouse)s.') % values
            else:
                text = _('This person also had relationship with %(spouse)s.') % values
    if text:
        text = text + " "
    return text

#-------------------------------------------------------------------------
#
# child_str
#
#-------------------------------------------------------------------------
def child_str(person, father_name="", mother_name="", dead=0, person_name=0):
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

    if person_name == 0:
        index = 0
    else:
        index = 1

    gender = person.get_gender()

    text = ""
    if mother_name and father_name:
        text = child_father_mother[gender][index][dead] % values
    elif mother_name:
        text = child_mother[gender][index][dead] % values
    elif father_name:
        text = child_father[gender][index][dead] % values
    if text:
        text = text + " "
    return text

#-------------------------------------------------------------------------
#
# find_spouse
#
#-------------------------------------------------------------------------
def find_spouse(person,family):
    if person.get_handle() == family.get_father_handle():
        spouse_handle = family.get_mother_handle()
    else:
        spouse_handle = family.get_father_handle()
    return spouse_handle

#-------------------------------------------------------------------------
#
# find_marriage
#
#-------------------------------------------------------------------------
def find_marriage(database,family):    
    for event_ref in family.get_event_ref_list():
        event = database.get_event_from_handle(event_ref.ref)
        if event and int(event.get_type()) == RelLib.EventType.MARRIAGE:
            return event
    return None

#-------------------------------------------------------------------------
#
# born_str
#
#-------------------------------------------------------------------------
def born_str(database,person,person_name=None,empty_date="",empty_place=""):
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
    if person_name == None:
        person_name = _nd.display(person)
    elif person_name == 0:
        name_index = 0

    text = ""
    
    bdate,bplace,bdate_full,bdate_mod,ddate,dplace,ddate_full,ddate_mod = \
                get_birth_death_strings(database,person,empty_date,empty_place)

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
            if bplace:
                text = born_modified_date_with_place[name_index][gender] % value_map
            else:
                text = born_modified_date_no_place[name_index][gender] % value_map
        elif bdate_full:
            if bplace:
                text = born_full_date_with_place[name_index][gender] % value_map
            else:
                text = born_full_date_no_place[name_index][gender] % value_map
        else:
            if bplace:
                text = born_partial_date_with_place[name_index][gender] % value_map
            else:
                text = born_partial_date_no_place[name_index][gender] % value_map
    else:
        if bplace:
            text = born_no_date_with_place[name_index][gender] % value_map
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
def died_str(database,person,person_name=None,empty_date="",empty_place="",
             age=None,age_units=0):
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
    if person_name == None:
        person_name = _nd.display(person)
    elif person_name == 0:
        name_index = 0

    text = ""

    bdate,bplace,bdate_full,bdate_mod,ddate,dplace,ddate_full,ddate_mod = \
                get_birth_death_strings(database,person,empty_date,empty_place)

    value_map = {
        'name'                : person_name, 
        'unknown_gender_name' : person_name, 
        'male_name'           : person_name, 
        'female_name'         : person_name, 
        'death_date'          : ddate,
        'modified_date'       : ddate,
        'death_place'         : dplace,
        'age'                 : age ,
        'month_year'          : ddate,
        }

    gender = person.get_gender()

    if ddate:
        if ddate_mod:
            if dplace:
                text = died_modified_date_with_place[name_index][gender][age_units] % value_map
            else:
                text = died_modified_date_no_place[name_index][gender][age_units] % value_map
        elif ddate_full:
            if dplace:
                text = died_full_date_with_place[name_index][gender][age_units] % value_map
            else:
                text = died_full_date_no_place[name_index][gender][age_units] % value_map
        else:
            if dplace:
                text = died_partial_date_with_place[name_index][gender][age_units] % value_map
            else:
                text = died_partial_date_no_place[name_index][gender][age_units] % value_map
    else:
        if dplace:
            text = died_no_date_with_place[name_index][gender][age_units] % value_map
        else:
            text = died_no_date_no_place[name_index][gender][age_units] % value_map
    if text:
        text = text + " "
    return text

#-------------------------------------------------------------------------
#
# buried_str
#
#-------------------------------------------------------------------------
def buried_str(database,person,person_name=None,empty_date="",empty_place=""):
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

    name_index = 0
    if person_name == None:
        person_name = _nd.display(person)
    elif person_name == 0:
        name_index = 1

    gender = person.get_gender()
        
    text = ""
    
    bplace = dplace = empty_place
    bdate = ddate = empty_date
    bdate_full = False
    bdate_mod = False
    
    burial = None
    for event_ref in person.get_event_ref_list():
        event = database.get_event_from_handle(event_ref.ref)
        if event and int(event.get_type()) == RelLib.EventType.BURIAL:
            burial = event
            break

    if burial:
        bdate = DateHandler.get_date(burial)
        bplace_handle = burial.get_place_handle()
        if bplace_handle:
            bplace = database.get_place_from_handle(bplace_handle).get_title()
        bdate_obj = burial.get_date_object()
        bdate_full = bdate_obj and bdate_obj.get_day_valid()
        bdate_mod = bdate_obj and bdate_obj.get_modifier() != RelLib.Date.MOD_NONE
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
        }

    if bdate and bdate_mod:
        if bplace: #male, date, place
            text = buried_modified_date_place[gender][name_index] % values
        else:      #male, date, no place
            text = buried_modified_date_no_place[gender][name_index] % values
    elif bdate and bdate_full:
        if bplace: #male, date, place
            text = buried_full_date_place[gender][name_index] % values
        else:      #male, date, no place
            text = buried_full_date_no_place[gender][name_index] % values
    elif bdate:
        if bplace: #male, month_year, place
            text =  buried_partial_date_place[gender][name_index] % values
        else:      #male, month_year, no place
            text = buried_partial_date_no_place[gender][name_index] % values
    elif bplace:   #male, no date, place
        text = buried_no_date_place[gender][name_index] % values
    else:          #male, no date, no place
        text = buried_no_date_no_place[gender][name_index] % values
        
    if text:
        text = text + " "
    return text

#-------------------------------------------------------------------------
#
# list_person_str
#
#-------------------------------------------------------------------------
def list_person_str(database,person,empty_date="",empty_place=""):
    """ 
    Briefly list person and birth/death events.
    """

    bdate,bplace,bdate_full,bdate_mod,ddate,dplace,ddate_full,ddate_mod = \
                        get_birth_death_strings(database,person)

    text = ""

    values = {
        'birth_date'  : bdate,
        'birth_place' : bplace,
        'death_date'  : ddate,
        'death_place' : dplace,
        }
    
    if bdate:
        if bplace:
            if ddate:
                if dplace:
                    text = _("Born: %(birth_date)s %(birth_place)s, "
                             "Died: %(death_date)s %(death_place)s.") % values
                else:
                    text = _("Born: %(birth_date)s %(birth_place)s, "
                             "Died: %(death_date)s.") % values
            else:
                if dplace:
                    text = _("Born: %(birth_date)s %(birth_place)s, "
                             "Died: %(death_place)s.") % values
                else:
                    text = _("Born: %(birth_date)s %(birth_place)s.") % values
        else:
            if ddate:
                if dplace:
                    text = _("Born: %(birth_date)s, "
                             "Died: %(death_date)s %(death_place)s.") % values
                else:
                    text = _("Born: %(birth_date)s, Died: %(death_date)s.") % values
            else:
                if dplace:
                    text = _("Born: %(birth_date)s, Died: %(death_place)s.") % values
                else:
                    text = _("Born: %(birth_date)s.") % values
    else:
        if bplace:
            if ddate:
                if dplace:
                    text = _("Born: %(birth_place)s, "
                             "Died: %(death_date)s %(death_place)s.") % values
                else:
                    text = _("Born: %(birth_place)s, "
                             "Died: %(death_date)s.") % values
            else:
                if dplace:
                    text = _("Born: %(birth_place)s, "
                             "Died: %(death_place)s.") % values
                else:
                    text = _("Born: %(birth_place)s.") % values
        else:
            if ddate:
                if dplace:
                    text = _("Died: %(death_date)s %(death_place)s.") % values
                else:
                    text = _("Died: %(death_date)s.") % values
            else:
                if dplace:
                    text = _("Died: %(death_place)s.") % values
                else:
                    text = ""
    return text

def get_birth_or_fallback(database,person):
    birth_ref = person.get_birth_ref()
    if birth_ref:   # regular birth found
        return database.get_event_from_handle(birth_ref.ref)
    # now search the event list for fallbacks
    for event_ref in person.get_primary_event_ref_list():
        event = database.get_event_from_handle(event_ref.ref)
        if event.get_type() in [RelLib.EventType.CHRISTEN, RelLib.EventType.BAPTISM]:
            return event
    return None    

def get_death_or_fallback(database,person):
    birth_ref = person.get_death_ref()
    if birth_ref:   # regular death found
        return database.get_event_from_handle(birth_ref.ref)
    # now search the event list for fallbacks
    for event_ref in person.get_primary_event_ref_list():
        event = database.get_event_from_handle(event_ref.ref)
        if event.get_type() in [RelLib.EventType.BURIAL, RelLib.EventType.CREMATION]:
            return event
    return None    

def old_calc_age(database,person):
    """
    Calulate age. 
    
    Returns a tuple (age,units) where units is an integer representing
    time units:
        no age info:    0
        years:          1
        months:         2
        days:           3
    """
    YEARS  = 1
    MONTHS = 2
    DAYS   = 3

    # FIXME: This is an old and ugly implementation. 
    # It must be changed to use the new age calculator.
    age = 0
    units = 0

    birth_ref = person.get_birth_ref()
    if birth_ref:
        birth = database.get_event_from_handle(birth_ref.ref).get_date_object()
        birth_year_valid = birth.get_year_valid()
    else:
        birth_year_valid = None
    death_ref = person.get_death_ref()
    if death_ref:
        death = database.get_event_from_handle(death_ref.ref).get_date_object()
        death_year_valid = death.get_year_valid()
    else:
        death_year_valid = None

    # wihtout at least a year for each event we're clueless
    if not (birth_year_valid and death_year_valid):
        return (age,units)
    
    # FIXME: The code below uses hard-coded 31 days in a month
    # and 12 month in a year. This is incorrect for half the Gregorian
    # months and for other calendars.
    # FIXME: We need to move to estimate_age !!!

    # If born and died in the same year, go to the months
    if death.get_year() == birth.get_year():
        if birth.get_month_valid() and death.get_month_valid():
            # if born and died in the same month, do the days
            if birth.get_month() == death.get_month() \
               and birth.get_day_valid() and death.get_day_valid():
                age = death.get_day() - birth.get_day()
                units = DAYS
            # if not the same month, just diff the months
            else:
                age = death.get_month() - birth.get_month()
                units = MONTHS
    # Born and died in different years
    else:
        age = death.get_year() - birth.get_year()
        units = YEARS
        if birth.get_month_valid() and death.get_month_valid():
            # Subtract one year if less than a last full year
            if birth.get_month() > death.get_month():
                age = age - 1

            # If less than a year (but still in different years)
            # then calculate month diff modulo 12
            if age == 0:
                age = 12 + death.get_month() - birth.get_month()
                units = MONTHS

    # This is the case of birth on Dec 30 and death on Jan 2
    # or birth on May 30 and death on June 2
    if age == 1 and units == MONTHS \
       and birth.get_day_valid() and death.get_day_valid() \
       and birth.get_day() > death.get_day():
        age = death.get_day() + 31 - birth.get_day()
        unit = DAYS

    return (age,units)

    
def common_name(person,use_call=False):
    if use_call and person.get_primary_name().get_call_name():
        return person.get_primary_name().get_call_name()
    else:
        return person.get_primary_name().get_first_name()

#-------------------------------------------------------------------------
#
# Indexing function
#
#-------------------------------------------------------------------------
def get_person_mark(db,person):
    """
    Returns a IndexMark that can be used to index a person in a report
    
    @param db: the GRAMPS database instance
    @param person: the the key is for
    """
    if not person:
        return None
    
    name = person.get_primary_name().get_name()
    birth = " "
    death = " "
    key = ""
    
    birth_ref = person.get_birth_ref()
    if birth_ref:
        birthEvt = db.get_event_from_handle(birth_ref.ref)
        birth = DateHandler.get_date(birthEvt)

    death_ref = person.get_death_ref()
    if death_ref:
        deathEvt = db.get_event_from_handle(death_ref.ref)
        death = DateHandler.get_date(deathEvt)

    if birth == " " and death == " ":
        key = name
    else:
        key = "%s (%s - %s)" % (name,birth,death)
        
    return BaseDoc.IndexMark( key, BaseDoc.INDEX_TYPE_ALP )

#-------------------------------------------------------------------------
#
# Address String
#
#-------------------------------------------------------------------------
def get_address_str(addr):
    """
    Returns a string that combines the elements of an addres
    
    @param addr: the GRAMPS address instance
    """
    str = ""
    elems = [ addr.get_street(),
              addr.get_city(),
              addr.get_county(),
              addr.get_state(),
              addr.get_country(),
              addr.get_postal_code(),
              addr.get_phone()   ]
    
    for info in elems:
        if info:
            if str == "":
                str = info
            else:
                str = "%s, %s" % (str,info)
    return str
    
def get_endnotes(sref_map,obj):
    if not obj:
        return ""
    
    slist = obj.get_source_references()
    
    if not slist:
        return ""

    msg = cStringIO.StringIO()
    first = 1
    for ref in slist:
        if not first:
            msg.write(',')
        first = 0
        ref_base = ref.get_reference_handle()
        the_key = 0
        for key in sref_map.keys():
            if ref_base == sref_map[key].get_reference_handle():
                the_key = key
                break
        if not the_key:
            the_key = len(sref_map) + 1
            sref_map[the_key] = ref
        msg.write("%d" % the_key)
    str = msg.getvalue()
    msg.close()
    return str
