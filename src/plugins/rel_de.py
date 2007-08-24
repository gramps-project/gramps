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

# $Id$

# Written by Alex Roitman, largely based on Relationship.py by Don Allingham.
# and on valuable input from Dr. Martin Senftleben
# Modified by Joachim Breitner to not use „Großcousine“, in accordance with
# http://de.wikipedia.org/wiki/Verwandtschaftsbeziehung

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
# German-specific definitions of relationships
#
#-------------------------------------------------------------------------

_removed_level = [ "",
		"", # " ersten Grades", but is usually omitted
		" zweiten Grades",
		" dritten Grades",
		" vierten Grades",
		" fünften Grades",
		" sechsten Grades",
		" siebten Grades",
		" achten Grades",
		" neunten Grades",
		" zehnten Grades",
		" elften Grades",
		" zwölften Grades",
		" dreizehnten Grades",
		" vierzehnten Grades",
		" fünfzehnten Grades",
		" sechzehnten Grades",
		" siebzehnten Grades",
		" achtzehnten Grades",
		" neunzehnten Grades",
		" zwanzigsten Grades",
	]

_father_level = [ "", "Vater (Ebene 1)", "Großvater (Ebene 2)", "Urgroßvater (Ebene 3)", 
    "Altvater (Ebene 4)", "Altgroßvater (Ebene 5)", "Alturgroßvater (Ebene 6)", 
    "Obervater (Ebene 7)", "Obergroßvater (Ebene 8)", "Oberurgroßvater (Ebene 9)",
    "Stammvater (Ebene 10)", "Stammgroßvater (Ebene 11)", "Stammurgroßvater (Ebene 12)",
    "Ahnenvater (Ebene 13)", "Ahnengroßvater (Ebene 14)", "Ahnenurgroßvater (Ebene 15)",
    "Urahnenvater (Ebene 16)", "Urahnengroßvater (Ebene 17)", "Urahnenurgroßvater (Ebene 18)",
    "Erzvater (Ebene 19)", "Erzgroßvater (Ebene 20)", "Erzurgroßvater (Ebene 21)", 
    "Erzahnenvater (Ebene 22)", "Erzahnengroßvater (Ebene 23)", "Erzahnenurgroßvater (Ebene 24)" ]

_mother_level = [ "", "Mutter (Ebene 1)", "Großmutter (Ebene 2)", "Urgroßmutter (Ebene 3)",
    "Altmutter (Ebene 4)", "Altgroßmutter (Ebene 5)", "Alturgroßmutter (Ebene 6)", 
    "Obermutter (Ebene 7)", "Obergroßmutter (Ebene 8)", "Oberurgroßmutter (Ebene 9)", 
    "Stammmutter (Ebene 10)", "Stammgroßmutter (Ebene 11)", "Stammurgroßmutter (Ebene 12)", 
    "Ahnenmutter (Ebene 13)", "Ahnengroßmutter (Ebene 14)", "Ahnenurgroßmutter (Ebene 15)", 
    "Urahnenmutter (Ebene 16)", "Urahnengroßmutter (Ebene 17)", "Urahnenurgroßmutter (Ebene 18)", 
    "Erzmutter (Ebene 19)", "Erzgroßmutter (Ebene 20)", "Erzurgroßmutter (Ebene 21)", 
    "Erzahnenmutter (Ebene 22)", "Erzahnengroßmutter (Ebene 23)", 
    "Erzahnenurgroßmutter (Ebene 24)" ]

_son_level = [ "", "Sohn", 
  "Enkel", 
  "Urenkel", 
  "Ururenkel", 
  "Urururenkel", 
  "Ururururenkel", 
  "Urururururenkel",
  "Ururururururenkel",
  "Urururururururenkel",
  "Ururururururururenkel",
  "Urururururururururenkel",
  "Ururururururururururenkel",
  "Urururururururururururenkel",
  "Ururururururururururururenkel",
  "Urururururururururururururenkel",
  "Ururururururururururururururenkel",
  "Urururururururururururururururenkel",
  "Ururururururururururururururururenkel",
  "Urururururururururururururururururenkel",
  "Ururururururururururururururururururenkel",
  "Urururururururururururururururururururenkel",
  "Ururururururururururururururururururururenkel",
  "Urururururururururururururururururururururenkel",
]

