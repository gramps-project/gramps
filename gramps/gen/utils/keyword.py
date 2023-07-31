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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Keyword translation interface
"""

# keyword, code, translated standard, translated upper
# in gen.display.name.py we find:
#        't' : title      = title
#        'f' : given      = given (first names)
#        'l' : surname    = full surname (lastname)
#        'c' : call       = callname
#        'x' : common     = nick name if existing, otherwise first first name (common name)
#        'i' : initials   = initials of the first names
#        'm' : primary    = primary surname (main)
#        '0m': primary[pre]= prefix primary surname (main)
#        '1m': primary[sur]= surname primary surname (main)
#        '2m': primary[con]= connector primary surname (main)
#        'y' : patronymic = pa/matronymic surname (father/mother) - assumed unique
#        '0y': patronymic[pre] = prefix      "
#        '1y': patronymic[sur] = surname     "
#        '2y': patronymic[con] = connector   "
#        'o' : notpatronymic = surnames without pa/matronymic and primary
#        'r' : rest       = non primary surnames
#        'p' : prefix     = list of all prefixes
#        'q' : rawsurnames = surnames without prefixes and connectors
#        's' : suffix     = suffix
#        'n' : nickname   = nick name
#        'g' : familynick = family nick name

from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

KEYWORDS = [
    ("title", "t", _("Title", "Person"), _("TITLE", "Person")),
    ("given", "f", _("Given"), _("GIVEN")),
    ("surname", "l", _("Surname"), _("SURNAME")),
    ("call", "c", _("Call", "Name"), _("CALL", "Name")),
    ("common", "x", _("Common", "Name"), _("COMMON", "Name")),
    ("initials", "i", _("Initials"), _("INITIALS")),
    ("suffix", "s", _("Suffix"), _("SUFFIX")),
    ("primary", "m", _("Primary", "Name"), _("PRIMARY")),
    ("primary[pre]", "0m", _("Primary[pre]"), _("PRIMARY[PRE]")),
    ("primary[sur]", "1m", _("Primary[sur]"), _("PRIMARY[SUR]")),
    ("primary[con]", "2m", _("Primary[con]"), _("PRIMARY[CON]")),
    ("patronymic", "y", _("Patronymic"), _("PATRONYMIC")),
    ("patronymic[pre]", "0y", _("Patronymic[pre]"), _("PATRONYMIC[PRE]")),
    ("patronymic[sur]", "1y", _("Patronymic[sur]"), _("PATRONYMIC[SUR]")),
    ("patronymic[con]", "2y", _("Patronymic[con]"), _("PATRONYMIC[CON]")),
    ("rawsurnames", "q", _("Rawsurnames"), _("RAWSURNAMES")),
    ("notpatronymic", "o", _("Notpatronymic"), _("NOTPATRONYMIC")),
    ("prefix", "p", _("Prefix"), _("PREFIX")),
    ("nickname", "n", _("Nickname"), _("NICKNAME")),
    ("familynick", "g", _("Familynick"), _("FAMILYNICK")),
]
KEY_TO_TRANS = {}
TRANS_TO_KEY = {}
for key, code, standard, upper in KEYWORDS:
    KEY_TO_TRANS[key] = standard
    KEY_TO_TRANS[key.upper()] = upper
    KEY_TO_TRANS["%" + ("%s" % code)] = standard
    KEY_TO_TRANS["%" + ("%s" % code.upper())] = upper
    TRANS_TO_KEY[standard.lower()] = key
    TRANS_TO_KEY[standard] = key
    TRANS_TO_KEY[upper] = key.upper()


def get_translation_from_keyword(keyword):
    """Return the translation of keyword"""
    return KEY_TO_TRANS.get(keyword, keyword)


def get_keyword_from_translation(word):
    """Return the keyword of translation"""
    return TRANS_TO_KEY.get(word, word)


def get_keywords():
    """Get all keywords, longest to shortest"""
    keys = list(KEY_TO_TRANS.keys())
    keys.sort(key=lambda a: len(a), reverse=True)
    return keys


def get_translations():
    """Get all translations, longest to shortest"""
    trans = list(TRANS_TO_KEY.keys())
    trans.sort(key=lambda a: len(a), reverse=True)
    return trans
