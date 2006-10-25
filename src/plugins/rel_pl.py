# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
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

# Written by Piotr Czubaszek, largely based on rel_de.py by Alex Roitman.

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

import RelLib
import Relationship
import types
from gettext import gettext as _
from PluginUtils import register_relcalc

#-------------------------------------------------------------------------
#
# Polish-specific definitions of relationships
#
#-------------------------------------------------------------------------

_male_cousin_level = [ "", "", 
  "drugi", "trzeci", "czwarty", "piąty", "szóśty","siódmy", "ósmy", "dziewiąty", "dziesiąty", "jedenasty", "dwunasty", "trzynasty", "czternasty", "piętnasty", "szesnasty", "siedemnasty","osiemnasty"
  ]

_female_cousin_level = [ "", "", 
  "druga", "trzecia", "czwarta", "piąta", "szóśta","siódma", "ósma", "dziewiąta", "dziesiąta", "jedenasta", "dwunasta", "trzynasta", "czternasta", "piętnasta", "szesnasta", "siedemnasta","osiemnasta"
  ]

_removed_level = [ "", "pierwszego", "drugiego", "trzeciego", "czwartego", "piątego",
  "szóstego", "siódmego", "ósmego", "dziewiątego", "dziesiątego", "jedenastego", "dwunastego", "trzynastego", "czternastego", "piętnastego", "szesnastego", "siedemnasego", "osiemnastego", "dziewiętnastego", "dwudziestego" ]

_father_level = [ "", "ojciec", 
  "dziadek", 
  "pradziadek", 
  "prapradziadek", 
  "praprapradziadek", 
  "praprapraprapradziadek",
  "prapraprapraprapradziadek",
  "praprapraprapraprapradziadek",
  "prapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek",
]

_mother_level = [ "", "matka", 
  "babcia", 
  "prababcia", 
  "praprababcia", 
  "prapraprababcia", 
  "prapraprapraprababcia",
  "praprapraprapraprababcia",
  "prapraprapraprapraprababcia",
  "praprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia",
]

_son_level = [ "", "syn", 
  "wnuk", 
  "prawnuk", 
  "praprawnuk", 
  "prapraprauwnuk", 
  "prapraprapraprawnuk",
  "praprapraprapraprawnuk",
  "prapraprapraprapraprawnuk",
  "praprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuk",
]

_daughter_level = [ "", "córka", 
  "wnuczka", 
  "prawnuczka", 
  "praprawnuczka", 
  "prapraprauwnuczka", 
  "prapraprapraprawnuczka", 
  "praprapraprapraprawnuczka", 
  "prapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapraprawnuczka", 
]

_sister_level_of_male = [ "", "siostra", "ciotka", 
  "babcia stryjeczna", 
  "prababcia stryjeczna", 
  "praprababcia stryjeczna", 
  "prapraprababcia stryjeczna", 
  "praprapraprababcia stryjeczna", 
  "prapraprapraprababcia stryjeczna", 
  "praprapraprapraprababcia stryjeczna", 
  "prapraprapraprapraprababcia stryjeczna", 
  "praprapraprapraprapraprababcia stryjeczna", 
  "prapraprapraprapraprapraprababcia stryjeczna", 
  "praprapraprapraprapraprapraprababcia stryjeczna", 
  "prapraprapraprapraprapraprapraprababcia stryjeczna", 
  "praprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "prapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "praprapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "prapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia stryjeczna", 
]

_sister_level_of_female = [ "", "siostra", "ciotka", 
  "babcia cioteczna", 
  "prababcia cioteczna", 
  "praprababcia cioteczna", 
  "prapraprababcia cioteczna", 
  "praprapraprababcia cioteczna", 
  "prapraprapraprababcia cioteczna", 
  "praprapraprapraprababcia cioteczna", 
  "prapraprapraprapraprababcia cioteczna", 
  "praprapraprapraprapraprababcia cioteczna", 
  "prapraprapraprapraprapraprababcia cioteczna", 
  "praprapraprapraprapraprapraprababcia cioteczna", 
  "prapraprapraprapraprapraprapraprababcia cioteczna", 
  "praprapraprapraprapraprapraprapraprababcia cioteczna", 
  "prapraprapraprapraprapraprapraprapraprababcia cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprababcia cioteczna", 
  "prapraprapraprapraprapraprapraprapraprapraprababcia cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprababcia cioteczna", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprababcia cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprababcia cioteczna", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia cioteczna", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprababcia cioteczna", 
]

