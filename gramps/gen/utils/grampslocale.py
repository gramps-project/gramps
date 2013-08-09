#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from __future__ import print_function
import gettext
import sys
import os
import codecs
import locale
import logging
LOG = logging.getLogger("grampslocale")
HAVE_ICU = False
_hdlr = None
# GrampsLocale initialization comes before command-line argument
# passing, so one must set the log level directly. The default is
# logging.WARN. Uncomment the following to change it to logging.DEBUG:
#LOG.setLevel(logging.DEBUG)
try:
    from icu import Locale, Collator
    HAVE_ICU = True
except ImportError:
    try:
        from PyICU import Locale, Collator
        HAVE_ICU = True
    except ImportError as err:
        LOG.warning("ICU not loaded because %s. Localization will be impaired. "
                    "Use your package manager to install PyICU", str(err))
ICU_LOCALES = None
if HAVE_ICU:
    ICU_LOCALES = Locale.getAvailableLocales()

        #Map our translated language codes to Microsoft Locale Names
        #Important: Maintain this list with new translations or they
        #won't work under MS Windows!
mslocales = {
    'ar': ('Arabic_Saudi Arabia', '1256'),
    'bg': ('Bulgrian_Bulgaria', '1251'),
    'br': None, #Windows has no translation for Breton
    'ca': ('Catalang_Spain', '1252'),
    'cs': ('Czech_Czech Republic', '1250'),
    'da': ('Danish_Denmark', '1252'),
    'de': ('German_Germany', '1252'),
    'en': ('English_United States', '1252'),
    'en_GB': ('English_United Kingdom', '1252'),
    'eo': None, #Windows has no translation for Esperanto
    'es': ('Spanish_Spain', '1252'),
    'fi': ('Finnish_Finland', '1252'),
    'fr': ('French_France', '1252'),
    'ga': None, #Windows has no translation for Gaelic
    'gr':  ('Greek_Greece', '1253'),
    'he': ('Hebrew_Israel', '1255'),
    'hr': ('Croatian_Croatia', '1250'),
    'hu': ('Hungarian_Hungary', '1250'),
    'it': ('Italian_Italy', '1252'),
    'ja': ('Japanese_Japan', '932'),
    'lt': ('Lithuanian_Lithuania', '1252'),
    'mk': None, #Windows has no translation for Macedonian
    'nb': ('Norwegian_Norway', '1252'),
    'nl': ('Dutch_Netherlands', '1252'),
    'nn': ('Norwegian-Nynorsk_Norway', '1252'),
    'pl': ('Polish_Poland', '1250'),
    'pt_BR': ('Portuguese_Brazil', '1252'),
    'pt_PT': ('Portuguese_Portugal', '1252'),
    'ro': ('Romanian_Romania', '1250'),
    'ru': ('Russian_Russia', '1251'),
    'sk': ('Slovak_Slovakia', '1250'),
    'sl': ('Slovenian_Slovenia', '1250'),
    'sq': ('Albanian_Albania', '1250'),
    'sr': ('Serbian(Cyrillic)_Serbia and Montenegro', '1251'),
    'sv': ('Swedish_Sweden', '1252'),
    'tr': ('Turkish_Turkey', '1254'),
    'uk': ('Ukrainian_Ukraine', '1251'),
    'vi': ('Vietnamese_Viet Nam', '1258'),
    'zh_CN': ('Chinese_China', '936'),
    }

def _check_mswin_locale(locale):
    msloc = None
    try:
        msloc = mslocales[locale[:5]]
        locale = locale[:5]
    except KeyError:
        try:
            msloc = mslocales[locale[:2]]
            locale = locale[:2]
        except KeyError:
            return (None, None)
    return (locale, msloc)

def _check_mswin_locale_reverse(locale):
    for (loc, msloc) in mslocales.items():
        if msloc and locale == msloc[0]:
            return (loc, msloc[1])

    return (None, None)

