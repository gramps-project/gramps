# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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
Validate localized date parser and displayer.

Based on the Check Localized Date Displayer and Parser tool.
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import unittest

import sys
if '-v' in sys.argv or '--verbose' in sys.argv:
    import logging
    logging.getLogger('').addHandler(logging.StreamHandler())
    log = logging.getLogger(".Date")
    log.setLevel(logging.DEBUG)

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ...lib import Date, DateError
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DateHandlerTest(unittest.TestCase):
    
    # See https://stackoverflow.com/questions/4732827/continuing-in-pythons-unittest-when-an-assertion-fails
    def setUp(self):
        self.assertionErrors = []
    
    def tearDown(self):
        self.assertEqual([], self.assertionErrors,
                         'Collected assertionErrors, likely to many to show.')

    def __base_test_all_languages(self, test, dates):
        
        # It would be nice to be able to grab ALL_LINGUAS from setup.py,
        # assuming that these are the languages supported in a release, and from
        # those languages exclude those that are not 100% implemented.
        # The result would go into 'languages' below, i.e. those undergoing test.
        # The tuple 'languages' has been built by looking at 
        # https://www.gramps-project.org/wiki/index.php/Template:Gramps_translations
        # together with the value of ALL_LINGUAS in setup.py.
        # (both as they looked at 2020-08-14)
        # Languages in the intersection are by default excluded from 'languages'
        # and thus removed, .i.e. commented out.
        # There are however two languages included that otherwise should have
        # be removed:
        #   - en_US: Maybe just a mistake to not include it in ALL_LINGUAS
        #   - sr_Latn: Maybe just a mistake to not include it in ALL_LINGUAS.
        #              _date_sr.py registers sr_Latn as well as sr. It is a bit
        #              suspicious though, that the two variants use the same
        #              parser.

        languages = (
            'ar', #PASSED. Uses own display.
                    # Used DateDisplayAR and DateParserAR without correct
                    # environment setting.
            'bg', #PASSED. Uses own display.
                    # Used DateDisplayBG and DateParserBG without correct
                    # environment setting.
            #'br', #PASSED? Missing _date_br.py. Not in ALL_LINGUAS.
                  # Tested with LANGUAGE=en_br, LC_TIME=br.UTF_8.
                  # Used DateDisplayGB and DateParser.
            'ca', #PASSED. Uses own display.
                    # Used DateDisplayCA and DateParserCA without correct
                    # environment setting.
            'cs',   #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayCZ and DateParserCZ without correct
                    # environment setting.
            'da', #PASSED. Uses own display.
                    # Used DateDisplayDa and DateParserDa without correct
                    # environment setting.
            'de', #PASSED. Uses own display.
                    # Used DateDisplayDE and DateParserDE without correct
                    # environment setting.
            'el', #PASSED. Uses own display.
                    # Used DateDisplayEL and DateParserEL without correct
                    # environment setting.
            'en_US', #PASSED. Uses DateDisplayGB.display_formatted.
                     # Tested with LANGUAGE=en_US, LC_TIME=en_US.UTF_8.
                     # Used DateDisplayEn and DateParser.
                     # Not in ALL_LINGUAS. Not needed to be there I guess.
            'en_GB', #PASSED
                    # Used DateDisplayGB and DateParser without correct
                    # environment setting.
            #'en_AU', #FAILED. Finds no parser. Caused by missing en_AU.po?
                    # Not in ALL_LINGUAS.
            #'eo', #FAILED. Missing _date_eo.py.
                     # Tested with LANGUAGE=eo, LC_TIME=eo.UTF_8.
                     # Used DateDisplayGB and DateParser.
            'es', #PASSED. Uses own display.
                    # Used DateDisplayES and DateParserES without correct
                    # environment setting.
            'fi', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayFI and DateParserFI without correct
                    # environment setting.
            'fr', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayFR and DateParserFR without correct
                    # environment setting.
            #'ga', #PASSED? Missing__date_ga.py, Not in ALL_LINGUAS.
                     # Tested with LANGUAGE=ga, LC_TIME=ga.UTF_8.
                     # Used DateDisplayGB and DateParser.
            #'he', #FAILED. Missing _date_he.py.
                     # Tested with LANGUAGE=he, LC_TIME=he.UTF_8.
                     # Used DateDisplayGB and DateParser.
                     # Fails due to that calendar is displayed in lang he and
                     # thus fails to match with the calendar name in English
                     # which the parser expects. Could be temporarily fixed
                     # in he.po by marking calendar translations as fuzzy even
                     # if they are not-
            'hr', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayHR and DateParserHR without correct
                    # environment setting.
            'hu', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayHU and DateParserHU without correct
                    # environment setting.
            'is', #PASSED. Uses own display,
                    # Used DateDisplayIa and DateParserIa without correct
                    # environment setting.
            'it', #PASSED. Uses own display,
                    # Used DateDisplayIT and DateParserIT without correct
                    # environment setting.
            'ja', #PASSED, uses display = DateDisplay.display_formatted.
                    # Used DateDisplayJA and DateParserJA without correct
                    # environment setting.
            'lt', #PASSED. Uses own display.
                    # Used DateDisplayLT and DateParserLT without correct
                    # environment setting.
            #'mk', #PASSED?, Missing_date_mk, Not in ALL_LINGUAS.
                     # Tested with LANGUAGE=mk, LC_TIME=mk.UTF_8.
                     # Used DateDisplayGB and DateParser.
            'nb', #PASSED. Uses own display.
                    # Used DateDisplayNb and DateParserNb without correct
                    # environment setting.
            'nl', #PASSED. Uses own display.
                    # Used DateDisplayNL and DateParserNL without correct
                    # environment setting.
            'nn', #PASSED? Missing__date_nn.py.
                    # Registered by _date_nb.py.
                    # Used DateDisplayNb and DateParserNb without correct
                    # environment setting.
            'pl', #PASSED. Uses own display.
                    # Used DateDisplayPL and DateParserPL without correct
                    # environment setting.
            'pt_BR', #PASSED. Uses own display.
                    # _date_pt.py registers pt_BR.
                    # Used DateDisplayPT and DateParserPT without correct
                    # environment setting.
            'pt_PT', #PASSED. Uses own display in _date_pt.py.
                    # Used DateDisplayPT and DateParserPT without correct
                    # environment setting.
            #'ro', #PASSED? Missing__date_ro.py. Not in ALL_LINGUAS.
                     # Tested with LANGUAGE=ro, LC_TIME=ro.UTF_8.
                     # Used DateDisplayGB and DateParser.
            'ru', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayRU and DateParserRU without correct
                    # environment setting.
            'sk', #PASSED. Uses own display.
                    # Used DateDisplaySK and DateParserSK without correct
                    # environment setting.
            'sl', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplaySL and DateParserSL without correct
                    # environment setting.
            'sq', #PASSED? Missing__date_sq.
                     # Tested with LANGUAGE=sq, LC_TIME=sq.UTF_8.
                     # Used DateDisplayGB and DateParser.
            'sr', #PASSED? Uses own display.
                    # Used DateDisplaySR_Cyrillic and DateParserSR without correct
                    # environment setting.
            'sr_Latn', #PASSED. Uses own display. Not in ALL_LINGUAS.
                    # However, _date_sr.py registers sr_Latn as well.
                    # I guess that is a mistake. 
                    # Used DateDisplaySR_Latin and DateParserSR without correct
                    # environment setting.
            'sv', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplaySv and DateParserSv without correct
                    # environment setting.
            'ta', #PASSED? Missing__date_ta.py,
                     # Tested with LANGUAGE=ta, LC_TIME=ta.UTF_8.
                     # Used DateDisplayGB and DateParser.
            'tr', #PASSED? Missing__date_tr.py.
                     # Tested with LANGUAGE=tr, LC_TIME=tr.UTF_8.
                     # Used DateDisplayGB and DateParser.
            'uk', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayUK and DateParserUK without correct
                    # environment setting.
            #'vi', #FAILED. Missing _date_vi.
                     # Tested with LANGUAGE=vi, LC_TIME=vi.UTF_8.
                     # Used DateDisplayGB and DateParser.
            'zh_CN', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayZH_CN and DateParserZH_CN without correct
                    # environment setting.
            'zh_HK', #PASSED. Missing__date_HK.
                    # Registered by _date_zh_TW.py.
                    # Used DateDisplayZH_TW and DateParserZH_TW without correct
                    # environment setting.
            'zh_TW', #PASSED. Uses display = DateDisplay.display_formatted.
                    # Used DateDisplayZH_TW and DateParserZH_TW without correct
                    # environment setting.
            )
        
        print(flush=True)
        print('   ' + self.__class__.__name__ + '.' + test +
              ': Testing date handling for languages ' + ', '.join(map(str, languages)))

        for language in languages:
            self.__test_language(test, language, dates)
    
    def __test_language(self, test, language, dates):
        
            import os
            environ_keys = ('LANGUAGE', 'LC_ALL', 'LC_LANG',
                            'LC_CTYPE', 'LC_NUMERIC', 'LC_TIME', 'LC_COLLATE',
                            'LC_MONETARY', 'LC_MESSAGES', 'LC_PAPER', 'LC_NAME',
                            'LC_ADDRESS', 'LC_TELEPHONE', 'LC_MEASUREMENT',
                            'LC_IDENTIFICATION')
            saved_environ_values = {}
            for key in environ_keys:
                if key in os.environ:
                    saved_environ_values[key] = os.environ[key]
                    del os.environ[key]
            os.environ['LANGUAGE'] = language
            os.environ['LANG'] = language + '.UTF-8'
            os.environ['LC_ALL'] = language + '.UTF-8'
            from ...utils.grampslocale import GrampsLocale
            locale = GrampsLocale(lang=language)
            displayer = locale.date_displayer
            parser = locale.date_parser
            print('   ... ' + test +
                  ': testing ' + language +
                  ': chosen displayer = ' + displayer.__class__.__name__ +
                  ', chosen parser = ' + parser.__class__.__name__ + ' ... ',
                  end='')
            passed = True
            for test_date in dates:
                datestr = displayer.display(test_date)
                new_date = parser.parse(datestr)
                try:
                    self.assertTrue(test_date.is_equal(new_date),
                                    "language: {}, parser: {}, displayer: {}, dates: {} -> {}, date details: {} -> {}".format(
                                        language,
                                        parser.__class__.__name__,
                                        displayer.__class__.__name__,
                                        test_date, new_date,
                                        test_date.__dict__, new_date.__dict__))
                except AssertionError as e:
                    passed = False
                    self.assertionErrors.append('Error in test ' + test +
                                                   ': ' + str(e))
            if passed:
                print('ok', flush=True)
            else:
                print('FAILED', flush=True)
            for key in saved_environ_values:
                os.environ[key] = saved_environ_values[key]
        
    def test_simple(self):

        dates = []
        for calendar in (Date.CAL_GREGORIAN, Date.CAL_JULIAN):
            for newyear in (Date.NEWYEAR_JAN1, Date.NEWYEAR_MAR25, (5,5)):
                for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                                Date.QUAL_CALCULATED):
                    for modifier in (Date.MOD_NONE, Date.MOD_BEFORE,
                                     Date.MOD_AFTER, Date.MOD_ABOUT):
                        for slash1 in (False,True):
                            for month in range(1, 13):
                                for day in (5, 27):
                                    d = Date()
                                    d.set(quality, modifier, calendar,
                                          (day, month, 1789, slash1),
                                          "Text comment",
                                          newyear)
                                    dates.append(d)
        self.__base_test_all_languages('test_simple', dates)
        
    def test_span(self):

        dates = []
        calendar = Date.CAL_GREGORIAN
        for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                        Date.QUAL_CALCULATED):
            for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
                for slash1 in (False, True):
                    for slash2 in (False, True):
                        for month in range(1, 13):
                            for day in (5, 27):
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       day, month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       day, 13-month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       32-day, month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)
                                d = Date()
                                d.set(quality, modifier, calendar,
                                      (day, month, 1789, slash1,
                                       32-day, 13-month, 1876, slash2),
                                      "Text comment")
                                dates.append(d)
            for slash in (False, True):
                for month in range(1, 13):
                    for day in (5, 27):
                        d = Date()
                        d.set(quality, Date.MOD_SPAN, calendar,
                              (day, month, 1789, slash) + Date.EMPTY,
                              "Text comment")
                        dates.append(d)
                        d = Date()
                        d.set(quality, Date.MOD_SPAN, calendar,
                              Date.EMPTY + (day, month, 1789, slash),
                              "Text comment")
                        dates.append(d)
        self.__base_test_all_languages('test_span', dates)

    def test_textual(self):
        
        dates = []
        calendar = Date.CAL_GREGORIAN
        modifier = Date.MOD_TEXTONLY
        for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                        Date.QUAL_CALCULATED):
            test_date = Date()
            test_date.set(quality, modifier, calendar, Date.EMPTY,
                          "This is a textual date")
            dates.append(test_date)
        self.__base_test_all_languages('test_textual', dates)

    def test_too_few_arguments(self):
        dateval = (4, 7, 1789, False)
        for l in range(1, len(dateval)):
            d = Date()
            with self.assertRaises(DateError):
                d.set(Date.QUAL_NONE, Date.MOD_NONE, Date.CAL_GREGORIAN,
                      dateval[:l], "Text comment")

    def test_too_few_span_arguments(self):
        dateval = (4, 7, 1789, False, 5, 8, 1876, False)
        for l in range(1, len(dateval)):
            d = Date()
            with self.assertRaises(DateError):
                d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                      dateval[:l], "Text comment")
        dateval = (4, 7, 1789, False, 0, 0, 0, False)
        for l in range(1, len(dateval)):
            d = Date()
            with self.assertRaises(DateError):
                d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                      dateval[:l], "Text comment")
        dateval = (0, 0, 0, False, 5, 8, 1876, False)
        for l in range(1, len(dateval)):
            d = Date()
            with self.assertRaises(DateError):
                d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                      dateval[:l], "Text comment")

    def test_invalid_day(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_NONE, Date.CAL_GREGORIAN,
                  (44, 7, 1789,False), "Text comment")

    def test_invalid_month(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE,Date.MOD_NONE, Date.CAL_GREGORIAN,
                  (4, 77, 1789, False), "Text comment")

    def test_invalid_month_with_ny(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE,Date.MOD_NONE, Date.CAL_GREGORIAN,
                  (4, 77, 1789, False), "Text comment", newyear=2)

    def test_invalid_span_day(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  (4, 7, 1789, False, 55, 8, 1876, False), "Text comment")
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  (0, 0, 0, False, 55, 8, 1876, False), "Text comment")
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  (55, 8, 1876, False, 0, 0, 0, False), "Text comment")

    def test_invalid_span_month(self):
        d = Date()
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  (4, 7, 1789, False, 5, 88, 1876, False), "Text comment")
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  ( 0, 0, 0, False, 5, 88, 1876, False), "Text comment")
        with self.assertRaises(DateError):
            d.set(Date.QUAL_NONE, Date.MOD_SPAN, Date.CAL_GREGORIAN,
                  (5, 88, 1876, False, 0, 0, 0, False), "Text comment")

if __name__ == "__main__":
    unittest.main()
