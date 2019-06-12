# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
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

"""Format of commonly used expressions, making use of a cache to not
recompute
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from html import escape

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..lib import EventType
from ..datehandler import get_date
from ..display.name import displayer as name_displayer
from ..display.place import displayer as place_displayer
from .db import (get_birth_or_fallback, get_death_or_fallback,
                 get_marriage_or_fallback)
from gramps.gen.utils.symbols import Symbols

#-------------------------------------------------------------------------
#
# FormattingHelper class
#
#-------------------------------------------------------------------------
class FormattingHelper:
    """Format of commonly used expressions, making use of a cache to not
    recompute
    """
    def __init__(self, dbstate, uistate=None):
        self.dbstate = dbstate
        self.uistate = uistate
        self._text_cache = {}
        self._markup_cache = {}
        self.symbols = Symbols()
        self.reload_symbols()

    def reload_symbols(self):
        self.clear_cache()
        if self.uistate and self.uistate.symbols:
            death_idx = self.uistate.death_symbol
            self.male = self.symbols.get_symbol_for_string(self.symbols.SYMBOL_MALE)
            self.female = self.symbols.get_symbol_for_string(self.symbols.SYMBOL_FEMALE)
            self.bth = self.symbols.get_symbol_for_string(self.symbols.SYMBOL_BIRTH)
            self.marr = self.symbols.get_symbol_for_string(self.symbols.SYMBOL_MARRIAGE)
            self.dth = self.symbols.get_death_symbol_for_char(death_idx)
        else:
            death_idx = self.symbols.DEATH_SYMBOL_LATIN_CROSS
            self.male = self.symbols.get_symbol_fallback(self.symbols.SYMBOL_MALE)
            self.female = self.symbols.get_symbol_fallback(self.symbols.SYMBOL_FEMALE)
            self.marr = self.symbols.get_symbol_fallback(self.symbols.SYMBOL_MARRIAGE)
            self.bth = self.symbols.get_symbol_fallback(self.symbols.SYMBOL_BIRTH)
            self.dth = self.symbols.get_death_symbol_fallback(death_idx)

    def format_relation(self, family, line_count, use_markup=False):
        """ Format a relation between parents of a family
        """
        if not family:
            return ""
        if use_markup:
            if family.handle in self._markup_cache:
                if line_count in self._markup_cache[family.handle]:
                    return self._markup_cache[family.handle][line_count]
        else:
            if family.handle in self._text_cache:
                if line_count in self._text_cache[family.handle]:
                    return self._text_cache[family.handle][line_count]

        text = ""
        marriage = get_marriage_or_fallback(self.dbstate.db, family)
        if marriage and use_markup and marriage.get_type() != EventType.MARRIAGE:
            mdate = "<i>%s %s</i>" % (self.marr, escape(get_date(marriage)))
            mplace = "<i>%s</i>" % escape(self.get_place_name(marriage.get_place_handle()))
            name = "<i>%s</i>" % str(marriage.get_type())
        elif marriage and use_markup:
            mdate = "%s %s" % (self.marr, escape(get_date(marriage)))
            mplace = escape(self.get_place_name(marriage.get_place_handle()))
            name = str(marriage.get_type())
        elif marriage:
            mdate = "%s %s" % (self.marr, get_date(marriage))
            mplace = self.get_place_name(marriage.get_place_handle())
            name = str(marriage.get_type())
        else:
            mdate = ""
            mplace = ""
            name = ""

        if line_count >= 1:
            text += mdate
            text += "\n"
        if line_count >= 2:
            text += name
            text += "\n"
        if line_count >= 3:
            text += mplace
            text += "\n"

        if not text:
            text = str(family.get_relationship())

        if use_markup:
            if not family.handle in self._markup_cache:
                self._markup_cache[family.handle] = {}
            self._markup_cache[family.handle][line_count] = text
        else:
            if not family.handle in self._text_cache:
                self._text_cache[family.handle] = {}
            self._text_cache[family.handle][line_count] = text

        return text

    def get_place_name(self, place_handle):
        """ Obtain a place name
        """
        text = ""
        if place_handle:
            place = self.dbstate.db.get_place_from_handle(place_handle)
            if place:
                place_title = place_displayer.display(self.dbstate.db, place)
                if place_title != "":
                    if len(place_title) > 25:
                        text = place_title[:24]+"..."
                    else:
                        text = place_title
        return text

    def format_person( self, person, line_count, use_markup=False):
        """fromat how info about a person should be presented
        """
        if not person:
            return ""
        if use_markup:
            if person.handle in self._markup_cache:
                if line_count in self._markup_cache[person.handle]:
                    return self._markup_cache[person.handle][line_count]
            name = escape(name_displayer.display(person))
        else:
            if person.handle in self._text_cache:
                if line_count in self._text_cache[person.handle]:
                    return self._text_cache[person.handle][line_count]
            name = name_displayer.display(person)
        text = name
        if line_count >= 3:
            birth = get_birth_or_fallback(self.dbstate.db, person)
            if birth and use_markup and birth.get_type() != EventType.BIRTH:
                bdate = "<i>%s</i>" % escape(get_date(birth))
                bplace = "<i>%s</i>" % escape(self.get_place_name(
                                                    birth.get_place_handle()))
            elif birth and use_markup:
                bdate = escape(get_date(birth))
                bplace = escape(self.get_place_name(birth.get_place_handle()))
            elif birth:
                bdate = get_date(birth)
                bplace = self.get_place_name(birth.get_place_handle())
            else:
                bdate = ""
                bplace = ""
            death = get_death_or_fallback(self.dbstate.db, person)
            if death and use_markup and death.get_type() != EventType.DEATH:
                ddate = "<i>%s</i>" % escape(get_date(death))
                dplace = "<i>%s</i>" % escape(self.get_place_name(
                                                    death.get_place_handle()))
            elif death and use_markup:
                ddate = escape(get_date(death))
                dplace = escape(self.get_place_name(death.get_place_handle()))
            elif death:
                ddate = get_date(death)
                dplace = self.get_place_name(death.get_place_handle())
            else:
                ddate = ""
                dplace = ""

            if line_count < 5:
                text = "%s\n%s %s\n%s %s" % (name, self.bth, bdate,
                                             self.dth, ddate)
            else:
                text = "%s\n%s %s\n  %s\n%s %s\n  %s" % (name, self.bth, bdate,
                                                         bplace, self.dth,
                                                         ddate, dplace)
        if use_markup:
            if not person.handle in self._markup_cache:
                self._markup_cache[person.handle] = {}
            self._markup_cache[person.handle][line_count] = text
        else:
            if not person.handle in self._text_cache:
                self._text_cache[person.handle] = {}
            self._text_cache[person.handle][line_count] = text
        return text

    def clear_cache( self):
        """clear the cache of kept format strings
        """
        self._text_cache = {}
        self._markup_cache = {}


class ImportInfo:
    """
    Class object that can hold information about the import
    """
    def __init__(self, default_info=None):
        """
        Init of the import class.

        This creates the datastructures to hold info
        """
        if default_info is None:
            self.info = {}
        else:
            self.info = default_info

    def info_text(self):
        """
        Construct an info message from the data in the class.
        """
        text = ""
        for key in self.info:
            # Do not fail; can this fail?
            try:
                text += "%s: %s\n" % (key, self.info[key])
            except:
                pass
        return text
