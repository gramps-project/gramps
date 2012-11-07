#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
# Copyright (C) 2012       Mathieu MD
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------

"""
French-specific classes for parsing and displaying dates.
"""
from __future__ import unicode_literals
import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------

from ..lib.date import Date
from ._dateparser import DateParser
from ._datedisplay import DateDisplay
from ._datehandler import register_datehandler
from . import _grampslocale

#-------------------------------------------------------------------------
#
# French parser
#
#-------------------------------------------------------------------------
class DateParserFR(DateParser):
    """
    Convert a text string into a Date object. If the date cannot be
    converted, the text string is assigned.
    """

    month_to_int = DateParser.month_to_int

    # Custom short months not the same as long months

    month_to_int["janv"] = 1
    month_to_int["févr"] = 2
    month_to_int["juil"] = 7
    month_to_int["sept"] = 9
    month_to_int["oct"] = 10
    month_to_int["déc"] = 12

    # Add common value

    month_to_int["bluviose"] = 5
    month_to_int["vendose"] = 6
    month_to_int["7bre"] = 9
    month_to_int["8bre"] = 10
    month_to_int["9bre"] = 11
    month_to_int["10bre"] = 12
    month_to_int["xbre"] = 12

    # Add common latin

    month_to_int["januaris"] = 1
    month_to_int["januarii"] = 1
    month_to_int["januarius"] = 1
    month_to_int["februaris"] = 2
    month_to_int["februarii"] = 2
    month_to_int["februarius"] = 2
    month_to_int["martii"] = 3
    month_to_int["martius"] = 3
    month_to_int["aprilis"] = 4
    month_to_int["maius"] = 5
    month_to_int["maii"] = 5
    month_to_int["junius"] = 6
    month_to_int["junii"] = 6
    month_to_int["julius"] = 7
    month_to_int["julii"] = 7
    month_to_int["augustus"] = 8
    month_to_int["augusti"] = 8
    month_to_int["septembris"] = 9
    month_to_int["7bris"] = 9
    month_to_int["september"] = 9
    month_to_int["october"] = 10
    month_to_int["octobris"] = 10
    month_to_int["8bris"] = 10
    month_to_int["novembris"] = 11
    month_to_int["9bris"] = 11
    month_to_int["november"] = 11
    month_to_int["decembris"] = 12
    month_to_int["10bris"] = 12
    month_to_int["xbris"] = 12
    month_to_int["december"] = 12

    #local and historical variants
    # Add common on east france

    month_to_int["janer"] = 1
    month_to_int["jenner"] = 1
    month_to_int["hartmonat"] = 1
    month_to_int["hartung"] = 1
    month_to_int["eismond"] = 1
    month_to_int["hornung"] = 2
    month_to_int["wintermonat"] = 2
    month_to_int["taumond"] = 2
    month_to_int["narrenmond"] = 2
    month_to_int["lenzing"] = 3
    month_to_int["ostermond"] = 4
    month_to_int["wonnemond"] = 5
    month_to_int["wiesenmonat"] = 5
    month_to_int["brachet"] = 6
    month_to_int["heuet"] = 7
    month_to_int["ernting"] = 8
    month_to_int["scheiding"] = 9
    month_to_int["gilbhard"] = 10
    month_to_int["nebelmonat"] = 11
    month_to_int["nebelung"] = 11
    month_to_int["julmond"] = 12

    modifier_to_int = {
        'avant': Date.MOD_BEFORE,
        'av.'  : Date.MOD_BEFORE,
        #u'av'  : Date.MOD_BEFORE, # Broke Hebrew "Av" month name
        #u'<'    : Date.MOD_BEFORE, # Worrying about XML/HTML parsing
        'après': Date.MOD_AFTER,
        'ap.'  : Date.MOD_AFTER,
        'ap'   : Date.MOD_AFTER,
        #u'>'    : Date.MOD_AFTER, # Worrying about XML/HTML parsing
        'environ'  : Date.MOD_ABOUT,
        'env.'     : Date.MOD_ABOUT,
        'env'      : Date.MOD_ABOUT,
        'circa'    : Date.MOD_ABOUT,
        'ca.'      : Date.MOD_ABOUT,
        'ca'       : Date.MOD_ABOUT,
        'c.'       : Date.MOD_ABOUT,
        'vers'     : Date.MOD_ABOUT,
        '~'        : Date.MOD_ABOUT,
        }

    calendar_to_int = {
        'grégorien': Date.CAL_GREGORIAN,
        'g'        : Date.CAL_GREGORIAN,
        'julien': Date.CAL_JULIAN,
        'j'     : Date.CAL_JULIAN,
        'hébreu': Date.CAL_HEBREW,
        'h'     : Date.CAL_HEBREW,
        'islamique': Date.CAL_ISLAMIC,
        'i'        : Date.CAL_ISLAMIC,
        'révolutionnaire': Date.CAL_FRENCH,
        'r'              : Date.CAL_FRENCH,
        'perse': Date.CAL_PERSIAN,
        'p'    : Date.CAL_PERSIAN,
        'suédois': Date.CAL_SWEDISH,
        's'      : Date.CAL_SWEDISH,
        }

    quality_to_int = {
        'estimée': Date.QUAL_ESTIMATED,
        'est.'   : Date.QUAL_ESTIMATED,
        'est'    : Date.QUAL_ESTIMATED,
        'calculée': Date.QUAL_CALCULATED,
        'calc.'   : Date.QUAL_CALCULATED,
        'calc'    : Date.QUAL_CALCULATED,
        'comptée' : Date.QUAL_CALCULATED,
        'compt.'  : Date.QUAL_CALCULATED,
        'compt'   : Date.QUAL_CALCULATED,
        }

    bce = ["avant le calendrier", "avant notre ère", "avant JC",
           "avant J.C"] + DateParser.bce

    def init_strings(self):
        """
        This method compiles regular expression strings for matching dates.
        
        Most of the re's in most languages can stay as is. span and range
        most likely will need to change. Whatever change is done, this method
        may be called first as DateParser.init_strings(self) so that the
        invariant expresions don't need to be repeteadly coded. All differences
        can be coded after DateParser.init_strings(self) call, that way they
        override stuff from this method. See DateParserRU() as an example.
        """
        DateParser.init_strings(self)

        # This self._numeric is different from the base
        # avoid bug gregorian / french calendar conversion (+/-10 days)

        self._numeric = re.compile("((\d+)[/\. ])?\s*((\d+)[/\.])?\s*(\d+)\s*$")
        self._span = re.compile("(de)\s+(?P<start>.+)\s+(à)\s+(?P<stop>.+)",
                                re.IGNORECASE)
        self._range = re.compile("(entre|ent\.|ent)\s+(?P<start>.+)\s+(et)\s+(?P<stop>.+)",
                                 re.IGNORECASE)

    # This self._text are different from the base
    # by adding ".?" after the first date and removing "\s*$" at the end

    #gregorian and julian

        self._text2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' %
                                 self._mon_str, re.IGNORECASE)

    #hebrew

        self._jtext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' %
                                  self._jmon_str, re.IGNORECASE)

    #french

        self._ftext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' %
                                  self._fmon_str, re.IGNORECASE)

    #persian

        self._ptext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' %
                                  self._pmon_str, re.IGNORECASE)

    #islamic

        self._itext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' %
                                  self._imon_str, re.IGNORECASE)

    #swedish

        self._stext2 = re.compile('(\d+)?.?\s+?%s\s*((\d+)(/\d+)?)?' %
                                  self._smon_str, re.IGNORECASE)