_brother_level_of_male = [ "", "brat", "stryj", 
  "dziadek stryjeczny", 
  "pradziadek stryjeczny", 
  "prapradziadek stryjeczny",
  "praprapradziadek stryjeczny", 
  "prapraprapradziadek stryjeczny", 
  "praprapraprapradziadek stryjeczny", 
  "prapraprapraprapradziadek stryjeczny", 
  "praprapraprapraprapradziadek stryjeczny", 
  "prapraprapraprapraprapradziadek stryjeczny", 
  "praprapraprapraprapraprapradziadek stryjeczny", 
  "prapraprapraprapraprapraprapradziadek stryjeczny", 
  "praprapraprapraprapraprapraprapradziadek stryjeczny", 
  "prapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "praprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "prapraprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "praprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "praprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek stryjeczny", 
]

_brother_level_of_female = [ "", "brat", "wuj", 
  "dziadek cioteczny", 
  "pradziadek cioteczny", 
  "prapradziadek cioteczny",
  "praprapradziadek cioteczny", 
  "prapraprapradziadek cioteczny", 
  "praprapraprapradziadek cioteczny", 
  "prapraprapraprapradziadek cioteczny", 
  "praprapraprapraprapradziadek cioteczny", 
  "prapraprapraprapraprapradziadek cioteczny", 
  "praprapraprapraprapraprapradziadek cioteczny", 
  "prapraprapraprapraprapraprapradziadek cioteczny", 
  "praprapraprapraprapraprapraprapradziadek cioteczny", 
  "prapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "praprapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "praprapraprapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "praprapraprapraprapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek cioteczny", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadek cioteczny", 
]

_nephew_level_of_brothers_son = [ "", "bratanek", 
  "syn bratanka", 
  "wnuk bratanka", 
  "prawnuk bratanka", 
  "prawnuk bratanka", 
  "praprawnuk bratanka", 
  "prapraprawnuk bratanka", 
  "praprapraprawnuk bratanka", 
  "prapraprapraprawnuk bratanka", 
  "praprapraprapraprawnuk bratanka", 
  "prapraprapraprapraprawnuk bratanka", 
  "praprapraprapraprapraprawnuk bratanka", 
  "prapraprapraprapraprapraprawnuk bratanka", 
  "praprapraprapraprapraprapraprawnuk bratanka", 
  "prapraprapraprapraprapraprapraprawnuk bratanka", 
  "praprapraprapraprapraprapraprapraprawnuk bratanka", 
  "prapraprapraprapraprapraprapraprapraprawnuk bratanka", 
  "praprapraprapraprapraprapraprapraprapraprawnuk bratanka", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuk bratanka", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuk bratanka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuk bratanka", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuk bratanka", 
]

_nephew_level_of_brothers_daughter = [ "", "bratanek", 
  "syn bratanicy", 
  "wnuk bratanicy", 
  "prawnuk bratanicy", 
  "prawnuk bratanicy", 
  "praprawnuk bratanicy", 
  "prapraprawnuk bratanicy", 
  "praprapraprawnuk bratanicy", 
  "prapraprapraprawnuk bratanicy", 
  "praprapraprapraprawnuk bratanicy", 
  "prapraprapraprapraprawnuk bratanicy", 
  "praprapraprapraprapraprawnuk bratanicy", 
  "prapraprapraprapraprapraprawnuk bratanicy", 
  "praprapraprapraprapraprapraprawnuk bratanicy", 
  "prapraprapraprapraprapraprapraprawnuk bratanicy", 
  "praprapraprapraprapraprapraprapraprawnuk bratanicy", 
  "prapraprapraprapraprapraprapraprapraprawnuk bratanicy", 
  "praprapraprapraprapraprapraprapraprapraprawnuk bratanicy", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuk bratanicy", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuk bratanicy", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuk bratanicy", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuk bratanicy", 
]

