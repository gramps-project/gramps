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
import fontconfig

# pylint: disable=superfluous-parens
# pylint: disable=anomalous-unicode-escape-in-string

class Symbols(object):
    # genealogical symbols
    SYMBOL_MALE                      = 0
    SYMBOL_FEMALE                    = 1
    SYMBOL_LESBIAN                   = 2
    SYMBOL_MALE_HOMOSEXUAL           = 3
    SYMBOL_HETEROSEXUAL              = 4
    SYMBOL_HERMAPHRODITE             = 5
    SYMBOL_TRANSGENDER               = 6
    SYMBOL_ASEXUAL_SEXLESS           = 7
    SYMBOL_NEUTER                    = 8
    SYMBOL_ILLEGITIM                 = 9
    SYMBOL_BIRTH                     = 10
    SYMBOL_BAPTISATION               = 11 # CHRISTENING
    SYMBOL_ENGAGED                   = 12
    SYMBOL_MARRIAGE                  = 13
    SYMBOL_DIVORCE                   = 14
    SYMBOL_UNMARRIED_PARTNERSHIP     = 15
    SYMBOL_BURIED                    = 16
    SYMBOL_CREMATED                  = 17 # Funeral urn
    SYMBOL_KILLED_IN_ACTION          = 18
    SYMBOL_EXTINCT                   = 19

    all_symbols = [
               # Name                                            (UNICODE char)
               #                      (HTML char) SUBSTITUTION string
               (_("Male"),                                       '\u2642',
                                      "&#9794;",  ""),
               (_("Female"),                                     '\u2640',
                                      "&#9792;",  ""),
               (_("Lesbianism"),                                 '\u26a2',
                                      "&#9890;",  ""),
               (_("Male homosexuality"),                         '\u26a3',
                                      "&#9891;",  ""),
               (_("Heterosexality"),                             '\u26a4',
                                      "&#9892;",  ""),
               (_("Transgender, hermaphrodite (in entomology)"), '\u26a5',
                                      "&#9893;",  ""),
               (_("Transgender"),                                '\u26a6',
                                      "&#9894;",  ""),
               (_("Asexuality, sexless, genderless"),            '\u26aa',
                                      "&#9898;",  ""),
               (_("Neuter"),                                     '\u26b2',
                                      "&#9906;",  ""),
               (_("Illegitim"),                                  '\u229b',
                                      "&#8859;",  ""),
               (_("Birth"),                                      '\u002a',
                                      "&#0042;",  "*"),
               (_("Baptism/Christening"),                        '\u007e',
                                      "&#0126;",  "~"),
               (_("Engaged"),                                    '\u26ac',
                                      "&#9900;",  "o"),
               (_("Marriage"),                                   '\u26ad',
                                      "&#9901;",  "oo"),
               (_("Divorce"),                                    '\u26ae',
                                      "&#9902;",  "o|o"),
               (_("Unmarried partnership"),                      '\u26af',
                                      "&#9903;", "o-o"),
               (_("Buried"),                                     '\u26b0',
                                      "&#9904;", "d"),
               (_("Cremated/Funeral urn"),                       '\u26b1',
                                      "&#9905;", "d"),
               (_("Killed in action"),                           '\u2694',
                                      "&#9908;", "d"),
               (_("Extinct"),                                    '\u2021',
                                      "&#8225;", ""),
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
    #                              (UNICODE char) (HTML char) SUBSTITUTED string
    death_symbols = [(_("Nothing"),
                                    "",         "",        ""),
                 ("x",
                                    "x",        "x",       "x"),
                 (_("Skull and crossbones") +' : \u2620',
                                    "&#9760;",  "\u2620",  "+"),
                 (_("Ankh")                 +' : \u2625',
                                    "&#9765;",  "\u2625",  "+"),
                 (_("Orthodox cross")       +' : \u2626',
                                    "&#9766;",  "\u2626",  "+"),
                 (_("Chi rho")              +' : \u2627',
                                    "&#9767;",  "\u2627",  "+"),
                 (_("Cross of lorraine")    +' : \u2628',
                                    "&#9768;",  "\u2628",  "+"),
                 (_("Cross of jerusalem")   +' : \u2629',
                                    "&#9769;",  "\u2629",  "+"),
                 (_("Star and crescent")    +' : \u262a',
                                    "&#9770;",  "\u262a",  "+"),
                 (_("West syriac cross")    +' : \u2670',
                                    "&#9840;",  "\u2670",  "+"),
                 (_("East syriac cross")    +' : \u2671',
                                    "&#9841;",  "\u2671",  "+"),
                 (_("Heavy greek cross")    +' : \u271a',
                                    "&#10010;", "\u271a",  "+"),
                 (_("Latin cross")          +' : \u271d',
                                    "&#10013;", "\u271d",  "+"),
                 (_("Shadowed White Latin cross")+' : \u271e',
                                    "&#10014;", "\u271e",  "+"),
                 (_("Maltese cross")        +' : \u2720',
                                    "&#10016;", "\u2720",  "+"),
                 (_("Star of david")        +' : \u2721',
                                    "&#10017;", "\u2721",  "+"),
                 (_("Dead"),
                                   _("Dead"),  _("Dead"), _("Dead"))
                ]

    def __init__(self):
        self.symbols = None
    #
    # functions for general symbols
    #
    def get_symbol_for_html(self, symbol):
        """ retun the html string like '&#9898;' """
        return self.all_symbols[symbol][2]

    def get_symbol_for_string(self, symbol):
        """ retun the utf-8 character like '\u2670' """
        return self.all_symbols[symbol][1]

    def get_symbol_replacement(self, symbol):
        """
        Return the replacement string.
        This is used if the utf-8 symbol in not present within a font.
        """
        return self.all_symbols[symbol][3]

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
        The symbol correspond to the selected string for html which is saved
        in the config section for interface.death-symbol
        """
        for element in self.death_symbols:
            if element[1] == symbol:
                return element[0]
        return ""

    def get_death_symbol_for_html(self, symbol):
        """
        return the html string like '&#9898;'.
        Should be used only here for test.
        """
        return self.death_symbols[symbol][1]

    def get_death_symbol_for_char(self, symbol):
        """
        Return the utf-8 character for the symbol.
        """
        return self.death_symbols[symbol][2]

    def get_death_symbol_for_string(self, symbol):
        """
        Return the utf-8 character for the symbol.
        The symbol correspond to the selected string for html which is saved
        in the config section for interface.death-symbol
        """
        for element in self.death_symbols:
            if element[1] == symbol:
                return element[2]
        return ""

    def get_death_symbol_replacement(self, symbol):
        """
        Return the string replacement for the symbol.
        The symbol correspond to the selected string for html which is saved
        in the config section for interface.death-symbol
        """
        for element in self.death_symbols:
            if element[1] == symbol:
                return element[3]
        return ""

    #
    # functions for all symbols
    #
    def get_how_many_symbols(self):
        return len(self.death_symbols) + len(self.all_symbols) - 3

if __name__ == '__main__':
    import random

    SYMBOLS = Symbols()
    print("#")
    print("# TEST for HTML results")
    print("#")

    # test first entry in the tab
    VALUE = SYMBOLS.get_symbol_for_html(SYMBOLS.SYMBOL_MALE)
    if VALUE == "&#9890;":
        EXAMPLE = '<em><font size +1>%s</font></em>' % VALUE
        print("The first element is correct :", VALUE, "example is ", EXAMPLE)
    # test the last entry
    VALUE = SYMBOLS.get_symbol_for_html(SYMBOLS.SYMBOL_EXTINCT)
    if VALUE == "&#10016;":
        EXAMPLE = '<em><font size +1>%s</font></em>' % VALUE
        print("The last element is correct :", VALUE, "example is ", EXAMPLE)
    # test a random entry
    RAND = random.randint(SYMBOLS.SYMBOL_MALE, SYMBOLS.SYMBOL_EXTINCT)
    VALUE = SYMBOLS.get_symbol_for_html(RAND)
    EXAMPLE = '<em><font size +1>%s</font></em>' % VALUE
    print("The element is :", VALUE, " for", RAND, "example is ", EXAMPLE)

    print("#")
    print("# TEST for STRING results")
    print("#")

    # test first entry in the tab
    VALUE = SYMBOLS.get_symbol_for_string(SYMBOLS.SYMBOL_MALE)
    if VALUE == '\u26a2':
        EXAMPLE = '<em><font size +1>%s</font></em>' % VALUE
        print("The first element is correct :", VALUE)
    # test the last entry
    VALUE = SYMBOLS.get_symbol_for_string(SYMBOLS.SYMBOL_EXTINCT)
    if VALUE == '\u26b1':
        print("The last element is correct :", VALUE)
    # test a random entry
    RAND = random.randint(SYMBOLS.SYMBOL_MALE, SYMBOLS.SYMBOL_EXTINCT)
    VALUE = SYMBOLS.get_symbol_for_string(RAND)
    print("The element is :", VALUE, " for", RAND)
    print("#")
    print("# TEST for all genealogical symbols")
    print("#")

    # try to get all the possible response.
    for rand in range(SYMBOLS.SYMBOL_MALE, SYMBOLS.SYMBOL_EXTINCT+1):
        VALUE = SYMBOLS.get_symbol_for_html(rand)
        VALUE1 = SYMBOLS.get_symbol_for_string(rand)
        VALUE2 = SYMBOLS.get_symbol_replacement(rand)
        print("Tha utf-8 char for '%s' is '%s' and the replacement value is '%s'" % (VALUE, VALUE1, VALUE2))

    print("#")
    print("# TEST for death symbol")
    print("#")

    # trying to get the utf-8 char
    VALUE = SYMBOLS.get_death_symbol_for_string("&#9760;")
    VALUE2 = SYMBOLS.get_death_symbol_replacement("&#9760;")
    print("Tha utf-8 char for %s is %s and the replacement value is %s" % ('&#9760;', VALUE, VALUE2))

    # trying to get the utf-8 char from a random value
    RAND = random.randint(SYMBOLS.DEATH_SYMBOL_NONE, SYMBOLS.DEATH_SYMBOL_DEAD)
    VALUE = SYMBOLS.get_death_symbol_for_html(RAND)
    VALUE1 = SYMBOLS.get_death_symbol_for_string(VALUE)
    VALUE2 = SYMBOLS.get_death_symbol_replacement(VALUE)
    print("The utf-8 char for %s is %s and the replacement value is %s" % (VALUE, VALUE1, VALUE2))

    print("#")
    print("# TEST for all death symbol")
    print("#")

    # try to get all the possible response.
    for rand in range(SYMBOLS.DEATH_SYMBOL_NONE, SYMBOLS.DEATH_SYMBOL_DEAD+1):
        VALUE = SYMBOLS.get_death_symbol_for_html(rand)
        VALUE1 = SYMBOLS.get_death_symbol_for_string(VALUE)
        VALUE2 = SYMBOLS.get_death_symbol_replacement(VALUE)
        print("Tha utf-8 char for '%s' is '%s' and the replacement value is '%s'" % (VALUE, VALUE1, VALUE2))


    # test all fonts for your distrib
    print("#")
    print("# TEST for all fonts available on your system")
    print("#")


    FONTS = fontconfig.query()

    print("#")
    print("# you have ", len(FONTS), "fonts on your system.")
    print("#")

    ALL_FONTS = {}
    for rand in range(SYMBOLS.SYMBOL_MALE, SYMBOLS.SYMBOL_EXTINCT+1):
        string = SYMBOLS.get_symbol_for_html(rand)
        VALUE = SYMBOLS.get_symbol_for_string(rand)
        nbx = 0
        for idx in range(0, len(FONTS)):
            font = FONTS[idx]
            fontname = font.family[0][1]
            try:
                vals = ALL_FONTS[fontname]
            except:
                ALL_FONTS[fontname] = []
            if font.has_char(VALUE):
                nbx += 1
                if VALUE not in ALL_FONTS[fontname]:
                    ALL_FONTS[fontname].append(VALUE)
        print("The char '%s' is present in %d font(s)" % (VALUE, nbx))

    for rand in range(SYMBOLS.DEATH_SYMBOL_SKULL, SYMBOLS.DEATH_SYMBOL_DEAD):
        string = SYMBOLS.get_death_symbol_for_html(rand)
        VALUE = SYMBOLS.get_death_symbol_for_string(string)
        NBx = 0
        for idx in range(0, len(FONTS)):
            font = FONTS[idx]
            fontname = font.family[0][1]
            try:
                vals = ALL_FONTS[fontname]
            except:
                ALL_FONTS[fontname] = []
            if font.has_char(VALUE):
                NBx += 1
                if VALUE not in ALL_FONTS[fontname]:
                    ALL_FONTS[fontname].append(VALUE)
        print("The char '%s' is present in %d font(s)" % (VALUE, NBx))

    print("#")
    print("# TEST for all death symbol")
    print("#")
    NB1 = NB2 = 0
    MAX_SYMBOLS = SYMBOLS.get_how_many_symbols()
    for font in ALL_FONTS.keys():
        font_usage = ALL_FONTS[font]
        if not font_usage:
            continue
        NB1 += 1
        if len(font_usage) == MAX_SYMBOLS: # If the font use all the symbols
            NB2 += 1
        if len(font_usage) > MAX_SYMBOLS - 15:
            chars = ""
            for rand in range(SYMBOLS.SYMBOL_MALE, SYMBOLS.SYMBOL_EXTINCT+1):
                char = SYMBOLS.get_symbol_for_string(rand)
                if char not in font_usage:
                    chars += char + ", "
            for rand in range(SYMBOLS.DEATH_SYMBOL_SKULL, SYMBOLS.DEATH_SYMBOL_DEAD):
                charh = SYMBOLS.get_death_symbol_for_html(rand)
                char = SYMBOLS.get_death_symbol_for_string(charh)
                if char not in font_usage:
                    chars += char + ", "
            if chars != "":
                print("Font :", font, ": missing characters are :", chars)

    print("#")
    print("# %d fonts use partialy genealogy symbols." % NB1)
    print("#")
    print("# %d fonts use all genealogy symbols." % NB2)
    print("#")
    print("# These usable fonts for genealogy are :")
    for font in ALL_FONTS.keys():
        font_usage = ALL_FONTS[font]
        if not font_usage:
            continue
        if len(font_usage) == MAX_SYMBOLS: # If the font use all the symbols
            print("# You can use :", font)
    print("#")