#-------------------------------------------------------------------------
#
# French display
#
#-------------------------------------------------------------------------
class DateDisplayFR(DateDisplay):
    """
    French language date display class. 
    """
    long_months = ( "", "janvier", "février", "mars", "avril", "mai", 
                    "juin", "juillet", "août", "septembre", "octobre", 
                    "novembre", "décembre" )
    
    short_months = ( "", "janv", "févr", "mars", "avril", "mai", "juin", 
                     "juil", "août", "sept", "oct", "nov", "déc" )

    calendar = ("", "Julien", "Hébreu", "Révolutionnaire",
                "Perse", "Islamique", "Suédois")

    _mod_str = ("", "avant ", "après ", "vers ", "", "", "")

    _qual_str = ("", "estimée ", "calculée ", "")

    _bce_str = "%s avant le calendrier"

    # Replace the previous "Numérique" by a string which
    # do have an explicit meaning: "System default (format)"
    _locale_tformat = _grampslocale.tformat
    _locale_tformat = _locale_tformat.replace('%d', "J")
    _locale_tformat = _locale_tformat.replace('%m', "M")
    _locale_tformat = _locale_tformat.replace('%Y', "A")
    
    formats = ("AAAA-MM-JJ (ISO)",  # 0
               "Défaut système (" + _locale_tformat + ")",        # 1
               "Jour Mois Année",   # 2
               "Jour MOI Année",    # 3
               "Jour. Mois Année",  # 4
               "Jour. MOI Année",   # 5
               "Mois Jour, Année",  # 6
               "MOI Jour, Année",   # 7
               )

    def _display_gregorian(self, date_val):
        """
        display gregorian calendar date in different format
        """
        year = self._slash_year(date_val[2], date_val[3])
        if self.format == 0:

            # ISO

            return self.display_iso(date_val)
        elif self.format == 1:

            # ISO

            if date_val[2] < 0 or date_val[3]:
                return self.display_iso(date_val)
            else:
                if date_val[0] == date_val[1] == 0:
                    value = str(date_val[2])
                else:
                    value = self._tformat.replace('%m', str(date_val[1]))
                    value = value.replace('%d', str(date_val[0]))

                    # base_display :
                    # value = value.replace('%Y', str(abs(date_val[2])))
                    # value = value.replace('-', '/')

                    value = value.replace('%Y', str(date_val[2]))
        elif self.format == 2:

            # Day Month Year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:

                value = "%d %s %s" % (date_val[0], 
                                      self.long_months[date_val[1]], year)
        elif self.format == 3:

            # Day MON Year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:

                value = "%d %s %s" % (date_val[0], 
                                      self.short_months[date_val[1]], year)
        elif self.format == 4:

            # Day. Month Year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:

                # base_display :
                # value = "%d %s %s" % (date_val[0], 
                #                       self.long_months[date_val[1]], year)

                value = "%d. %s %s" % (date_val[0], 
                                       self.long_months[date_val[1]],
                                       year)
        elif self.format == 5:

            # Day. MON Year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:

                # base_display :
                # value = "%d %s %s" % (date_val[0], 
                #                       self.short_months[date_val[1]], year)

                value = "%d. %s %s" % (date_val[0], 
                                      self.short_months[date_val[1]], year)
        elif self.format == 6:

            # Month Day, Year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.long_months[date_val[1]], year)
            else:
                value = "%s %d, %s" % (self.long_months[date_val[1]],
                                       date_val[0], year)
        elif self.format == 7:

            # MON Day, Year

            if date_val[0] == 0:
                if date_val[1] == 0:
                    value = year
                else:
                    value = "%s %s" % (self.short_months[date_val[1]], year)
            else:
                value = "%s %d, %s" % (self.short_months[date_val[1]],
                                       date_val[0], year)
        else:
            return self.display_iso(date_val)
                        
        if date_val[2] < 0:
            return self._bce_str % value
        else:
            return value

    def display(self, date):
        """
        Return a text string representing the date.
        """

        mod = date.get_modifier()
        cal = date.get_calendar()
        qual = date.get_quality()
        start = date.get_start_date()
        newyear = date.get_new_year()

        qual_str = (self._qual_str)[qual]

        if mod == Date.MOD_TEXTONLY:
            return date.get_text()
        elif start == Date.EMPTY:
            return ""
        elif mod == Date.MOD_SPAN:
            date1 = self.display_cal[cal](start)
            date2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'de', date1, 'à', 
            date2, scal)
        elif mod == Date.MOD_RANGE:
            date1 = self.display_cal[cal](start)
            date2 = self.display_cal[cal](date.get_stop_date())
            scal = self.format_extras(cal, newyear)
            return "%s%s %s %s %s%s" % (qual_str, 'entre', date1, 'et',
                    date2, scal)
        else:
            text = self.display_cal[date.get_calendar()](start)
            scal = self.format_extras(cal, newyear)
            return "%s%s%s%s" % (qual_str, (self._mod_str)[mod], text, 
            scal)

#-------------------------------------------------------------------------
#
# Register classes
#
#-------------------------------------------------------------------------

register_datehandler(('fr_FR', 'fr', 'french', 'French', 'fr_CA',
                     'fr_BE', 'fr_CH'), DateParserFR, DateDisplayFR)