_nephew_level_of_sisters_son = [ "", "siostrzeniec", 
  "syn siostrzeńca", 
  "wnuk siostrzeńca", 
  "prawnuk siostrzeńca", 
  "prawnuk siostrzeńca", 
  "praprawnuk siostrzeńca", 
  "prapraprawnuk siostrzeńca", 
  "praprapraprawnuk siostrzeńca", 
  "prapraprapraprawnuk siostrzeńca", 
  "praprapraprapraprawnuk siostrzeńca", 
  "prapraprapraprapraprawnuk siostrzeńca", 
  "praprapraprapraprapraprawnuk siostrzeńca", 
  "prapraprapraprapraprapraprawnuk siostrzeńca", 
  "praprapraprapraprapraprapraprawnuk siostrzeńca", 
  "prapraprapraprapraprapraprapraprawnuk siostrzeńca", 
  "praprapraprapraprapraprapraprapraprawnuk siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprawnuk siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprawnuk siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuk siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuk siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuk siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuk siostrzeńca", 
]

_nephew_level_of_sisters_daughter = [ "", "siostrzeniec", 
  "syn siostrzenicy", 
  "wnuk siostrzenicy", 
  "prawnuk siostrzenicy", 
  "prawnuk siostrzenicy", 
  "praprawnuk siostrzenicy", 
  "prapraprawnuk siostrzenicy", 
  "praprapraprawnuk siostrzenicy", 
  "prapraprapraprawnuk siostrzenicy", 
  "praprapraprapraprawnuk siostrzenicy", 
  "prapraprapraprapraprawnuk siostrzenicy", 
  "praprapraprapraprapraprawnuk siostrzenicy", 
  "prapraprapraprapraprapraprawnuk siostrzenicy", 
  "praprapraprapraprapraprapraprawnuk siostrzenicy", 
  "prapraprapraprapraprapraprapraprawnuk siostrzenicy", 
  "praprapraprapraprapraprapraprapraprawnuk siostrzenicy", 
  "prapraprapraprapraprapraprapraprapraprawnuk siostrzenicy", 
  "praprapraprapraprapraprapraprapraprapraprawnuk siostrzenicy", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuk siostrzenicy", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuk siostrzenicy", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuk siostrzenicy", 
  "praprapraprapraprapraprapraprapraprapraprapraprapraprawnuk siostrzenicy", 
]

_niece_level_of_brothers_son = [ "", "bratanica", 
  "córka bratanka", 
  "wnuczka bratanka", 
  "prawnuczka bratanka", 
  "prawnuczka bratanka", 
  "praprawnuczka bratanka", 
  "prapraprawnuczka bratanka", 
  "praprapraprawnuczka bratanka", 
  "prapraprapraprawnuczka bratanka", 
  "praprapraprapraprawnuczka bratanka", 
  "prapraprapraprapraprawnuczka bratanka", 
  "praprapraprapraprapraprawnuczka bratanka", 
  "prapraprapraprapraprapraprawnuczka bratanka", 
  "praprapraprapraprapraprapraprawnuczka bratanka", 
  "prapraprapraprapraprapraprapraprawnuczka bratanka", 
  "praprapraprapraprapraprapraprapraprawnuczka bratanka", 
  "prapraprapraprapraprapraprapraprapraprawnuczka bratanka", 
  "praprapraprapraprapraprapraprapraprapraprawnuczka bratanka", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuczka bratanka", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuczka bratanka", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuczka bratanka", 
]

_niece_level_of_brothers_daughter = [ "", "bratanica", 
  "córka bratanicy", 
  "wnuczka bratanicy", 
  "prawnuczka bratanicy", 
  "prawnuczka bratanicy", 
  "praprawnuczka bratanicy", 
  "prapraprawnuczka bratanicy", 
  "praprapraprawnuczka bratanicy", 
  "prapraprapraprawnuczka bratanicy", 
  "praprapraprapraprawnuczka bratanicy", 
  "prapraprapraprapraprawnuczka bratanicy", 
  "praprapraprapraprapraprawnuczka bratanicy", 
  "prapraprapraprapraprapraprawnuczka bratanicy", 
  "praprapraprapraprapraprapraprawnuczka bratanicy", 
  "prapraprapraprapraprapraprapraprawnuczka bratanicy", 
  "praprapraprapraprapraprapraprapraprawnuczka bratanicy", 
  "prapraprapraprapraprapraprapraprapraprawnuczka bratanicy", 
  "praprapraprapraprapraprapraprapraprapraprawnuczka bratanicy", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuczka bratanicy", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuczka bratanicy", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuczka bratanicy", 
]

