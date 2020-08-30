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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
"""
Classes for relationships.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import logging

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .lib import Person, ChildRefType, EventType, FamilyRelType
from .plug import PluginRegister, BasePluginManager
from .const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

MALE = Person.MALE
FEMALE = Person.FEMALE
UNKNOWN = Person.UNKNOWN

LOG = logging.getLogger("gen.relationship")
LOG.addHandler(logging.StreamHandler())

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

_LEVEL_NAME = ["", "first", "second", "third", "fourth", "fifth", "sixth",
               "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
               "thirteenth", "fourteenth", "fifteenth", "sixteenth",
               "seventeenth", "eighteenth", "nineteenth", "twentieth",
               "twenty-first", "twenty-second", "twenty-third", "twenty-fourth",
               "twenty-fifth", "twenty-sixth", "twenty-seventh", "twenty-eighth",
               "twenty-ninth", "thirtieth", "thirty-first", "thirty-second",
               "thirty-third", "thirty-fourth", "thirty-fifth", "thirty-sixth",
               "thirty-seventh", "thirty-eighth", "thirty-ninth", "fortieth",
               "forty-first", "forty-second", "forty-third", "forty-fourth",
               "forty-fifth", "forty-sixth", "forty-seventh", "forty-eighth",
               "forty-ninth", "fiftieth" ]

_REMOVED_LEVEL = ["", " once removed", " twice removed",
                  " three times removed",
                  " four times removed", " five times removed",
                  " six times removed",
                  " seven times removed", " eight times removed",
                  " nine times removed",
                  " ten times removed", " eleven times removed",
                  " twelve times removed",
                  " thirteen times removed", " fourteen times removed",
                  " fifteen times removed",
                  " sixteen times removed", " seventeen times removed",
                  " eighteen times removed",
                  " nineteen times removed", " twenty times removed",
                  " twenty-one times removed", " twenty-two times removed",
                  " twenty-three times removed", " twenty-four times removed",
                  " twenty-five times removed", " twenty-six times removed",
                  " twenty-seven times removed", " twenty-eight times removed",
                  " twenty-nine times removed", " thirty times removed",
                  " thirty-one times removed", " thirty-two times removed",
                  " thirty-three times removed", " thirty-four times removed",
                  " thirty-five times removed", " thirty-six times removed",
                  " thirty-seven times removed", " thirty-eight times removed",
                  " thirty-nine times removed", " forty times removed",
                  " forty-one times removed", " forty-two times removed",
                  " forty-three times removed", " forty-four times removed",
                  " forty-five times removed", " forty-six times removed",
                  " forty-seven times removed", " forty-eight times removed",
                  " forty-nine times removed", " fifty times removed", ]

_PARENTS_LEVEL = ["", "parents", "grandparents", "great grandparents",
                  "second great grandparents",
                  "third great grandparents",
                  "fourth great grandparents",
                  "fifth great grandparents",
                  "sixth great grandparents",
                  "seventh great grandparents",
                  "eighth great grandparents",
                  "ninth great grandparents",
                  "tenth great grandparents",
                  "eleventh great grandparents",
                  "twelfth great grandparents",
                  "thirteenth great grandparents",
                  "fourteenth great grandparents",
                  "fifteenth great grandparents",
                  "sixteenth great grandparents",
                  "seventeenth great grandparents",
                  "eighteenth great grandparents",
                  "nineteenth great grandparents",
                  "twentieth great grandparents",
                  "twenty-first great grandparents",
                  "twenty-second great grandparents",
                  "twenty-third great grandparents",
                  "twenty-fourth great grandparents",
                  "twenty-fifth great grandparents",
                  "twenty-sixth great grandparents",
                  "twenty-seventh great grandparents",
                  "twenty-eighth great grandparents",
                  "twenty-ninth great grandparents",
                  "thirtieth great grandparents",
                  "thirty-first great grandparents",
                  "thirty-second great grandparents",
                  "thirty-third great grandparents",
                  "thirty-fourth great grandparents",
                  "thirty-fifth great grandparents",
                  "thirty-sixth great grandparents",
                  "thirty-seventh great grandparents",
                  "thirty-eighth great grandparents",
                  "thirty-ninth great grandparents",
                  "fortieth great grandparents",
                  "forty-first great grandparents",
                  "forty-second great grandparents",
                  "forty-third great grandparents",
                  "forty-fourth great grandparents",
                  "forty-fifth great grandparents",
                  "forty-sixth great grandparents",
                  "forty-seventh great grandparents",
                  "forty-eighth great grandparents",
                  "forty-ninth great grandparents",
                  "fiftieth great grandparents", ]

_FATHER_LEVEL = ["", "%(step)sfather%(inlaw)s", "%(step)sgrandfather%(inlaw)s",
                 "great %(step)sgrandfather%(inlaw)s",
                 "second great %(step)sgrandfather%(inlaw)s",
                 "third great %(step)sgrandfather%(inlaw)s",
                 "fourth great %(step)sgrandfather%(inlaw)s",
                 "fifth great %(step)sgrandfather%(inlaw)s",
                 "sixth great %(step)sgrandfather%(inlaw)s",
                 "seventh great %(step)sgrandfather%(inlaw)s",
                 "eighth great %(step)sgrandfather%(inlaw)s",
                 "ninth great %(step)sgrandfather%(inlaw)s",
                 "tenth great %(step)sgrandfather%(inlaw)s",
                 "eleventh great %(step)sgrandfather%(inlaw)s",
                 "twelfth great %(step)sgrandfather%(inlaw)s",
                 "thirteenth great %(step)sgrandfather%(inlaw)s",
                 "fourteenth great %(step)sgrandfather%(inlaw)s",
                 "fifteenth great %(step)sgrandfather%(inlaw)s",
                 "sixteenth great %(step)sgrandfather%(inlaw)s",
                 "seventeenth great %(step)sgrandfather%(inlaw)s",
                 "eighteenth great %(step)sgrandfather%(inlaw)s",
                 "nineteenth great %(step)sgrandfather%(inlaw)s",
                 "twentieth great %(step)sgrandfather%(inlaw)s",
                 "twenty-first great %(step)sgrandfather%(inlaw)s",
                 "twenty-second great %(step)sgrandfather%(inlaw)s",
                 "twenty-third great %(step)sgrandfather%(inlaw)s",
                 "twenty-fourth great %(step)sgrandfather%(inlaw)s",
                 "twenty-fifth great %(step)sgrandfather%(inlaw)s",
                 "twenty-sixth great %(step)sgrandfather%(inlaw)s",
                 "twenty-seventh great %(step)sgrandfather%(inlaw)s",
                 "twenty-eighth great %(step)sgrandfather%(inlaw)s",
                 "twenty-ninth great %(step)sgrandfather%(inlaw)s",
                 "thirtieth great %(step)sgrandfather%(inlaw)s",
                 "thirty-first great %(step)sgrandfather%(inlaw)s",
                 "thirty-second great %(step)sgrandfather%(inlaw)s",
                 "thirty-third great %(step)sgrandfather%(inlaw)s",
                 "thirty-fourth great %(step)sgrandfather%(inlaw)s",
                 "thirty-fifth great %(step)sgrandfather%(inlaw)s",
                 "thirty-sixth great %(step)sgrandfather%(inlaw)s",
                 "thirty-seventh great %(step)sgrandfather%(inlaw)s",
                 "thirty-eighth great %(step)sgrandfather%(inlaw)s",
                 "thirty-ninth great %(step)sgrandfather%(inlaw)s",
                 "fourtieth great %(step)sgrandfather%(inlaw)s",
                 "forty-first great %(step)sgrandfather%(inlaw)s",
                 "forty-second great %(step)sgrandfather%(inlaw)s",
                 "forty-third great %(step)sgrandfather%(inlaw)s",
                 "forty-fourth great %(step)sgrandfather%(inlaw)s",
                 "forty-fifth great %(step)sgrandfather%(inlaw)s",
                 "forty-sixth great %(step)sgrandfather%(inlaw)s",
                 "forty-seventh great %(step)sgrandfather%(inlaw)s",
                 "forty-eighth great %(step)sgrandfather%(inlaw)s",
                 "forty-ninth great %(step)sgrandfather%(inlaw)s",
                 "fiftieth great %(step)sgrandfather%(inlaw)s", ]

_MOTHER_LEVEL = ["", "%(step)smother%(inlaw)s",
                 "%(step)sgrandmother%(inlaw)s",
                 "great %(step)sgrandmother%(inlaw)s",
                 "second great %(step)sgrandmother%(inlaw)s",
                 "third great %(step)sgrandmother%(inlaw)s",
                 "fourth great %(step)sgrandmother%(inlaw)s",
                 "fifth great %(step)sgrandmother%(inlaw)s",
                 "sixth great %(step)sgrandmother%(inlaw)s",
                 "seventh great %(step)sgrandmother%(inlaw)s",
                 "eighth great %(step)sgrandmother%(inlaw)s",
                 "ninth great %(step)sgrandmother%(inlaw)s",
                 "tenth great %(step)sgrandmother%(inlaw)s",
                 "eleventh great %(step)sgrandmother%(inlaw)s",
                 "twelfth great %(step)sgrandmother%(inlaw)s",
                 "thirteenth great %(step)sgrandmother%(inlaw)s",
                 "fourteenth great %(step)sgrandmother%(inlaw)s",
                 "fifteenth great %(step)sgrandmother%(inlaw)s",
                 "sixteenth great %(step)sgrandmother%(inlaw)s",
                 "seventeenth great %(step)sgrandmother%(inlaw)s",
                 "eighteenth great %(step)sgrandmother%(inlaw)s",
                 "nineteenth great %(step)sgrandmother%(inlaw)s",
                 "twentieth great %(step)sgrandmother%(inlaw)s",
                 "twenty-first great %(step)sgrandmother%(inlaw)s",
                 "twenty-second great %(step)sgrandmother%(inlaw)s",
                 "twenty-third great %(step)sgrandmother%(inlaw)s",
                 "twenty-fourth great %(step)sgrandmother%(inlaw)s",
                 "twenty-fifth great %(step)sgrandmother%(inlaw)s",
                 "twenty-sixth great %(step)sgrandmother%(inlaw)s",
                 "twenty-seventh great %(step)sgrandmother%(inlaw)s",
                 "twenty-eighth great %(step)sgrandmother%(inlaw)s",
                 "twenty-ninth great %(step)sgrandmother%(inlaw)s",
                 "thirtieth great %(step)sgrandmother%(inlaw)s",
                 "thirty-first great %(step)sgrandmother%(inlaw)s",
                 "thirty-second great %(step)sgrandmother%(inlaw)s",
                 "thirty-third great %(step)sgrandmother%(inlaw)s",
                 "thirty-forth great %(step)sgrandmother%(inlaw)s",
                 "thirty-fifth great %(step)sgrandmother%(inlaw)s",
                 "thirty-sixth great %(step)sgrandmother%(inlaw)s",
                 "thirty-seventh great %(step)sgrandmother%(inlaw)s",
                 "thirty-eighth great %(step)sgrandmother%(inlaw)s",
                 "thirty-ninth great %(step)sgrandmother%(inlaw)s",
                 "fourtieth great %(step)sgrandmother%(inlaw)s",
                 "forty-first great %(step)sgrandmother%(inlaw)s",
                 "forty-second great %(step)sgrandmother%(inlaw)s",
                 "forty-third great %(step)sgrandmother%(inlaw)s",
                 "forty-fourth great %(step)sgrandmother%(inlaw)s",
                 "forty-fifth great %(step)sgrandmother%(inlaw)s",
                 "forty-sixth great %(step)sgrandmother%(inlaw)s",
                 "forty-seventh great %(step)sgrandmother%(inlaw)s",
                 "forty-eighth great %(step)sgrandmother%(inlaw)s",
                 "forty-ninth great %(step)sgrandmother%(inlaw)s",
                 "fiftieth great %(step)sgrandmother%(inlaw)s", ]

_SON_LEVEL = ["", "%(step)sson%(inlaw)s", "%(step)sgrandson%(inlaw)s",
              "great %(step)sgrandson%(inlaw)s",
              "second great %(step)sgrandson%(inlaw)s",
              "third great %(step)sgrandson%(inlaw)s",
              "fourth great %(step)sgrandson%(inlaw)s",
              "fifth great %(step)sgrandson%(inlaw)s",
              "sixth great %(step)sgrandson%(inlaw)s",
              "seventh great %(step)sgrandson%(inlaw)s",
              "eighth great %(step)sgrandson%(inlaw)s",
              "ninth great %(step)sgrandson%(inlaw)s",
              "tenth great %(step)sgrandson%(inlaw)s",
              "eleventh great %(step)sgrandson%(inlaw)s",
              "twelfth great %(step)sgrandson%(inlaw)s",
              "thirteenth great %(step)sgrandson%(inlaw)s",
              "fourteenth great %(step)sgrandson%(inlaw)s",
              "fifteenth great %(step)sgrandson%(inlaw)s",
              "sixteenth great %(step)sgrandson%(inlaw)s",
              "seventeenth great %(step)sgrandson%(inlaw)s",
              "eighteenth great %(step)sgrandson%(inlaw)s",
              "nineteenth great %(step)sgrandson%(inlaw)s",
              "twentieth great %(step)sgrandson%(inlaw)s",
              "twenty-first great %(step)sgrandson%(inlaw)s",
              "twenty-second great %(step)sgrandson%(inlaw)s",
              "twenty-third great %(step)sgrandson%(inlaw)s",
              "twenty-fourth great %(step)sgrandson%(inlaw)s",
              "twenty-fifth great %(step)sgrandson%(inlaw)s",
              "twenty-sixth great %(step)sgrandson%(inlaw)s",
              "twenty-seventh great %(step)sgrandson%(inlaw)s",
              "twenty-eighth great %(step)sgrandson%(inlaw)s",
              "twenty-ninth great %(step)sgrandson%(inlaw)s",
              "thirtieth great %(step)sgrandson%(inlaw)s",
              "thirty-first great %(step)sgrandson%(inlaw)s",
              "thirty-second great %(step)sgrandson%(inlaw)s",
              "thirty-third great %(step)sgrandson%(inlaw)s",
              "thirty-forth great %(step)sgrandson%(inlaw)s",
              "thirty-fifth great %(step)sgrandson%(inlaw)s",
              "thirty-sixth great %(step)sgrandson%(inlaw)s",
              "thirty-seventh great %(step)sgrandson%(inlaw)s",
              "thirty-eighth great %(step)sgrandson%(inlaw)s",
              "thirty-ninth great %(step)sgrandson%(inlaw)s",
              "fourtieth great %(step)sgrandson%(inlaw)s",
              "forty-first great %(step)sgrandson%(inlaw)s",
              "forty-second great %(step)sgrandson%(inlaw)s",
              "forty-third great %(step)sgrandson%(inlaw)s",
              "forty-fourth great %(step)sgrandson%(inlaw)s",
              "forty-fifth great %(step)sgrandson%(inlaw)s",
              "forty-sixth great %(step)sgrandson%(inlaw)s",
              "forty-seventh great %(step)sgrandson%(inlaw)s",
              "forty-eighth great %(step)sgrandson%(inlaw)s",
              "forty-ninth great %(step)sgrandson%(inlaw)s",
              "fiftieth great %(step)sgrandson%(inlaw)s", ]

_DAUGHTER_LEVEL = ["", "%(step)sdaughter%(inlaw)s",
                   "%(step)sgranddaughter%(inlaw)s",
                   "great %(step)sgranddaughter%(inlaw)s",
                   "second great %(step)sgranddaughter%(inlaw)s",
                   "third great %(step)sgranddaughter%(inlaw)s",
                   "fourth great %(step)sgranddaughter%(inlaw)s",
                   "fifth great %(step)sgranddaughter%(inlaw)s",
                   "sixth great %(step)sgranddaughter%(inlaw)s",
                   "seventh great %(step)sgranddaughter%(inlaw)s",
                   "eighth great %(step)sgranddaughter%(inlaw)s",
                   "ninth great %(step)sgranddaughter%(inlaw)s",
                   "tenth great %(step)sgranddaughter%(inlaw)s",
                   "eleventh great %(step)sgranddaughter%(inlaw)s",
                   "twelfth great %(step)sgranddaughter%(inlaw)s",
                   "thirteenth great %(step)sgranddaughter%(inlaw)s",
                   "fourteenth great %(step)sgranddaughter%(inlaw)s",
                   "fifteenth great %(step)sgranddaughter%(inlaw)s",
                   "sixteenth great %(step)sgranddaughter%(inlaw)s",
                   "seventeenth great %(step)sgranddaughter%(inlaw)s",
                   "eighteenth great %(step)sgranddaughter%(inlaw)s",
                   "nineteenth great %(step)sgranddaughter%(inlaw)s",
                   "twentieth great %(step)sgranddaughter%(inlaw)s",
                   "twenty-first great %(step)sgranddaughter%(inlaw)s",
                   "twenty-second great %(step)sgranddaughter%(inlaw)s",
                   "twenty-third great %(step)sgranddaughter%(inlaw)s",
                   "twenty-fourth great %(step)sgranddaughter%(inlaw)s",
                   "twenty-fifth great %(step)sgranddaughter%(inlaw)s",
                   "twenty-sixth great %(step)sgranddaughter%(inlaw)s",
                   "twenty-seventh great %(step)sgranddaughter%(inlaw)s",
                   "twenty-eighth great %(step)sgranddaughter%(inlaw)s",
                   "twenty-ninth great %(step)sgranddaughter%(inlaw)s",
                   "thirtieth great %(step)sgranddaughter%(inlaw)s",
                   "thirty-first great %(step)sgranddaughter%(inlaw)s",
                   "thirty-second great %(step)sgranddaughter%(inlaw)s",
                   "thirty-third great %(step)sgranddaughter%(inlaw)s",
                   "thirty-forth great %(step)sgranddaughter%(inlaw)s",
                   "thirty-fifth great %(step)sgranddaughter%(inlaw)s",
                   "thirty-sixth great %(step)sgranddaughter%(inlaw)s",
                   "thirty-seventh great %(step)sgranddaughter%(inlaw)s",
                   "thirty-eighth great %(step)sgranddaughter%(inlaw)s",
                   "thirty-ninth great %(step)sgranddaughter%(inlaw)s",
                   "fourtieth great %(step)sgranddaughter%(inlaw)s",
                   "forty-first great %(step)sgranddaughter%(inlaw)s",
                   "forty-second great %(step)sgranddaughter%(inlaw)s",
                   "forty-third great %(step)sgranddaughter%(inlaw)s",
                   "forty-fourth great %(step)sgranddaughter%(inlaw)s",
                   "forty-fifth great %(step)sgranddaughter%(inlaw)s",
                   "forty-sixth great %(step)sgranddaughter%(inlaw)s",
                   "forty-seventh great %(step)sgranddaughter%(inlaw)s",
                   "forty-eighth great %(step)sgranddaughter%(inlaw)s",
                   "forty-ninth great %(step)sgranddaughter%(inlaw)s",
                   "fiftieth great %(step)sgranddaughter%(inlaw)s", ]

_SISTER_LEVEL = ["", "%(step)ssister%(inlaw)s", "%(step)saunt%(inlaw)s",
                 "%(step)sgrandaunt%(inlaw)s",
                 "great %(step)sgrandaunt%(inlaw)s",
                 "second great %(step)sgrandaunt%(inlaw)s",
                 "third great %(step)sgrandaunt%(inlaw)s",
                 "fourth great %(step)sgrandaunt%(inlaw)s",
                 "fifth great %(step)sgrandaunt%(inlaw)s",
                 "sixth great %(step)sgrandaunt%(inlaw)s",
                 "seventh great %(step)sgrandaunt%(inlaw)s",
                 "eighth great %(step)sgrandaunt%(inlaw)s",
                 "ninth great %(step)sgrandaunt%(inlaw)s",
                 "tenth great %(step)sgrandaunt%(inlaw)s",
                 "eleventh great %(step)sgrandaunt%(inlaw)s",
                 "twelfth great %(step)sgrandaunt%(inlaw)s",
                 "thirteenth great %(step)sgrandaunt%(inlaw)s",
                 "fourteenth great %(step)sgrandaunt%(inlaw)s",
                 "fifteenth great %(step)sgrandaunt%(inlaw)s",
                 "sixteenth great %(step)sgrandaunt%(inlaw)s",
                 "seventeenth great %(step)sgrandaunt%(inlaw)s",
                 "eighteenth great %(step)sgrandaunt%(inlaw)s",
                 "nineteenth great %(step)sgrandaunt%(inlaw)s",
                 "twentieth great %(step)sgrandaunt%(inlaw)s",
                 "twenty-first great %(step)sgrandaunt%(inlaw)s",
                 "twenty-second great %(step)sgrandaunt%(inlaw)s",
                 "twenty-third great %(step)sgrandaunt%(inlaw)s",
                 "twenty-fourth great %(step)sgrandaunt%(inlaw)s",
                 "twenty-fifth great %(step)sgrandaunt%(inlaw)s",
                 "twenty-sixth great %(step)sgrandaunt%(inlaw)s",
                 "twenty-seventh great %(step)sgrandaunt%(inlaw)s",
                 "twenty-eighth great %(step)sgrandaunt%(inlaw)s",
                 "twenty-ninth great %(step)sgrandaunt%(inlaw)s",
                 "thirtieth great %(step)sgrandaunt%(inlaw)s",
                 "thirty-first great %(step)sgrandaunt%(inlaw)s",
                 "thirty-second great %(step)sgrandaunt%(inlaw)s",
                 "thirty-third great %(step)sgrandaunt%(inlaw)s",
                 "thirty-forth great %(step)sgrandaunt%(inlaw)s",
                 "thirty-fifth great %(step)sgrandaunt%(inlaw)s",
                 "thirty-sixth great %(step)sgrandaunt%(inlaw)s",
                 "thirty-seventh great %(step)sgrandaunt%(inlaw)s",
                 "thirty-eighth great %(step)sgrandaunt%(inlaw)s",
                 "thirty-ninth great %(step)sgrandaunt%(inlaw)s",
                 "fourtieth great %(step)sgrandaunt%(inlaw)s",
                 "forty-first great %(step)sgrandaunt%(inlaw)s",
                 "forty-second great %(step)sgrandaunt%(inlaw)s",
                 "forty-third great %(step)sgrandaunt%(inlaw)s",
                 "forty-fourth great %(step)sgrandaunt%(inlaw)s",
                 "forty-fifth great %(step)sgrandaunt%(inlaw)s",
                 "forty-sixth great %(step)sgrandaunt%(inlaw)s",
                 "forty-seventh great %(step)sgrandaunt%(inlaw)s",
                 "forty-eighth great %(step)sgrandaunt%(inlaw)s",
                 "forty-ninth great %(step)sgrandaunt%(inlaw)s",
                 "fiftieth great %(step)sgrandaunt%(inlaw)s", ]

_BROTHER_LEVEL = ["", "%(step)sbrother%(inlaw)s", "%(step)suncle%(inlaw)s",
                  "%(step)sgranduncle%(inlaw)s",
                  "great %(step)sgranduncle%(inlaw)s",
                  "second great %(step)sgranduncle%(inlaw)s",
                  "third great %(step)sgranduncle%(inlaw)s",
                  "fourth great %(step)sgranduncle%(inlaw)s",
                  "fifth great %(step)sgranduncle%(inlaw)s",
                  "sixth great %(step)sgranduncle%(inlaw)s",
                  "seventh great %(step)sgranduncle%(inlaw)s",
                  "eighth great %(step)sgranduncle%(inlaw)s",
                  "ninth great %(step)sgranduncle%(inlaw)s",
                  "tenth great %(step)sgranduncle%(inlaw)s",
                  "eleventh great %(step)sgranduncle%(inlaw)s",
                  "twelfth great %(step)sgranduncle%(inlaw)s",
                  "thirteenth great %(step)sgranduncle%(inlaw)s",
                  "fourteenth great %(step)sgranduncle%(inlaw)s",
                  "fifteenth great %(step)sgranduncle%(inlaw)s",
                  "sixteenth great %(step)sgranduncle%(inlaw)s",
                  "seventeenth great %(step)sgranduncle%(inlaw)s",
                  "eighteenth great %(step)sgranduncle%(inlaw)s",
                  "nineteenth great %(step)sgranduncle%(inlaw)s",
                  "twentieth great %(step)sgranduncle%(inlaw)s",
                  "twenty-first great %(step)sgranduncle%(inlaw)s",
                  "twenty-second great %(step)sgranduncle%(inlaw)s",
                  "twenty-third great %(step)sgranduncle%(inlaw)s",
                  "twenty-fourth great %(step)sgranduncle%(inlaw)s",
                  "twenty-fifth great %(step)sgranduncle%(inlaw)s",
                  "twenty-sixth great %(step)sgranduncle%(inlaw)s",
                  "twenty-seventh great %(step)sgranduncle%(inlaw)s",
                  "twenty-eighth great %(step)sgranduncle%(inlaw)s",
                  "twenty-ninth great %(step)sgranduncle%(inlaw)s",
                  "thirtieth great %(step)sgranduncle%(inlaw)s",
                  "thirty-first great %(step)sgranduncle%(inlaw)s",
                  "thirty-second great %(step)sgranduncle%(inlaw)s",
                  "thirty-third great %(step)sgranduncle%(inlaw)s",
                  "thirty-fourth great %(step)sgranduncle%(inlaw)s",
                  "thirty-fifth great %(step)sgranduncle%(inlaw)s",
                  "thirty-sixth great %(step)sgranduncle%(inlaw)s",
                  "thirty-seventh great %(step)sgranduncle%(inlaw)s",
                  "thirty-eighth great %(step)sgranduncle%(inlaw)s",
                  "thirty-ninth great %(step)sgranduncle%(inlaw)s",
                  "fourtieth great %(step)sgranduncle%(inlaw)s",
                  "forty-first great %(step)sgranduncle%(inlaw)s",
                  "forty-second great %(step)sgranduncle%(inlaw)s",
                  "forty-third great %(step)sgranduncle%(inlaw)s",
                  "forty-fourth great %(step)sgranduncle%(inlaw)s",
                  "forty-fifth great %(step)sgranduncle%(inlaw)s",
                  "forty-sixth great %(step)sgranduncle%(inlaw)s",
                  "forty-seventh great %(step)sgranduncle%(inlaw)s",
                  "forty-eighth great %(step)sgranduncle%(inlaw)s",
                  "forty-ninth great %(step)sgranduncle%(inlaw)s",
                  "fiftieth great %(step)sgranduncle%(inlaw)s", ]

_NEPHEW_LEVEL = ["", "%(step)snephew%(inlaw)s", "%(step)sgrandnephew%(inlaw)s",
                 "great %(step)sgrandnephew%(inlaw)s",
                 "second great %(step)sgrandnephew%(inlaw)s",
                 "third great %(step)sgrandnephew%(inlaw)s",
                 "fourth great %(step)sgrandnephew%(inlaw)s",
                 "fifth great %(step)sgrandnephew%(inlaw)s",
                 "sixth great %(step)sgrandnephew%(inlaw)s",
                 "seventh great %(step)sgrandnephew%(inlaw)s",
                 "eighth great %(step)sgrandnephew%(inlaw)s",
                 "ninth great %(step)sgrandnephew%(inlaw)s",
                 "tenth great %(step)sgrandnephew%(inlaw)s",
                 "eleventh great %(step)sgrandnephew%(inlaw)s",
                 "twelfth great %(step)sgrandnephew%(inlaw)s",
                 "thirteenth great %(step)sgrandnephew%(inlaw)s",
                 "fourteenth great %(step)sgrandnephew%(inlaw)s",
                 "fifteenth great %(step)sgrandnephew%(inlaw)s",
                 "sixteenth great %(step)sgrandnephew%(inlaw)s",
                 "seventeenth great %(step)sgrandnephew%(inlaw)s",
                 "eighteenth great %(step)sgrandnephew%(inlaw)s",
                 "nineteenth great %(step)sgrandnephew%(inlaw)s",
                 "twentieth great %(step)sgrandnephew%(inlaw)s",
                 "twenty-first great %(step)sgrandnephew%(inlaw)s",
                 "twenty-second great %(step)sgrandnephew%(inlaw)s",
                 "twenty-third great %(step)sgrandnephew%(inlaw)s",
                 "twenty-fourth great %(step)sgrandnephew%(inlaw)s",
                 "twenty-fifth great %(step)sgrandnephew%(inlaw)s",
                 "twenty-sixth great %(step)sgrandnephew%(inlaw)s",
                 "twenty-seventh great %(step)sgrandnephew%(inlaw)s",
                 "twenty-eighth great %(step)sgrandnephew%(inlaw)s",
                 "twenty-ninth great %(step)sgrandnephew%(inlaw)s",
                 "thirtieth great %(step)sgrandnephew%(inlaw)s",
                 "thirty-first great %(step)sgrandnephew%(inlaw)s",
                 "thirty-second great %(step)sgrandnephew%(inlaw)s",
                 "thirty-third great %(step)sgrandnephew%(inlaw)s",
                 "thirty-fourth great %(step)sgrandnephew%(inlaw)s",
                 "thirty-fifth great %(step)sgrandnephew%(inlaw)s",
                 "thirty-sixth great %(step)sgrandnephew%(inlaw)s",
                 "thirty-seventh great %(step)sgrandnephew%(inlaw)s",
                 "thirty-eighth great %(step)sgrandnephew%(inlaw)s",
                 "thirty-ninth great %(step)sgrandnephew%(inlaw)s",
                 "fourtieth great %(step)sgrandnephew%(inlaw)s",
                 "forty-first great %(step)sgrandnephew%(inlaw)s",
                 "forty-second great %(step)sgrandnephew%(inlaw)s",
                 "forty-third great %(step)sgrandnephew%(inlaw)s",
                 "forty-fourth great %(step)sgrandnephew%(inlaw)s",
                 "forty-fifth great %(step)sgrandnephew%(inlaw)s",
                 "forty-sixth great %(step)sgrandnephew%(inlaw)s",
                 "forty-seventh great %(step)sgrandnephew%(inlaw)s",
                 "forty-eighth great %(step)sgrandnephew%(inlaw)s",
                 "forty-ninth great %(step)sgrandnephew%(inlaw)s",
                 "fiftieth great %(step)sgrandnephew%(inlaw)s", ]

_NIECE_LEVEL = ["", "%(step)sniece%(inlaw)s", "%(step)sgrandniece%(inlaw)s",
                "great %(step)sgrandniece%(inlaw)s",
                "second great %(step)sgrandniece%(inlaw)s",
                "third great %(step)sgrandniece%(inlaw)s",
                "fourth great %(step)sgrandniece%(inlaw)s",
                "fifth great %(step)sgrandniece%(inlaw)s",
                "sixth great %(step)sgrandniece%(inlaw)s",
                "seventh great %(step)sgrandniece%(inlaw)s",
                "eighth great %(step)sgrandniece%(inlaw)s",
                "ninth great %(step)sgrandniece%(inlaw)s",
                "tenth great %(step)sgrandniece%(inlaw)s",
                "eleventh great %(step)sgrandniece%(inlaw)s",
                "twelfth great %(step)sgrandniece%(inlaw)s",
                "thirteenth great %(step)sgrandniece%(inlaw)s",
                "fourteenth great %(step)sgrandniece%(inlaw)s",
                "fifteenth great %(step)sgrandniece%(inlaw)s",
                "sixteenth great %(step)sgrandniece%(inlaw)s",
                "seventeenth great %(step)sgrandniece%(inlaw)s",
                "eighteenth great %(step)sgrandniece%(inlaw)s",
                "nineteenth great %(step)sgrandniece%(inlaw)s",
                "twentieth great %(step)sgrandniece%(inlaw)s",
                "twenty-first great %(step)sgrandniece%(inlaw)s",
                "twenty-second great %(step)sgrandniece%(inlaw)s",
                "twenty-third great %(step)sgrandniece%(inlaw)s",
                "twenty-fourth great %(step)sgrandniece%(inlaw)s",
                "twenty-fifth great %(step)sgrandniece%(inlaw)s",
                "twenty-sixth great %(step)sgrandniece%(inlaw)s",
                "twenty-seventh great %(step)sgrandniece%(inlaw)s",
                "twenty-eighth great %(step)sgrandniece%(inlaw)s",
                "twenty-ninth great %(step)sgrandniece%(inlaw)s",
                "thirtieth great %(step)sgrandniece%(inlaw)s",
                "thirty-first great %(step)sgrandniece%(inlaw)s",
                "thirty-second great %(step)sgrandniece%(inlaw)s",
                "thirty-third great %(step)sgrandniece%(inlaw)s",
                "thirty-fourth great %(step)sgrandniece%(inlaw)s",
                "thirty-fifth great %(step)sgrandniece%(inlaw)s",
                "thirty-sixth great %(step)sgrandniece%(inlaw)s",
                "thirty-seventh great %(step)sgrandniece%(inlaw)s",
                "thirty-eighth great %(step)sgrandniece%(inlaw)s",
                "thirty-ninth great %(step)sgrandniece%(inlaw)s",
                "fourtieth great %(step)sgrandniece%(inlaw)s",
                "forty-first great %(step)sgrandniece%(inlaw)s",
                "forty-second great %(step)sgrandniece%(inlaw)s",
                "forty-third great %(step)sgrandniece%(inlaw)s",
                "forty-fourth great %(step)sgrandniece%(inlaw)s",
                "forty-fifth great %(step)sgrandniece%(inlaw)s",
                "forty-sixth great %(step)sgrandniece%(inlaw)s",
                "forty-seventh great %(step)sgrandniece%(inlaw)s",
                "forty-eighth great %(step)sgrandniece%(inlaw)s",
                "forty-ninth great %(step)sgrandniece%(inlaw)s",
                "fiftieth great %(step)sgrandniece%(inlaw)s", ]

_CHILDREN_LEVEL = ["",
                   "children",
                   "grandchildren",
                   "great grandchildren",
                   "second great grandchildren",
                   "third great grandchildren",
                   "fourth great grandchildren",
                   "fifth great grandchildren",
                   "sixth great grandchildren",
                   "seventh great grandchildren",
                   "eighth great grandchildren",
                   "ninth great grandchildren",
                   "tenth great grandchildren",
                   "eleventh great grandchildren",
                   "twelfth great grandchildren",
                   "thirteenth great grandchildren",
                   "fourteenth great grandchildren",
                   "fifteenth great grandchildren",
                   "sixteenth great grandchildren",
                   "seventeenth great grandchildren",
                   "eighteenth great grandchildren",
                   "nineteenth great grandchildren",
                   "twentieth great grandchildren",
                   "twenty-first great grandchildren",
                   "twenty-second great grandchildren",
                   "twenty-third great grandchildren",
                   "twenty-fourth great grandchildren",
                   "twenty-fifth great grandchildren",
                   "twenty-sixth great grandchildren",
                   "twenty-seventh great grandchildren",
                   "twenty-eighth great grandchildren",
                   "twenty-ninth great grandchildren",
                   "thirtieth great grandchildren",
                   "thirty-first great grandchildren",
                   "thirty-second great grandchildren",
                   "thirty-third great grandchildren",
                   "thirty-fourth great grandchildren",
                   "thirty-fifth great grandchildren",
                   "thirty-sixth great grandchildren",
                   "thirty-seventh great grandchildren",
                   "thirty-eighth great grandchildren",
                   "thirty-ninth great grandchildren",
                   "fourtieth great grandchildren",
                   "forty-first great grandchildren",
                   "forty-second great grandchildren",
                   "forty-third great grandchildren",
                   "forty-fourth great grandchildren",
                   "forty-fifth great grandchildren",
                   "forty-sixth great grandchildren",
                   "forty-seventh great grandchildren",
                   "forty-eighth great grandchildren",
                   "forty-ninth great grandchildren",
                   "fiftieth great grandchildren", ]

_SIBLINGS_LEVEL = ["",
                   "siblings",
                   "uncles/aunts",
                   "granduncles/aunts",
                   "great granduncles/aunts",
                   "second great granduncles/aunts",
                   "third great granduncles/aunts",
                   "fourth great granduncles/aunts",
                   "fifth great granduncles/aunts",
                   "sixth great granduncles/aunts",
                   "seventh great granduncles/aunts",
                   "eighth great granduncles/aunts",
                   "ninth great granduncles/aunts",
                   "tenth great granduncles/aunts",
                   "eleventh great granduncles/aunts",
                   "twelfth great granduncles/aunts",
                   "thirteenth great granduncles/aunts",
                   "fourteenth great granduncles/aunts",
                   "fifteenth great granduncles/aunts",
                   "sixteenth great granduncles/aunts",
                   "seventeenth great granduncles/aunts",
                   "eighteenth great granduncles/aunts",
                   "nineteenth great granduncles/aunts",
                   "twentieth great granduncles/aunts",
                   "twenty-first great granduncles/aunts",
                   "twenty-second great granduncles/aunts",
                   "twenty-third great granduncles/aunts",
                   "twenty-fourth great granduncles/aunts",
                   "twenty-fifth great granduncles/aunts",
                   "twenty-sixth great granduncles/aunts",
                   "twenty-seventh great granduncles/aunts",
                   "twenty-eighth great granduncles/aunts",
                   "twenty-ninth great granduncles/aunts",
                   "thirtieth great granduncles/aunts",
                   "thirty-first great granduncles/aunts",
                   "thirty-second great granduncles/aunts",
                   "thirty-third great granduncles/aunts",
                   "thirty-fourth great granduncles/aunts",
                   "thirty-fifth great granduncles/aunts",
                   "thirty-sixth great granduncles/aunts",
                   "thirty-seventh great granduncles/aunts",
                   "thirty-eighth great granduncles/aunts",
                   "thirty-ninth great granduncles/aunts",
                   "fortieth great granduncles/aunts",
                   "forty-first great granduncles/aunts",
                   "forty-second great granduncles/aunts",
                   "forty-third great granduncles/aunts",
                   "forty-fourth great granduncles/aunts",
                   "forty-fifth great granduncles/aunts",
                   "forty-sixth great granduncles/aunts",
                   "forty-seventh great granduncles/aunts",
                   "forty-eighth great granduncles/aunts",
                   "forty-ninth great granduncles/aunts",
                   "fiftienth great granduncles/aunts", ]

_SIBLING_LEVEL = ["",
                  "%(step)ssibling%(inlaw)s",
                  "%(step)suncle/aunt%(inlaw)s",
                  "%(step)sgranduncle/aunt%(inlaw)s",
                  "great %(step)sgranduncle/aunt%(inlaw)s",
                  "second great %(step)sgranduncle/aunt%(inlaw)s",
                  "third great %(step)sgranduncle/aunt%(inlaw)s",
                  "fourth great %(step)sgranduncle/aunt%(inlaw)s",
                  "fifth great %(step)sgranduncle/aunt%(inlaw)s",
                  "sixth great %(step)sgranduncle/aunt%(inlaw)s",
                  "seventh great %(step)sgranduncle/aunt%(inlaw)s",
                  "eighth great %(step)sgranduncle/aunt%(inlaw)s",
                  "ninth great %(step)sgranduncle/aunt%(inlaw)s",
                  "tenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "eleventh great %(step)sgranduncle/aunt%(inlaw)s",
                  "twelfth great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirteenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "fourteenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "fifteenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "sixteenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "seventeenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "eighteenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "nineteenth great %(step)sgranduncle/aunt%(inlaw)s",
                  "twentieth great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-first great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-second great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-third great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-fourth great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-fifth great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-sixth great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-seventh great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-eighth great %(step)sgranduncle/aunt%(inlaw)s",
                  "twenty-ninth great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirtieth great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-first great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-second great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-third great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-fourth great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-fifth great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-sixth great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-seventh great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-eighth great %(step)sgranduncle/aunt%(inlaw)s",
                  "thirty-ninth great %(step)sgranduncle/aunt%(inlaw)s",
                  "fortieth great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-first great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-second great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-third great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-fourth great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-fifth great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-sixth great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-seventh great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-eighth great %(step)sgranduncle/aunt%(inlaw)s",
                  "forty-ninth great %(step)sgranduncle/aunt%(inlaw)s",
                  "fiftieth great %(step)sgranduncle/aunt%(inlaw)s", ]

_NEPHEWS_NIECES_LEVEL = ["",
                         "siblings",
                         "nephews/nieces",
                         "grandnephews/nieces",
                         "great grandnephews/nieces",
                         "second great grandnephews/nieces",
                         "third great grandnephews/nieces",
                         "fourth great grandnephews/nieces",
                         "fifth great grandnephews/nieces",
                         "sixth great grandnephews/nieces",
                         "seventh great grandnephews/nieces",
                         "eighth great grandnephews/nieces",
                         "ninth great grandnephews/nieces",
                         "tenth great grandnephews/nieces",
                         "eleventh great grandnephews/nieces",
                         "twelfth great grandnephews/nieces",
                         "thirteenth great grandnephews/nieces",
                         "fourteenth great grandnephews/nieces",
                         "fifteenth great grandnephews/nieces",
                         "sixteenth great grandnephews/nieces",
                         "seventeenth great grandnephews/nieces",
                         "eighteenth great grandnephews/nieces",
                         "nineteenth great grandnephews/nieces",
                         "twentieth great grandnephews/nieces",
                         "twenty-first great grandnephews/nieces",
                         "twenty-second great grandnephews/nieces",
                         "twenty-third great grandnephews/nieces",
                         "twenty-fourth great grandnephews/nieces",
                         "twenty-fifth great grandnephews/nieces",
                         "twenty-sixth great grandnephews/nieces",
                         "twenty-seventh great grandnephews/nieces",
                         "twenty-eighth great grandnephews/nieces",
                         "twenty-ninth great grandnephews/nieces",
                         "thirtieth great grandnephews/nieces",
                         "thirty-first great grandnephews/nieces",
                         "thirty-second great grandnephews/nieces",
                         "thirty-third great grandnephews/nieces",
                         "thirty-fourth great grandnephews/nieces",
                         "thirty-fifth great grandnephews/nieces",
                         "thirty-sixth great grandnephews/nieces",
                         "thirty-seventh great grandnephews/nieces",
                         "thirty-eighth great grandnephews/nieces",
                         "thirty-ninth great grandnephews/nieces",
                         "fortieth great grandnephews/nieces",
                         "forty-first great grandnephews/nieces",
                         "forty-second great grandnephews/nieces",
                         "forty-third great grandnephews/nieces",
                         "forty-fourth great grandnephews/nieces",
                         "forty-fifth great grandnephews/nieces",
                         "forty-sixth great grandnephews/nieces",
                         "forty-seventh great grandnephews/nieces",
                         "forty-eighth great grandnephews/nieces",
                         "forty-ninth great grandnephews/nieces",
                         "fiftieth great grandnephews/nieces", ]


#-------------------------------------------------------------------------
#
# RelationshipCalculator
#
#-------------------------------------------------------------------------
class RelationshipCalculator:
    """
    The relationship calculator helps to determine the relationship between
    two people.
    """
    REL_MOTHER = 'm'               # going up to mother
    REL_FATHER = 'f'               # going up to father
    REL_MOTHER_NOTBIRTH = 'M'      # going up to mother, not birth relation
    REL_FATHER_NOTBIRTH = 'F'      # going up to father, not birth relation
    REL_SIBLING = 's'              # going sideways to sibling (no parents)
    REL_FAM_BIRTH = 'a'            # going up to family (mother and father)
    REL_FAM_NONBIRTH = 'A'         # going up to family, not birth relation
    REL_FAM_BIRTH_MOTH_ONLY = 'b'  # going up to fam, only birth rel to mother
    REL_FAM_BIRTH_FATH_ONLY = 'c'  # going up to fam, only birth rel to father

    REL_FAM_INLAW_PREFIX = 'L'     # going to the partner.

    #sibling types
    NORM_SIB = 0                   # same birth parents
    HALF_SIB_MOTHER = 1            # same mother, father known to be different
    HALF_SIB_FATHER = 2            # same father, mother known to be different
    STEP_SIB = 3                   # birth parents known to be different
    UNKNOWN_SIB = 4                # insufficient data to draw conclusion

    #sibling strings
    STEP = 'step'
    HALF = 'half-'

    INLAW = '-in-law'

    #partner types
    PARTNER_MARRIED = 1
    PARTNER_UNMARRIED = 2
    PARTNER_CIVIL_UNION = 3
    PARTNER_UNKNOWN_REL = 4
    PARTNER_EX_MARRIED = 5
    PARTNER_EX_UNMARRIED = 6
    PARTNER_EX_CIVIL_UNION = 7
    PARTNER_EX_UNKNOWN_REL = 8

    def __init__(self):
        self.signal_keys = []
        self.state_signal_key = None
        self.storemap = False
        self.dirtymap = True
        self.stored_map = None
        self.map_handle = None
        self.map_meta = None
        self.__db_connected = False
        self.depth = 15
        try:
            from .config import config
            self.set_depth(config.get('behavior.generation-depth'))
        except ImportError:
            pass

        #data storage to communicate with recursive functions
        self.__max_depth_reached = False
        self.__loop_detected = False
        self.__max_depth = 0
        self.__all_families = False
        self.__all_dist = False
        self.__only_birth = False
        self.__crosslinks = False
        self.__msg = []

    def set_depth(self, depth):
        """
        Set how deep relationships must be searched. Input must be an
        integer > 0
        """
        if depth != self.depth:
            self.depth = depth
            self.dirtymap = True

    def get_depth(self):
        """
        Obtain depth of relationship search
        """
        return self.depth

    DIST_FATHER = "distant %(step)sancestor%(inlaw)s (%(level)d generations)"

    def _get_father(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_FATHER_LEVEL) - 1:
            return self.DIST_FATHER % {'step': step, 'inlaw': inlaw,
                                       'level': level}
        else:
            return _FATHER_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    DIST_SON = "distant %(step)sdescendant%(inlaw)s (%(level)d generations)"

    def _get_son(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_SON_LEVEL) - 1:
            return self.DIST_SON % {'step': step, 'inlaw': inlaw,
                                    'level': level}
        else:
            return _SON_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    DIST_MOTHER = "distant %(step)sancestor%(inlaw)s (%(level)d generations)"

    def _get_mother(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_MOTHER_LEVEL) - 1:
            return self.DIST_MOTHER % {'step': step, 'inlaw': inlaw,
                                       'level': level}
        else:
            return _MOTHER_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    DIST_DAUGHTER = "distant %(step)sdescendant%(inlaw)s (%(level)d generations)"

    def _get_daughter(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_DAUGHTER_LEVEL) - 1:
            return self.DIST_DAUGHTER % {'step': step, 'inlaw': inlaw,
                                         'level': level}
        else:
            return _DAUGHTER_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    def _get_parent_unknown(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level < len(_LEVEL_NAME):
            return _LEVEL_NAME[level] + ' ' + '%sancestor%s' % (step, inlaw)
        else:
            return "distant %sancestor%s (%d generations)" % (step, inlaw,
                                                              level)

    DIST_CHILD = "distant %(step)sdescendant (%(level)d generations)"

    def _get_child_unknown(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level < len(_LEVEL_NAME):
            return _LEVEL_NAME[level] + ' ' + '%(step)sdescendant%(inlaw)s' % {
                'step': step, 'inlaw': inlaw}
        else:
            return self.DIST_CHILD % {'step': step, 'level': level}

    DIST_AUNT = "distant %(step)saunt%(inlaw)s"

    def _get_aunt(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_SISTER_LEVEL) - 1:
            return self.DIST_AUNT % {'step': step, 'inlaw': inlaw}
        else:
            return _SISTER_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    DIST_UNCLE = "distant %(step)suncle%(inlaw)s"

    def _get_uncle(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_BROTHER_LEVEL) - 1:
            return self.DIST_UNCLE % {'step': step, 'inlaw': inlaw}
        else:
            return _BROTHER_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    DIST_NEPHEW = "distant %(step)snephew%(inlaw)s"

    def _get_nephew(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_NEPHEW_LEVEL) - 1:
            return self.DIST_NEPHEW % {'step': step, 'inlaw': inlaw}
        else:
            return _NEPHEW_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    DIST_NIECE = "distant %(step)sniece%(inlaw)s"

    def _get_niece(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level > len(_NIECE_LEVEL) - 1:
            return self.DIST_NIECE % {'step': step, 'inlaw': inlaw}
        else:
            return _NIECE_LEVEL[level] % {'step': step, 'inlaw': inlaw}

    def _get_cousin(self, level, removed, dir='', step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if removed == 0 and level < len(_LEVEL_NAME):
            return "%s %scousin%s" % (_LEVEL_NAME[level], step, inlaw)
        elif removed > len(_REMOVED_LEVEL)-1 or level > len(_LEVEL_NAME)-1:
            return "distant %srelative%s" % (step, inlaw)
        else:
            return "%s %scousin%s%s%s" % (_LEVEL_NAME[level],
                                          step, inlaw,
                                          _REMOVED_LEVEL[removed], dir)

    DIST_SIB = "distant %(step)suncle/aunt%(inlaw)s"

    def _get_sibling(self, level, step='', inlaw=''):
        """
        Internal english method to create relation string
        """
        if level < len(_SIBLING_LEVEL):
            return _SIBLING_LEVEL[level] % {'step': step, 'inlaw': inlaw}
        else:
            return self.DIST_SIB % {'step': step, 'inlaw': inlaw}

    def get_sibling_type(self, db, orig, other):
        """
        Translation free determination of type of orig and other as siblings
        The procedure returns sibling types, these can be passed to
        get_sibling_relationship_string.
        Only call this method if known that orig and other are siblings
        """
        fatherorig, motherorig = self.get_birth_parents(db, orig)
        fatherother, motherother = self.get_birth_parents(db, other)
        if fatherorig and motherorig and fatherother and motherother:
            if fatherother == fatherorig and motherother == motherorig:
                return self.NORM_SIB
            elif fatherother == fatherorig:
                #all birth parents are known, one
                return self.HALF_SIB_FATHER
            elif motherother == motherorig:
                return self.HALF_SIB_MOTHER
            else:
                return self.STEP_SIB
        else:
            # some birth parents are not known, hence we or cannot know if
            # half siblings. step siblings might be possible, otherwise give up
            orig_nb_par = self._get_nonbirth_parent_list(db, orig)
            if fatherother and fatherother in orig_nb_par:
                #the birth parent of other is non-birth of orig
                if motherother and motherother == motherorig:
                    return self.HALF_SIB_MOTHER
                else:
                    return self.STEP_SIB
            if motherother and motherother in orig_nb_par:
                #the birth parent of other is non-birth of orig
                if fatherother and fatherother == fatherorig:
                    return self.HALF_SIB_FATHER
                else:
                    return self.STEP_SIB
            other_nb_par = self._get_nonbirth_parent_list(db, other)
            if fatherorig and fatherorig in other_nb_par:
                #the one birth parent of other is non-birth of orig
                if motherorig and motherother == motherorig:
                    return self.HALF_SIB_MOTHER
                else:
                    return self.STEP_SIB
            if motherorig and motherorig in other_nb_par:
                #the one birth parent of other is non-birth of orig
                if fatherother and fatherother == fatherorig:
                    return self.HALF_SIB_FATHER
                else:
                    return self.STEP_SIB
            #there is an unknown birth parent, it could be that this is the
            # birth parent of the other person
            return self.UNKNOWN_SIB

    def get_birth_parents(self, db, person):
        """
        Method that returns the birthparents of a person as tuple
        (mother handle, father handle), if no known birthparent, the
        handle is replaced by None
        """
        birthfather = None
        birthmother = None
        for fam in person.get_parent_family_handle_list():
            family = db.get_family_from_handle(fam)
            if not family:
                continue
            childrel = [(ref.get_mother_relation(), ref.get_father_relation())
                        for ref in family.get_child_ref_list()
                        if ref.ref == person.handle]
            if not birthmother and childrel[0][0] == ChildRefType.BIRTH:
                birthmother = family.get_mother_handle()
            if not birthfather and childrel[0][1] == ChildRefType.BIRTH:
                birthfather = family.get_father_handle()
            if birthmother and birthfather:
                break
        return (birthmother, birthfather)

    def _get_nonbirth_parent_list(self, db, person):
        """
        Returns a list of handles of parents of which it is known
        they are not birth parents.
        So all parents which do not have relation BIRTH or UNKNOWN
        are returned.
        """
        nb_parents = []
        for fam in person.get_parent_family_handle_list():
            family = db.get_family_from_handle(fam)
            if not family:
                continue
            childrel = [(ref.get_mother_relation(), ref.get_father_relation())
                        for ref in family.get_child_ref_list()
                        if ref.ref == person.handle]
            if childrel[0][0] != ChildRefType.BIRTH \
                    and childrel[0][0] != ChildRefType.UNKNOWN:
                nb_parents.append(family.get_mother_handle())
            if childrel[0][1] != ChildRefType.BIRTH \
                    and childrel[0][1] != ChildRefType.UNKNOWN:
                nb_parents.append(family.get_father_handle())
        #make every person appear only once:
        return list(set(nb_parents))

    def _get_spouse_type(self, db, orig, other, all_rel=False):
        """
        Translation free determination if orig and other are partners.
        The procedure returns partner types, these can be passed to
        get_partner_relationship_string.
        If all_rel=False, returns None or a partner type.
        If all_rel=True, returns a list, empty if no partner
        """
        val = []
        for family_handle in orig.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)
            # return first found spouse type
            if family and other.get_handle() in [family.get_father_handle(),
                                                 family.get_mother_handle()]:
                family_rel = family.get_relationship()
                #check for divorce event:
                ex = False
                for eventref in family.get_event_ref_list():
                    event = db.get_event_from_handle(eventref.ref)
                    if event and (event.get_type() == EventType.DIVORCE
                                  or event.get_type() == EventType.ANNULMENT):
                        ex = True
                        break
                if family_rel == FamilyRelType.MARRIED:
                    if ex:
                        val.append(self.PARTNER_EX_MARRIED)
                    else:
                        val.append(self.PARTNER_MARRIED)
                elif family_rel == FamilyRelType.UNMARRIED:
                    if ex:
                        val.append(self.PARTNER_EX_UNMARRIED)
                    else:
                        val.append(self.PARTNER_UNMARRIED)
                elif family_rel == FamilyRelType.CIVIL_UNION:
                    if ex:
                        val.append(self.PARTNER_EX_CIVIL_UNION)
                    else:
                        val.append(self.PARTNER_CIVIL_UNION)
                else:
                    if ex:
                        val.append(self.PARTNER_EX_UNKNOWN_REL)
                    else:
                        val.append(self.PARTNER_UNKNOWN_REL)

        if all_rel:
            return val
        else:
            #last relation is normally the defenitive relation
            if val:
                return val[-1]
            else:
                return None

    def is_spouse(self, db, orig, other, all_rel=False):
        """
        Determine the spouse relation
        """
        spouse_type = self._get_spouse_type(db, orig, other, all_rel)
        if spouse_type:
            return self.get_partner_relationship_string(spouse_type,
                                                        orig.get_gender(),
                                                        other.get_gender())
        else:
            return None

    def get_relationship_distance_new(self, db, orig_person,
                                      other_person,
                                      all_families=False,
                                      all_dist=False,
                                      only_birth=True):
        """
        Return if all_dist == True a 'tuple, string':
        (rank, person handle, firstRel_str, firstRel_fam,
        secondRel_str, secondRel_fam), msg
        or if all_dist == True a 'list of tuple, string':
        [.....], msg:

        .. note:: _new can be removed once all rel_xx modules no longer
                  overwrite get_relationship_distance

        The tuple or list of tuples consists of:

        ==============  =====================================================
        Element         Description
        ==============  =====================================================
        rank            Total number of generations from common ancestor to
                        the two persons, rank is -1 if no relations found
        person_handle   The Common ancestor
        firstRel_str    String with the path to the common ancestor
                        from orig Person
        firstRel_fam    Family numbers along the path as a list, eg [0,0,1].
                        For parent in multiple families, eg [0. [0, 2], 1]
        secondRel_str   String with the path to the common ancestor
                        from otherPerson
        secondRel_fam   Family numbers along the path, eg [0,0,1].
                        For parent in multiple families, eg [0. [0, 2], 1]
        msg             List of messages indicating errors. Empyt list if no
                        errors.
        ==============  =====================================================

        Example:  firstRel_str = 'ffm' and firstRel_fam = [2,0,1] means
        common ancestor is mother of the second family of the father of the
        first family of the father of the third family.

        Note that the same person might be present twice if the person is
        reached via a different branch too. Path (firstRel_str and
        secondRel_str) will of course be different.

        :param db: database to work on
        :param orig_person: first person
        :type orig_person: Person Obj
        :param other_person: second person, relation is sought between
                             first and second person
        :type other_person:  Person Obj
        :param all_families: if False only Main family is searched, otherwise
                             all families are used
        :type all_families: bool
        :param all_dist: if False only the shortest distance is returned,
                         otherwise all relationships
        :type all_dist:  bool
        :param only_birth: if True only parents with birth relation are
                           considered
        :type only_birth:  bool
        """
        #data storage to communicate with recursive functions
        self.__max_depth_reached = False
        self.__loop_detected = False
        self.__max_depth = self.get_depth()
        self.__all_families = all_families
        self.__all_dist = all_dist
        self.__only_birth = only_birth
        self.__crosslinks = False    # no crosslinks

        first_rel = -1
        second_rel = -1
        self.__msg = []

        common = []
        first_map = {}
        second_map = {}
        rank = 9999999

        try:
            if (self.storemap and self.stored_map is not None
                    and self.map_handle == orig_person.handle
                    and not self.dirtymap):
                first_map = self.stored_map
                self.__max_depth_reached, self.__loop_detected, \
                 self.__all_families,\
                 self.__all_dist, self.__only_birth,\
                 self.__crosslinks, self.__msg = self.map_meta
                self.__msg = list(self.__msg)
            else:
                self.__apply_filter(db, orig_person, '', [], first_map)
                self.map_meta = (self.__max_depth_reached,
                                 self.__loop_detected,
                                 self.__all_families,
                                 self.__all_dist, self.__only_birth,
                                 self.__crosslinks, list(self.__msg))
            self.__apply_filter(db, other_person, '', [], second_map,
                                stoprecursemap=first_map)
        except RuntimeError:
            return (-1, None, -1, [], -1, []), \
                            [_("Relationship loop detected")] + self.__msg

        if self.storemap:
            self.stored_map = first_map
            self.dirtymap = False
            self.map_handle = orig_person.handle

        for person_handle in second_map:
            if person_handle in first_map:
                com = []
                #a common ancestor
                for rel1, fam1 in zip(first_map[person_handle][0],
                                      first_map[person_handle][1]):
                    len1 = len(rel1)
                    for rel2, fam2 in zip(second_map[person_handle][0],
                                          second_map[person_handle][1]):
                        len2 = len(rel2)
                        #collect paths to arrive at common ancestor
                        com.append((len1+len2, person_handle, rel1, fam1,
                                    rel2, fam2))
                #insert common ancestor in correct position,
                #  if shorter links, check if not subset
                #  if longer links, check if not superset
                pos = 0
                for (ranknew, handlenew, rel1new, fam1new, rel2new,
                     fam2new) in com:
                    insert = True
                    for rank, handle, rel1, fam1, rel2, fam2 in common:
                        if ranknew < rank:
                            break
                        elif ranknew >= rank:
                            #check subset
                            if rel1 == rel1new[:len(rel1)] and \
                                    rel2 == rel2new[:len(rel2)]:
                                #subset relation exists already
                                insert = False
                                break
                        pos += 1
                    if insert:
                        if common:
                            common.insert(pos, (ranknew, handlenew, rel1new,
                                                fam1new, rel2new, fam2new))
                        else:
                            common = [(ranknew, handlenew, rel1new, fam1new,
                                       rel2new, fam2new)]
                        #now check if superset must be deleted from common
                        deletelist = []
                        index = pos+1
                        for (rank, handle, rel1, fam1, rel2,
                             fam2) in common[pos+1:]:
                            if rel1new == rel1[:len(rel1new)] and \
                                    rel2new == rel2[:len(rel2new)]:
                                deletelist.append(index)
                            index += 1
                        deletelist.reverse()
                        for index in deletelist:
                            del common[index]
        #check for extra messages
        if self.__max_depth_reached:
            self.__msg += [_('Family Tree reaches back more than the maximum '
                             '%d generations searched.\nIt is possible that '
                             'relationships have been missed') %
                           (self.__max_depth)]

        if common and not self.__all_dist:
            rank = common[0][0]
            person_handle = common[0][1]
            first_rel = common[0][2]
            first_fam = common[0][3]
            second_rel = common[0][4]
            second_fam = common[0][5]
            return (rank, person_handle, first_rel, first_fam, second_rel,
                    second_fam), self.__msg
        if common:
            #list with tuples (rank, handle person,rel_str_orig,rel_fam_orig,
            #       rel_str_other,rel_fam_str) and messages
            return common, self.__msg
        if not self.__all_dist:
            return  (-1, None, '', [], '', []), self.__msg
        else:
            return [(-1, None, '', [], '', [])], self.__msg

    def __apply_filter(self, db, person, rel_str, rel_fam, pmap,
                       depth=1, stoprecursemap=None):
        """
        Typically this method is called recursively in two ways:
        First method is stoprecursemap= None
        In this case a recursemap is builded by storing all data.

        Second method is with a stoprecursemap given
        In this case parents are recursively looked up. If present in
        stoprecursemap, a common ancestor is found, and the method can
        stop looking further. If however self.__crosslinks == True, the data
        of first contains loops, and parents
        will be looked up anyway an stored if common. At end the doubles
        are filtered out
        """
        if person is None or not person.handle:
            return

        if depth > self.__max_depth:
            self.__max_depth_reached = True
            #print('Maximum ancestor generations ('+str(depth)+') reached', \
            #            '(' + rel_str + ').',\
            #            'Stopping relation algorithm.')
            return
        depth += 1

        commonancestor = False
        store = True                            #normally we store all parents
        if stoprecursemap:
            store = False                       #but not if a stop map given
            if person.handle in stoprecursemap:
                commonancestor = True
                store = True

        #add person to the map, take into account that person can be obtained
        #from different sides
        if person.handle in pmap:
            #person is already a grandparent in another branch, we already have
            # had lookup of all parents, we call that a crosslink
            if not stoprecursemap:
                self.__crosslinks = True
            pmap[person.handle][0] += [rel_str]
            pmap[person.handle][1] += [rel_fam]
            #check if there is no loop father son of his son, ...
            # loop means person is twice reached, same rel_str in begin
            for rel1 in pmap[person.handle][0]:
                for rel2 in pmap[person.handle][0]:
                    if len(rel1) < len(rel2) and \
                            rel1 == rel2[:len(rel1)]:
                        #loop, keep one message in storage!
                        self.__loop_detected = True
                        self.__msg += [_("Relationship loop detected:") + " " +
                                       _("Person %(person)s connects to himself via %(relation)s")  %
                                       {'person' : person.get_primary_name().get_name(),
                                        'relation' : rel2[len(rel1):]}]
                        return
        elif store:
            pmap[person.handle] = [[rel_str], [rel_fam]]

        #having added person to the pmap, we only look up recursively to
        # parents if this person is not common relative
        # if however the first map has crosslinks, we need to continue reduced
        if commonancestor and not self.__crosslinks:
            #don't continue search, great speedup!
            return

        family_handles = []
        main = person.get_main_parents_family_handle()
        if main:
            family_handles = [main]
        if self.__all_families:
            family_handles = person.get_parent_family_handle_list()

        try:
            parentstodo = {}
            fam = 0
            for family_handle in family_handles:
                rel_fam_new = rel_fam + [fam]
                family = db.get_family_from_handle(family_handle)
                if not family:
                    continue
                #obtain childref for this person
                childrel = [(ref.get_mother_relation(),
                             ref.get_father_relation())
                            for ref in family.get_child_ref_list()
                            if ref.ref == person.handle]
                fhandle = family.father_handle
                mhandle = family.mother_handle
                for data in [(fhandle, self.REL_FATHER,
                              self.REL_FATHER_NOTBIRTH, childrel[0][1]),
                             (mhandle, self.REL_MOTHER,
                              self.REL_MOTHER_NOTBIRTH, childrel[0][0])]:
                    if data[0] and data[0] not in parentstodo:
                        persontodo = db.get_person_from_handle(data[0])
                        if data[3] == ChildRefType.BIRTH:
                            addstr = data[1]
                        elif not self.__only_birth:
                            addstr = data[2]
                        else:
                            addstr = ''
                        if addstr:
                            parentstodo[data[0]] = (persontodo,
                                                    rel_str + addstr,
                                                    rel_fam_new)
                    elif data[0] and data[0] in parentstodo:
                        #this person is already scheduled to research
                        #update family list
                        famlist = parentstodo[data[0]][2]
                        if not isinstance(famlist[-1], list) and \
                                fam != famlist[-1]:
                            famlist = famlist[:-1] + [[famlist[-1]]]
                        if isinstance(famlist[-1], list) and \
                                fam not in famlist[-1]:
                            famlist = famlist[:-1] + [famlist[-1] + [fam]]
                            parentstodo[data[0]] = (parentstodo[data[0]][0],
                                                    parentstodo[data[0]][1],
                                                    famlist)
                if not fhandle and not mhandle and stoprecursemap is None:
                    #family without parents, add brothers for orig person
                    #other person has recusemap, and will stop when seeing
                    #the brother.
                    child_list = [ref.ref for ref in family.get_child_ref_list()
                                  if ref.ref != person.handle]
                    addstr = self.REL_SIBLING
                    for chandle in child_list:
                        if chandle in pmap:
                            pmap[chandle][0] += [rel_str + addstr]
                            pmap[chandle][1] += [rel_fam_new]
                            #person is already a grandparent in another branch
                        else:
                            pmap[chandle] = [[rel_str+addstr], [rel_fam_new]]
                fam += 1

            for handle, data in parentstodo.items():
                self.__apply_filter(db, data[0],
                                    data[1], data[2],
                                    pmap, depth, stoprecursemap)
        except:
            import traceback
            traceback.print_exc()
            return

    def collapse_relations(self, relations):
        """
        Internal method to condense the relationships as returned by
        get_relationship_distance_new.
        Common ancestors in the same family are collapsed to one entry,
        changing the person paths to family paths, eg 'mf' and 'mm' become 'ma'

        relations : list of relations as returned by
                    get_relationship_distance_new with all_dist = True

        returns : the same data as relations, but collapsed, hence the
                  handle entry is now a list of handles, and the
                  path to common ancestors can now contain family
                  identifiers (eg 'a', ...)
                  In the case of sibling, this is replaced by family
                  with common ancestor handles empty list []!
        """
        if relations[0][0] == -1:
            return relations
        commonnew = []
        existing_path = []
        for relation in relations:
            relstrfirst = None
            commonhandle = [relation[1]]
            if relation[2]:
                relstrfirst = relation[2][:-1]
            relstrsec = None
            if relation[4]:
                relstrsec = relation[4][:-1]
            relfamfirst = relation[3][:]
            relfamsec = relation[5][:]
            #handle pure sibling:
            rela2 = relation[2]
            rela4 = relation[4]
            if relation[2] and relation[2][-1] == self.REL_SIBLING:
                #sibling will be the unique common ancestor,
                #change to a family with unknown handle for common ancestor
                rela2 = relation[2][:-1] + self.REL_FAM_BIRTH
                rela4 = relation[4] + self.REL_FAM_BIRTH
                relfamsec = relfamsec + [relfamfirst[-1]]
                relstrsec = relation[4][:-1]
                commonhandle = []

            # a unique path to family of common person:
            familypaths = []
            if relfamfirst and isinstance(relfamfirst[-1], list):
                if relfamsec and isinstance(relfamsec[-1], list):
                    for val1 in relfamfirst[-1]:
                        for val2 in relfamsec[-1]:
                            familypaths.append((relstrfirst, relstrsec,
                                                relfamfirst[:-1] + [val1],
                                                relfamsec[:-1] + [val2]))
                else:
                    for val1 in relfamfirst[-1]:
                        familypaths.append((relstrfirst, relstrsec,
                                            relfamfirst[:-1] + [val1],
                                            relfamsec))
            elif relfamsec and isinstance(relfamsec[-1], list):
                for val2 in relfamsec[-1]:
                    familypaths.append((relstrfirst, relstrsec,
                                        relfamfirst,
                                        relfamsec[:-1] + [val2]))
            else:
                familypaths.append((relstrfirst, relstrsec,
                                    relfamfirst, relfamsec))
            for familypath in familypaths:
                #familypath = (relstrfirst, relstrsec, relfamfirst, relfamsec)
                try:
                    posfam = existing_path.index(familypath)
                except ValueError:
                    posfam = None
                #if relstr is '', the ancestor is unique, if posfam None,
                # first time we see this family path
                if (posfam is not None and relstrfirst is not None and
                        relstrsec is not None):
                    # We already have a common ancestor of this family, just
                    # add the other, setting correct family relation.
                    tmp = commonnew[posfam]
                    frstcomstr = rela2[-1]
                    scndcomstr = tmp[2][-1]
                    newcomstra = self._famrel_from_persrel(frstcomstr,
                                                           scndcomstr)
                    frstcomstr = rela4[-1]
                    scndcomstr = tmp[4][-1]
                    newcomstrb = self._famrel_from_persrel(frstcomstr,
                                                           scndcomstr)

                    commonnew[posfam] = (tmp[0], tmp[1]+commonhandle,
                                         rela2[:-1]+newcomstra,
                                         tmp[3], rela4[:-1]+newcomstrb,
                                         tmp[5])
                else:
                    existing_path.append(familypath)
                    commonnew.append((relation[0], commonhandle, rela2,
                                      familypath[2], rela4, familypath[3]))
        #we now have multiple person handles, single families, now collapse
        #  families again if all else equal
        collapsed = commonnew[:1]
        for rel in commonnew[1:]:
            found = False
            for newrel in collapsed:
                if newrel[0:3] == rel[0:3] and newrel[4] == rel[4]:
                    #another familypath to arrive at same result, merge
                    path1 = []
                    path2 = []
                    for a, b in zip(newrel[3], rel[3]):
                        if a == b:
                            path1.append(a)
                        elif isinstance(a, list):
                            path1.append(a.append(b))
                        else:
                            path1.append([a, b])
                    for a, b in zip(newrel[5], rel[5]):
                        if a == b:
                            path2.append(a)
                        elif isinstance(a, list):
                            path2.append(a.append(b))
                        else:
                            path2.append([a, b])
                    newrel[3][:] = path1[:]
                    newrel[5][:] = path2[:]
                    found = True
                    break
            if not found:
                collapsed.append(rel)

        return collapsed

    def _famrel_from_persrel(self, persrela, persrelb):
        """
        Conversion from eg 'f' and 'm' to 'a', so relation to the two
        persons of a common family is converted to a family relation
        """
        if persrela == persrelb:
            #should not happen, procedure called in error, just return value
            return persrela
        if ((persrela == self.REL_MOTHER and persrelb == self.REL_FATHER) or
                (persrelb == self.REL_MOTHER and persrela == self.REL_FATHER)):
            return self.REL_FAM_BIRTH
        if ((persrela == self.REL_MOTHER and
             persrelb == self.REL_FATHER_NOTBIRTH) or
                (persrelb == self.REL_MOTHER and
                 persrela == self.REL_FATHER_NOTBIRTH)):
            return self.REL_FAM_BIRTH_MOTH_ONLY
        if ((persrela == self.REL_FATHER and
             persrelb == self.REL_MOTHER_NOTBIRTH) or
                (persrelb == self.REL_FATHER and
                 persrela == self.REL_MOTHER_NOTBIRTH)):
            return self.REL_FAM_BIRTH_FATH_ONLY
        #catch calling with family relations already, return val
        if (persrela == self.REL_FAM_BIRTH or
                persrela == self.REL_FAM_BIRTH_FATH_ONLY or
                persrela == self.REL_FAM_BIRTH_MOTH_ONLY or
                persrela == self.REL_FAM_NONBIRTH):
            return persrela
        if (persrelb == self.REL_FAM_BIRTH or
                persrelb == self.REL_FAM_BIRTH_FATH_ONLY or
                persrelb == self.REL_FAM_BIRTH_MOTH_ONLY or
                persrelb == self.REL_FAM_NONBIRTH):
            return persrelb
        return self.REL_FAM_NONBIRTH

    def only_birth(self, path):
        """
        Given a path to common ancestor. Return True if only birth
        relations, False otherwise
        """
        for value in path:
            if value in [self.REL_FAM_NONBIRTH, self.REL_FATHER_NOTBIRTH,
                         self.REL_MOTHER_NOTBIRTH]:
                return False
        return True

    def get_one_relationship(self, db, orig_person, other_person,
                             extra_info=False, olocale=glocale):
        """
        Returns a string representing the most relevant relationship between
        the two people. If extra_info = True, extra information is returned:
        (relation_string, distance_common_orig, distance_common_other)

        If olocale is passed in (a GrampsLocale) that language will be used.

        :param olocale: allow selection of the relationship language
        :type olocale: a GrampsLocale instance
        """
        self._locale = olocale
        stop = False
        if orig_person is None:
            rel_str = _("undefined")
            stop = True

        if not stop and orig_person.get_handle() == other_person.get_handle():
            rel_str = ''
            stop = True

        if not stop:
            is_spouse = self.is_spouse(db, orig_person, other_person)
            if is_spouse:
                rel_str = is_spouse
                stop = True

        if stop:
            if extra_info:
                return (rel_str, -1, -1)
            else:
                return rel_str

        data, msg = self.get_relationship_distance_new(
            db, orig_person, other_person, all_dist=True, all_families=True,
            only_birth=False)
        if data[0][0] == -1:
            if extra_info:
                return ('', -1, -1)
            else:
                return ''

        data = self.collapse_relations(data)

        #most relevant relationship is a birth family relation of lowest rank
        databest = [data[0]]
        rankbest = data[0][0]
        for rel in data:
            #data is sorted on rank
            if rel[0] == rankbest:
                databest.append(rel)
        rel = databest[0]
        dist_orig = len(rel[2])
        dist_other = len(rel[4])
        if len(databest) == 1:
            birth = self.only_birth(rel[2]) and self.only_birth(rel[4])
            if dist_orig == dist_other == 1:
                rel_str = self.get_sibling_relationship_string(
                    self.get_sibling_type(db, orig_person, other_person),
                    orig_person.get_gender(),
                    other_person.get_gender())
            else:
                rel_str = self.get_single_relationship_string(
                    dist_orig, dist_other,
                    orig_person.get_gender(), other_person.get_gender(),
                    rel[2], rel[4], only_birth=birth,
                    in_law_a=False, in_law_b=False)
        else:
            order = [self.REL_FAM_BIRTH, self.REL_FAM_BIRTH_MOTH_ONLY,
                     self.REL_FAM_BIRTH_FATH_ONLY, self.REL_MOTHER,
                     self.REL_FATHER, self.REL_SIBLING, self.REL_FAM_NONBIRTH,
                     self.REL_MOTHER_NOTBIRTH, self.REL_FATHER_NOTBIRTH]
            orderbest = order.index(self.REL_MOTHER)
            for relother in databest:
                relbirth = self.only_birth(rel[2]) and self.only_birth(rel[4])
                if relother[2] == '' or relother[4] == '':
                    #direct relation, take that
                    rel = relother
                    break
                if not relbirth and self.only_birth(relother[2]) \
                                and self.only_birth(relother[4]):
                    #birth takes precedence
                    rel = relother
                    continue
                if order.index(relother[2][-1]) < order.index(rel[2][-1]) and\
                        order.index(relother[2][-1]) < orderbest:
                    rel = relother
                    continue
                if order.index(relother[4][-1]) < order.index(rel[4][-1]) and\
                        order.index(relother[4][-1]) < orderbest:
                    rel = relother
                    continue
                if order.index(rel[2][-1]) < orderbest or \
                        order.index(rel[4][-1]) < orderbest:
                    #keep the good one
                    continue
                if order.index(relother[2][-1]) < order.index(rel[2][-1]):
                    rel = relother
                    continue
                if order.index(relother[2][-1]) == order.index(rel[2][-1]) and\
                        order.index(relother[4][-1]) < order.index(rel[4][-1]):
                    rel = relother
                    continue
            dist_orig = len(rel[2])
            dist_other = len(rel[4])
            birth = self.only_birth(rel[2]) and self.only_birth(rel[4])
            if dist_orig == dist_other == 1:
                rel_str = self.get_sibling_relationship_string(
                    self.get_sibling_type(db, orig_person, other_person),
                    orig_person.get_gender(),
                    other_person.get_gender())
            else:
                rel_str = self.get_single_relationship_string(
                    dist_orig, dist_other,
                    orig_person.get_gender(), other_person.get_gender(),
                    rel[2], rel[4], only_birth=birth,
                    in_law_a=False, in_law_b=False)
        if extra_info:
            return (rel_str, dist_orig, dist_other)
        else:
            return rel_str

    def get_all_relationships(self, db, orig_person, other_person):
        """
        Return a tuple, of which the first entry is a list with all
        relationships in text, and the second a list of lists of all common
        ancestors that have that text as relationship
        """
        relstrings = []
        commons = {}
        if orig_person is None:
            return ([], [])

        if orig_person.get_handle() == other_person.get_handle():
            return ([], [])

        is_spouse = self.is_spouse(db, orig_person, other_person)
        if is_spouse:
            relstrings.append(is_spouse)
            commons[is_spouse] = []

        data, msg = self.get_relationship_distance_new(
            db, orig_person, other_person, all_dist=True, all_families=True,
            only_birth=False)
        if data[0][0] != -1:
            data = self.collapse_relations(data)
            for rel in data:
                rel2 = rel[2]
                rel4 = rel[4]
                rel1 = rel[1]
                dist_orig = len(rel[2])
                dist_other = len(rel[4])
                if rel[2] and rel[2][-1] == self.REL_SIBLING:
                    rel2 = rel2[:-1] + self.REL_FAM_BIRTH
                    dist_other += 1
                    rel4 = rel4 + self.REL_FAM_BIRTH
                    rel1 = None
                birth = self.only_birth(rel2) and self.only_birth(rel4)
                if dist_orig == dist_other == 1:
                    rel_str = self.get_sibling_relationship_string(
                        self.get_sibling_type(db, orig_person, other_person),
                        orig_person.get_gender(), other_person.get_gender())
                else:
                    rel_str = self.get_single_relationship_string(
                        dist_orig, dist_other,
                        orig_person.get_gender(), other_person.get_gender(),
                        rel2, rel4, only_birth=birth,
                        in_law_a=False, in_law_b=False)
                if rel_str not in relstrings:
                    relstrings.append(rel_str)
                    if rel1:
                        commons[rel_str] = rel1
                    else:
                        #unknown parent eg
                        commons[rel_str] = []
                else:
                    if rel1:
                        commons[rel_str].extend(rel1)
        #construct the return tupply, relstrings is ordered on rank automatic
        common_list = []
        for rel_str in relstrings:
            common_list.append(commons[rel_str])
        return (relstrings, common_list)

    def get_plural_relationship_string(self, Ga, Gb,
                                       reltocommon_a='', reltocommon_b='',
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        Provide a string that describes the relationsip between a person, and
        a group of people with the same relationship. E.g. "grandparents" or
        "children".

        Ga and Gb can be used to mathematically calculate the relationship.

        .. seealso::
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions

        :param Ga: The number of generations between the main person and the
                   common ancestor.
        :type Ga: int
        :param Gb: The number of generations between the group of people and the
                   common ancestor
        :type Gb: int
        :param reltocommon_a: relation path to common ancestor or common
                              Family for person a.
                              Note that length = Ga
        :type reltocommon_a: str
        :param reltocommon_b: relation path to common ancestor or common
                              Family for person b.
                              Note that length = Gb
        :type reltocommon_b: str
        :param only_birth: True if relation between a and b is by birth only
                           False otherwise
        :type only_birth: bool
        :param in_law_a: True if path to common ancestors is via the partner
                         of person a
        :type in_law_a: bool
        :param in_law_b: True if path to common ancestors is via the partner
                         of person b
        :type in_law_b: bool
        :returns: A string describing the relationship between the person and
                  the group.
        :rtype: str
        """
        rel_str = "distant relatives"
        if Ga == 0:
            # These are descendants
            if Gb < len(_CHILDREN_LEVEL):
                rel_str = _CHILDREN_LEVEL[Gb]
            else:
                rel_str = "distant descendants"
        elif Gb == 0:
            # These are parents/grand parents
            if Ga < len(_PARENTS_LEVEL):
                rel_str = _PARENTS_LEVEL[Ga]
            else:
                rel_str = "distant ancestors"
        elif Gb == 1:
            # These are siblings/aunts/uncles
            if Ga < len(_SIBLINGS_LEVEL):
                rel_str = _SIBLINGS_LEVEL[Ga]
            else:
                rel_str = "distant uncles/aunts"
        elif Ga == 1:
            # These are nieces/nephews
            if Gb < len(_NEPHEWS_NIECES_LEVEL):
                rel_str = _NEPHEWS_NIECES_LEVEL[Gb]
            else:
                rel_str = "distant nephews/nieces"
        elif Ga > 1 and Ga == Gb:
            # These are cousins in the same generation
            if Ga <= len(_LEVEL_NAME):
                rel_str = "%s cousins" % _LEVEL_NAME[Ga-1]
            else:
                rel_str = "distant cousins"
        elif Ga > 1 and Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            if Gb <= len(_LEVEL_NAME) and (Ga-Gb) < len(_REMOVED_LEVEL):
                rel_str = "%s cousins%s (up)" % (_LEVEL_NAME[Gb-1],
                                                 _REMOVED_LEVEL[Ga-Gb])
            else:
                rel_str = "distant cousins"
        elif Gb > 1 and Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            if Ga <= len(_LEVEL_NAME) and (Gb-Ga) < len(_REMOVED_LEVEL):
                rel_str = "%s cousins%s (down)" % (_LEVEL_NAME[Ga-1],
                                                   _REMOVED_LEVEL[Gb-Ga])
            else:
                rel_str = "distant cousins"

        if in_law_b is True:
            rel_str = "spouses of %s" % rel_str

        return rel_str

    def get_single_relationship_string(self, Ga, Gb, gender_a, gender_b,
                                       reltocommon_a, reltocommon_b,
                                       only_birth=True,
                                       in_law_a=False, in_law_b=False):
        """
        Provide a string that describes the relationsip between a person, and
        another person. E.g. "grandparent" or "child".

        To be used as: 'person b is the grandparent of a', this will be in
        translation string:  'person b is the %(relation)s of a'

        Note that languages with gender should add 'the' inside the
        translation, so eg in french:  'person b est %(relation)s de a'
        where relation will be here: le grandparent

        Ga and Gb can be used to mathematically calculate the relationship.

        .. seealso::
            http://en.wikipedia.org/wiki/Cousin#Mathematical_definitions

        Some languages need to know the specific path to the common ancestor.
        Those languages should use reltocommon_a and reltocommon_b which is
        a string like 'mfmf'.

        The possible string codes are:

        =======================  ===========================================
        Code                     Description
        =======================  ===========================================
        REL_MOTHER               # going up to mother
        REL_FATHER               # going up to father
        REL_MOTHER_NOTBIRTH      # going up to mother, not birth relation
        REL_FATHER_NOTBIRTH      # going up to father, not birth relation
        REL_FAM_BIRTH            # going up to family (mother and father)
        REL_FAM_NONBIRTH         # going up to family, not birth relation
        REL_FAM_BIRTH_MOTH_ONLY  # going up to fam, only birth rel to mother
        REL_FAM_BIRTH_FATH_ONLY  # going up to fam, only birth rel to father
        =======================  ===========================================

        Prefix codes are stripped, so REL_FAM_INLAW_PREFIX is not present.
        If the relation starts with the inlaw of the person a, then 'in_law_a'
        is True, if it starts with the inlaw of person b, then 'in_law_b' is
        True.

        Also REL_SIBLING (# going sideways to sibling (no parents)) is not
        passed to this routine. The collapse_relations changes this to a
        family relation.

        Hence, calling routines should always strip REL_SIBLING and
        REL_FAM_INLAW_PREFIX before calling get_single_relationship_string()
        Note that only_birth=False, means that in the reltocommon one of the
        NOTBIRTH specifiers is present.

        The REL_FAM identifiers mean that the relation is not via a common
        ancestor, but via a common family (note that that is not possible for
        direct descendants or direct ancestors!). If the relation to one of the
        parents in that common family is by birth, then 'only_birth' is not
        set to False. The only_birth() method is normally used for this.

        :param Ga: The number of generations between the main person and the
                   common ancestor.
        :type Ga: int
        :param Gb: The number of generations between the other person and the
                   common ancestor.
        :type Gb: int
        :param gender_a: gender of person a
        :type gender_a: int gender
        :param gender_b: gender of person b
        :type gender_b: int gender
        :param reltocommon_a: relation path to common ancestor or common
                              Family for person a.
                              Note that length = Ga
        :type reltocommon_a: str
        :param reltocommon_b: relation path to common ancestor or common
                              Family for person b.
                              Note that length = Gb
        :type reltocommon_b: str
        :param in_law_a:  True if path to common ancestors is via the partner
                          of person a
        :type in_law_a: bool
        :param in_law_b: True if path to common ancestors is via the partner
                         of person b
        :type in_law_b: bool
        :param only_birth: True if relation between a and b is by birth only
                           False otherwise
        :type only_birth: bool
        :returns: A string describing the relationship between the two people
        :rtype: str

        .. note:: 1. the self.REL_SIBLING should not be passed to this routine,
                     so we should not check on it. All other self.
                  2. for better determination of siblings, use if Ga=1=Gb
                     get_sibling_relationship_string
        """
        if only_birth:
            step = ''
        else:
            step = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ''

        rel_str = "distant %srelative%s" % (step, inlaw)

        if Ga == 0:
            # b is descendant of a
            if Gb == 0:
                rel_str = 'same person'
            elif gender_b == MALE:
                rel_str = self._get_son(Gb, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_daughter(Gb, step, inlaw)
            else:
                rel_str = self._get_child_unknown(Gb, step, inlaw)
        elif Gb == 0:
            # b is parents/grand parent of a
            if gender_b == MALE:
                rel_str = self._get_father(Ga, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_mother(Ga, step, inlaw)
            else:
                rel_str = self._get_parent_unknown(Ga, step, inlaw)
        elif Gb == 1:
            # b is sibling/aunt/uncle of a
            if gender_b == MALE:
                rel_str = self._get_uncle(Ga, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_aunt(Ga, step, inlaw)
            else:
                rel_str = self._get_sibling(Ga, step, inlaw)
        elif Ga == 1:
            # b is niece/nephew of a
            if gender_b == MALE:
                rel_str = self._get_nephew(Gb-1, step, inlaw)
            elif gender_b == FEMALE:
                rel_str = self._get_niece(Gb-1, step, inlaw)
            elif Gb < len(_NIECE_LEVEL) and Gb < len(_NEPHEW_LEVEL):
                rel_str = "%s or %s" % (self._get_nephew(Gb-1, step, inlaw),
                                        self._get_niece(Gb-1, step, inlaw))
            else:
                rel_str = "distant %snephews/nieces%s" % (step, inlaw)
        elif Ga == Gb:
            # a and b cousins in the same generation
            rel_str = self._get_cousin(Ga-1, 0, dir='', step=step, inlaw=inlaw)
        elif Ga > Gb:
            # These are cousins in different generations with the second person
            # being in a higher generation from the common ancestor than the
            # first person.
            rel_str = self._get_cousin(Gb-1, Ga-Gb, dir=' (up)',
                                       step=step, inlaw=inlaw)
        elif Gb > Ga:
            # These are cousins in different generations with the second person
            # being in a lower generation from the common ancestor than the
            # first person.
            rel_str = self._get_cousin(Ga-1, Gb-Ga, dir=' (down)',
                                       step=step, inlaw=inlaw)
        return rel_str

    def get_sibling_relationship_string(self, sib_type, gender_a, gender_b,
                                        in_law_a=False, in_law_b=False):
        """
        Determine the string giving the relation between two siblings of
        type sib_type.
        Eg: b is the brother of a
        Here 'brother' is the string we need to determine
        This method gives more details about siblings than
        get_single_relationship_string can do.

        .. warning:: DON'T TRANSLATE THIS PROCEDURE IF LOGIC IS EQUAL IN YOUR
                     LANGUAGE, AND SAME METHODS EXIST (get_uncle, get_aunt,
                     get_sibling)
        """
        if sib_type == self.NORM_SIB or sib_type == self.UNKNOWN_SIB:
            typestr = ''
        elif sib_type == self.HALF_SIB_MOTHER \
                or sib_type == self.HALF_SIB_FATHER:
            typestr = self.HALF
        elif sib_type == self.STEP_SIB:
            typestr = self.STEP

        if in_law_a or in_law_b:
            inlaw = self.INLAW
        else:
            inlaw = ''

        if gender_b == MALE:
            rel_str = self._get_uncle(1, typestr, inlaw)
        elif gender_b == FEMALE:
            rel_str = self._get_aunt(1, typestr, inlaw)
        else:
            rel_str = self._get_sibling(1, typestr, inlaw)
        return rel_str

    def get_partner_relationship_string(self, spouse_type, gender_a, gender_b):
        """
        Determine the string giving the relation between two partners of
        type spouse_type.
        Eg: b is the spouse of a
        Here 'spouse' is the string we need to determine

        .. warning:: DON'T TRANSLATE THIS PROCEDURE IF LOGIC IS EQUAL IN YOUR
                     LANGUAGE, AS GETTEXT IS ALREADY USED !
        """
        #english only needs gender of b, we don't guess if unknown like in old
        # procedure as that is stupid in present day cases!
        gender = gender_b

        if not spouse_type:
            return ''

        trans_text = _
        # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)
        if hasattr(self, '_locale') and self._locale != glocale:
            trans_text = self._locale.translation.sgettext

        if spouse_type == self.PARTNER_MARRIED:
            if gender == MALE:
                return trans_text("husband")
            elif gender == FEMALE:
                return trans_text("wife")
            else:
                return trans_text("spouse", "gender unknown")
        elif spouse_type == self.PARTNER_EX_MARRIED:
            if gender == MALE:
                return trans_text("ex-husband")
            elif gender == FEMALE:
                return trans_text("ex-wife")
            else:
                return trans_text("ex-spouse", "gender unknown")
        elif spouse_type == self.PARTNER_UNMARRIED:
            if gender == MALE:
                return trans_text("partner", "male,unmarried")
            elif gender == FEMALE:
                return trans_text("partner", "female,unmarried")
            else:
                return trans_text("partner", "gender unknown,unmarried")
        elif spouse_type == self.PARTNER_EX_UNMARRIED:
            if gender == MALE:
                return trans_text("ex-partner", "male,unmarried")
            elif gender == FEMALE:
                return trans_text("ex-partner", "female,unmarried")
            else:
                return trans_text("ex-partner", "gender unknown,unmarried")
        elif spouse_type == self.PARTNER_CIVIL_UNION:
            if gender == MALE:
                return trans_text("partner", "male,civil union")
            elif gender == FEMALE:
                return trans_text("partner", "female,civil union")
            else:
                return trans_text("partner", "gender unknown,civil union")
        elif spouse_type == self.PARTNER_EX_CIVIL_UNION:
            if gender == MALE:
                return trans_text("former partner", "male,civil union")
            elif gender == FEMALE:
                return trans_text("former partner", "female,civil union")
            else:
                return trans_text("former partner", "gender unknown,civil union")
        elif spouse_type == self.PARTNER_UNKNOWN_REL:
            if gender == MALE:
                return trans_text("partner", "male,unknown relation")
            elif gender == FEMALE:
                return trans_text("partner", "female,unknown relation")
            else:
                return trans_text("partner", "gender unknown,unknown relation")
        else:
            # here we have spouse_type == self.PARTNER_EX_UNKNOWN_REL
            #   or other not catched types
            if gender == MALE:
                return trans_text("former partner", "male,unknown relation")
            elif gender == FEMALE:
                return trans_text("former partner", "female,unknown relation")
            else:
                return trans_text("former partner", "gender unknown,unknown relation")

    def connect_db_signals(self, dbstate):
        """
        We can save work by storing a map, however, if database changes
        this map must be regenerated.
        Before close, the calling app must call disconnect_db_signals
        """
        if self.__db_connected:
            return
        assert len(self.signal_keys) == 0
        self.state_signal_key = dbstate.connect('database-changed',
                                                self._dbchange_callback)
        self.__connect_db_signals(dbstate.db)

    def __connect_db_signals(self, db):
        signals = ['person-add', 'person-update', 'person-delete',
                   'person-rebuild', 'family-add', 'family-update',
                   'family-delete', 'family-rebuild', 'database-changed']
        for name in signals:
            self.signal_keys.append(db.connect(name, self._datachange_callback))
        self.storemap = True
        self.__db_connected = True

    def disconnect_db_signals(self, dbstate):
        """
        Method to disconnect to all signals the relationship calculator is
        subscribed
        """
        dbstate.disconnect(self.state_signal_key)
        list(map(dbstate.db.disconnect, self.signal_keys))
        self.storemap = False
        self.stored_map = None

    def _dbchange_callback(self, db):
        """
        When database changes, the map can no longer be used.
        Connects must be remade
        """
        self.dirtymap = True
        #signals are disconnected on close of old database, connect to new
        self.__connect_db_signals(db)

    def _datachange_callback(self, handle_list=None):
        """
        When data in database changes, the map can no  longer be used.
        As the map might be in use or might be generated at the moment,
        this method sets a dirty flag. Before reusing the map, this flag
        will be checked
        """
        self.dirtymap = True

#-------------------------------------------------------------------------
#
# define the default relationshipcalculator
#
#-------------------------------------------------------------------------

__RELCALC_CLASS = None

def get_relationship_calculator(reinit=False, clocale=glocale):
    """
    Return the relationship calculator for the current language.

    If clocale is passed in (a GrampsLocale) then that language will be used.

    :param clocale: allow selection of the relationship language
    :type clocale: a GrampsLocale instance

    """
    global __RELCALC_CLASS

    if __RELCALC_CLASS is None or reinit:
        lang = clocale.language[0]
        __RELCALC_CLASS = RelationshipCalculator
        # If lang not set default to English relationship calulator
        # See if lang begins with en_, English_ or english_
        # If so return standard relationship calculator.
        if lang.startswith("en") or lang == "C":
            return __RELCALC_CLASS()
        # set correct non English relationship calculator based on lang
        relation_translation_found = False
        for plugin in PluginRegister.get_instance().relcalc_plugins():
            if lang in plugin.lang_list:
                pmgr = BasePluginManager.get_instance()
                # the loaded module is put in variable mod
                mod = pmgr.load_plugin(plugin)
                if mod:
                    __RELCALC_CLASS = getattr(mod, plugin.relcalcclass)
                    relation_translation_found = True
                    break
        if not relation_translation_found and \
            len(PluginRegister.get_instance().relcalc_plugins()):
            LOG.warning(_("Family relationship translator not available for "
                          "language '%s'. Using 'english' instead."), lang)
    return __RELCALC_CLASS()

#-------------------------------------------------------------------------
#
# Tests
#
#-------------------------------------------------------------------------
MAX = 30
FMT = '%+50s'

def _test(rcalc, onlybirth, inlawa, inlawb, printrelstr, test_num=None):
    """
    This is a generic test suite for the singular relationship
    TRANSLATORS: do NOT translate, use __main__ !
    """
    import sys
    import random
    random.seed()
    def _rand_f_m():
        if random.randint(0, 1) == 0:
            return 'f'
        else:
            return 'm'

    def _rand_relstr(length, endstr):
        if length == 0:
            return ''
        else:
            relstr = ''
            for i in range(length-1):
                relstr += _rand_f_m()
            return relstr + endstr

    if test_num is None:
        print("""
Select a test:
  0 - all tests
  1 - testing sons
  2 - testing daughters
  3 - testing unknown children
  4 - testing grandfathers
  5 - testing grandmothers
  6 - testing unknown parents
  7 - testing nieces
  8 - testing nephews
  9 - testing unknown nephews/nieces
  10 - testing uncles
  11 - testing aunts
  12 - testing unknown uncles/aunts
  13 - testing male cousins same generation
  14 - testing female cousins same generation
  15 - testing unknown cousins same generation
  16 - testing some cousins up
  17 - testing some cousins down

Please enter a test number and press Enter for continue:
    """)
        test_num = sys.stdin.readline().strip()
        test_num = int(test_num)

    if test_num == 0 or test_num == 1:
        print('\ntesting sons')
        #sys.stdin.readline()
        for i in range(MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                0, i, MALE, MALE, '', relstr, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 2:
        print('\ntesting daughters\n')
        #sys.stdin.readline()
        for i in range(MAX):
            relstr = _rand_relstr(i, 'm')
            rel = FMT % rcalc.get_single_relationship_string(
                0, i, MALE, FEMALE, '', relstr, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 3:
        print('\ntesting unknown children\n')
        #sys.stdin.readline()
        for i in range(MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                0, i, MALE, UNKNOWN, '', relstr, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 4:
        print('\ntesting grandfathers\n')
        #sys.stdin.readline()
        for i in range(MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                i, 0, FEMALE, MALE, relstr, '', only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 5:
        print('\ntesting grandmothers\n')
        #sys.stdin.readline()
        for i in range(MAX):
            relstr = _rand_relstr(i, 'm')
            rel = FMT % rcalc.get_single_relationship_string(
                i, 0, FEMALE, FEMALE, relstr, '', only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 6:
        print('\ntesting unknown parents\n')
        #sys.stdin.readline()
        for i in range(MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                i, 0, FEMALE, UNKNOWN, relstr, '', only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 7:
        print('\ntesting nieces\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstr = _rand_relstr(i, 'm')
            rel = FMT % rcalc.get_single_relationship_string(
                1, i, FEMALE, FEMALE, 'm', relstr, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 8:
        print('\ntesting nephews\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                1, i, FEMALE, MALE, 'f', relstr, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 9:
        print('\ntesting unknown nephews/nieces\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                1, i, FEMALE, UNKNOWN, 'f', relstr, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 10:
        print('\ntesting uncles\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                i, 1, FEMALE, MALE, relstr, 'f', only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 11:
        print('\ntesting aunts\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstr = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                i, 1, MALE, FEMALE, relstr, 'f', only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 12:
        print('\ntesting unknown uncles/aunts\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstr = _rand_relstr(i, 'm')
            rel = FMT % rcalc.get_single_relationship_string(
                i, 1, MALE, UNKNOWN, relstr, 'm', only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstr)
            else:
                print(rel)
    if test_num == 0 or test_num == 13:
        print('\ntesting male cousins same generation\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstra = _rand_relstr(i, 'f')
            relstrb = _rand_relstr(i, 'f')
            rel = FMT % rcalc.get_single_relationship_string(
                i, i, MALE, MALE, relstra, relstrb, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstra, relstrb)
            else:
                print(rel)
    if test_num == 0 or test_num == 14:
        print('\ntesting female cousins same generation\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstra = _rand_relstr(i, 'm')
            relstrb = _rand_relstr(i, 'm')
            rel = FMT % rcalc.get_single_relationship_string(
                i, i, MALE, FEMALE, relstra, relstrb, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstra, relstrb)
            else:
                print(rel)
    if test_num == 0 or test_num == 15:
        print('\ntesting unknown cousins same generation\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            relstra = _rand_relstr(i, 'm')
            relstrb = _rand_relstr(i, 'm')
            rel = FMT % rcalc.get_single_relationship_string(
                i, i, MALE, UNKNOWN, relstra, relstrb, only_birth=onlybirth,
                in_law_a=inlawa, in_law_b=inlawb)
            if printrelstr:
                print(rel + ' |info:', relstra, relstrb)
            else:
                print(rel)
    if test_num == 0 or test_num == 16:
        print('\ntesting some cousins up\n')
        #sys.stdin.readline()
        random.seed()
        for i in range(1, MAX):
            for j in range(i, MAX):
                rnd = random.randint(0, 100)
                if rnd < 10:
                    relstra = _rand_relstr(j, 'f')
                    relstrb = _rand_relstr(i, 'f')
                    if rnd < 5:
                        rel = (FMT + ' |info: female, Ga=%2d, Gb=%2d') % (
                            rcalc.get_single_relationship_string(
                                j, i, MALE, FEMALE, relstra, relstrb,
                                only_birth=onlybirth,
                                in_law_a=inlawa, in_law_b=inlawb), j, i)
                        if printrelstr:
                            print(rel + ' |info:', relstra, relstrb)
                        else:
                            print(rel)
                    else:
                        rel = (FMT + ' |info:   male, Ga=%2d, Gb=%2d') % (
                            rcalc.get_single_relationship_string(
                                j, i, MALE, MALE, relstra, relstrb,
                                only_birth=onlybirth,
                                in_law_a=inlawa, in_law_b=inlawb), j, i)
                        if printrelstr:
                            print(rel + ' |info:', relstra, relstrb)
                        else:
                            print(rel)
    if test_num == 0 or test_num == 17:
        print('\ntesting some cousins down\n')
        #sys.stdin.readline()
        for i in range(1, MAX):
            for j in range(i, MAX):
                rnd = random.randint(0, 100)
                if rnd < 10:
                    relstra = _rand_relstr(i, 'f')
                    relstrb = _rand_relstr(j, 'f')
                    if rnd < 5:
                        rel = (FMT + ' |info: female, Ga=%2d, Gb=%2d') % (
                            rcalc.get_single_relationship_string(
                                i, j, MALE, FEMALE, relstra, relstrb,
                                only_birth=onlybirth,
                                in_law_a=inlawa, in_law_b=inlawb), i, j)
                        if printrelstr:
                            print(rel + ' |info:', relstra, relstrb)
                        else:
                            print(rel)
                    else:
                        rel = (FMT + ' |info:   male, Ga=%2d, Gb=%2d') % (
                            rcalc.get_single_relationship_string(
                                i, j, MALE, MALE, relstra, relstrb,
                                only_birth=onlybirth,
                                in_law_a=inlawa, in_law_b=inlawb), i, j)
                        if printrelstr:
                            print(rel + ' |info:', relstra, relstrb)
                        else:
                            print(rel)

def _testsibling(rcalc):
    vals = [(rcalc.NORM_SIB, 'sibling'),
            (rcalc.HALF_SIB_MOTHER, 'half sib mother side'),
            (rcalc.HALF_SIB_FATHER, 'half sib father side'),
            (rcalc.STEP_SIB, 'step sib'),
            (rcalc.UNKNOWN_SIB, 'undetermined sib')]
    for gendr, strgen in [(MALE, 'male'),
                          (FEMALE, 'female'),
                          (UNKNOWN, 'unknown')]:
        for inlaw in [False, True]:
            for sibt, text in vals:
                print(FMT % rcalc.get_sibling_relationship_string(
                    sibt, MALE, gendr, in_law_a=inlaw) +
                      ' |info:', text, strgen)

def _test_spouse(rcalc):
    vals = [(rcalc.PARTNER_MARRIED, 'married'),
            (rcalc.PARTNER_UNMARRIED, 'unmarried'),
            (rcalc.PARTNER_CIVIL_UNION, 'civil union'),
            (rcalc.PARTNER_UNKNOWN_REL, 'unknown rel'),
            (rcalc.PARTNER_EX_MARRIED, 'ex-married'),
            (rcalc.PARTNER_EX_UNMARRIED, 'ex-unmarried'),
            (rcalc.PARTNER_EX_CIVIL_UNION, 'ex civil union'),
            (rcalc.PARTNER_EX_UNKNOWN_REL, 'ex unknown rel')]

    for gender, strgen in [(MALE, 'male'),
                           (FEMALE, 'female'),
                           (UNKNOWN, 'unknown')]:
        for spouse_type, text in vals:
            print(FMT % rcalc.get_partner_relationship_string(
                spouse_type, MALE, gender) +
                  ' |info: gender='+strgen+', rel='+text)

def test(rcalc, printrelstr):
    """
    This is a generic test suite for the singular relationship
    TRANSLATORS: do NOT translate, call this from
                 __main__ in the rel_xx.py module.
    """
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Test the Relationship Calculator')
    parser.add_argument('-r', type=int, help='type of the relations test')
    parser.add_argument('-s', type=int, help='type of the singular relationship test')

    args = parser.parse_args()
    test_num = args.r

    if test_num is None:
        print("""
Select a test:
  0 - all tests
  1 - Test normal relations
  2 - Test step relations
  3 - Test in-law relations (first pers)
  4 - Test step and in-law relations
  5 - Test sibling types
  6 - Test partner types

Letter 'f' means Father, 'm' means Mother

Please enter a test number and press Enter for continue:
    """)
        test_num = sys.stdin.readline().strip()
        test_num = int(test_num)

    if test_num == 0 or test_num == 1:
        print('\n\n=== Test normal relations ===')
        _test(rcalc, True, False, False, printrelstr, args.s)

    if test_num == 0 or test_num == 2:
        print('\n\n=== Test step relations ===')
        _test(rcalc, False, False, False, printrelstr, args.s)

    if test_num == 0 or test_num == 3:
        print('\n\n=== Test in-law relations (first pers) ===')
        _test(rcalc, True, True, False, printrelstr, args.s)

    if test_num == 0 or test_num == 4:
        print('\n\n=== Test step and in-law relations ===')
        _test(rcalc, False, True, False, printrelstr, args.s)

    if test_num == 0 or test_num == 5:
        print('\n\n=== Test sibling types ===')
        _testsibling(rcalc)

    if test_num == 0 or test_num == 6:
        print('\n\n=== Test partner types ===')
        _test_spouse(rcalc)

if __name__ == "__main__":
    """
    TRANSLATORS, copy this if statement at the bottom of your
    rel_xx.py module, after adding: 'from Relationship import test'
    and test your work with:
    export PYTHONPATH=/path/to/gramps/src
    python src/plugins/rel_xx.py

    See eg rel_fr.py at the bottom
    """
    REL_CALC = RelationshipCalculator()
    test(REL_CALC, True)
