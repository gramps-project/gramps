# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009-2010  Andrew I Baznikin
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

# Written by Bernard Banko, inspired from rel_ru.py by Alex Roitman.
"""
Slovenian-specific definitions of relationships
"""
#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

from gramps.gen.lib import Person
import gramps.gen.relationship

#-------------------------------------------------------------------------

_ancestors = [ u"", u"starš", u"stari starš", u"prastari starš" ]
_fathers = [ u"", u"oče", u"ded", u"praded", u"prapraded" ]
_mothers = [ u"", u"mati", u"babica", u"prababica", u"praprababica" ]
_descendants = [
  u"", u"otrok", u"vnuk(inja)", u"pravnuk(inja)", u"prapravnuk(inja)" ]
_sons = [ u"", u"sin", u"vnuk", u"pravnuk", u"prapravnuk" ]
_daughters = [ u"", u"hči", u"vnukinja", u"pravnukinja", u"prapravnukinja" ]
_maleCousins = [ u"", u"brat", u"bratranec", u"mali bratranec" ]
_femaleCousins = [ u"", u"sestra", u"sestrična", u"mala sestrična" ]
_someCousins = [ u"", u"brat ali sestra", u"bratranec ali sestrična",
  u"mali bratranec ali mala sestrična" ]
_aunts = [ u"", u"teta", u"stara teta", u"prateta", u"praprateta" ]
_uncles = [ u"", u"stric", u"stari stric", u"prastric", u"praprastric" ]  
_nieces = [ u"", u"nečakinja", u"pranečakinja", u"prapranečakinja" ]
_nephews = [ u"", u"nečak", u"pranečak", u"prapranečak" ]

#plural
_children = [ u"", u"otroci", u"vnuki", u"pravnuki", u"prapravnuki" ]
_parents = [ u"", u"starši", u"stari starši", u"prastarši", u"praprastarši" ]
_siblings = [ u"", u"sorojenci", u"strici", u"stari strici", u"prastrici",
  u"praprastrici" ]