_niece_level_of_sisters_son = [ "", "siostrzenica", 
  "córka siostrzeńca", 
  "wnuczka siostrzeńca", 
  "prawnuczka siostrzeńca", 
  "prawnuczka siostrzeńca", 
  "praprawnuczka siostrzeńca", 
  "prapraprawnuczka siostrzeńca", 
  "praprapraprawnuczka siostrzeńca", 
  "prapraprapraprawnuczka siostrzeńca", 
  "praprapraprapraprawnuczka siostrzeńca", 
  "prapraprapraprapraprawnuczka siostrzeńca", 
  "praprapraprapraprapraprawnuczka siostrzeńca", 
  "prapraprapraprapraprapraprawnuczka siostrzeńca", 
  "praprapraprapraprapraprapraprawnuczka siostrzeńca", 
  "prapraprapraprapraprapraprapraprawnuczka siostrzeńca", 
  "praprapraprapraprapraprapraprapraprawnuczka siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprawnuczka siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprawnuczka siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuczka siostrzeńca", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuczka siostrzeńca", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuczka siostrzeńca", 
]

_niece_level_of_sisters_daughter = [ "", "siostrzenica", 
  "córka siostrzenicy", 
  "wnuczka siostrzenicy", 
  "prawnuczka siostrzenicy", 
  "prawnuczka siostrzenicy", 
  "praprawnuczka siostrzenicy", 
  "prapraprawnuczka siostrzenicy", 
  "praprapraprawnuczka siostrzenicy", 
  "prapraprapraprawnuczka siostrzenicy", 
  "praprapraprapraprawnuczka siostrzenicy", 
  "prapraprapraprapraprawnuczka siostrzenicy", 
  "praprapraprapraprapraprawnuczka siostrzenicy", 
  "prapraprapraprapraprapraprawnuczka siostrzenicy", 
  "praprapraprapraprapraprapraprawnuczka siostrzenicy", 
  "prapraprapraprapraprapraprapraprawnuczka siostrzenicy", 
  "praprapraprapraprapraprapraprapraprawnuczka siostrzenicy", 
  "prapraprapraprapraprapraprapraprapraprawnuczka siostrzenicy", 
  "praprapraprapraprapraprapraprapraprapraprawnuczka siostrzenicy", 
  "prapraprapraprapraprapraprapraprapraprapraprawnuczka siostrzenicy", 
  "praprapraprapraprapraprapraprapraprapraprapraprawnuczka siostrzenicy", 
  "prapraprapraprapraprapraprapraprapraprapraprapraprawnuczka siostrzenicy", 
]