_daughter_level = [ "", "Tochter", 
  "Enkelin", 
  "Urenkelin", 
  "Ururenkelin",  
  "Urururenkelin", 
  "Ururururenkelin",
  "Urururururenkelin", 
  "Ururururururenkelin", 
  "Urururururururenkelin", 
  "Ururururururururenkelin", 
  "Urururururururururenkelin", 
  "Ururururururururururenkelin", 
  "Urururururururururururenkelin", 
  "Ururururururururururururenkelin", 
  "Urururururururururururururenkelin", 
  "Ururururururururururururururenkelin", 
  "Urururururururururururururururenkelin", 
  "Ururururururururururururururururenkelin", 
  "Urururururururururururururururururenkelin", 
  "Ururururururururururururururururururenkelin", 
  "Urururururururururururururururururururenkelin", 
  "Ururururururururururururururururururururenkelin", 
  "Urururururururururururururururururururururenkelin", 
]

_aunt_level = [ "", "Tante", 
  "Großtante", 
  "Urgroßtante", 
  "Ururgroßtante", 
  "Urururgroßtante", 
  "Ururururgroßtante", 
  "Urururururgroßtante", 
  "Ururururururgroßtante", 
  "Urururururururgroßtante", 
  "Ururururururururgroßtante", 
  "Urururururururururgroßtante", 
  "Ururururururururururgroßtante", 
  "Urururururururururururgroßtante", 
  "Ururururururururururururgroßtante", 
  "Urururururururururururururgroßtante", 
  "Ururururururururururururururgroßtante", 
  "Urururururururururururururururgroßtante", 
  "Ururururururururururururururururgroßtante", 
  "Urururururururururururururururururgroßtante", 
  "Ururururururururururururururururururgroßtante", 
  "Urururururururururururururururururururgroßtante", 
  "Ururururururururururururururururururururgroßtante", 
]

_uncle_level = [ "", "Onkel", 
  "Großonkel", 
  "Urgroßonkel", 
  "Ururgroßonkel",
  "Urururgroßonkel", 
  "Ururururgroßonkel", 
  "Urururururgroßonkel", 
  "Ururururururgroßonkel", 
  "Urururururururgroßonkel", 
  "Ururururururururgroßonkel", 
  "Urururururururururgroßonkel", 
  "Ururururururururururgroßonkel", 
  "Urururururururururururgroßonkel", 
  "Ururururururururururururgroßonkel", 
  "Urururururururururururururgroßonkel", 
  "Ururururururururururururururgroßonkel", 
  "Urururururururururururururururgroßonkel", 
  "Ururururururururururururururururgroßonkel", 
  "Urururururururururururururururururgroßonkel", 
  "Ururururururururururururururururururgroßonkel", 
  "Urururururururururururururururururururgroßonkel", 
  "Ururururururururururururururururururururgroßonkel", 
]

_nephew_level = [ "", "Neffe", 
  "Großneffe", 
  "Urgroßneffe", 
  "Ururgroßneffe", 
  "Urururgroßneffe", 
  "Ururururgroßneffe", 
  "Urururururgroßneffe", 
  "Ururururururgroßneffe", 
  "Urururururururgroßneffe", 
  "Ururururururururgroßneffe", 
  "Urururururururururgroßneffe", 
  "Ururururururururururgroßneffe", 
  "Urururururururururururgroßneffe", 
  "Ururururururururururururgroßneffe", 
  "Urururururururururururururgroßneffe", 
  "Ururururururururururururururgroßneffe", 
  "Urururururururururururururururgroßneffe", 
  "Ururururururururururururururururgroßneffe", 
  "Urururururururururururururururururgroßneffe", 
  "Ururururururururururururururururururgroßneffe", 
  "Urururururururururururururururururururgroßneffe", 
  "Ururururururururururururururururururururgroßneffe", 
]

_niece_level = [ "", "Nichte", 
  "Großnichte", 
  "Urgroßnichte", 
  "Ururgroßnichte", 
  "Urururgroßnichte", 
  "Ururururgroßnichte", 
  "Urururururgroßnichte", 
  "Ururururururgroßnichte", 
  "Urururururururgroßnichte", 
  "Ururururururururgroßnichte", 
  "Urururururururururgroßnichte", 
  "Ururururururururururgroßnichte", 
  "Urururururururururururgroßnichte", 
  "Ururururururururururururgroßnichte", 
  "Urururururururururururururgroßnichte", 
  "Ururururururururururururururgroßnichte", 
  "Urururururururururururururururgroßnichte", 
  "Ururururururururururururururururgroßnichte", 
  "Urururururururururururururururururgroßnichte", 
  "Ururururururururururururururururururgroßnichte", 
  "Urururururururururururururururururururgroßnichte", 
]