_neph_niec = [ u"", u"nečaki", u"pranečaki", u"prapranečaki" ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class RelationshipCalculator(gramps.gen.relationship.RelationshipCalculator):
  """
  RelationshipCalculator Class
  """

  def __init__(self):
    gramps.gen.relationship.RelationshipCalculator.__init__(self)

  def getAncestor(self, level):
    if level > len(_ancestors)-1:
      return u"%s-krat-pra-prednik" % (level-2)
    else:
      return _ancestors[level]
      
  def getFather(self, level):
    if level > len(_fathers)-1:
      return u"%s-krat-pra-ded" % (level-2)
    else:
      return _fathers[level]
      
  def getMother(self, level):
    if level > len(_mothers)-1:
      return u"%s-krat-pra-babica" % (level-2)
    else:
      return _mothers[level]
      
  def getSon(self, level):
    if level > len(_sons)-1:
      return u"%s-krat-pra-vnuk" % (level-2)
    else:
      return _sons[level]
      
  def getDaughter(self, level):
    if level > len(_daughters)-1:
      return u"%s-krat-pra-vnukinja" % (level-2)
    else:
      return _daughters[level]
      
  def getDescendant(self, level):
    if level > len(_descendants)-1:
      return u"%s-krat-pra-vnuk(inja)" % (level-2)
    else:
      return _descendants[level]
      
  def getMaleCousin(self, level):
    if level > len(_maleCousins)-1:
      return u"bratranec v %s. kolenu" % (level*2)
    else:
      return _maleCousins[level]

  def getFemaleCousin(self, level):
    if level > len(_femaleCousins)-1:
      return u"sestrična v %s. kolenu" % (level*2)
    else:
      return _femaleCousins[level]

  def getSomeCousin(self, level):
    if level > len(_someCousins)-1:
      return u"bratranec ali sestrična v %s. kolenu" % (level*2)
    else:
      return _someCousins[level]
      
  def getSuffix(self, distance, level):
    # distance-level = 2Gb <=> Gb=1
    if distance-level == 2 or distance < 6:
      return u""
    else:
      return u" v %s. kolenu" % (distance)
      
  def getAunt(self, distance, level):
    if distance == 5 and level == 1:
      return u"mala teta"
    elif level > len(_aunts)-1:
      return u"%s-krat-pra-teta%s" % (level-2, self.getSuffix(distance, level))
    else:
      return u"%s%s" % (_aunts[level], self.getSuffix(distance, level))
      
  def getUncle(self, distance, level):
    if distance == 5 and level == 1:
      return u"mali stric"
    elif level > len(_uncles)-1:
      return u"%s-krat-pra-stric%s" % (level-2, self.getSuffix(distance, level))
    else:
      return u"%s%s" % (_uncles[level], self.getSuffix(distance, level))

  def getNiece(self, distance, level):
    if distance == 5 and level == 1:
      return u"mala nečakinja"
    elif level > len(_nieces)-1:
      return u"%s-krat-pra-nečakinja%s" % (level-1, self.getSuffix(distance, level))
    else:
      return u"%s%s" % (_nieces[level], self.getSuffix(distance, level))
      
  def getNephew(self, distance, level):
    if distance == 5 and level == 1:
      return u"mali nečak"
    elif level > len(_nephews)-1:
      return u"%s-krat-pra-nečak%s" % (level-1, self.getSuffix(distance, level))
    else:
      return u"%s%s" % (_nephews[level], self.getSuffix(distance, level))
  
  def get_single_relationship_string(
    self, Ga, Gb, gender_a, gender_b, reltocommon_a, reltocommon_b,
    only_birth=True, in_law_a=False, in_law_b=False):
    """
        Provide a string that describes the relationsip between a person, and
        another person. E.g. "grandparent" or "child".
        To be used as: 'person b is the grandparent of a', this will 
            be in translation string :
                            'person b is the %(relation)s of a'
            Note that languages with gender should add 'the' inside the 
            translation, so eg in french:
                            'person b est %(relation)s de a'
            where relation will be here: le grandparent
        
        Ga and Gb can be used to mathematically calculate the relationship.
        See the Wikipedia entry for more information:
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions
    """        
    if Gb == 0:
      if Ga == 0: rel_str = "ista oseba"
      elif gender_b == Person.MALE:
        rel_str = (self.getFather(Ga))
      elif gender_b == Person.FEMALE: 
        rel_str = (self.getMother(Ga))
      else:
        rel_str = (self.getAncestor(Ga))
    elif Ga == 0:
      if gender_b == Person.MALE:
        rel_str = (self.getSon(Gb))
      elif gender_b == Person.FEMALE: 
        rel_str = (self.getDaughter(Gb))
      else:
        rel_str = (self.getDescendant(Gb))
    elif Ga == Gb:
      if gender_b == Person.MALE:
        rel_str = (self.getMaleCousin(Gb))
      elif gender_b == Person.FEMALE:
        rel_str = (self.getFemaleCousin(Gb))
      else:
        rel_str = (self.getSomeCousin(Gb))
    elif Ga > Gb:
      if gender_b == Person.FEMALE:
        rel_str = (self.getAunt(Ga+Gb, Ga-Gb))
      else:
        rel_str = (self.getUncle(Ga+Gb, Ga-Gb)) # we'll use male for unknown sex
    else: #Ga < Gb
      if gender_b == Person.FEMALE:
        rel_str = (self.getNiece(Ga+Gb, Gb-Ga))
      else:
        rel_str = (self.getNephew(Ga+Gb, Gb-Ga)) # we'll use male for unknown sex
    return rel_str
    

  def get_sibling_relationship_string(self, sib_type, gender_a, gender_b, 
                                        in_law_a=False, in_law_b=False):
    """ Determine the string giving the relation between two siblings of
        type sib_type.
        Eg: b is the brother of a
          Here 'brother' is the string we need to determine
          This method gives more details about siblings than 
          get_single_relationship_string can do.
          DON'T TRANSLATE THIS PROCEDURE IF LOGIC IS EQUAL IN YOUR LANGUAGE,
          AND SAME METHODS EXIST (get_uncle, get_aunt, get_sibling
    """    
    gender = gender_b #we don't need gender_a
    inlaw = in_law_a or in_law_b
    if sib_type == self.HALF_SIB_MOTHER or sib_type == self.HALF_SIB_FATHER:
      prefix = u"pol"
    else:
      prefix = u""
      
    if sib_type < self.STEP_SIB:
    # ie. NORM_SIB or one of HALF_SIBs
      if not inlaw:
        if gender == Person.MALE:
          rel_str = u"%sbrat" % (prefix)
        elif gender == Person.FEMALE:
          rel_str = u"%ssestra" % (prefix)
        else:
          rel_str = u"%sbrat ali %ssestra" % (prefix, prefix)
      else:
        if gender == Person.MALE:
          rel_str = u"%ssvak" % (prefix)
        elif gender == Person.FEMALE:
          rel_str = u"%ssvakinja" % (prefix)
        else:
          rel_str = u"%ssvak ali %ssvakinja" % (prefix, prefix)
    else:
      rel_str = u""
    return rel_str

  
  def get_plural_relationship_string(
    self, Ga, Gb, reltocommon_a='', reltocommon_b='', only_birth=True,
    in_law_a=False, in_law_b=False):
    
    distance = Ga+Gb
    rel_str = u"sorodniki v %s. kolenu" % (distance)
    if Ga == 0:
    # These are descendants
      if Gb < len(_children):
        rel_str = _children[Gb]
      else:
        rel_str = u"%s-krat-pra-vnuki" % (Gb-2)
    elif Gb == 0:
    # These are parents/grand parents
      if Ga < len(_parents):
        rel_str = _parents[Ga]
      else:
        rel_str = u"%s-krat-pra-starši" % (Ga-2)
    elif Gb == 1:
    # These are siblings/aunts/uncles
      if Ga < len(_siblings):
        rel_str = _siblings[Ga]
      else:
        rel_str = u"%s-krat-pra-strici" % (Ga-2)
    elif Ga == 1:
    # These are nieces/nephews
      if Gb < len(_neph_niec):
        rel_str = _neph_niec[Gb]
      else:
        rel_str = u"%s-krat-pra-nečaki" % (Gb-1)
    elif Ga == Gb:
    # These are cousins in the same generation
      if Ga == 2:
        rel_str = u"bratranci"
      elif Ga == 3:
        rel_str = u"mali bratranci"
      else:
        rel_str = u"bratranci v %s. kolenu" % (distance)
    elif Ga > Gb:
    # These are cousins in different generations with the second person 
    # being in a higher generation from the common ancestor than the 
    # first person.
      level = Ga - Gb
      if distance == 5:
        rel_str = u"mali strici"
      elif level < len(_siblings)-1:
        # len-1 and level+1 to skip the siblings in uncles' levels
        rel_str = u"%s v %s. kolenu" % (_siblings[level+1], distance)
      else:
        rel_str = u"%s-krat-pra-strici v %s. kolenu" % (level-2, distance)
    else: #Gb > Ga:
    # These are cousins in different generations with the second person 
    # being in a lower generation from the common ancestor than the 
    # first person.
      level = Gb - Ga
      if distance == 5:
        rel_str = u"mali nečaki"
      elif level < len(_neph_niec):
        rel_str = u"%s v %s. kolenu" % (_neph_niec[level], distance)
      else:
        rel_str = u"%s-krat-pra-nečaki v %s. kolenu" % (level-1, distance) 
    if in_law_b == True:
      rel_str = "zakonci, ki jih imajo %s" % rel_str
    return rel_str

if __name__ == "__main__":
  """TRANSLATORS, copy this if statement at the bottom of your 
      rel_xx.py module, and test your work with:
      python src/plugins/rel/rel_xx.py
  """
  from gramps.gen.relationship import test
  RC = RelationshipCalculator()
  test(RC, True)
#  
#from PluginMgr import register_relcalc
#    register_relcalc(RelationshipCalculatorClass,["sl","sl_SI","sl-SI","slovenian","Slovenian","slovenščina"])