_parents_level = [ "", "rodzice", 
  "dziadkowie", 
  "pradziadkowie", 
  "prapradziadkowie", 
  "praprapraudziadkowie", 
  "praprapraprapradziadkowie",
  "prapraprapraprapradziadkowie",
  "praprapraprapraprapradziadkowie",
  "prapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "prapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
  "praprapraprapraprapraprapraprapraprapraprapraprapraprapraprapradziadkowie",
]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(Relationship.RelationshipCalculator):

    def __init__(self,db):
        Relationship.RelationshipCalculator.__init__(self,db)

    def get_parents(self,level):
        if level>len(_parents_level)-1:
            return "dalecy przodkowie"
        else:
            return _parents_level[level]

    def get_junior_male_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_male_cousin_level)-1:
            return "daleki krewny"
        else:
            return "%s kuzyn %s stopnia" % (_male_cousin_level[level],_removed_level[removed])

    def get_senior_male_cousin_of_male(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_brother_level_of_male)-1:
            return "daleki krewny"
        else:
            return "%s %s stopnia" % (_brother_level_of_male[level],_removed_level[removed])

    def get_senior_male_cousin_of_female(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_brother_level_of_female)-1:
            return "daleki krewny"
        else:
            return "%s %s stopnia" % (_brother_level_of_female[level],_removed_level[removed])

    def get_junior_female_cousin(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_female_cousin_level)-1:
            return "daleka krewna"
        else:
            return "%s kuzynka %s stopnia" % (_female_cousin_level[level],_removed_level[removed])

    def get_senior_female_cousin_of_male(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_sister_level_of_male)-1:
            return "daleka krewna"
        else:
            return "%s %s stopnia" % (_sister_level_of_male[level],_removed_level[removed])

    def get_senior_female_cousin_of_female(self,level,removed):
        if removed > len(_removed_level)-1 or level>len(_sister_level_of_female)-1:
            return "daleka krewna"
        else:
            return "%s %s stopnia" % (_sister_level_of_female[level],_removed_level[removed])

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "daleki przodek"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "daleki potomek"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "daleki przodek"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "daleki potomek"
        else:
            return _daughter_level[level]

    def get_aunt_of_male(self,level):
        if level>len(_sister_level_of_male)-1:
            return "daleki przodek"
        else:
            return _sister_level_of_male[level]

    def get_aunt_of_female(self,level):
        if level>len(_sister_level_of_female)-1:
            return "daleki przodek"
        else:
            return _sister_level_of_female[level]

    def get_uncle_of_male(self,level):
        if level>len(_brother_level_of_male)-1:
            return "daleki przodek"
        else:
            return _brother_level_of_male[level]

    def get_uncle_of_female(self,level):
        if level>len(_brother_level_of_female)-1:
            return "daleki przodek"
        else:
            return _brother_level_of_female[level]

    def get_nephew_of_brothers_son(self,level):
        if level>len(_nephew_level_of_brothers_son)-1:
            return "daleki potomek"
        else:
		return _nephew_level_of_brothers_son[level]

    def get_nephew_of_brothers_daughter(self,level):
        if level>len(_nephew_level_of_brothers_daughter)-1:
            return "daleki potomek"
        else:
		return _nephew_level_of_brothers_daughter[level]

    def get_nephew_of_sisters_son(self,level):
        if level>len(_nephew_level_of_sisters_son)-1:
            return "daleki potomek"
        else:
		return _nephew_level_of_sisters_son[level]

    def get_nephew_of_sisters_daughter(self,level):
        if level>len(_nephew_level_of_sisters_daughter)-1:
            return "daleki potomek"
        else:
		return _nephew_level_of_sisters_daughter[level]

    def get_niece_of_brothers_son(self,level):
        if level>len(_niece_level_of_brothers_son)-1:
            return "daleki potomek"
        else:
            return _niece_level_of_brothers_son[level]

    def get_niece_of_brothers_daughter(self,level):
        if level>len(_niece_level_of_brothers_daughter)-1:
            return "daleki potomek"
        else:
            return _niece_level_of_brothers_daughter[level]

    def get_niece_of_sisters_son(self,level):
        if level>len(_niece_level_of_sisters_son)-1:
            return "daleki potomek"
        else:
            return _niece_level_of_sisters_son[level]

    def get_niece_of_sisters_daughter(self,level):
        if level>len(_niece_level_of_sisters_daughter)-1:
            return "daleki potomek"
        else:
            return _niece_level_of_sisters_daughter[level]

    def get_relationship_distance(self,orig_person,other_person):
        """
        Returns a tuple (firstRel,secondRel,common):
        
        firstRel    Number of generations from the orig_person to their
                    closest common ancestor
        secondRel   Number of generations from the other_person to their
                    closest common ancestor
        common      list of their common ancestors, the closest is the first
        
        is returned
        """
        
        firstRel = -1
        secondRel = -1
        common = []

        firstMap = {}
        firstList = []
        secondMap = {}
        secondList = []
        rank = 9999999

        try:
            self.apply_filter(orig_person,'',firstList,firstMap)
            self.apply_filter(other_person,'',secondList,secondMap)
        except RuntimeError:
            return (firstRel,secondRel,_("Relationship loop detected"))

        for person_handle in firstList:
            if person_handle in secondList:
                new_rank = len(firstMap[person_handle])
                if new_rank < rank:
                    rank = new_rank
                    common = [ person_handle ]
                elif new_rank == rank:
                    common.append(person_handle)

        if common:
            person_handle = common[0]
            secondRel = firstMap[person_handle]
            firstRel = secondMap[person_handle]

        return (firstRel,secondRel,common,firstList,secondList)

    def get_relationship(self,orig_person,other_person):
        """
        Returns a string representing the relationshp between the two people,
        along with a list of common ancestors (typically father,mother) 
        
        Special cases: relation strings "", "undefined" and "spouse".
        """

        if orig_person == None:
            return ("undefined",[])
    
        if orig_person.get_handle() == other_person.get_handle():
            return ('', [])

        is_spouse = self.is_spouse(orig_person,other_person)
        if is_spouse:
            return (is_spouse,[])

        (firstRel,secondRel,common,firstList,secondList) = self.get_relationship_distance(orig_person,other_person)
        
        if type(common) == types.StringType or type(common) == types.UnicodeType:
            return (common,[])
        elif common:
            person_handle = common[0]
        else:
            return ("",[])

        firstRel = len(firstRel)
	secondRelatives = secondRel
        secondRel = len(secondRel)

        if firstRel == 0:
            if secondRel == 0:
                return ('',common)
            elif other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_father(secondRel),common)
            else:
                return (self.get_mother(secondRel),common)
        elif secondRel == 0:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_son(firstRel),common)
            else:
                return (self.get_daughter(firstRel),common)
        elif firstRel == 1:
            families1 = self.db.get_person_from_handle(common[0]).get_family_handle_list()
            families2 = None
            if len(common) >1:
                families2 = self.db.get_person_from_handle(common[1]).get_family_handle_list()
            for ancFamily_handle in families1:
                if families2:
                    if ancFamily_handle in families2:
                        ancFamily = self.db.get_family_from_handle(ancFamily_handle)
                    else:
                        continue
                else:
                    ancFamily = self.db.get_family_from_handle(ancFamily_handle)
                children = ancFamily.get_child_ref_list()
                for sibling in children:
                    if sibling.ref in firstList:
                        # discriminate between siblings/uncles etc. and stepsiblings/stepuncles
                        if other_person.get_main_parents_family_handle() == self.db.get_person_from_handle(sibling.ref).get_main_parents_family_handle():
                            if other_person.get_gender() == RelLib.Person.MALE:
                                if self.db.get_person_from_handle(sibling.ref).get_gender() == RelLib.Person.MALE:
                                    # brat / stryj / (pra)dziadek stryjeczny
                                    return (self.get_uncle_of_male(secondRel),common)
                                else:
                                    # brat / wuj / (pra)dziadek cioteczny
                                    return (self.get_uncle_of_female(secondRel),common)
                            else:
                                if self.db.get_person_from_handle(sibling.ref).get_gender() == RelLib.Person.MALE:
                                    # siostra / ciotka / (pra)babcia stryjeczna
                                    return (self.get_aunt_of_male(secondRel),common)
                                else:
                                    # siostra / ciotka / (pra)babcia cioteczna
                                    return (self.get_aunt_of_female(secondRel),common)
                        else:
                            if other_person.get_gender() == RelLib.Person.MALE:
                                if self.db.get_person_from_handle(sibling.ref).get_gender() == RelLib.Person.MALE:
                                    # brat / stryj / (pra)dziadek stryjeczny
                                    return (self.get_uncle_of_male(secondRel)+" (przyrodni)",common)
                                else:
                                    # brat / wuj / (pra)dziadek cioteczny
                                    return (self.get_uncle_of_female(secondRel)+" (przyrodni)",common)
                            else:
                                if self.db.get_person_from_handle(sibling.ref).get_gender() == RelLib.Person.MALE:
                                    # siostra / ciotka / (pra)babcia stryjeczna
                                    return (self.get_aunt_of_male(secondRel)+" (przyrodnia)",common)
                                else:
                                    # siostra / ciotka / (pra)babcia cioteczna
                                    return (self.get_aunt_of_female(secondRel)+" (przyrodnia)",common)
        elif secondRel == 1:
            families1 = self.db.get_person_from_handle(common[0]).get_family_handle_list()
            families2 = None
            if len(common) >1:
                families2 = self.db.get_person_from_handle(common[1]).get_family_handle_list()
            for ancFamily_handle in families1:
                if families2:
                    if ancFamily_handle in families2:
                        ancFamily = self.db.get_family_from_handle(ancFamily_handle)
                    else:
                        continue
                else:
                    ancFamily = self.db.get_family_from_handle(ancFamily_handle)
                children = ancFamily.get_child_ref_list()
                for sibling_handle in children:
                    if sibling_handle.ref in secondList:
                        sibling = self.db.get_person_from_handle(sibling_handle.ref)
                        families = sibling.get_family_handle_list()
                        for sibFamily in families:
                            for child_handle in self.db.get_family_from_handle(sibFamily).get_child_ref_list():
                                if child_handle.ref in secondList:
                                    child = self.db.get_person_from_handle(child_handle.ref)
                                    if other_person.get_gender() == RelLib.Person.MALE:
                                        if sibling.get_gender() == RelLib.Person.MALE:
                                            if child.get_gender() == RelLib.Person.MALE:
                                                # bratanek / syn bratanka
                                                return (self.get_nephew_of_brothers_son(firstRel-1))
                                            else:
                                                # bratanek / syn bratanicy
                                                return (self.get_nephew_of_brothers_daughter(firstRel-1),common)
                                        else:
                                            if child.get_gender() == RelLib.Person.MALE:
                                                # siostrzeniec / syn siostrzeńca
                                                return (self.get_nephew_of_sisters_son(firstRel-1),common)
                                            else:
                                                # siostrzniec / syn siostrzenicy
                                                return (self.get_nephew_of_sisters_daughter(firstRel-1),common)
                                    else:
                                        if sibling.get_gender() == RelLib.Person.MALE:
                                            if child.get_gender() == RelLib.Person.MALE:
                                                # bratanica / córka bratanka
                                                return (self.get_niece_of_brothers_son(firstRel-1),common)
                                            else:
                                                # bratanica / córka bratanicy
                                                return (self.get_niece_of_brothers_daughter(firstRel-1),common)
                                        else:
                                            if child.get_gender() == RelLib.Person.MALE:
                                                # siostrzenica / córka siostrzeńca
                                                return (self.get_niece_of_sisters_son(firstRel-1),common)
                                            else:
                                                # siostrzenica / córka siostrzenicy
                                                return (self.get_niece_of_sisters_daughter(firstRel-1),common)
        elif secondRel > firstRel:
            families1 = self.db.get_person_from_handle(common[0]).get_family_handle_list()
            families2 = None
            if len(common) >1:
                families2 = self.db.get_person_from_handle(common[1]).get_family_handle_list()
            for ancFamily_handle in families1:
                if families2:
                    if ancFamily_handle in families2:
                        ancFamily = self.db.get_family_from_handle(ancFamily_handle)
                    else:
                        continue
                else:
                    ancFamily = self.db.get_family_from_handle(ancFamily_handle)
                children = ancFamily.get_child_ref_list()
                for sibling in children:
                    if sibling.ref in firstList:
                        if other_person.get_gender() == RelLib.Person.MALE:
                            if self.db.get_person_from_handle(sibling.ref).get_gender() == RelLib.Person.MALE:
                                return (self.get_senior_male_cousin_of_male(secondRel-firstRel+1,secondRel-1),common)
                            else:
                                return (self.get_senior_male_cousin_of_female(secondRel-firstRel+1,secondRel-1),common)
                        else:
                            if self.db.get_person_from_handle(sibling.ref).get_gender() == RelLib.Person.MALE:
                                return (self.get_senior_female_cousin_of_male(secondRel-firstRel+1,secondRel-1),common)
                            else:
                                return (self.get_senior_female_cousin_of_female(secondRel-firstRel+1,secondRel-1),common)
        else:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_junior_male_cousin(secondRel-1,firstRel-1),common)
            else:
                return (self.get_junior_female_cousin(secondRel-1,firstRel-1),common)
    
#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["pl","PL","pl_PL","polski","Polski","pl_PL.UTF-8", "pl_PL.UTF8", "pl_PL.utf-8", "pl_PL.utf8", "pl_PL.iso-8859-2", "pl_PL.iso8859-2", "pl_PL.cp1250", "pl_PL.cp-1250"])
