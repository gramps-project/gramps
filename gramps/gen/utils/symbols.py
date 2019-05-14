#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015-      Serge Noiraud
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
# https://en.wikipedia.org/wiki/Miscellaneous_Symbols
# http://www.w3schools.com/charsets/ref_utf_symbols.asp
#

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

# pylint: disable=superfluous-parens
# pylint: disable=anomalous-unicode-escape-in-string

class Symbols(object):
    # genealogical symbols
    SYMBOL_FEMALE                    = 0
    SYMBOL_MALE                      = 1
    SYMBOL_ASEXUAL_SEXLESS           = 2 # Unknown
    SYMBOL_LESBIAN                   = 3
    SYMBOL_MALE_HOMOSEXUAL           = 4
    SYMBOL_HETEROSEXUAL              = 5
    SYMBOL_HERMAPHRODITE             = 6
    SYMBOL_TRANSGENDER               = 7
    SYMBOL_NEUTER                    = 8

    SYMBOL_ILLEGITIM                 = 9
    SYMBOL_BIRTH                     = 10
    SYMBOL_BAPTISM                   = 11 # CHRISTENING
    SYMBOL_ENGAGED                   = 12
    SYMBOL_MARRIAGE                  = 13
    SYMBOL_DIVORCE                   = 14
    SYMBOL_UNMARRIED_PARTNERSHIP     = 15
    SYMBOL_BURIED                    = 16
    SYMBOL_CREMATED                  = 17 # Funeral urn
    SYMBOL_KILLED_IN_ACTION          = 18
    SYMBOL_EXTINCT                   = 19

    all_symbols = [
               # Name                     UNICODE       SUBSTITUTION
               (_("Female"),              '\u2640',     ""),
               (_("Male"),                '\u2642',     ""),
               (_("Asexuality, sexless, genderless"), '\u26aa', ""),
               (_("Lesbianism"),          '\u26a2',     "oo"),
               (_("Male homosexuality"),  '\u26a3',     "oo"),
               (_("Heterosexuality"),     '\u26a4',     "oo"),
               (_("Transgender, hermaphrodite (in entomology)"), '\u26a5', ""),
               (_("Transgender"),         '\u26a6',     ""),
               (_("Neuter"),              '\u26b2',     ""),

               (_("Illegitimate"),        '\u229b',     ""),
               (_("Birth"),               '\u002a',     "*"),
               (_("Baptism/Christening"), '\u007e',     "~"),
               (_("Engaged"),             '\u26ac',     "o"),
               (_("Marriage"),            '\u26ad',     "oo"),
               (_("Divorce"),             '\u26ae',     "o|o"),
               (_("Unmarried partnership"), '\u26af',   "o-o"),
               (_("Buried"),              '\u26b0',     "d"),
               (_("Cremated/Funeral urn"), '\u26b1',    "d"),
               (_("Killed in action"),    '\u2694',     "d"),
               (_("Extinct"),             '\u2021',     ""),
              ]

    # genealogical death symbols
    DEATH_SYMBOL_NONE                      = 0
    DEATH_SYMBOL_X                         = 1
    DEATH_SYMBOL_SKULL                     = 2
    DEATH_SYMBOL_ANKH                      = 3
    DEATH_SYMBOL_ORTHODOX_CROSS            = 4
    DEATH_SYMBOL_CHI_RHO                   = 5
    DEATH_SYMBOL_LORRAINE_CROSS            = 6
    DEATH_SYMBOL_JERUSALEM_CROSS           = 7
    DEATH_SYMBOL_STAR_CRESCENT             = 8
    DEATH_SYMBOL_WEST_SYRIAC_CROSS         = 9
    DEATH_SYMBOL_EAST_SYRIAC_CROSS         = 10
    DEATH_SYMBOL_HEAVY_GREEK_CROSS         = 11
    DEATH_SYMBOL_LATIN_CROSS               = 12
    DEATH_SYMBOL_SHADOWED_LATIN_CROSS      = 13
    DEATH_SYMBOL_MALTESE_CROSS             = 14
    DEATH_SYMBOL_STAR_OF_DAVID             = 15
    DEATH_SYMBOL_DEAD                      = 16

    # The following is used in the global preferences in the display tab.
    #                Name
    #                                                  UNICODE    SUBSTITUTION
    death_symbols = [(_("Nothing"),                    "",        ""),
                     ("x",                             "x",       "x"),
                     (_("Skull and crossbones"),       "\u2620",  "+"),
                     (_("Ankh"),                       "\u2625",  "+"),
                     (_("Orthodox cross"),             "\u2626",  "+"),
                     (_("Chi rho"),                    "\u2627",  "+"),
                     (_("Cross of Lorraine"),          "\u2628",  "+"),
                     (_("Cross of Jerusalem"),         "\u2629",  "+"),
                     (_("Star and crescent"),          "\u262a",  "+"),
                     (_("West Syriac cross"),          "\u2670",  "+"),
                     (_("East Syriac cross"),          "\u2671",  "+"),
                     (_("Heavy Greek cross"),          "\u271a",  "+"),
                     (_("Latin cross"),                "\u271d",  "+"),
                     (_("Shadowed White Latin cross"), "\u271e",  "+"),
                     (_("Maltese cross"),              "\u2720",  "+"),
                     (_("Star of David"),              "\u2721",  "+"),
                     (_("Dead"),                       _("Dead"), _("Dead"))
                ]

    def __init__(self):
        self.symbols = None
    #
    # functions for general symbols
    #
    def get_symbol_for_html(self, symbol):
        """ return the html string like '&#9898;' """
        return '&#%d;' % ord(self.all_symbols[symbol][1])

    def get_symbol_name(self, symbol):
        """
        Return the name of the symbol.
        """
        return self.all_symbols[symbol][0]

    def get_symbol_for_string(self, symbol):
        """ return the utf-8 character like '\u2670' """
        return self.all_symbols[symbol][1]

    def get_symbol_fallback(self, symbol):
        """
        Return the replacement string.
        This is used if the utf-8 symbol in not present within a font.
        """
        return self.all_symbols[symbol][2]

    #
    # functions for death symbols
    #
    def get_death_symbols(self):
        """
        Return the list of death symbols.
        This is used in the global preference to choose which symbol we'll use.
        """
        return self.death_symbols

    def get_death_symbol_name(self, symbol):
        """
        Return the name of the symbol.
        """
        return self.death_symbols[symbol][0]

    def get_death_symbol_for_html(self, symbol):
        """
        return the html string like '&#9898;'.
        """
        return '&#%d;' % ord(self.death_symbols[symbol][1])

    def get_death_symbol_for_char(self, symbol):
        """
        Return the utf-8 character for the symbol.
        """
        return self.death_symbols[symbol][1]

    def get_death_symbol_fallback(self, symbol):
        """
        Return the string replacement for the symbol.
        """
        return self.death_symbols[symbol][2]

    #
    # functions for all symbols
    #
    def get_how_many_symbols(self):
        return len(self.death_symbols) + len(self.all_symbols) - 4