_parents_level = [ "", "Eltern", "Großeltern", "Urgroßeltern", 
"Alteltern", "Altgroßeltern", "Alturgroßeltern", "Obereltern", 
"Obergroßeltern", "Oberurgroßeltern", "Stammeltern", "Stammgroßeltern", 
"Stammurgroßeltern", "Ahneneltern", "Ahnengroßeltern", "Ahnenurgroßeltern", 
"Urahneneltern", "Urahnengroßeltern", "Urahnenurgroßeltern",
"Erzeltern", "Erzgroßeltern", "Erzurgroßeltern", "Erzahneneltern",
"Erzahnengroßeltern", "Erzahnenurgroßeltern", 
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
            return "remote ancestors"
        else:
            return _parents_level[level]

    def get_father(self,level):
        if level>len(_father_level)-1:
            return "remote ancestor"
        else:
            return _father_level[level]

    def get_son(self,level):
        if level>len(_son_level)-1:
            return "remote descendant"
        else:
            return _son_level[level]

    def get_mother(self,level):
        if level>len(_mother_level)-1:
            return "remote ancestor"
        else:
            return _mother_level[level]

    def get_daughter(self,level):
        if level>len(_daughter_level)-1:
            return "remote descendant"
        else:
            return _daughter_level[level]

    def get_aunt(self,level,removed):
        if level>len(_aunt_level)-1 or removed > len(_removed_level)-1:
            return "remote ancestor"
        else:
            return _aunt_level[level] + _removed_level[removed]

    def get_uncle(self,level,removed):
        if level>len(_uncle_level)-1 or removed > len(_removed_level)-1:
            return "remote ancestor"
        else:
            return _uncle_level[level] + _removed_level[removed]

    def get_niece(self,level,removed):
        if level>len(_niece_level)-1 or removed > len(_removed_level)-1:
            return "remote ancestor"
        else:
            return _niece_level[level] + _removed_level[removed]

    def get_nephew(self,level,removed):
        if level>len(_nephew_level)-1 or removed > len(_removed_level)-1:
            return "remote ancestor"
        else:
            return _nephew_level[level] + _removed_level[removed]

    def get_male_cousin(self,removed):
        if removed>len(_removed_level)-1:
            return "remote descendant"
        elif removed==0:
            return "Bruder"
        else:
            return "Cousin"+_removed_level[removed]

    def get_female_cousin(self,removed):
        if removed>len(_removed_level)-1:
            return "remote descendant"
        elif removed==0:
            return "Schwester"
        else:
            return "Cousine"+_removed_level[removed]

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

        (firstRel,secondRel,common) = self.get_relationship_distance(orig_person,other_person)
        
        if type(common) == types.StringType or type(common) == types.UnicodeType:
            return (common,[])
        elif common:
            person_handle = common[0]
        else:
            return ("",[])

        firstRel = len(firstRel)
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
        elif secondRel > firstRel:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_uncle(secondRel-firstRel,firstRel),common)
            else:
                return (self.get_aunt(secondRel-firstRel,firstRel),common)
        elif secondRel < firstRel:
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_nephew(firstRel-secondRel,secondRel),common)
            else:
		    return (self.get_niece(firstRel-secondRel,secondRel),common)
        else: # obviously secondRel == firstRel
            if other_person.get_gender() == RelLib.Person.MALE:
                return (self.get_male_cousin(firstRel-1),common)
            else:
                return (self.get_female_cousin(firstRel-1),common)
    
#-------------------------------------------------------------------------
#
# Register this class with the Plugins system 
#
#-------------------------------------------------------------------------
register_relcalc(RelationshipCalculator,
    ["de","DE","de_DE","deutsch","Deutsch","de_DE.UTF8","de_DE@euro","de_DE.UTF8@euro",
            "german","German", "de_DE.UTF-8", "de_DE.utf-8", "de_DE.utf8"])
