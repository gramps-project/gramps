# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2023       John Ralls
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
win32locale provides l18n setup for the Microsoft Windows platform.
"""
import os
import locale
from ctypes import cdll
import logging

LOG = logging.getLogger("." + __name__)
LOG.propagate = True


# Map of languages for converting to Microsoft locales and naming
# locales for display to the user.  It's important to add to this list
# when a new translation is added.  Note the dummy _(): That's just to
# get xgettext to include the string in gramps.pot; actual translation
# is done in _get_language_string() below.
# (The gramps officially-supported language list is ALL_LINGUAS in setup.py)
def _(msgid):
    return msgid


_LOCALE_NAMES = {
    "ar": ("Arabic_Saudi Arabia", "1256", _("Arabic")),
    "bg": ("Bulgrian_Bulgaria", "1251", _("Bulgarian")),
    # Windows has no translation for Breton
    "br": (None, None, _("Breton")),
    "ca": ("Catalan_Spain", "1252", _("Catalan")),
    "cs": ("Czech_Czech Republic", "1250", _("Czech")),
    "da": ("Danish_Denmark", "1252", _("Danish")),
    "de": ("German_Germany", "1252", _("German")),
    "de_AT": ("German_Austria", "1252", _("German (Austria)")),
    "el": ("Greek_Greece", "1253", _("Greek")),
    "en": ("English_United States", "1252", _("English (USA)")),
    "en_GB": ("English_United Kingdom", "1252", _("English")),
    # Windows has no translation for Esperanto
    "eo": (None, None, _("Esperanto")),
    "es": ("Spanish_Spain", "1252", _("Spanish")),
    "fa": ("Farsi_Iran", "1256", _("Farsi")),
    "fi": ("Finnish_Finland", "1252", _("Finnish")),
    "fr": ("French_France", "1252", _("French")),
    # Windows has no translation for Gaelic
    "ga": (None, None, _("Gaelic")),
    "gl": ("Galician_Spain", "1252", _("Galician")),
    "he": ("Hebrew_Israel", "1255", _("Hebrew")),
    "hr": ("Croatian_Croatia", "1250", _("Croatian")),
    "hu": ("Hungarian_Hungary", "1250", _("Hungarian")),
    "id": ("Indonesian", "1057", _("Indonesian")),
    "is": ("Icelandic", "1252", _("Icelandic")),
    "it": ("Italian_Italy", "1252", _("Italian")),
    "ja": ("Japanese_Japan", "932", _("Japanese")),
    "lt": ("Lithuanian_Lithuania", "1252", _("Lithuanian")),
    # Windows has no translation for Macedonian
    "mk": (None, None, _("Macedonian")),
    "nb": ("Norwegian_Norway", "1252", _("Norwegian Bokmal")),
    "nl": ("Dutch_Netherlands", "1252", _("Dutch")),
    "nn": ("Norwegian-Nynorsk_Norway", "1252", _("Norwegian Nynorsk")),
    "pl": ("Polish_Poland", "1250", _("Polish")),
    "pt_BR": ("Portuguese_Brazil", "1252", _("Portuguese (Brazil)")),
    "pt_PT": ("Portuguese_Portugal", "1252", _("Portuguese (Portugal)")),
    "ro": ("Romanian_Romania", "1250", _("Romanian")),
    "ru": ("Russian_Russia", "1251", _("Russian")),
    "sk": ("Slovak_Slovakia", "1250", _("Slovak")),
    "sl": ("Slovenian_Slovenia", "1250", _("Slovenian")),
    "sq": ("Albanian_Albania", "1250", _("Albanian")),
    "sr": ("Serbian(Cyrillic)_Serbia and Montenegro", "1251", _("Serbian")),
    "sv": ("Swedish_Sweden", "1252", _("Swedish")),
    # Windows has no codepage for Tamil
    "ta": (None, None, _("Tamil")),
    "tr": ("Turkish_Turkey", "1254", _("Turkish")),
    "uk": ("Ukrainian_Ukraine", "1251", _("Ukrainian")),
    "vi": ("Vietnamese_Vietnam", "1258", _("Vietnamese")),
    "zh_CN": ("Chinese_China", "936", _("Chinese (Simplified)")),
    "zh_HK": ("Chinese_Hong Kong", "950", _("Chinese (Hong Kong)")),
    "zh_TW": ("Chinese_Taiwan", "950", _("Chinese (Traditional)")),
}


def _check_mswin_locale(loc):
    msloc = None
    try:
        msloc = _LOCALE_NAMES[loc[:5]][:2]
        newloc = loc[:5]
    except KeyError:
        try:
            msloc = _LOCALE_NAMES[loc[:2]][:2]
            newloc = loc[:2]
        except KeyError:
            # US English is the outlier, all other English locales want
            # real English:
            if loc[:2] == ("en") and loc[:5] != "en_US":
                return ("en_GB", "1252")
            return (None, None)
    return (newloc, msloc)


def _check_mswin_locale_reverse(loc):
    (lang, country) = loc.split("_")
    # US English is the outlier, all other English locales want real English:
    if lang == "English" and country != "United States":
        return ("en_GB", "1252")

    for newloc, msloc in _LOCALE_NAMES.items():
        if not msloc[0] is None and loc == msloc[0]:
            return (newloc, msloc[1])

    # Didn't get a full language-country match, find the first locale
    # with the same language:
    for newloc, msloc in _LOCALE_NAMES.items():
        if loc == msloc[2] or lang == msloc[2]:
            return (newloc, msloc[1])

    return (None, None)


def _set_lang(glocale):
    if "LANG" in os.environ:
        (lang, loc) = _check_mswin_locale(os.environ["LANG"])
        if loc:
            locale.setlocale(locale.LC_ALL, ".".join(loc))
            glocale.lang = lang
            glocale.encoding = loc[1]
        else:
            LOG.debug("%%LANG%% value %s not usable", os.environ["LANG"])
    if not glocale.lang:
        locale.setlocale(locale.LC_ALL, "")
        (pylang, pyenc) = locale.getlocale()
        # Sometimes getlocale returns a Microsoft locale code
        (lang, enc) = _check_mswin_locale_reverse(pylang)
        if not lang is None:
            glocale.lang = lang
            glocale.encoding = enc
        else:  # and sometimes it returns a POSIX locale
            (lang, enc) = _check_mswin_locale(pylang)
            if not lang is None:
                glocale.lang = lang
                glocale.encoding = enc
            else:
                LOG.debug("No usable locale found in environment")

    if not glocale.lang:
        glocale.lang = "C"
        glocale.encoding = "cp1252"


def _set_languages(glocale):
    lang = None
    if "LC_MESSAGES" in os.environ:
        lang = glocale.check_available_translations(os.environ["LC_MESSAGES"])
    if lang:
        glocale.language = [lang]
    else:
        LOG.debug("No translation for %%LC_MESSAGES%% locale")
    if "LANGUAGE" in os.environ:
        language = [
            x
            for x in [
                glocale.check_available_translations(l)
                for l in os.environ["LANGUAGE"].split(":")
            ]
            if x
        ]
        if language:
            glocale.language = language
        else:
            LOG.debug("No languages with translations found " "in %%LANGUAGES%%")
    if not glocale.language:
        glocale.language = [glocale.lang[:5]]


def _set_collation(glocale, have_icu, icu_locales):
    coll = None
    if "COLLATION" in os.environ:
        coll = os.environ["COLLATION"]
        if have_icu:
            if coll[:2] in icu_locales:
                glocale.collation = coll
            else:
                glocale.collation = glocale.lang
        else:
            (coll, loc) = _check_mswin_locale(coll)
            if not loc:
                (coll, loc) = _check_mswin_locale(glocale.lang)
                glocale.collation = ".".join(loc)
                locale.setlocale(locale.LC_COLLATE, glocale.collation)
    else:
        if have_icu:
            glocale.collation = glocale.lang
        else:
            (coll, loc) = _check_mswin_locale(glocale.lang)
            if loc:
                glocale.collation = ".".join(loc)
            else:
                glocale.collation = "C"
                locale.setlocale(locale.LC_COLLATE, glocale.collation)


def _set_calendar(glocale):
    # We can't import datahandler stuff or we'll get a circular
    # dependency, so we rely on the available translations list
    if "LC_TIME" in os.environ:
        glocale.calendar = (
            glocale.check_available_translations(os.environ["LC_TIME"]) or glocale.lang
        )
    else:
        glocale.calendar = glocale.lang


def win32_locale_init_from_env(glocale, have_icu, icu_locales):
    """
    The Windows implementation of Python ignores environment
    variables when setting the locale; it only pays attention to
    the control panel language settings -- which for practical
    purposes limits one to the language for which one purchased
    Windows. This function enables using alternative
    localizations.
    """
    _set_lang(glocale)
    _set_languages(glocale)
    _set_collation(glocale, have_icu, icu_locales)
    _set_calendar(glocale)


def win32_locale_bindtextdomain(localedomain, localedir):
    """
    Help routine for loading and setting up libintl attributes
    Returns libintl
    """
    try:
        libintl = cdll.LoadLibrary("libintl-8")
        libintl.bindtextdomain(localedomain, localedir)
        libintl.textdomain(localedomain)
        libintl.bind_textdomain_codeset(localedomain, "UTF-8")

    except WindowsError:
        LOG.warning(
            "Localization library libintl not on %PATH%, "
            "localization will be incomplete"
        )