#------------------------------------------------------------------------
#
# GrampsLocale Class
#
#------------------------------------------------------------------------
class GrampsLocale(object):
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

    @localedir: The full path to the top level directory containing
                the translation files. Defaults to sys.prefix/share/locale.

    @lang:      A single locale value which is used for unset locale.LC_FOO
                settings.

    @domain:    The name of the applicable translation file. The default is
                "gramps", indicating files in LC_MESSAGES named gramps.mo.

    @languages: A list of two or five character codes corresponding to
                subidrectries in the localedir, e.g. "fr" or "zh_CN".
    """
    DEFAULT_TRANSLATION_STR = "default"
    __first_instance = None
    encoding = None
    _lang_map = None
    _country_map = None

    def __new__(cls, localedir=None, lang=None, domain=None, languages=None):
        if not GrampsLocale.__first_instance:
            cls.__first_instance = super(GrampsLocale, cls).__new__(cls)
            cls.__first_instance.initialized = False
            return cls.__first_instance

        if not cls.__first_instance.initialized:
            raise RuntimeError("Second GrampsLocale created before first one was initialized")
        if ((lang is None or lang == cls.__first_instance.lang)
            and (localedir is None or localedir == cls.__first_instance.localedir)
            and (domain is None or domain == cls.__first_instance.localedomain)
            and (languages is None or len(languages) == 0 or
                 languages == cls.__first_instance.languages)):
            return cls.__first_instance

        return super(GrampsLocale, cls).__new__(cls)

    def _win_init_environment(self):
        """
        The Windows implementation of Python ignores environment
        variables when setting the locale; it only pays attention to
        the control panel language settings -- which for practical
        purposes limits one to the language for which one purchased
        Windows. This function enables using alternative
        localizations.
        """

        if 'LANG' in os.environ:
            (lang, loc) = _check_mswin_locale(os.environ['LANG'])
            if loc:
                locale.setlocale(locale.LC_ALL, '.'.join(loc))
                self.lang = lang
                self.encoding = loc[1]
            else:
                LOG.debug("%%LANG%% value %s not usable", os.environ['LANG'])
        if not self.lang:
            locale.setlocale(locale.LC_ALL, '')
            (lang, encoding) = locale.getlocale()
            loc = _check_mswin_locale_reverse(lang)
            if loc:
                self.lang = loc[0]
                self.encoding = loc[1]
            else:
                (lang, loc) = _check_mswin_locale(lang)
                if lang:
                    self.lang = lang
                    self.encoding = loc[1]
                else:
                    LOG.debug("No usable locale found in environment")

        if not self.lang:
            self.lang = 'C'
            self.encoding = 'cp1252'

        if 'LC_MESSAGES' in os.environ:
            lang = self.check_available_translations(os.environ['LC_MESSAGES'])
            if lang:
                self.language = [lang]
            else:
                LOG.debug("No translation for %%LC_MESSAGES%% locale")
        if 'LANGUAGE' in os.environ:
            language = [x for x in [self.check_available_translations(l)
                                    for l in os.environ["LANGUAGE"].split(":")]
                        if x]
            if language:
                self.language = language
            else:
                LOG.debug("No languages with translations found in %%LANGUAGES%%")
        if not self.language:
            self.language = [self.lang[:5]]

        if 'LC_COLLATE' in os.environ:
            coll = os.environ['LC_COLLATE']
            if HAVE_ICU:
                if coll[:5] in ICU_LOCALES:
                    self.collation = coll
                else:
                    self.collation = self.lang
            else:
                (coll, loc) = _check_mswin_locale(coll)
                if not loc:
                    (coll, loc) = _check_mswin_locale(self.lang)
                    self.collation = '.'.join(loc)
                    locale.setlocale(locale.LC_COLLATE, self.collation )
        else:
            if HAVE_ICU:
                self.collation = self.lang
            else:
                (coll, loc) = _check_mswin_locale(self.lang)
                if loc:
                    self.collation = '.'.join(loc)
                else:
                    self.collation = 'C'
                locale.setlocale(locale.LC_COLLATE, self.collation )

# We can't import datahandler stuff or we'll get a circular
# dependency, so we rely on the available translations list
        if 'LC_TIME' in os.environ:
            self.calendar = self.check_available_translations(os.environ['LC_TIME']) or self.lang
        else:
            self.calendar = self.lang

        if 'LC_NUMERIC' in os.environ:
            self.numeric = os.environ['LC_NUMERIC']
        else:
            self.numeric = self.lang

        if 'LC_MONETARY' in os.environ:
            self.currency = os.environ['LC_MONETARY']
        else:
            self.currency = self.lang

    def _init_from_environment(self):

        def _check_locale(locale):
            if not locale[0]:
                return False
            lang = self.check_available_translations(locale[0])
            if not lang:
                return False
            self.lang = locale[0]
            self.encoding = locale[1]
            self.language = [lang]
            return True

        _failure = False
        try:
            locale.setlocale(locale.LC_ALL, '')
            if not _check_locale(locale.getlocale()):
                if not _check_locale(locale.getdefaultlocale()):
                    LOG.debug("Usable locale not found, localization settings ignored.");
                    self.lang = 'C'
                    self.encoding = 'ascii'
                    self.language = ['en']
                    _failure = True

        except locale.Error as err:
            LOG.debug("Locale error %s, localization settings ignored.",
                        err);
            self.lang = 'C'
            self.encoding = 'ascii'
            self.language = ['en']
            _failure = True

        #LC_MESSAGES
        (loc, enc) = locale.getlocale(locale.LC_MESSAGES)
        if loc:
            language = self.check_available_translations(loc)
            if language:
                self.language = [language]
            else:
                LOG.debug("No translation for LC_MESSAGES locale %s", loc)

        # $LANGUAGE overrides $LANG, $LC_MESSAGES
        if "LANGUAGE" in os.environ:
            language = [x for x in [self.check_available_translations(l)
                                    for l in os.environ["LANGUAGE"].split(":")]
                            if x]
            if language:
                self.language = language
                if not self.lang.startswith(self.language[0]):
                    LOG.debug("Overiding locale setting %s with LANGUAGE setting %s", self.lang, self.language[0])
            elif _failure:
                LOG.warning("No valid locale settings found, using US English")

        if HAVE_ICU:
            self.calendar = locale.getlocale(locale.LC_TIME)[0] or self.lang[:5]
            self.collation = locale.getlocale(locale.LC_COLLATE)[0] or self.lang[:5]
        else:
            loc = locale.getlocale(locale.LC_TIME)
            if loc and self.check_available_translations(loc[0]):
                self.calendar = '.'.join(loc)
            else:
                self.calendar = self.lang

        loc = locale.getlocale(locale.LC_COLLATE)
        if loc and loc[0]:
            self.collation = '.'.join(loc)
        else:
            self.collation = self.lang

        loc = locale.getlocale(locale.LC_NUMERIC)
        if loc and loc[0]:
            self.numeric = '.'.join(loc)
        else:
            self.numeric = self.lang

        loc = locale.getlocale(locale.LC_MONETARY)
        if loc and loc[0]:
            self.currency = '.'.join(loc)
        else:
            self.currency = self.lang

    def _win_bindtextdomain(self, localedomain, localedir):
        """
        Help routine for loading and setting up libintl attributes
        Returns libintl
        """
        from ctypes import cdll
        try:
            libintl = cdll.LoadLibrary('libintl-8')
            libintl.bindtextdomain(localedomain,
                                   localedir.encode(sys.getfilesystemencoding()))
            libintl.textdomain(localedomain)
            libintl.bind_textdomain_codeset(localedomain, "UTF-8")

        except WindowsError:
            LOG.warning("Localization library libintl not on %PATH%, localization will be incomplete")

    def __init_first_instance(self):
        """
        Initialize the primary locale from whatever might be
        available. We only do this once, and the resulting
        GrampsLocale is returned by default.
        """
        global _hdlr
        _hdlr = logging.StreamHandler()
        _hdlr.setFormatter(logging.Formatter(fmt="%(name)s.%(levelname)s: %(message)s"))
        LOG.addHandler(_hdlr)

        # Even the first instance can be overridden by passing lang
        # and languages to the constructor. If it isn't (which is the
        # expected behavior), do platform-specific setup:
        if not (self.lang and self.language):
            if sys.platform == 'darwin':
                from . import maclocale
                maclocale.mac_setup_localization(self)
            elif sys.platform == 'win32':
                self._win_init_environment()
            else:
                self._init_from_environment()
        else:
            self.numeric = self.currency = self.calendar = self.collation = self.lang

        if not self.lang:
            self.lang = 'en_US.UTF-8'
        if not self.language:
            self.language.append('en')
        if not self.localedir and not self.lang.startswith('en'):
            LOG.warning("No translations for %s were found, setting localization to U.S. English", self.localedomain)
            self.lang = 'en_US.UTF-8'
            self.language = ['en']

#Next, we need to know what is the encoding from the native
#environment. This is used by python standard library funcions which
#localize their output, e.g. time.strftime(). NB: encoding is a class variable.
        if not self.encoding:
            self.encoding = (locale.getpreferredencoding()
                             or sys.getdefaultencoding())
        LOG.debug("Setting encoding to %s", self.encoding)
#Ensure that output is encoded correctly to stdout and stderr. This is
#much less cumbersome and error-prone than encoding individual outputs
#and better handles the differences between Python 2 and Python 3:
        _encoding = sys.stdout.encoding or sys.getdefaultencoding()
        if sys.version_info[0] < 3:
            sys.stdout = codecs.getwriter(_encoding)(sys.stdout,
                                                     'backslashreplace')
            sys.stderr = codecs.getwriter(_encoding)(sys.stderr,
                                                     'backslashreplace')
        else:
            sys.stdout = codecs.getwriter(_encoding)(sys.stdout.detach(),
                                                     'backslashreplace')
            sys.stderr = codecs.getwriter(_encoding)(sys.stderr.detach(),
                                                     'backslashreplace')


        # Make sure that self.lang and self.language are reflected
        # back into the environment for Gtk to use when its
        # initialized. If self.lang isn't 'C', make sure that it has a
        # 'UTF-8' suffix, because that's all that GtkBuilder can
        # digest.

        # Linux note: You'll get unsupported locale errors from Gtk
        # and untranslated strings if the requisite UTF-8 locale isn't
        # installed. This is particularly a problem on Debian and
        # Debian-derived distributions which by default don't install
        # a lot of locales.
        lang = locale.normalize(self.language[0] if self.language[0] else 'C')
        check_lang = lang.split('.')
        if not check_lang[0]  in ('C', 'en'):
            if len(check_lang) < 2  or check_lang[1] not in ("utf-8", "UTF-8"):
                lang = '.'.join((check_lang[0], 'UTF-8'))

        os.environ["LANG"] = lang
        os.environ["LANGUAGE"] = ':'.join([l for l in self.language])

        # GtkBuilder uses GLib's g_dgettext wrapper, which oddly is bound
        # with locale instead of gettext. Win32 doesn't support bindtextdomain.
        if self.localedir:
            if not sys.platform == 'win32':
                locale.bindtextdomain(self.localedomain, self.localedir)
            else:
                self._win_bindtextdomain(self.localedomain, self.localedir)

    def _init_secondary_locale(self):
        """
        Init a secondary locale. Secondary locales are used to provide
        an alternate localization to the one used for the UI; for
        example, some reports offer the option to use a different
        language.
        """
        if not self.localedir:
            LOG.warning("No Localedir provided, unable to find translations")

        if not self.localedomain:
            if _firstlocaledomain:
                self.localedomain = _first.localedomain
            else:
                self.localedomain = "gramps"

        _first = self._GrampsLocale__first_instance
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

    def __init__(self, localedir=None, lang=None, domain=None, languages=None):
        """
        Init a GrampsLocale. Run __init_first_instance() to set up the
        environment if this is the first run. Return __first_instance
        otherwise if called without arguments.
        """
        global _hdlr
        #initialized is special, used only for the "first instance",
        #and created by __new__(). It's used to prevent re-__init__ing
        #__first_instance when __new__() returns its pointer.
        if hasattr(self, 'initialized') and self.initialized:
            return
        _first = self._GrampsLocale__first_instance

        # Everything breaks without localedir, so get that set up
        # first.  Warnings are logged in _init_first_instance or
        # _init_secondary_locale if this comes up empty.
        if localedir and os.path.exists(os.path.abspath(localedir)):
            self.localedir = localedir
        elif _first and _first.localedir:
            self.localedir = _first.localedir
        else:
            self.localedir = None

        self.lang = lang
        self.localedomain = domain or 'gramps'
        if languages:
            self.language = [x for x in [self.check_available_translations(l)
                                         for l in languages.split(":")]
                             if x]
        else:
            self.language = None

         #For alternate collation sequences. Works only with ICU, and
         #set only on Macs.
        self.coll_qualifier = None
        _first = self._GrampsLocale__first_instance
        if self == _first:
            self._GrampsLocale__init_first_instance()
        else:
            self._init_secondary_locale()

        self.icu_locales = {}
        self.collator = None
        if HAVE_ICU:
            self.icu_locales["default"] = Locale.createFromName(self.lang)
            if self.collation and self.collation != self.lang:
                self.icu_locales["collation"] = Locale.createFromName(self.collation)
            else:
                self.icu_locales["collation"] = self.icu_locales["default"]
            try:
                self.collator = Collator.createInstance(self.icu_locales["collation"])
            except ICUError as err:
                LOG.warning("Unable to create collator: %s", str(err))
                self.collator = None

        try:
            self.translation = self._get_translation(self.localedomain,
                                                     self.localedir,
                                                     self.language)
        except ValueError:
            LOG.warning("Unable to find translation for languages in %s, using US English", ':'.join(self.language))
            self.translation = GrampsNullTranslations()
            self.translation._language = "en"

        # This is a no-op for secondaries but needs the translation
        # set, so it needs to be here.
        self._set_dictionaries()

        if _hdlr:
            LOG.removeHandler(_hdlr)

        self._dd = self._dp = None
        #Guards against running twice on the first instance.
        self.initialized = True

    def _get_translation(self, domain = None,
                         localedir = None,
                         languages=None):
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
                translator = gettext.translation(domain, localedir,
                                                 [lang],
                                                 class_ = GrampsTranslations)
                translator._language = lang
                return translator

            elif lang.startswith("en") or lang.startswith("C"):
                translator = GrampsNullTranslations()
                translator._language = "en"
                return translator

        if not languages or len(languages) == 0:
            LOG.warning("No language provided, using US English")
        else:
            raise ValueError("No usable translations in %s" %
                             ':'.join(languages))
        translator = GrampsNullTranslations()
        translator._language = "en"
        return translator

    def _set_dictionaries(self):
        """
        Create a dictionary of language names localized to the
        GrampsLocale's primary language, keyed by language and country
        code. Note that _lang_map and _country_map are class
        variables, so this function is no-op in secondary locales.
        """
        _ = self.translation.gettext
        if not self._lang_map:
            self._lang_map = {
                "ar" : _("Arabic"),
                "bg" : _("Bulgarian"),
                "ca" : _("Catalan"),
                "cs" : _("Czech"),
                "da" : _("Danish"),
                "de" : _("German"),
                "el" : _("Greek"),
                "en" : _("English"),
                "eo" : _("Esperanto"),
                "es" : _("Spanish"),
                "fi" : _("Finnish"),
                "fr" : _("French"),
                "he" : _("Hebrew"),
                "hr" : _("Croatian"),
                "hu" : _("Hungarian"),
                "it" : _("Italian"),
                "ja" : _("Japanese"),
                "lt" : _("Lithuanian"),
                "mk" : _("Macedonian"),
                "nb" : _("Norwegian Bokmal"),
                "nl" : _("Dutch"),
                "nn" : _("Norwegian Nynorsk"),
                "pl" : _("Polish"),
                "pt" : _("Portuguese"),
                "ro" : _("Romanian"),
                "ru" : _("Russian"),
                "sk" : _("Slovak"),
                "sl" : _("Slovenian"),
                "sq" : _("Albanian"),
                "sv" : _("Swedish"),
                "tr" : _("Turkish"),
                "uk" : _("Ukrainian"),
                "vi" : _("Vietnamese"),
                "zh" : _("Chinese")
            }

        if not self._country_map:
            self._country_map = {
                "BR" : _("Brazil"),
                "CN" : _("China"),
                "PT" : _("Portugal")
                }

    def _get_language_string(self, lang_code):
        """
        Given a language code of the form "lang_region", return a text string
        representing that language.
        """
        code_parts = lang_code.rsplit("_")

        lang = code_parts[0]

        if lang in self._lang_map:
            lang = self._lang_map[lang]

        country = None
        if len(code_parts) > 1:
            country = code_parts[1]
        if country in self._country_map:
            country = self._country_map[country]
            lang = "%(language)s (%(country)s)" % \
                { 'language' : lang, 'country'  : country  }

        return lang

#-------------------------------------------------------------------------
#
# Properties
#
#-------------------------------------------------------------------------
    @property
    def date_displayer(self):
        """
        Return the locale's date displayer; if it hasn't already been
        cached, set it from datehandler.LANG_TO_DISPLAY. If one isn't
        available for the selected locale, attempt to fall back on the
        first_instance's locale before settling on the 'C' displayer.
        NB: This is the getter for the date_displayer property
        """
        if self._dd:
            return self._dd

        from gramps.gen.config import config
        try:
            val = config.get('preferences.date-format')
        except AttributeError:
            val = 0;

        from gramps.gen.datehandler import LANG_TO_DISPLAY as displayers
        _first = self._GrampsLocale__first_instance
        if self.calendar in displayers:
            self._dd = displayers[self.calendar](val)
        elif self.calendar[:2] in displayers:
            self._dd = displayers[self.calendar[:2]](val)
        elif self != _first and _first.calendar in displayers:
            self._dd = displayers[_first.calendar](val)
        elif self != _first and _first.calendar[:2] in displayers:
            self._dd = displayers[_first.calendar[:2]](val)
        else:
            self._dd = displayers['C'](val)

        return self._dd

    @property
    def date_parser(self):
        """
        Return the locale's date parser; if it hasn't already been
        cached, set it from datehandler.LANG_TO_PARSER. If one isn't
        available for the selected locale, attempt to fall back on the
        first_instance's locale before settling on the 'C' parser.
        NB: This is the getter for the date_parser property
        """
        if self._dp:
            return self._dp

        from gramps.gen.datehandler import LANG_TO_PARSER as parsers
        _first = self._GrampsLocale__first_instance
        if self.calendar in parsers:
            self._dp = parsers[self.calendar]()
        elif self.calendar[:2] in parsers:
            self._dp = parsers[self.calendar]()
        elif self != _first and _first.calendar in parsers:
            self._dp = parsers[_first.calendar]()
        elif self != _first and _first.calendar[:2] in parsers:
            self._dp = parsers[_first.calendar[:2]]()
        else:
            self._dp = parsers['C']()

        return self._dp

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------

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


    def get_addon_translator(self, filename, domain="addon",
                             languages=None):
        """
        Get a translator for an addon.

        filename - filename of a file in directory with full path, or
                   None to get from self.
        domain   - the name of the .mo file under the LANG/LC_MESSAGES dir
        languages - a list of languages to force
        returns  - a gettext.translation object

        Example:
        _ = glocale.get_addon_translator(languages=["fr_BE.utf8"]).gettext

        See the python gettext documentation.
        Assumes path/filename
            path/locale/LANG/LC_MESSAGES/addon.mo.
        """
        gramps_translator = self._get_translation()

        path = self.localedir
        if filename:
            path = os.path.join(os.path.dirname(os.path.abspath(filename)), "locale")
        if languages:
            addon_translator = self._get_translation(domain,
                                                     path,
                                                     languages=languages)
        else:
            addon_translator = self._get_translation(domain, path)
        gramps_translator.add_fallback(addon_translator)
        return gramps_translator # with a language fallback

    def get_available_translations(self, localedir = None, localedomain = None):
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
            localedomain = 'gramps'

        for langdir in os.listdir(self.localedir):
            mofilename = os.path.join(localedir, langdir,
                                      "LC_MESSAGES",
                                      "%s.mo" % localedomain )
            if os.path.exists(mofilename):
                languages.append(langdir)

        languages.sort()

        return languages

    def check_available_translations(self, locale):
        """
        Test a locale for having a translation available
        locale -- string with standard language code, locale code, or name
        """
        if not self.localedir:
            return None
        #Note that this isn't a typo for self.language; self.languages
        #is cached so we don't have to query the file system every
        #time this function is called.
        if not hasattr(self, 'languages'):
            self.languages = self.get_available_translations()

        if not locale:
            return None

        if locale[:5] in self.languages:
            return locale[:5]
        if locale[:2] in self.languages:
            return locale[:2]

        return None

    def get_language_dict(self):
        '''
        return a dictionary of language names : codes for use by language
        pickers.
        '''
        langs = {}
        for code in self.get_available_translations():
            langs[self._get_language_string(code)] = code

        return langs


    def trans_objclass(self, objclass_str):
        """
        Translates objclass_str into "... %s", where objclass_str
        is 'Person', 'person', 'Family', 'family', etc.
        """
        _ = self.translation.gettext
        objclass = objclass_str.lower()
        if objclass == "person":
            return _("the person")
        elif objclass == "family":
            return _("the family")
        elif objclass == "place":
            return _("the place")
        elif objclass == "event":
            return _("the event")
        elif objclass == "repository":
            return _("the repository")
        elif objclass == "note":
            return _("the note")
        elif objclass in ["media", "mediaobject"]:
            return _("the media")
        elif objclass == "source":
            return _("the source")
        elif objclass == "filter":
            return _("the filter")
        else:
            return _("See details")

    def getfilesystemencoding(self):
        """
        If the locale isn't configured correctly, this will return
        'ascii' or 'ANSI_X3.4-1968' or some other unfortunate
        result. Current unix systems all encode filenames in utf-8,
        and Microsoft Windows uses utf-16 (which they call mbcs). Make
        sure we return the right value.
        """
        encoding = sys.getfilesystemencoding()

        if encoding in ("utf-8", "UTF-8", "utf8", "UTF8", "mbcs", "MBCS"):
            return encoding

        return "utf-8"

    def sort_key(self, string):
        """
        Return a value suitable to pass to the "key" parameter of sorted()
        """

        if HAVE_ICU and self.collator:
            #ICU can digest strings and unicode
            return self.collator.getCollationKey(string).getByteArray()
        else:
            try:
                if sys.version_info[0] < 3 and isinstance(string, unicode):
                    key = locale.strxfrm(string.encode("utf-8", "replace"))
                else:
                    key = locale.strxfrm(string)

            except Exception as err:
                LOG.warn("Failed to obtain key for %s because %s",
                         self.collation, str(err))
                return string
            return key

    def strcoll(self, string1, string2):
        """
        Given two localized strings, compare them and return -1 if
        string1 would sort first, 1 if string2 would, and 0 if
        they are the same.
        """
        key1 = self.sort_key(string1)
        key2 = self.sort_key(string2)
        return (-1 if key1 < key2 else (1 if key1 > key2 else 0))


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
        from gramps.gen.lib.grampstype import GrampsType
        return GrampsType.xml_str(name)

    def format(self, format, val, grouping=False, monetary=False):
        """
        Format a number in the current numeric locale. See python's
        locale.format for details.  ICU's formatting codes are
        incompatible with locale's, so just use locale.format for now.
        """
        return locale.format(format, val, grouping, monetary)

    def format_string(self, format, val, grouping=False):
        """
        Format a string in the current numeric locale. See python's
        locale.format_string for details.  ICU's message formatting codes are
        incompatible with locale's, so just use locale.format_string
        for now.
        """
        return locale.format_string(format, val, grouping)

    def float(self, val):
        """
        Parse a string to a floating point number. Uses locale.atof(),
        in future with ICU present will use icu.NumberFormat.parse().
        """
        try:
            return locale.atof(val)
        except ValueError:
            point = locale.localeconv()['decimal_point']
            sep = locale.localeconv()['thousands_sep']
            try:
                if point == ',':
                    return locale.atof(val.replace(' ', sep).replace('.', sep))
                elif point == '.':
                    return locale.atof(val.replace(' ', sep).replace(',', sep))
                else:
                    return None
            except ValueError:
                return None

#-------------------------------------------------------------------------
#
# Translations Classes
#
#-------------------------------------------------------------------------
class GrampsTranslations(gettext.GNUTranslations):
    """
    Overrides and extends gettext.GNUTranslations. See the Python gettext
    "Class API" documentation for how to use this.
    """
    def language(self):
        """
        Return the target languge of this translations object.
        """
        return self._language

    def gettext(self, msgid):
        """
        Obtain translation of gettext, return a unicode object
        :param msgid: The string to translated.
        :type msgid: unicode
        :returns: Translation or the original.
        :rtype: unicode
        """
        # If msgid =="" then gettext will return po file header
        # and that's not what we want.
        if len(msgid.strip()) == 0:
            return msgid
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ugettext(self, msgid)
        else:
            return gettext.GNUTranslations.gettext(self, msgid)

    def ngettext(self, singular, plural, num):
        """
        The translation of singular/plural is returned unless the translation is
        not available and the singular contains the separator. In that case,
        the returned value is the singular.

        :param singular: The singular form of the string to be translated.
                         may contain a context seperator
        :type singular: unicode
        :param plural: The plural form of the string to be translated.
        :type plural: unicode
        :param num: the amount for which to decide the translation
        :type num: int
        :returns: Translation or the original.
        :rtype: unicode
        """
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ungettext(self, singular,
                                                     plural, num)
        else:
            return gettext.GNUTranslations.ngettext(self, singular,
                                                    plural, num)

    def sgettext(self, msgid, sep='|'):
        """
        Strip the context used for resolving translation ambiguities.

        The translation of msgid is returned unless the translation is
        not available and the msgid contains the separator. In that case,
        the returned value is the portion of msgid following the last
        separator. Default separator is '|'.

        :param msgid: The string to translated.
        :type msgid: unicode
        :param sep: The separator marking the context.
        :type sep: unicode
        :returns: Translation or the original with context stripped.
        :rtype: unicode
        """
        msgval = self.gettext(msgid)
        if msgval == msgid:
            sep_idx = msgid.rfind(sep)
            msgval = msgid[sep_idx+1:]
        return msgval

class GrampsNullTranslations(gettext.NullTranslations):
    """
    Extends gettext.NullTranslations to provide the sgettext method.

    Note that it's necessary for msgid to be unicode. If it's not,
    neither will be the returned string.
    """
    def sgettext(self, msgid, sep='|'):
        msgval = self.gettext(msgid)
        if msgval == msgid:
            sep_idx = msgid.rfind(sep)
            msgval = msgid[sep_idx+1:]
        return msgval

    def language(self):
        """
        The null translation returns the raw msgids, which are in English
        """
        return "en"
