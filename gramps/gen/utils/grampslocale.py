# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
# Copyright (C) 2013       John Ralls
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
GrampsLocale encapsulates localization and locale
initialization. There's a default locale object but more can be
created with a different locale and translation binding to enable
generating reports in languages and locales other than the one used
for the user interface.
"""

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
import gettext
import sys
import os
import locale
import logging
import time

from binascii import hexlify

from .grampstranslation import GrampsTranslations, GrampsNullTranslations

if sys.platform == "darwin":
    from .maclocale import mac_setup_localization

if sys.platform == "win32":
    from .win32locale import win32_locale_init_from_env, win32_locale_bindtextdomain

from .win32locale import _LOCALE_NAMES

LOG = logging.getLogger("." + __name__)
LOG.propagate = True
HAVE_ICU = False
_ICU_ERR = None
_HDLR = None
# GrampsLocale initialization comes before command-line argument
# passing, so one must set the log level directly. The default is
# logging.WARN. Uncomment the following to change it to logging.DEBUG:
# LOG.setLevel(logging.DEBUG)
try:
    from icu import Locale, Collator, ICUError

    HAVE_ICU = True
except ImportError:
    try:
        from PyICU import Locale, Collator, ICUError

        HAVE_ICU = True
    except ImportError as err:
        ERRSTR = str(err)
        # No logger, save the warning message for later.
        _ICU_ERR = (
            f"ICU not loaded because {ERRSTR}. Localization will be "
            "impaired. Use your package manager to install PyICU"
        )

ICU_LOCALES = None
if HAVE_ICU:
    ICU_LOCALES = Locale.getAvailableLocales()
# locales with right-to-left text
_RTL_LOCALES = ("ar", "he")

# locales with less than 70% currently translated
INCOMPLETE_TRANSLATIONS = ("ar", "bg", "sq", "ta", "tr", "zh_HK", "zh_TW")


def _check_gformat():
    """
    Some OS environments do not support the locale.nl_langinfo() method
    of determing month names and other date related information.
    """
    try:
        gformat = locale.nl_langinfo(locale.D_FMT).replace("%y", "%Y")
        # Gramps treats dates with '-' as ISO format, so replace separator
        # on locale dates that use '-' to prevent confict
        gformat = gformat.replace("-", "/")
    except locale.Error:
        # Depending on the locale, the value returned for 20th Feb 2009
        # could be '20/2/2009', '20/02/2009', '20.2.2009', '20.02.2009',
        # '20-2-2009', '20-02-2009', '2009/02/20', '2009.02.20',
        # '2009-02-20', or '09-02-20' so to reduce the possible values to
        # test for, make sure both the month and the day are double digits,
        # preferably greater than 12 for human readablity

        timestr = time.strftime("%x", (2005, 10, 25, 1, 1, 1, 1, 1, 1))

        # Gramps treats dates with '-' as ISO format, so replace separator
        # on locale dates that use '-' to prevent confict
        timestr = timestr.replace("-", "/")

        time2fmt_map = {
            "25/10/2005": "%d/%m/%Y",
            "10/25/2005": "%m/%d/%Y",
            "2005/10/25": "%Y/%m/%d",
            "25.10.2005": "%d.%m.%Y",
            "10.25.2005": "%m.%d.%Y",
            "2005.10.25": "%Y.%m.%d",
        }

        try:
            gformat = time2fmt_map[timestr]
        except KeyError:
            gformat = "%d/%m/%Y"  # default value
    return gformat


# ------------------------------------------------------------------------
#
# GrampsLocale Class
#
# ------------------------------------------------------------------------
class GrampsLocale:
    """
    Encapsulate a locale.  This class is a sort-of-singleton: The
    first instance created will query the environment and OSX defaults
    for missing parameters (precedence is parameters passed to the
    constructor, environment variables LANG, LC_COLLATE, LC_TIME,
    etc., and LANGUAGE, OSX defaults settings when that's the
    platform).  Subsequent calls to the constructor with no or
    identical parameters will return the same Grampslocale
    object. Construction with different parameters will result in a
    new GrampsLocale instance with the specified parameters, but any
    parameters left out will be filled in from the first instance.

    :param localedir: The full path to the top level directory containing the
                      translation files. Defaults to sys.prefix/share/locale.

    :param lang: A single locale value which is used for unset locale.LC_FOO
                 settings.

    :param domain: The name of the applicable translation file. The default is
                   "gramps", indicating files in LC_MESSAGES named gramps.mo.

    :param languages: String with a ':'-separated list of two or five character
                      codes corresponding to subidrectries in the localedir,
                      e.g.: "fr" or "zh_CN".
    """

    DEFAULT_TRANSLATION_STR = "default"
    __first_instance = None
    encoding = None

    def __new__(cls, localedir=None, lang=None, domain=None, languages=None):
        if not GrampsLocale.__first_instance:
            cls.__first_instance = super(GrampsLocale, cls).__new__(cls)
            cls.__first_instance.initialized = False
            return cls.__first_instance

        if not cls.__first_instance.initialized:
            raise RuntimeError(
                "Second GrampsLocale created before " "first one was initialized"
            )
        if cls.__first_instance._matches(localedir, lang, domain, languages):
            return cls.__first_instance

        return super(GrampsLocale, cls).__new__(cls)

    def _matches(self, localedir, lang, domain, languages):
        matches = localedir is None or self.localedir == localedir
        matches = matches and (lang is None or self.lang == lang)
        matches = matches and (domain is None or self.localedomain == domain)
        return matches and (
            languages is None or len(languages) == 0 or self.language == languages
        )

    def _init_from_environment(self):
        def _check_locale(loc):
            if not loc[0]:
                return False
            lang = self.check_available_translations(loc[0])
            if not lang and loc[0].startswith("en"):
                loc = ("en_GB", "UTF-8")
                lang = "en_GB"
            if not lang:
                return False
            self.lang = loc[0]
            self.encoding = loc[1]
            self.language = [lang]
            return True

        _failure = False
        try:
            locale.setlocale(locale.LC_ALL, "")
            if not _check_locale(locale.getlocale(category=locale.LC_MESSAGES)):
                LOG.debug("Usable locale not found, localization " "settings ignored.")
                self.lang = "C"
                self.encoding = "ascii"
                self.language = ["en"]
                _failure = True

        except locale.Error as loc_err:
            LOG.debug("Locale error %s, localization settings ignored.", loc_err)
            self.lang = "C"
            self.encoding = "ascii"
            self.language = ["en"]
            _failure = True

        # LC_MESSAGES
        loc_tuple = locale.getlocale(locale.LC_MESSAGES)
        loc = loc_tuple[0]
        if loc:
            language = self.check_available_translations(loc)
            if language:
                self.language = [language]
            else:
                LOG.debug("No translation for LC_MESSAGES locale %s", loc)

        if HAVE_ICU:
            self.calendar = locale.getlocale(locale.LC_TIME)[0] or self.lang[:5]
            self.collation = locale.getlocale(locale.LC_COLLATE)[0] or self.lang[:5]
        else:
            loc = locale.getlocale(locale.LC_TIME)
            if loc and self.check_available_translations(loc[0]):
                self.calendar = ".".join(loc)
            else:
                self.calendar = self.lang

        loc = locale.getlocale(locale.LC_COLLATE)
        if loc and loc[0]:
            self.collation = ".".join(loc)
        else:
            self.collation = self.lang

        if HAVE_ICU and "COLLATION" in os.environ:
            self.collation = os.environ["COLLATION"]

        # $LANGUAGE overrides $LANG, $LC_MESSAGES
        if "LANGUAGE" in os.environ:
            language = [
                x
                for x in [
                    self.check_available_translations(l)
                    for l in os.environ["LANGUAGE"].split(":")
                ]
                if x
            ]
            if language:
                self.language = language
                if not self.lang.startswith(self.language[0]):
                    LOG.debug(
                        "Overiding locale setting '%s' with " "LANGUAGE setting '%s'",
                        self.lang,
                        self.language[0],
                    )
                    self.lang = self.calendar = self.language[0]
            elif _failure:
                LOG.warning("No valid locale settings found, using US English")

        if __debug__:
            LOG.debug(
                "The locale tformat for '%s' is '%s'", self.lang, _check_gformat()
            )

    def __init_first_instance(self):
        """
        Initialize the primary locale from whatever might be
        available. We only do this once, and the resulting
        GrampsLocale is returned by default.
        """
        global _HDLR
        _HDLR = logging.StreamHandler()
        _HDLR.setFormatter(
            logging.Formatter(fmt="%(name)s.%(levelname)s: " "%(message)s")
        )
        LOG.addHandler(_HDLR)

        # Now that we have a logger set up we can issue the icu error if needed.
        if not HAVE_ICU:
            LOG.warning(_ICU_ERR)

        # Even the first instance can be overridden by passing lang
        # and languages to the constructor. If it isn't (which is the
        # expected behavior), do platform-specific setup:
        if not (self.lang and self.language):
            if sys.platform == "darwin":
                mac_setup_localization(self)
            elif sys.platform == "win32":
                win32_locale_init_from_env(self, HAVE_ICU, ICU_LOCALES)
            else:
                self._init_from_environment()
        else:
            self.calendar = self.collation = self.lang

        if not self.lang:
            self.lang = "en_US.UTF-8"
        if not self.language:
            self.language.append("en")
        if not self.localedir and not self.lang.startswith("en"):
            LOG.warning(
                "No translations for %s were found, setting "
                "localization to U.S. English",
                self.localedomain,
            )
            self.lang = "en_US.UTF-8"
            self.language = ["en"]

        # Next, we need to know what is the encoding from the native
        # environment. This is used by python standard library funcions which
        # localize their output, e.g. time.strftime(). NB: encoding is a class variable.
        if not self.encoding:
            self.encoding = locale.getpreferredencoding() or sys.getdefaultencoding()
        LOG.debug("Setting encoding to %s", self.encoding)

        # Make sure that self.lang and self.language are reflected
        # back into the environment for Gtk to use when its
        # initialized. If self.lang isn't 'C', make sure that it has a
        # 'UTF-8' suffix, because that's all that GtkBuilder can
        # digest.

        # Gtk+ has an 'en' po, but we don't. This is worked-around for
        # our GrampsTranslation class but that isn't used to retrieve
        # translations in GtkBuilder (glade), a direct call to libintl
        # (gettext) is. If 'en' is in the translation list it gets
        # skipped in favor of the next language, which can cause
        # inappropriate translations of strings in glade/ui files. To
        # prevent this, if 'en' is in self.language it's the last
        # entry:

        if "en" in self.language:
            self.language = self.language[: self.language.index("en") + 1]

        # Linux note: You'll get unsupported locale errors from Gtk
        # and untranslated strings if the requisite UTF-8 locale isn't
        # installed. This is particularly a problem on Debian and
        # Debian-derived distributions which by default don't install
        # a lot of locales.
        lang = locale.normalize(self.language[0] if self.language[0] else "C")
        check_lang = lang.split(".")
        if not check_lang[0] in ("C", "en"):
            if len(check_lang) < 2 or check_lang[1] not in ("utf-8", "UTF-8"):
                lang = ".".join((check_lang[0], "UTF-8"))

        os.environ["LANG"] = lang
        # We need to convert 'en' and 'en_US' to 'C' to avoid confusing
        # GtkBuilder when it's retrieving strings from our Glade files
        # since we have neither an en.po nor an en_US.po.

        os.environ["LANGUAGE"] = ":".join(self.language)

        # GtkBuilder uses GLib's g_dgettext wrapper, which oddly is bound
        # with locale instead of gettext. Win32 doesn't support bindtextdomain.
        if self.localedir:
            if sys.platform == "win32":
                win32_locale_bindtextdomain(
                    self.localedomain.encode("utf-8"), self.localedir.encode("utf-8")
                )
            else:
                # bug12278, _build_popup_ui() under linux and macOS
                locale.textdomain(self.localedomain)
                locale.bindtextdomain(self.localedomain, self.localedir)

        self.rtl_locale = False
        if self.language[0] in _RTL_LOCALES:
            self.rtl_locale = True  # right-to-left

    def _init_secondary_locale(self):
        """
        Init a secondary locale. Secondary locales are used to provide
        an alternate localization to the one used for the UI; for
        example, some reports offer the option to use a different
        language.

        This GrampsLocale class does no caching of the secondary locale.
        If any caching is desired it must be done externally.
        """
        if not self.localedir:
            LOG.warning("No Localedir provided, unable to find translations")

        _first = self._GrampsLocale__first_instance
        if not self.localedomain:
            if _first.localedomain:
                self.localedomain = _first.localedomain
            else:
                self.localedomain = "gramps"

        if not self.lang and _first.lang:
            self.lang = _first.lang

        if not self.language:
            if self.lang:
                trans = self.check_available_translations(self.lang)
            if trans:
                self.language = [trans]

        if not self.language and _first.language:
            self.language = _first.language

        self.calendar = self.collation = self.lang

        self.rtl_locale = False
        if self.language[0] in _RTL_LOCALES:
            self.rtl_locale = True  # right-to-left

    def __init__(self, localedir=None, lang=None, domain=None, languages=None):
        """
        Init a GrampsLocale. Run __init_first_instance() to set up the
        environment if this is the first run. Return __first_instance
        otherwise if called without arguments.
        """
        global _HDLR
        # initialized is special, used only for the "first instance",
        # and created by __new__(). It's used to prevent re-__init__ing
        # __first_instance when __new__() returns its pointer.
        if hasattr(self, "initialized") and self.initialized:
            return
        self.localedir = None
        self.collator = None
        self.collation = None
        self.calendar = None
        self.rtl_locale = False
        _first = self._GrampsLocale__first_instance
        # Everything breaks without localedir, so get that set up
        # first.  Warnings are logged in __init_first_instance or
        # _init_secondary_locale if this comes up empty.
        if localedir and os.path.exists(os.path.abspath(localedir)):
            self.localedir = localedir
        elif (
            _first
            and hasattr(_first, "localedir")
            and _first.localedir
            and os.path.exists(os.path.abspath(_first.localedir))
        ):
            self.localedir = _first.localedir
        else:
            LOG.warning(
                "Missing or invalid localedir %s; no translations"
                " will be available.",
                repr(localedir),
            )
        self.lang = lang
        self.localedomain = domain or "gramps"
        if languages:
            self.language = [
                x
                for x in [
                    self.check_available_translations(l) for l in languages.split(":")
                ]
                if x
            ]
        else:
            self.language = None

        if self == _first:
            self._GrampsLocale__init_first_instance()
        else:
            self._init_secondary_locale()

        self.icu_locales = {}
        if HAVE_ICU:
            self.icu_locales["default"] = Locale.createFromName(self.lang)
            if self.collation and self.collation != self.lang:
                collation = Locale.createFromName(self.collation)
                self.icu_locales["collation"] = collation
            else:
                self.icu_locales["collation"] = self.icu_locales["default"]
            try:
                collation = self.icu_locales["collation"]
                self.collator = Collator.createInstance(collation)
            except ICUError as icu_err:
                LOG.warning("Unable to create collator: %s", str(icu_err))
                self.collator = None

        try:
            self.translation = self._get_translation(
                self.localedomain, self.localedir, self.language
            )
        except ValueError:
            LOG.warning(
                "Unable to find translation for languages in %s, " "using US English",
                ":".join(self.language),
            )
            self.translation = GrampsNullTranslations()
            self.translation.lang = "en"

        if _HDLR:
            LOG.removeHandler(_HDLR)
            _HDLR = None
        self._dd = self._dp = None
        # Guards against running twice on the first instance.
        self.initialized = True

    def _get_translation(self, domain=None, localedir=None, languages=None):
        """
        Get a translation of one of our classes. Doesn't return the
        singleton so that it can be used by get_addon_translation()
        """
        if not domain:
            domain = self.localedomain
        if not languages:
            languages = self.language
        if not localedir:
            localedir = self.localedir

        for lang in languages:
            if gettext.find(domain, localedir, [lang]):
                translator = gettext.translation(
                    domain,
                    localedir=localedir,
                    languages=[lang],
                    class_=GrampsTranslations,
                )
                translator.lang = lang
                return translator

            if lang.startswith("en") or lang.startswith("C"):
                translator = GrampsNullTranslations()
                translator.lang = "en"
                return translator

        if not languages or len(languages) == 0:
            LOG.warning("No language provided, using US English")
        else:
            lang_str = ":".join(languages)
            raise ValueError(f"No usable translations in {lang_str}" f" for {domain}")
        translator = GrampsNullTranslations()
        translator.lang = "en"
        return translator

    def _get_language_string(self, lang_code):
        """
        Given a language code of the form "lang_region", return a text string
        representing that language.
        """
        try:
            lang = _LOCALE_NAMES[lang_code][2]
        except KeyError:
            try:
                lang = _LOCALE_NAMES[lang_code[:2]][2]
            except KeyError:
                LOG.debug("Gramps has no translation for %s", lang_code)
                lang = None
        except IndexError:
            LOG.debug("Bad Index for tuple %s\n", _LOCALE_NAMES[lang_code][0])
            lang = None

        if lang:
            return self.translation.gettext(lang)
        return lang

    # -------------------------------------------------------------------------
    #
    # Properties
    #
    # -------------------------------------------------------------------------
    @property
    def date_displayer(self):
        """
        Return the locale's date displayer; if it hasn't already been
        cached, set it from datehandler.LANG_TO_DISPLAY. If one isn't
        available for the selected locale, attempt to fall back on the
        first_instance's locale before settling on the 'C' displayer.

        .. note:: This is the getter for the date_displayer property
        """
        if self._dd:
            return self._dd
        # PyLint will whine about these not being at the top level but putting
        # it there creates a circular import.
        from ..config import config
        from ..datehandler import LANG_TO_DISPLAY as displayers

        try:
            val = config.get("preferences.date-format")
        except AttributeError:
            val = 0

        _first = self._GrampsLocale__first_instance
        if self.calendar in displayers:
            self._dd = displayers[self.calendar](val)
        elif self.calendar and self.calendar[:2] in displayers:
            self._dd = displayers[self.calendar[:2]](val)
        elif self != _first and _first.calendar in displayers:
            self._dd = displayers[_first.calendar](val, blocale=self)
        elif self != _first and _first.calendar and _first.calendar[:2] in displayers:
            self._dd = displayers[_first.calendar[:2]](val, blocale=self)
        else:
            self._dd = displayers["C"](val, blocale=self)

        return self._dd

    @property
    def date_parser(self):
        """
        Return the locale's date parser; if it hasn't already been
        cached, set it from datehandler.LANG_TO_PARSER. If one isn't
        available for the selected locale, attempt to fall back on the
        first_instance's locale before settling on the 'C' parser.

        .. note:: This is the getter for the date_parser property
        """
        if self._dp:
            return self._dp
        # PyLint will whine about this not being at the top level but putting
        # it there creates a circular import.
        from ..datehandler import LANG_TO_PARSER as parsers

        _first = self._GrampsLocale__first_instance
        if self.calendar in parsers:
            self._dp = parsers[self.calendar]()
        elif self.calendar and self.calendar[:2] in parsers:
            self._dp = parsers[self.calendar]()
        elif self != _first and _first.calendar in parsers:
            self._dp = parsers[_first.calendar]()
        elif self != _first and _first.calendar and _first.calendar[:2] in parsers:
            self._dp = parsers[_first.calendar[:2]]()
        else:
            self._dp = parsers["C"]()

        return self._dp

    # -------------------------------------------------------------------------
    #
    # Public Functions
    #
    # -------------------------------------------------------------------------

    def get_localedomain(self):
        """
        Get the LOCALEDOMAIN used for the Gramps application.
        Required by gui/glade.py to pass to Gtk.Builder
        """
        return self.localedomain

    def get_language_list(self):
        """
        Return the list of configured languages.  Used by
        ViewManager.check_for_updates to select the language for the
        addons descriptions.
        """
        return self.language

    def locale_code(self):
        """
        Return the locale code.
        """
        return self.lang

    def get_addon_translator(self, filename, domain="addon", languages=None):
        """
        Get a translator for an addon.

        :param filename: filename of a file in directory with full path, or
                         None to get from self.
        :param domain: the name of the .mo file under the LANG/LC_MESSAGES dir
        :param languages: a list of languages to force
        :returns: a gettext.translation object

        Example::

        _ = glocale.get_addon_translator(languages=["fr_BE.utf8"]).gettext

        .. seealso:: the python gettext documentation.

        Assumes path/filename = path/locale/LANG/LC_MESSAGES/addon.mo.
        """
        gramps_translator = self._get_translation(languages=languages)

        path = self.localedir
        if filename:
            path = os.path.join(os.path.dirname(os.path.abspath(filename)), "locale")
        if languages:
            addon_translator = self._get_translation(domain, path, languages=languages)
        else:
            addon_translator = self._get_translation(domain, path)
        gramps_translator.add_fallback(addon_translator)
        return gramps_translator  # with a language fallback

    def get_available_translations(self, localedir=None, localedomain=None):
        """
        Get a list of available translations.

        :returns: A list of translation languages.
        :rtype: unicode[]

        """
        languages = ["en"]

        if not localedir and self.localedir:
            localedir = self.localedir
        else:
            return languages

        if not localedomain and self.localedomain:
            localedomain = self.localedomain
        else:
            localedomain = "gramps"

        for langdir in os.listdir(self.localedir):
            mofilename = os.path.join(
                localedir, langdir, "LC_MESSAGES", f"{localedomain}.mo"
            )
            if os.path.exists(mofilename):
                languages.append(langdir)

        languages.sort()

        return languages

    def check_available_translations(self, loc):
        """
        Test a locale for having a translation available
        locale -- string with standard language code, locale code, or name
        """
        if not self.localedir:
            return None
        # Note that this isn't a typo for self.language; self.language
        # is cached so we don't have to query the file system every
        # time this function is called.
        if not hasattr(self, "languages"):
            self.languages = self.get_available_translations()

        if not loc:
            return None

        if loc[:5] in self.languages:
            return loc[:5]
        # US English is the outlier, all other English locales want real English:
        if loc[:2] == "en" and loc[:5] != "en_US":
            return "en_GB"
        if loc[:2] in self.languages:
            return loc[:2]
        return None

    def get_language_dict(self):
        """
        return a dictionary of language names : codes for use by language
        pickers.
        """
        return {
            self._get_language_string(code): code
            for code in self.get_available_translations()
            if self._get_language_string(code)
        }

    def trans_objclass(self, objclass_str):
        """
        Translates objclass_str into "... %s", where objclass_str
        is 'Person', 'person', 'Family', 'family', etc.
        """
        _ = self.translation.gettext
        objclass = objclass_str.lower()
        if objclass == "person":
            retval = _("the person")
        elif objclass == "family":
            retval = _("the family")
        elif objclass == "place":
            retval = _("the place")
        elif objclass == "event":
            retval = _("the event")
        elif objclass == "repository":
            retval = _("the repository")
        elif objclass == "note":
            retval = _("the note")
        elif objclass == "media":
            retval = _("the media")
        elif objclass == "source":
            retval = _("the source")
        elif objclass == "filter":
            retval = _("the filter")
        elif objclass == "citation":
            retval = _("the citation")
        else:
            retval = _("See details")

        return retval

    def sort_key(self, string):
        """
        Return a value suitable to pass to the "key" parameter of sorted()
        """

        if HAVE_ICU and self.collator:
            # ICU can digest strings and unicode
            # Use hexlify() as to make a consistent string, fixing bug #10077
            key = self.collator.getCollationKey(string)
            return hexlify(key.getByteArray()).decode()

        if isinstance(string, bytes):
            string = string.decode("utf-8", "replace")
        try:
            key = locale.strxfrm(string)
        except ICUError as icu_err:
            LOG.warning(
                "Failed to obtain key for %s because %s", self.collation, str(icu_err)
            )
            return string
        return key

    def get_collation(self):
        """
        Return the collation without any character encoding.
        """
        if self.collation is not None:
            return self.collation.split(".")[0]
        return "C"

    def strcoll(self, string1, string2):
        """
        Given two localized strings, compare them and return -1 if
        string1 would sort first, 1 if string2 would, and 0 if
        they are the same.
        """
        key1 = self.sort_key(string1)
        key2 = self.sort_key(string2)
        return -1 if key1 < key2 else (1 if key1 > key2 else 0)

    def get_date(self, date):
        """
        Return a string representing the date appropriate for the language being
        translated.

        :param date: The date to be represented.
        :type date: :class:`~gen.lib.date.Date`
        :returns: The date as text in the proper language.
        :rtype: unicode
        """
        return self.date_displayer.display(date)

    def get_type(self, name):
        """
        Return a string representing the name appropriate for the language being
        translated.

        :param name: The name type to be represented.
        :returns: The name as text in the proper language.
        :rtype: unicode
        """
        # PyLint will complain about this not being at top level but putting it there
        # creates a circular import.
        from ..lib.grampstype import GrampsType

        return GrampsType.xml_str(name)

    def format_string(self, fmt, val, grouping=False, monetary=False):
        """
        Format a string in the current numeric locale. See python's
        locale.format_string for details.  ICU's message formatting codes are
        incompatible with locale's, so just use locale.format_string
        for now.
        """
        return locale.format_string(fmt, val, grouping, monetary)

    def float(self, val):
        """
        Parse a string to a floating point number. Uses locale.atof(),
        in future with ICU present will use icu.NumberFormat.parse().
        """
        try:
            return locale.atof(val)
        except ValueError:
            point = locale.localeconv()["decimal_point"]
            sep = locale.localeconv()["thousands_sep"]
            try:
                if point == ",":
                    return locale.atof(val.replace(" ", sep).replace(".", sep))
                if point == ".":
                    return locale.atof(val.replace(" ", sep).replace(",", sep))
                return None
            except ValueError:
                return None
